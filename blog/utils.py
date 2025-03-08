import logging
import threading

from django.db.models import F

from blog.models import Blog
logger = logging.getLogger("django")


class BlogViewCountSingleton(object):
    _instance = None
    _BlogViewCount = {}
    _lock = threading.Lock()  # 用于线程安全

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_blogview_count(self, blog_id):
        return self._BlogViewCount.get(blog_id, 0)

    def increment_blogview_count(self, blog_id):
        with self._lock:
            if blog_id not in self._BlogViewCount:
                self._BlogViewCount[blog_id] = 0
            self._BlogViewCount[blog_id] += 1

    def save_to_database(self, blog_id=None):
        print("saving blog visit count to database")
        with self._lock:
            if blog_id:
                print(f"saving blog id: {blog_id} visit count to database")
                # Update only the specified blog
                count = self._BlogViewCount.get(blog_id, 0)
                print('count is ', count)
                if count > 0:
                    logger.info(f"更新博客 {blog_id} 的访问计数")
                    Blog.objects.filter(id=blog_id).update(access_times=F("access_times") + count)
                    self._BlogViewCount[blog_id] = 0
            else:
                # Update all blogs with positive counts
                for blog_id, count in self._BlogViewCount.items():
                    print("yes+++++++")
                    if count > 0:
                        logger.info(f"更新博客 {blog_id} 的访问计数")
                        print(f"更新博客 {blog_id} 的访问计数: {count}")
                        Blog.objects.filter(id=blog_id).update(access_times=F("access_times") + count)
                        self._BlogViewCount[blog_id] = 0