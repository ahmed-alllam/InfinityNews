from core.news_scrapers.fox_business_scraper import FoxBusinessScraper
from core.news_scrapers.fox_news_scraper import FoxNewsScraper
from core.news_scrapers.shorouk_news_scraper import ShoroukNewsScraper
from core.news_scrapers.youm7_scraper import Youm7Scraper

scrapers = (Youm7Scraper(), FoxNewsScraper(), FoxBusinessScraper(), ShoroukNewsScraper())
