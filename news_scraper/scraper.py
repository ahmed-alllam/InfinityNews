import re
import time
from urllib.parse import urljoin

import dateparser
import pytz
import requests
from bs4 import BeautifulSoup

from news.models import Source, Post, PostTag, Category


class BaseNewsScraper:
    def __init__(self, title, base_url, categories, format='html.parser',
                 list_container_tag_name='', list_container_attr_name='', list_container_attr_value='',
                 container_tag_name='', container_attr_name='', container_attr_value='',
                 title_tag_name='', title_attr_name='', title_attr_value='',
                 description_tag_name='', description_attr_name='', description_attr_value='',
                 body_tag_name='', body_attr_name='', body_attr_value='',
                 image_tag_name='img', image_attr_name='', image_attr_value='',
                 timestamp_tag_name='', timestamp_attr_name='', timestamp_attr_value='',
                 url_tag_name='a', url_attr_name='', url_attr_value='',
                 tags_tag_name='', tags_attr_name='', tags_attr_value='',
                 time_between_requests=0, max_scraped_pages=3, timezone='EET'):

        self.title = title
        self.base_url = base_url
        self.categories = categories
        self.format = format
        self.list_container_tag_name = list_container_tag_name  # usually div
        self.list_container_attr_name = list_container_attr_name  # usually id or class
        self.list_container_attr_value = list_container_attr_value
        self.container_tag_name = container_tag_name
        self.container_attr_name = container_attr_name
        self.container_attr_value = container_attr_value
        self.title_tag_name = title_tag_name  # usually a
        self.title_attr_name = title_attr_name
        self.title_attr_value = title_attr_value
        self.description_tag_name = description_tag_name  # usually p or div
        self.description_attr_name = description_attr_name
        self.description_attr_value = description_attr_value
        self.body_tag_name = body_tag_name  # usually div or article
        self.body_attr_name = body_attr_name
        self.body_attr_value = body_attr_value
        self.image_tag_name = image_tag_name  # usually img
        self.image_attr_name = image_attr_name
        self.image_attr_value = image_attr_value
        self.timestamp_tag_name = timestamp_tag_name
        self.timestamp_attr_name = timestamp_attr_name
        self.timestamp_attr_value = timestamp_attr_value
        self.url_tag_name = url_tag_name
        self.url_attr_name = url_attr_name
        self.url_attr_value = url_attr_value
        self.tags_tag_name = tags_tag_name
        self.tags_attr_name = tags_attr_name
        self.tags_attr_value = tags_attr_value
        self.time_between_requests = time_between_requests
        self.timezone = timezone
        self.max_scraped_pages = max_scraped_pages

    def scrape(self):
        source = Source.objects.get_or_create(title=self.title)[0]
        posts = []
        for category, url in self.categories.items():
            url = urljoin(self.base_url, url)
            posts.extend(self.scrape_category(source, category, url))
        return posts

    def scrape_category(self, source, title, url):
        category = Category.objects.get_or_create(title=title)[0]
        has_next = True
        page_index = 1
        category_posts = []
        while has_next and page_index <= self.max_scraped_pages:  # won't scrape more than 3 pages by default
            time.sleep(self.time_between_requests)
            page = self.get_page_at_index(url, page_index).content
            page_posts, has_next = self.scrape_page(source, category, page)
            category_posts.extend(page_posts)
            page_index += 1
        return category_posts

    def scrape_page(self, source, category, page):
        page = BeautifulSoup(page, self.format)
        posts_list_container = self.get_posts_list_container(page)
        posts = []

        for post_container in self.get_post_container(posts_list_container):
            post, tags = self.scrape_post(source, category, post_container)
            if Post.objects.filter(source=source, category=category, title=post.title).exists():
                return posts, False
            posts.append(post)
            post.save()

            post.tags.set(tags)

        return posts, True

    def scrape_post(self, source, category, post_container):
        title = self.get_post_title(post_container)
        url = self.get_post_url(post_container)

        time.sleep(self.time_between_requests)
        detailed_post_container = BeautifulSoup(requests.get(url).content, self.format)

        description = self.get_post_description(post_container, detailed_post_container)
        image = self.get_post_image(post_container, detailed_post_container)
        body = self.get_post_body(detailed_post_container)
        timestamp = self.get_post_timestamp(post_container, detailed_post_container)
        tags = [PostTag.objects.get_or_create(tag=tag)[0]
                for tag in self.get_post_tag_names(post_container, detailed_post_container)]

        post = Post(source=source, category=category, title=title, image=image,
                    detail_url=url, description=description, timestamp=timestamp,
                    body=body)

        return post, tags

    def get_posts_list_container(self, page):
        return page.find(self.list_container_tag_name,
                         {self.list_container_attr_name: self.list_container_attr_value})

    def get_post_container(self, posts_list_container):
        return posts_list_container.find_all(self.container_tag_name,
                                             {self.container_attr_name: self.container_attr_value})

    def get_post_title(self, post_container):
        return post_container.find(self.title_tag_name,
                                   {self.title_attr_name: self.title_attr_value}).text.strip()

    def get_post_url(self, post_container):
        return urljoin(self.base_url,
                       post_container.find(self.url_tag_name,
                                           {self.url_attr_name: self.url_attr_value})['href'])

    def get_post_description(self, post_container, detailed_post_container):
        return post_container.find(self.description_tag_name,
                                   {self.description_attr_name: self.description_attr_value}).text.strip()

    def get_post_image(self, post_container, detailed_post_container):
        return urljoin(self.base_url, post_container.find(self.image_tag_name)['src'])

    def get_post_body(self, post_page):
        return str(post_page.find(self.body_tag_name, {self.body_attr_name: self.body_attr_value})).strip()

    def get_post_timestamp(self, post_container, detailed_post_container):
        timestamp = post_container.find(self.timestamp_tag_name,
                                        {self.timestamp_attr_name: self.timestamp_attr_value}).text.strip()
        parsed_timestamp = dateparser.parse(timestamp)
        if self.timezone:
            tz = pytz.timezone(self.timezone)
            parsed_timestamp = parsed_timestamp.replace(tzinfo=tz).astimezone(pytz.utc)

        return parsed_timestamp

    def get_post_tag_names(self, post_container, detailed_post_container):
        tags = []
        for tag in detailed_post_container.find(self.tags_tag_name,
                                                {self.tags_attr_name: self.tags_attr_value}).find_all('a'):
            tags.append(tag.text.strip())
        return tags

    def get_page_at_index(self, url, index):
        return requests.get(self.get_page_url_at_index(url, index))

    def get_page_url_at_index(self, url, index):
        raise NotImplementedError()


class Youm7Scraper(BaseNewsScraper):
    def __init__(self):
        super().__init__('youm7', 'https://www.youm7.com',
                         {'Breaking News': 'Section/أخبار-عاجلة/65/x',
                          'Politics': 'Section/سياسة/319/x', 'Reports': 'Section/تقارير-مصرية/97/x',
                          'Culture': 'Section/ثقافة/94/x', 'Accidents': 'Section/حوادث/203/x',
                          'Finance': 'Section/اقتصاد-وبورصة/297/x',
                          'Investigations': 'Section/تحقيقات-وملفات/12/x',
                          'Sports': 'Section/أخبار-الرياضة/298/x',
                          'Football': 'Section/كرة-عالمية/332/x',
                          'Arabic News': 'Section/أخبار-عربية/88/x',
                          'Global News': 'Section/أخبار-عالمية/286/x',
                          'Caricature': 'Section/كاريكاتير-اليوم/192/x',
                          'Art': 'Section/فن/48/x', 'TV': 'Section/تليفزيون/251/x',
                          'Woman': 'Section/المرأة-والمنوعات/89/x',
                          'Albums': 'Section/ألبومات-اليوم-السابع/291/x',
                          'Health': 'Section/صحة-وطب/245/x',
                          'Technology': 'Section/علوم-و-تكنولوجيا/328/x',
                          'States': 'Section/أخبار-المحافظات/296/x'},
                         list_container_tag_name='div', list_container_attr_name='id',
                         list_container_attr_value='paging', container_tag_name='div',
                         container_attr_name='class', container_attr_value='col-xs-12 bigOneSec',
                         title_tag_name='a', description_tag_name='p', body_tag_name='div',
                         body_attr_name='id', body_attr_value='articleBody',
                         timestamp_tag_name='span', timestamp_attr_name='class',
                         timestamp_attr_value='newsDate', tags_tag_name='div',
                         tags_attr_name='class', tags_attr_value='tags')

    def get_post_title(self, post_container):
        return post_container.find('h3').find(self.title_tag_name).text

    def get_post_timestamp(self, post_container, detailed_post_container):
        timestamp = post_container.find(self.timestamp_tag_name,
                                        {self.timestamp_attr_name: re.compile(self.timestamp_attr_value + '.*')}).text
        parsed_timestamp = dateparser.parse(timestamp)
        if self.timezone:
            tz = pytz.timezone(self.timezone)
            parsed_timestamp = parsed_timestamp.replace(tzinfo=tz).astimezone(pytz.utc)

        return parsed_timestamp

    def get_page_url_at_index(self, url, index):
        return url.replace('x', str(index))


youm7_scraper = Youm7Scraper()
