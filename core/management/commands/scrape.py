import datetime
import signal

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import BaseCommand

from core.news_scraper.scraper import scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.start()
        for scraper in scrapers:
            scheduler.add_job(scrape, "interval", minutes=5, args=(scraper,), next_run_time=datetime.datetime.now())

        signal.pause()


def scrape(scraper):
    print("starting scraping " + scraper.title)
    scraper.scrape()
