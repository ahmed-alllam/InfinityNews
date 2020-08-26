from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management import BaseCommand

from core.news_scraper.scraper import scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BlockingScheduler()
        scheduler.add_job(scrape, "interval", minutes=5)
        scheduler.start()


def scrape():
        for scraper in scrapers:
            try:
                scraper.scrape()
            except:
                print("An exception occurred")
