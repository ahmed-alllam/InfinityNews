import time

import requests
from bs4 import BeautifulSoup

from news.models import Source, Post, SourceCategory, PostTag


class BaseNewsScraper:
    # todo: soft code id
    def __init__(self, title, base_url, categories, format='html.parser', list_container_tag='',
                 list_container_id='', container_tag='', container_id='', title_tag='',
                 title_id='', description_tag='', description_id='', body_tag='',
                 body_id='', image_tag='', image_id='', timestamp_tag='',
                 timestamp_id='', url_tag='', url_id='', tags_tag='',
                 tags_id='', time_between_requests=0):

        self.title = title
        self.base_url = base_url
        self.categories = categories
        self.format = format
        self.list_container_tag = list_container_tag
        self.list_container_id = list_container_id
        self.container_tag = container_tag
        self.container_id = container_id
        self.title_tag = title_tag
        self.title_id = title_id
        self.description_tag = description_tag
        self.description_id = description_id
        self.body_tag = body_tag
        self.body_id = body_id
        self.image_tag = image_tag
        self.image_id = image_id
        self.timestamp_tag = timestamp_tag
        self.timestamp_id = timestamp_id
        self.url_tag = url_tag
        self.url_id = url_id
        self.tags_tag = tags_tag
        self.tags_id = tags_id
        self.time_between_requests = time_between_requests

    def scrape(self):
        source = Source.objects.get(title=self.title)
        posts = []
        for category, url in self.categories:
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
        posts_list_container = beautiful_soup.find(self.list_container_tag,
                                                   attrs={'id': self.list_container_id})
        posts = []
        for post_container in posts_list_container.find_all(self.container_tag,
                                                            attrs={'id': self.container_id}):
            post = self.scrape_post(source, category, post_container)
            if Post.objects.exists(source=source, category=category, title=post.title):
                return posts, False
            posts.append(post)
            post.save()
        return posts, True

    def scrape_post(self, source, category, post_container):
        title = self.get_post_title(post_container)
        url = self.get_post_url(post_container)

        time.sleep(self.time_between_requests)
        post_page = BeautifulSoup(requests.get(url), self.format)

        description = self.get_post_description(post_container, post_page)
        image = self.get_post_image(post_container, post_page)
        body = self.get_post_body(post_page)
        timestamp = self.get_post_timestamp(post_container, post_page)
        tags = [PostTag.objects.get_or_create(tag=tag)[0]
                for tag in self.get_post_tags(post_container, post_page)]

        return Post(source=source, category=category, tags=tags, title=title, image=image,
                    detail_url=url, description=description, timestamp=timestamp,
                    body=body)

    def get_post_title(self, post_container):
        return post_container.find(self.title_tag, attrs={'id': self.title_id}).text

    def get_post_url(self, post_container):
        return post_container.find(self.url_tag, attrs={'id': self.url_id}).text

    def get_post_description(self, post_container, post_page):
        return post_container.find(self.description_tag, attrs={'id': self.description_id}).text

    def get_post_image(self, post_container, post_page):
        return post_container.find(self.image_tag, attrs={'id': self.image_id}).text

    def get_post_body(self, post_page):
        body = ''
        for tag in post_page.find(self.body_tag, attrs={'id': self.body_id}):
            body += tag.text
        return body

    def get_post_timestamp(self, post_container, post_page):
        return post_container.find(self.timestamp_tag, attrs={'id': self.timestamp_id}).text

    def get_post_tags(self, post_container, post_page):
        tags = []
        for tag in post_page.find(self.tags_tag, attrs={'id': self.tags_id}).find_all('a'):
            tags.append(tag)
        return tags

    def get_page_at_index(self, url, index):
        raise NotImplementedError()
