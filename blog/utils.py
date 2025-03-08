import threading
from os import access

import redis
from django.db.models import F

from blog.models import Blog
from blog_auth.views import logger


class BlogViewCountSingleton(object):
    _instance = None
    _BlogViewCount = {}
    _lock = threading.Lock()  # 用于线程安全

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_blogview_count(self, blog_id):
        with self._lock:
            return self._BlogViewCount.get(blog_id, 0)

    def increment_blogview_count(self, blog_id):
        with self._lock:
            if blog_id not in self._BlogViewCount:
                self._BlogViewCount[blog_id] = 0
            self._BlogViewCount[blog_id] += 1

    def save_to_database(self, blog_id):
        with self._lock:
            logger.info(f"get lock")
            blogview_count = self.get_blogview_count(blog_id)
            if blogview_count > 0:
                logger.info(f"save lock")
                Blog.objects.filter(id=blog_id).update(access_times=F("access_times")+blogview_count)
                self._BlogViewCount[blog_id] = 0