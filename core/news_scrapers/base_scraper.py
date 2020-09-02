import re
import time
from abc import ABC

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
