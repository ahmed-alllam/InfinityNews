import json
from urllib.parse import urljoin

import requests

from core.news_scrapers.base_scraper import BaseNewsScraper


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
