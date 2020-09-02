import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.news_scrapers.base_scraper import BaseNewsScraper


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
