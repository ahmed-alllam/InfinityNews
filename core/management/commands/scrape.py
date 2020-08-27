from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management import BaseCommand

from core.news_scraper.scraper import scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        for index, scraper in enumerate(scrapers):
            scheduler = BlockingScheduler()
            scheduler.add_job(scrape, "interval", minutes=5 + (index * 2), args=scraper)
            scheduler.start()


def scrape(scraper):
    try:
        print("starting scraping " + scraper.title)
        scraper.scrape()
    except Exception as e:
        print("An exception occurred" + str(e))
