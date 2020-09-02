from urllib.parse import urljoin

from core.news_scrapers.json_scraper import JsonNewsScraper


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
