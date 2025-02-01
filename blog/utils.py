import redis

from blog.models import Blog
from blog_auth.views import logger


class BlogViewCountSingleton(object):
    _instance = None
    _BlogViewCount = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(
               cls, *args, **kwargs
            )
        return cls._instance

    def get_blogview_count(self, blog_id):
        return self._BlogViewCount.get(blog_id, 0)

    def increment_blogview_count(self, blog_id):
        if blog_id not in self._BlogViewCount:
            self._BlogViewCount[blog_id] = 0
        self._BlogViewCount[blog_id] += 1

    def save_to_database(self, blog_id):
        blogview_count = self.get_blogview_count(blog_id)

        if blogview_count > 0:
            blog = Blog.objects.get(id=blog_id)
            blog.access_times += blogview_count
            blog.save()
            self._BlogViewCount[blog_id] = 0
