from django_cron import CronJobBase, Schedule
from .utils import BlogViewCountSingleton
import logging


logger = logging.getLogger('django_cron')

class BlogAccessCron(CronJobBase):
    schedule = Schedule(run_every_mins=1)
    code = "blog.cron.accesstimes"

    def do(self):
        print("do")
        blogcount = BlogViewCountSingleton()
        print("blogcount.count", blogcount.get_blogview_count())