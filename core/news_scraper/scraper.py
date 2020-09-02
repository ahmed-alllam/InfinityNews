import json
import re
import time
from abc import ABC
from urllib.parse import urljoin

import dateparser
import pytz
import requests
from bs4 import BeautifulSoup

from news.models import Source, Post, PostTag, Category


class BaseNewsScraper(ABC):
    def __init__(self, title, base_url, categories, time_between_requests=0,
                 max_scraped_pages=2, timezone='EET', body_tag_name='',
                 body_attr_name='', body_attr_value=''):
        self.title = title
        self.base_url = base_url
        self.categories = categories
        self.time_between_requests = time_between_requests
        self.timezone = timezone
        self.max_scraped_pages = max_scraped_pages
        self.session = requests.session()
        self.body_tag_name = body_tag_name  # usually div or article
        self.body_attr_name = body_attr_name
        self.body_attr_value = body_attr_value

    def scrape(self):
        source = Source.objects.get_or_create(title=self.title, website=self.base_url)[0]
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

                if Post.objects.filter(source=source, category=category, detail_url=post.detail_url):
                    return posts, False
                posts.append(post)
                post.save()

                post.tags.set(tags)

        return posts, True

    def scrape_post(self, source, category, category_url, post_container):
        title = self.get_post_title(post_container)
        url = self.get_post_url(post_container, category_url)

        time.sleep(self.time_between_requests)
        detailed_post_container = self.get_post_detailed_container(url)

        description = self.get_post_description(post_container, detailed_post_container)
        thumbnail = self.get_post_thumbnail(post_container, detailed_post_container)
        full_image = self.get_post_full_image(post_container, detailed_post_container) or thumbnail

        print('Scraped post from: ' + source.title + ' in category: ' + category.title + ' with title: ' + title)

        body = self.get_post_body(detailed_post_container)
        if body:
            body = self.format_post_body(*body)

        timestamp = self.get_post_utc_timestamp(post_container, detailed_post_container)
        tags = [PostTag.objects.get_or_create(tag=tag)[0]
                for tag in self.get_post_tags(post_container, detailed_post_container)]

        post = Post(source=source, category=category, title=title, thumbnail=thumbnail,
                    full_image=full_image, detail_url=url, description=description,
                    timestamp=timestamp, body=body)

        return post, tags

    def get_max_scraped_pages(self, category):
        return self.max_scraped_pages

    def get_category_url(self, title, url):
        raise NotImplementedError()

    def get_page_at_index(self, url, index):
        raise NotImplementedError()

    def get_page_url_at_index(self, url, index):
        raise NotImplementedError()

    def get_posts_list_containers(self, page):
        raise NotImplementedError()

    def get_post_containers(self, posts_list_container):
        raise NotImplementedError()

    def get_post_title(self, post_container):
        raise NotImplementedError()

    def get_post_url(self, post_container, category_url):
        raise NotImplementedError()

    def get_post_description(self, post_container, detailed_post_container):
        raise NotImplementedError()

    def get_post_thumbnail(self, post_container, detailed_post_container):
        raise NotImplementedError()

    def get_post_full_image(self, post_container, detailed_post_container):
        raise NotImplementedError()

    def get_post_detailed_container(self, url):
        return BeautifulSoup(self.session.get(url).content, 'lxml')

    def get_post_body(self, post_page):
        attrs = {}
        if self.body_attr_name and self.body_attr_value:
            attrs = {self.body_attr_name: re.compile(self.body_attr_value + '.*')}

        post_body = post_page.find(self.body_tag_name, attrs) or ''
        style_tags = post_page.find_all('link')
        style_tags.extend(post_page.find_all('style'))

        styles = ''
        for tag in style_tags:
            styles += str(tag)

        return post_body, styles

    def format_post_body(self, body, styles):
        if body:
            for tag in body.find_all(re.compile("div|span|p")):
                text = tag.text
                if not text or (isinstance(text, str) and not text.strip()):
                    tag.extract()

            [tag.extract() for tag in body.select("br:last-child") or []]

            full_body = body.prettify()

            required_style = """<style>:not(head) { max-width: 100%; object-fit: scale-down;
                margin: auto; line-height: 1.8;} </style>"""

            return '<head>' + required_style + styles + '</head>' + '<body dir=\"auto\">' + full_body + '</body>'
        else:
            return ''

    def get_post_utc_timestamp(self, post_container, detailed_post_container):
        timestamp = self.get_post_timestamp(post_container, detailed_post_container)

        if not timestamp:
            return None

        parsed_timestamp = dateparser.parse(timestamp)

        if self.timezone:
            tz = pytz.timezone(self.timezone)
            parsed_timestamp = parsed_timestamp.replace(tzinfo=tz).astimezone(pytz.utc)

        return parsed_timestamp

    def get_post_timestamp(self, post_container, detailed_post_container):
        raise NotImplementedError()

    def get_post_tags(self, post_container, detailed_post_container):
        raise NotImplementedError()


class HtmlNewsScraper(BaseNewsScraper):
    def __init__(self, list_container_tag_name='', list_container_attr_name='',
                 list_container_attr_value='', container_tag_name='',
                 container_attr_name='', container_attr_value='',
                 title_tag_name='', title_attr_name='', title_attr_value='',
                 description_tag_name='p', description_attr_name='', description_attr_value='',
                 thumbnail_tag_name='img', thumbnail_attr_name='', thumbnail_attr_value='',
                 full_image_tag_name='img', full_image_attr_name='', full_image_attr_value='',
                 timestamp_tag_name='', timestamp_attr_name='', timestamp_attr_value='',
                 url_tag_name='a', url_attr_name='', url_attr_value='', tags_tag_name='',
                 tags_attr_name='', tags_attr_value='', **kwargs):

        super().__init__(**kwargs)
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
        self.thumbnail_tag_name = thumbnail_tag_name  # usually img
        self.thumbnail_attr_name = thumbnail_attr_name
        self.thumbnail_attr_value = thumbnail_attr_value
        self.full_image_tag_name = full_image_tag_name  # usually img
        self.full_image_attr_name = full_image_attr_name
        self.full_image_attr_value = full_image_attr_value
        self.timestamp_tag_name = timestamp_tag_name
        self.timestamp_attr_name = timestamp_attr_name
        self.timestamp_attr_value = timestamp_attr_value
        self.url_tag_name = url_tag_name
        self.url_attr_name = url_attr_name
        self.url_attr_value = url_attr_value
        self.tags_tag_name = tags_tag_name
        self.tags_attr_name = tags_attr_name
        self.tags_attr_value = tags_attr_value

    def get_category_url(self, title, url):
        return urljoin(self.base_url, url)

    def get_page_at_index(self, url, index):
        response = self.session.get(self.get_page_url_at_index(url, index))

        assert response.status_code == 200
        return BeautifulSoup(response.content, 'lxml')

    def get_page_url_at_index(self, url, index):
        raise NotImplementedError()

    def get_posts_list_containers(self, page):
        attrs = {}
        if self.list_container_attr_name and self.list_container_attr_value:
            attrs = {self.list_container_attr_name: re.compile(self.list_container_attr_value + '.*')}

        containers = page.find_all(self.list_container_tag_name, attrs)

        assert containers
        return containers

    def get_post_containers(self, posts_list_container):
        attrs = {}
        if self.container_attr_name and self.container_attr_value:
            attrs = {self.container_attr_name: re.compile(self.container_attr_value + '.*')}

        containers = posts_list_container.find_all(self.container_tag_name, attrs)

        assert containers
        return containers

    def get_post_title(self, post_container):
        attrs = {}
        if self.title_attr_name and self.title_attr_value:
            attrs = {self.title_attr_name: re.compile(self.title_attr_value + '.*')}

        title = post_container.find(self.title_tag_name, attrs)
        return title.text.strip() if title else ''

    def get_post_url(self, post_container, category_url):
        attrs = {}
        if self.url_attr_name and self.url_attr_value:
            attrs = {self.url_attr_name: re.compile(self.url_attr_value + '.*')}

        url = post_container.find(self.url_tag_name, attrs)['href']

        return urljoin(self.base_url, url)

    def get_post_description(self, post_container, detailed_post_container):
        attrs = {}
        if self.description_attr_name and self.description_attr_value:
            attrs = {self.description_attr_name: re.compile(self.description_attr_value + '.*')}

        description = post_container.find(self.description_tag_name, attrs)

        return description.text.strip() if description else ''

    def get_post_thumbnail(self, post_container, detailed_post_container):
        attrs = {}
        if self.thumbnail_attr_name and self.thumbnail_attr_value:
            attrs = {self.thumbnail_attr_name: re.compile(self.thumbnail_attr_value + '.*')}

        thumbnail = post_container.find(self.thumbnail_tag_name, attrs)['src']

        if thumbnail.startswith('http://'):
            thumbnail = thumbnail.replace('http://', 'https://')

        return urljoin(self.base_url, thumbnail)

    def get_post_full_image(self, post_container, detailed_post_container):
        attrs = {}
        if self.full_image_attr_name and self.full_image_attr_value:
            attrs = {self.full_image_attr_name: re.compile(self.full_image_attr_value + '.*')}

        full_image = detailed_post_container.find(self.full_image_tag_name, attrs)

        if not full_image:
            return ''

        full_image = full_image['src']

        if full_image.startswith('http://'):
            full_image = full_image.replace('http://', 'https://')

        return urljoin(self.base_url, full_image)

    def get_post_timestamp(self, post_container, detailed_post_container):
        attrs = {}
        if self.timestamp_attr_name and self.timestamp_attr_value:
            attrs = {self.timestamp_attr_name: re.compile(self.timestamp_attr_value + '.*')}

        return post_container.find(self.timestamp_tag_name, attrs).text.strip()

    def get_post_tags(self, post_container, detailed_post_container):
        tags = []
        attrs = {}
        if self.tags_attr_name and self.tags_attr_value:
            attrs = {self.tags_attr_name: re.compile(self.tags_attr_value + '.*')}

        tags_container = detailed_post_container.find(self.tags_tag_name, attrs)

        if tags_container:
            for tag in tags_container.find_all('a'):
                tags.append(tag.text.strip())
        return tags


class JsonNewsScraper(BaseNewsScraper):
    def __init__(self, title_json_name='', description_json_name='',
                 thumbnail_json_name='', full_image_json_name='',
                 timestamp_json_name='', url_json_name='',
                 tags_json_name='', **kwargs):
        super().__init__(**kwargs)
        self.title_json_name = title_json_name
        self.description_json_name = description_json_name
        self.thumbnail_json_name = thumbnail_json_name
        self.full_image_json_name = full_image_json_name
        self.timestamp_json_name = timestamp_json_name
        self.url_json_name = url_json_name
        self.tags_json_name = tags_json_name

    def get_category_url(self, title, url):
        raise NotImplementedError()

    def get_page_at_index(self, url, index):
        return json.loads(requests.get(self.get_page_url_at_index(url, index)).content)

    def get_page_url_at_index(self, url, index):
        raise NotImplementedError()

    def get_posts_list_containers(self, page):
        return [page, ]

    def get_post_containers(self, posts_list_container):
        return posts_list_container

    def get_post_title(self, post_container):
        return post_container.get(self.title_json_name, '')

    def get_post_url(self, post_container, category_url):
        return urljoin(self.base_url, post_container.get(self.url_json_name, ''))

    def get_post_description(self, post_container, detailed_post_container):
        return post_container.get(self.description_json_name, '')

    def get_post_thumbnail(self, post_container, detailed_post_container):
        thumbnail = post_container.get(self.thumbnail_json_name, '')

        if thumbnail.startswith('http://'):
            thumbnail = thumbnail.replace('http://', 'https://')

        return urljoin(self.base_url, thumbnail)

    def get_post_full_image(self, post_container, detailed_post_container):
        image_url = post_container.get(self.full_image_json_name, '')

        if not image_url:
            return ''

        if image_url.startswith('http://'):
            image_url = image_url.replace('http://', 'https://')

        return urljoin(self.base_url, image_url)

    def get_post_timestamp(self, post_container, detailed_post_container):
        return post_container.get(self.timestamp_json_name, '')

    def get_post_tags(self, post_container, detailed_post_container):
        return post_container.get(self.tags_json_name, '')


class Youm7Scraper(HtmlNewsScraper):
    def __init__(self):
        super().__init__(title='اليوم السابع', base_url='https://www.youm7.com',
                         categories={'Breaking': 'Section/أخبار-عاجلة/65/x',
                                     'Politics': 'Section/سياسة/319/x', 'Reports': 'Section/تقارير-مصرية/97/x',
                                     'Culture': 'Section/ثقافة/94/x', 'Accidents': 'Section/حوادث/203/x',
                                     # 'Finance': 'Section/اقتصاد-وبورصة/297/x',
                                     # 'Investigations': 'Section/تحقيقات-وملفات/12/x',
                                     'Sports': 'Section/أخبار-الرياضة/298/x',
                                     'Football': 'Section/كرة-عالمية/332/x',
                                     'Arabic': 'Section/أخبار-عربية/88/x',
                                     'Global': 'Section/أخبار-عالمية/286/x',
                                     # 'Caricature': 'Section/كاريكاتير-اليوم/192/x',
                                     # 'Art': 'Section/فن/48/x', 'TV': 'Section/تليفزيون/251/x',
                                     # 'Woman': 'Section/المرأة-والمنوعات/89/x',
                                     # 'Albums': 'Section/ألبومات-اليوم-السابع/291/x',
                                     'Health': 'Section/صحة-وطب/245/x',
                                     'Technology': 'Section/علوم-و-تكنولوجيا/328/x',
                                     'States': 'Section/أخبار-المحافظات/296/x'},
                         list_container_tag_name='div', list_container_attr_name='id',
                         list_container_attr_value='paging', container_tag_name='div',
                         container_attr_name='class', container_attr_value='col-xs-12 bigOneSec',
                         full_image_attr_name='class', full_image_attr_value='img-responsive',
                         title_tag_name='h3', body_tag_name='div',
                         body_attr_name='id', body_attr_value='articleBody',
                         timestamp_tag_name='span', timestamp_attr_name='class',
                         timestamp_attr_value='newsDate', tags_tag_name='div',
                         tags_attr_name='class', tags_attr_value='tags')

    def get_page_url_at_index(self, url, index):
        return url.replace('x', str(index))

    def get_post_full_image(self, post_container, detailed_post_container):
        detailed_post_container = detailed_post_container.find('div', {'class': 'img-cont'})
        return super().get_post_full_image(post_container, detailed_post_container)


youm7_scraper = Youm7Scraper()


class FoxNewsScraper(JsonNewsScraper):
    def __init__(self):
        super().__init__(title='Fox News', base_url='https://www.foxnews.com',
                         categories={'Us': 'us', 'Global': 'world',  # 'Opinion': 'opinion',
                                     'Politics': 'politics', 'Entertainment': 'entertainment'},
                         title_json_name='title', description_json_name='description',
                         thumbnail_json_name='imageUrl', url_json_name='url',
                         timestamp_json_name='publicationDate', body_attr_value='article-body',
                         body_tag_name='div', body_attr_name='class', timezone='UTC')

    def get_post_tags(self, post_container, detailed_post_container):
        return [post_container.get('category', {}).get('name', ''), ]

    def format_post_body(self, body, styles):
        if body:
            [tag.extract() for tag in body.select(".ad-container")]

        return super().format_post_body(body, styles)

    def get_category_url(self, title, url):
        category_name = self.categories[title]
        return urljoin(self.base_url, ('api/article-search?isCategory=true&isTag=false' +
                                       '&isKeyword=false&isFixed=false&isFeedUrl=false&' +
                                       'searchSelected={}&contentTypes=%7B%22interactive' +
                                       '%22:false,%22slideshow%22:false,%22video%22:false,' +
                                       '%22article%22:true%7D&size=30').format(category_name))

    def get_page_url_at_index(self, url, index):
        return url + ('&offset=%d' % (30 * (index - 1)))


fox_news_scraper = FoxNewsScraper()


class FoxBusinessScraper(HtmlNewsScraper):
    def __init__(self):
        super().__init__(title='Fox Business', base_url='https://www.foxbusiness.com',
                         categories={'Money': 'money', 'Markets': 'markets',  # 'Lifestyle': 'lifestyle',
                                     # 'Estates': 'real-estate',
                                     'Technology': 'technology',
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

    def get_post_tags(self, post_container, detailed_post_container):
        tag = post_container.find(self.tags_tag_name,
                                  {self.tags_attr_name:
                                       re.compile(self.tags_attr_value + '.*')})

        return [tag.text.strip()] if tag else []

    def get_page_url_at_index(self, url, index):
        return url


fox_business_scraper = FoxBusinessScraper()


class ShoroukNewsScraper(HtmlNewsScraper):
    def __init__(self):
        super().__init__(title='الشروق', base_url='https://www.shorouknews.com',
                         categories={'Egypt': 'egypt', 'Politics': 'Politics',
                                     'Sports': 'sports', 'Art': 'art', 'Money': 'Economy',
                                     # 'Accidents': 'accidents', 'TV': 'tv', 'Woman': 'ladies',
                                     'Technology': 'variety/Internet-Comm', 'Science': 'variety/sciences',
                                     'Health': 'variety/health',
                                     # 'Cars': 'auto', 'Culture': 'Culture'
                                     },
                         list_container_tag_name='ul', list_container_attr_name='class',
                         list_container_attr_value='listing', container_tag_name='li',
                         title_tag_name='div', title_attr_name='class', title_attr_value='text',
                         full_image_attr_name='id', full_image_attr_value='Body_Body_imageMain',
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

        page = BeautifulSoup(response.content, 'lxml')

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

scrapers = (youm7_scraper, fox_news_scraper, fox_business_scraper, shorouk_news_scraper,)
