import json
import re
import time
from urllib.parse import urljoin

import dateparser
import pytz
import requests
from bs4 import BeautifulSoup, Tag

from news.models import Source, Post, PostTag, Category


class BaseNewsScraper:
    def __init__(self, title, base_url, categories, format='html.parser',
                 list_container_tag_name='', list_container_attr_name='', list_container_attr_value='',
                 container_tag_name='', container_attr_name='', container_attr_value='',
                 title_tag_name='', title_attr_name='',
                 title_attr_value='', title_json_name='',
                 description_tag_name='p', description_attr_name='',
                 description_attr_value='', description_json_name='',
                 body_tag_name='', body_attr_name='', body_attr_value='',
                 image_tag_name='img', image_attr_name='',
                 image_attr_value='', image_json_name='',
                 timestamp_tag_name='', timestamp_attr_name='',
                 timestamp_attr_value='', timestamp_json_name='',
                 url_tag_name='a', url_attr_name='',
                 url_attr_value='', url_json_name='',
                 tags_tag_name='', tags_attr_name='',
                 tags_attr_value='', time_between_requests=0,
                 max_scraped_pages=3, timezone='EET'):

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
        self.title_json_name = title_json_name
        self.description_tag_name = description_tag_name  # usually p or div
        self.description_attr_name = description_attr_name
        self.description_attr_value = description_attr_value
        self.description_json_name = description_json_name
        self.body_tag_name = body_tag_name  # usually div or article
        self.body_attr_name = body_attr_name
        self.body_attr_value = body_attr_value
        self.image_tag_name = image_tag_name  # usually img
        self.image_attr_name = image_attr_name
        self.image_attr_value = image_attr_value
        self.image_json_name = image_json_name
        self.timestamp_tag_name = timestamp_tag_name
        self.timestamp_attr_name = timestamp_attr_name
        self.timestamp_attr_value = timestamp_attr_value
        self.timestamp_json_name = timestamp_json_name
        self.url_tag_name = url_tag_name
        self.url_attr_name = url_attr_name
        self.url_attr_value = url_attr_value
        self.url_json_name = url_json_name
        self.tags_tag_name = tags_tag_name
        self.tags_attr_name = tags_attr_name
        self.tags_attr_value = tags_attr_value
        self.time_between_requests = time_between_requests
        self.timezone = timezone
        self.max_scraped_pages = max_scraped_pages
        self.session = requests.session()

    def scrape(self):
        source = Source.objects.get_or_create(title=self.title)[0]
        posts = []
        for category, url in self.categories.items():
            url = self.get_category_url(category, url)
            posts.extend(self.scrape_category(source, category, url))
        return posts

    def scrape_category(self, source, title, url):
        category = Category.objects.get_or_create(title=title)[0]
        has_next = True
        page_index = 1
        category_posts = []
        while has_next and page_index <= self.get_max_scraped_pages(title):  # won't scrape more than 3 pages by default
            try:
                time.sleep(self.time_between_requests)
                page = self.get_page_at_index(url, page_index)
                page_posts, has_next = self.scrape_page(source, category, url, page)
            except AssertionError:
                print("Error Parsing Page")
                continue
            finally:
                page_index += 1

            category_posts.extend(page_posts)
        return category_posts

    def scrape_page(self, source, category, category_url, page):
        posts = []

        for posts_list_container in self.get_posts_list_containers(page):
            for post_container in self.get_post_containers(posts_list_container):
                try:
                    post, tags = self.scrape_post(source, category, category_url, post_container)
                except AssertionError:
                    print("Error Parsing Post")
                    continue

                if Post.objects.filter(source=source, category=category, title=post.title,
                                       detail_url=post.detail_url).exists():
                    return posts, False
                posts.append(post)
                post.save()

                post.tags.set(tags)

        return posts, True

    def scrape_post(self, source, category, category_url, post_container):
        title = self.get_post_title(post_container)
        url = self.get_post_url(post_container, category_url)

        time.sleep(self.time_between_requests)
        detailed_post_container = BeautifulSoup(self.session.get(url).content, 'html.parser')

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

    def get_max_scraped_pages(self, category):
        return self.max_scraped_pages

    def get_category_url(self, title, url):
        return urljoin(self.base_url, url)

    def get_page_at_index(self, url, index):
        response = self.session.get(self.get_page_url_at_index(url, index))

        assert response.status_code == 200

        if self.format == 'html.parser':
            return BeautifulSoup(response.content, self.format)
        elif self.format == 'json':
            return json.loads(response.content)

    def get_page_url_at_index(self, url, index):
        raise NotImplementedError()

    def get_posts_list_containers(self, page):
        containers = []
        if isinstance(page, BeautifulSoup):
            attrs = {}
            if self.list_container_attr_name and self.list_container_attr_value:
                attrs = {self.list_container_attr_name: re.compile(self.list_container_attr_value + '.*')}

            containers = page.find_all(self.list_container_tag_name, attrs)

        elif isinstance(page, list):
            containers = [page, ]

        assert containers
        return containers

    def get_post_containers(self, posts_list_container):
        containers = []
        if isinstance(posts_list_container, Tag):
            attrs = {}
            if self.container_attr_name and self.container_attr_value:
                attrs = {self.container_attr_name: re.compile(self.container_attr_value + '.*')}

            containers = posts_list_container.find_all(self.container_tag_name, attrs)

        elif isinstance(posts_list_container, list):
            containers = posts_list_container

        assert containers
        return containers

    def get_post_title(self, post_container):
        if isinstance(post_container, Tag):
            attrs = {}
            if self.title_attr_name and self.title_attr_value:
                attrs = {self.title_attr_name: re.compile(self.title_attr_value + '.*')}

            title = post_container.find(self.title_tag_name, attrs)
            return title.text.strip() if title else ''

        elif isinstance(post_container, dict):
            return post_container.get(self.title_json_name, '')

    def get_post_url(self, post_container, category_url):
        url = ''

        if isinstance(post_container, Tag):
            attrs = {}
            if self.url_attr_name and self.url_attr_value:
                attrs = {self.url_attr_name: re.compile(self.url_attr_value + '.*')}

            url = post_container.find(self.url_tag_name, attrs)['href']

        elif isinstance(post_container, dict):
            url = post_container.get(self.url_json_name, '')

        return urljoin(self.base_url, url)

    def get_post_description(self, post_container, detailed_post_container):
        if isinstance(post_container, Tag):
            attrs = {}
            if self.description_attr_name and self.description_attr_value:
                attrs = {self.description_attr_name: re.compile(self.description_attr_value + '.*')}

            description = post_container.find(self.description_tag_name, attrs)

            return description.text.strip() if description else ''

        elif isinstance(post_container, dict):
            return post_container.get(self.description_json_name, '')

    def get_post_image(self, post_container, detailed_post_container):
        image = ''

        if isinstance(post_container, Tag):
            attrs = {}
            if self.image_attr_name and self.image_attr_value:
                attrs = {self.image_attr_name: re.compile(self.image_attr_value + '.*')}

            image = post_container.find(self.image_tag_name, attrs)['src']

        elif isinstance(post_container, dict):
            image = post_container.get(self.image_json_name, '')

        return urljoin(self.base_url, image)

    def get_post_body(self, post_page):
        attrs = {}
        if self.body_attr_name and self.body_attr_value:
            attrs = {self.body_attr_name: re.compile(self.body_attr_value + '.*')}

        body = post_page.find(self.body_tag_name, attrs)
        return str(body).strip() if body else ''

    def get_post_timestamp(self, post_container, detailed_post_container):
        timestamp = ''

        if isinstance(post_container, Tag):
            attrs = {}
            if self.timestamp_attr_name and self.timestamp_attr_value:
                attrs = {self.timestamp_attr_name: re.compile(self.timestamp_attr_value + '.*')}

            timestamp = post_container.find(self.timestamp_tag_name, attrs)

        elif isinstance(post_container, dict):
            timestamp = post_container.get(self.timestamp_json_name, '')

        if not timestamp:
            return None

        timestamp = timestamp.text.strip()

        parsed_timestamp = dateparser.parse(timestamp)
        if self.timezone:
            tz = pytz.timezone(self.timezone)
            parsed_timestamp = parsed_timestamp.replace(tzinfo=tz).astimezone(pytz.utc)

        return parsed_timestamp

    def get_post_tag_names(self, post_container, detailed_post_container):
        tags = []
        attrs = {}
        if self.tags_attr_name and self.tags_attr_value:
            attrs = {self.tags_attr_name: re.compile(self.tags_attr_value + '.*')}

        tags_container = detailed_post_container.find(self.tags_tag_name, attrs)

        if tags_container:
            for tag in tags_container.find_all('a'):
                tags.append(tag.text.strip())
        return tags


class Youm7Scraper(BaseNewsScraper):
    def __init__(self):
        super().__init__('اليوم السابع', 'https://www.youm7.com',
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
                         title_tag_name='h3', body_tag_name='div',
                         body_attr_name='id', body_attr_value='articleBody',
                         timestamp_tag_name='span', timestamp_attr_name='class',
                         timestamp_attr_value='newsDate', tags_tag_name='div',
                         tags_attr_name='class', tags_attr_value='tags')

    def get_page_url_at_index(self, url, index):
        return url.replace('x', str(index))


youm7_scraper = Youm7Scraper()


class FoxNewsScraper(BaseNewsScraper):
    def __init__(self):
        super().__init__('Fox News', 'https://www.foxnews.com',
                         {'US News': 'us', 'Global News': 'world', 'Opinion': 'opinion',
                          'Politics': 'politics', 'Entertainment': 'entertainment'},
                         title_json_name='title', description_json_name='description',
                         image_json_name='imageUrl', timestamp_json_name='publicationDate',
                         body_tag_name='div', body_attr_name='class',
                         body_attr_value='article-body', url_json_name='url',
                         timezone='UTC', format='json')

    # todo: handle video posts

    def get_post_tag_names(self, post_container, detailed_post_container):
        return [post_container.get('category', {}).get('name', ''), ]

    def get_category_url(self, title, url):
        category_name = self.categories[title]
        return urljoin(self.base_url, ('api/article-search?isCategory=true&isTag=false' +
                                       '&isKeyword=false&isFixed=false&isFeedUrl=false&' +
                                       'searchSelected={}&contentTypes=%7B%22interactive' +
                                       '%22:true,%22slideshow%22:true,%22video%22:true,' +
                                       '%22article%22:true%7D&size=30').format(category_name))

    def get_page_url_at_index(self, url, index):
        return url + ('&offset=%d' % (30 * (index - 1)))


fox_news_scraper = FoxNewsScraper()


class FoxBusinessScraper(BaseNewsScraper):
    def __init__(self):
        super().__init__('Fox Business', 'https://www.foxbusiness.com',
                         {'Money': 'money', 'Markets': 'markets', 'Lifestyle': 'lifestyle',
                          'Real Estate': 'real-estate', 'Technology': 'technology',
                          'Sports': 'sports'},
                         list_container_tag_name='div', list_container_attr_name='class',
                         list_container_attr_value='collection collection-river content',
                         container_tag_name='article', container_attr_name='class',
                         container_attr_value='article', title_tag_name='h3',
                         title_attr_name='class', title_attr_value='title',
                         description_attr_name='class', description_attr_value='dek',
                         timestamp_tag_name='time', timestamp_attr_name='class',
                         timestamp_attr_value='time', tags_tag_name='span',
                         tags_attr_name='class', tags_attr_value='pill-text',
                         body_tag_name='div', body_attr_name='class',
                         body_attr_value='article-body', timezone='UTC', max_scraped_pages=1)

    def get_post_tag_names(self, post_container, detailed_post_container):
        tag = post_container.find(self.tags_tag_name,
                                  {self.tags_attr_name:
                                       re.compile(self.tags_attr_value + '.*')})

        return (tag.text.strip()) if tag else ()

    def get_page_url_at_index(self, url, index):
        return url


fox_business_scraper = FoxBusinessScraper()


class ShoroukNewsScraper(BaseNewsScraper):
    def __init__(self):
        super().__init__('الشروق', 'https://www.shorouknews.com',
                         {'Egypt News': 'egypt', 'Politics': 'Politics',
                          'Sports': 'sports', 'Art': 'art', 'Money': 'Economy',
                          'Accidents': 'accidents', 'TV': 'tv', 'Woman': 'ladies',
                          'Technology': 'variety/Internet-Comm', 'Science': 'variety/sciences',
                          'Health': 'variety/health', 'Cars': 'auto', 'Culture': 'Culture'},
                         list_container_tag_name='ul', list_container_attr_name='class',
                         list_container_attr_value='listing', container_tag_name='li',
                         title_tag_name='div', title_attr_name='class', title_attr_value='text',
                         timestamp_tag_name='span', body_tag_name='div', body_attr_name='class',
                         body_attr_value='eventContent eventContentNone', tags_tag_name='div',
                         tags_attr_name='class', tags_attr_value='relatedWords')
        self.__VIEWSTATE = ''
        self.__VIEWSTATEGENERATOR = ''
        self.__EVENTVALIDATION = ''

    def get_page_at_index(self, url, index):
        if index == 1:
            response = self.session.get(self.get_page_url_at_index(url, index))
        else:
            response = self.session.post(self.get_page_url_at_index(url, index), data={
                '__VIEWSTATE': self.__VIEWSTATE,
                '__VIEWSTATEGENERATOR': self.__VIEWSTATEGENERATOR,
                '__EVENTTARGET': 'ctl00$ctl00$Body$Body$AspNetPager',
                '__EVENTARGUMENT': index,
                '__EVENTVALIDATION': self.__EVENTVALIDATION,
            })

        assert response.status_code == 200

        page = BeautifulSoup(response.content, self.format)

        # hidden fields to send in next request
        self.__VIEWSTATE = str(page.find('input', type='hidden', id='__VIEWSTATE')['value'])
        self.__VIEWSTATEGENERATOR = str(page.find('input', type='hidden', id='__VIEWSTATEGENERATOR')['value'])
        self.__EVENTVALIDATION = str(page.find('input', type='hidden', id='__EVENTVALIDATION')['value'])

        return page

    def get_page_url_at_index(self, url, index):
        return url

    def get_post_title(self, post_container):
        title_container = post_container.find(self.title_tag_name,
                                              {self.title_attr_name: self.title_attr_value})
        title = title_container.find('a') if title_container else None
        return title.text.strip() if title else ''


shorouk_news_scraper = ShoroukNewsScraper()
