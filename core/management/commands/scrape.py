from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management import BaseCommand

from core.news_scraper.scraper import scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BlockingScheduler()
        scheduler.add_job(scrape, "interval", minutes=1)
        scheduler.start()


def scrape():
        for scraper in scrapers:
            try:
                scraper.scrape()
            except Exception as e:
                print("An exception occurred" + str(e))
