from django.core.management import BaseCommand

from core.news_scraper.scraper import scrapers


class Command(BaseCommand):
    def handle(self, *args, **options):
        for scraper in scrapers:
            try:
                scraper.scrape()
            except:
                print("An exception occurred")
