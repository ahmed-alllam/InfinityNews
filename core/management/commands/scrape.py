import datetime
import signal

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import BaseCommand

from core import news_scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.start()
        for scraper in news_scrapers.scrapers:
            scheduler.add_job(scrape, "interval", minutes=5, args=(scraper,), next_run_time=datetime.datetime.now())

        signal.pause()


def scrape(scraper):
    print("starting scraping " + scraper.title)
    scraper.scrape()
