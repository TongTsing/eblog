from django_cron import CronJobBase, Schedule
from .utils import BlogViewCountSingleton
import logging


logger = logging.getLogger('django_cron')

class BlogAccessCron(CronJobBase):
    schedule = Schedule(run_every_mins=1)
    code = "blog.cron.accesstimes"

    def do(self):
        logger.log("Starting Cron")
        blogcount = BlogViewCountSingleton()

        for blog_id, access_times in blogcount.items():
            if access_times:
                blogcount.save_to_database(blog_id)
