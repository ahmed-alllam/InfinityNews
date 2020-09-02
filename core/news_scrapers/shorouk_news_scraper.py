from bs4 import BeautifulSoup

from core.news_scrapers.html_scraper import HtmlNewsScraper


class ShoroukNewsScraper(HtmlNewsScraper):
    def __init__(self):
        super().__init__(title='الشروق', base_url='https://www.shorouknews.com',
                         categories={'Egypt': 'egypt', 'Politics': 'Politics',
                                     'Sports': 'sports', 'Art': 'art', 'Money': 'Economy',
                                     # 'Accidents': 'accidents', 'TV': 'tv', ‫#‬ 'Woman': 'ladies',
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
