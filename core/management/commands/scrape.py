from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import BaseCommand

from core.news_scraper.scraper import scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.start()
        for index, scraper in enumerate(scrapers):
            scheduler.add_job(scrape, "interval", minutes=5 + (index * 5), args=(scraper,))


def scrape(scraper):
    try:
        print("starting scraping " + scraper.title)
        scraper.scrape()
    except Exception as e:
        print("An exception occurred" + str(e))
