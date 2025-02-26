from django_cron import CronJobBase, Schedule
from .utils import BlogViewCountSingleton
from .models import *
from django.db.models import Q, F

class BlogAccessCron(CronJobBase):
    scheduler = Schedule(run_every_mins=1)
    code = "blog.cron.accesstimes"

    def do(self):
        blogcount = BlogViewCountSingleton()

        for blog_id, access_times in blogcount.items():
            if access_times:
                blogcount.save_to_database(blog_id)
