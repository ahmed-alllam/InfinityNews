from core.news_scrapers.html_scraper import HtmlNewsScraper


class Youm7Scraper(HtmlNewsScraper):
    def __init__(self):
        super().__init__(title='اليوم السابع', base_url='https://www.youm7.com',
                         categories={'Breaking': 'Section/أخبار-عاجلة/65/x',
                                     'Politics': 'Section/سياسة/319/x', 'Reports': 'Section/تقارير-مصرية/97/x',
                                     ‫#‬ 'Culture': 'Section/ثقافة/94/x', 'Accidents': 'Section/حوادث/203/x',
                                     # 'Finance': 'Section/اقتصاد-وبورصة/297/x',
                                     # 'Investigations': 'Section/تحقيقات-وملفات/12/x',
                                     'Sports': 'Section/أخبار-الرياضة/298/x',
                                     'Football': 'Section/كرة-عالمية/332/x',
                                     ‫#‬ 'Arabic': 'Section/أخبار-عربية/88/x',
                                     'Global': 'Section/أخبار-عالمية/286/x',
                                     # 'Caricature': 'Section/كاريكاتير-اليوم/192/x',
                                     # 'Art': 'Section/فن/48/x', 'TV': 'Section/تليفزيون/251/x',
                                     # 'Woman': 'Section/المرأة-والمنوعات/89/x',
                                     # 'Albums': 'Section/ألبومات-اليوم-السابع/291/x',
                                     'Health': 'Section/صحة-وطب/245/x',
                                     'Technology': 'Section/علوم-و-تكنولوجيا/328/x',
                                     'Egypt': 'Section/أخبار-المحافظات/296/x'},
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
