from apscheduler.schedulers.blocking import BlockingScheduler

from core.management.commands.scrape import scrape

scheduler = BlockingScheduler()
scheduler.add_job(scrape, "interval", minutes=5)

scheduler.start()
