from django_cron import CronJobBase, Schedule
from .utils import BlogViewCountSingleton
import logging


logger = logging.getLogger('django_cron')

class BlogAccessCron(CronJobBase):
    schedule = Schedule(run_every_mins=1)
    code = "blog.cron.accesstimes"

    def do(self):
        logger.info("startting BlogAccessCron")
        blogcount = BlogViewCountSingleton()

        for blog_id, access_times in blogcount._BlogViewCount.items():
            if access_times:
                blogcount.save_to_database(blog_id)
