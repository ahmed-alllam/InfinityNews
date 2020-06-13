import time

import dateparser
import pytz
import requests
from bs4 import BeautifulSoup

from news.models import Source, Post, SourceCategory, PostTag


class BaseNewsScraper:
    def __init__(self, title, base_url, categories, format='html.parser',
                 list_container_tag_name='', list_container_attr_name='', list_container_attr_value='',
                 container_tag_name='', container_attr_name='', container_attr_value='',
                 title_tag_name='', title_attr_name='', title_attr_value='',
                 description_tag_name='', description_attr_name='', description_attr_value='',
                 body_tag_name='', body_attr_name='', body_attr_value='',
                 image_tag_name='img', image_attr_name='', image_attr_value='',
                 timestamp_tag_name='', timestamp_attr_name='', timestamp_attr_value='',
                 url_tag_name='', url_attr_name='', url_attr_value='',
                 tags_tag_name='', tags_attr_name='', tags_attr_value='',
                 time_between_requests=0, timezone='EET'):

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

    def scrape(self):
        source = Source.objects.get_or_create(title=self.title)[0]
        posts = []
        for category, url in self.categories.items():
            posts.extend(self.scrape_category(source, category, url))
        return posts

    def scrape_category(self, source, title, url):
        category = SourceCategory.objects.get_or_create(source=source, title=title)[0]
        has_next = True
        page_index = 1
        category_posts = []
        while has_next:
            time.sleep(self.time_between_requests)
            page = requests.get(self.get_page_at_index(url, page_index)).content
            page_posts, has_next = self.scrape_page(source, category, page)
            category_posts.extend(page_posts)
            page_index += 1
        return category_posts

    def scrape_page(self, source, category, page):
        beautiful_soup = BeautifulSoup(page, self.format)
        posts_list_container = beautiful_soup.find(self.list_container_tag_name,
                                                   {self.list_container_attr_name:
                                                        self.list_container_attr_value})
        posts = []
        for post_container in posts_list_container.find_all(self.container_tag_name,
                                                            {self.container_attr_name:
                                                                 self.container_attr_value}):
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
        post_page = BeautifulSoup(requests.get(url).content, self.format)

        description = self.get_post_description(post_container, post_page)
        image = self.get_post_image(post_container, post_page)
        body = self.get_post_body(post_page)
        timestamp = self.get_post_timestamp(post_container, post_page)
        tags = [PostTag.objects.get_or_create(tag=tag)[0]
                for tag in self.get_post_tag_names(post_container, post_page)]

        post = Post(source=source, category=category, title=title, image=image,
                    detail_url=url, description=description, timestamp=timestamp,
                    body=body)

        return post, tags

    def get_post_title(self, post_container):
        return post_container.find(self.title_tag_name, {self.title_attr_name:
                                                             self.title_attr_value}).text

    def get_post_url(self, post_container):
        return self.base_url + post_container.find(self.url_tag_name, {self.url_attr_name:
                                                                           self.url_attr_value})['href']

    def get_post_description(self, post_container, post_page):
        return post_container.find(self.description_tag_name,
                                   {self.description_attr_name:
                                        self.description_attr_value}).text

    def get_post_image(self, post_container, post_page):
        return post_container.find(self.image_tag_name)['src']

    def get_post_body(self, post_page):
        return str(post_page.find(self.body_tag_name, {self.body_attr_name:
                                                           self.body_attr_value}))

    def get_post_timestamp(self, post_container, post_page):
        timestamp = post_container.find(self.timestamp_tag_name,
                                        {self.timestamp_attr_name:
                                             self.timestamp_attr_value}).text
        parsed_timestamp = dateparser.parse(timestamp)
        if self.timezone:
            tz = pytz.timezone(self.timezone)
            parsed_timestamp = parsed_timestamp.replace(tzinfo=tz).astimezone(pytz.utc)

        return parsed_timestamp

    def get_post_tag_names(self, post_container, post_page):
        tags = []
        for tag in post_page.find(self.tags_tag_name, {self.tags_attr_name:
                                                           self.tags_attr_value}).find_all('a'):
            tags.append(tag.text)
        return tags

    def get_page_at_index(self, url, index):
        raise NotImplementedError()
