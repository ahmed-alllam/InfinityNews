import re

from core.news_scrapers.html_scraper import HtmlNewsScraper


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
