import logging
import threading
import aioredis

from django.db.models import F

from blog.models import Blog
from eblog import settings

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
        if blog_id not in self._BlogViewCount:
            self._BlogViewCount[blog_id] = 0
        self._BlogViewCount[blog_id] += 1

    def save_to_database(self, blog_id=None):
        print("saving blog visit count to database")

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


class RedisCLient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._redis = None
        return cls._instance

    async def get_redis(self):
        """获取 Redis 连接"""
        if not self._redis:
            self._redis = await aioredis.from_url(settings.REDIS_URL)
        return self._redis

    async def close(self):
        """关闭 Redis 连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None



class BlogAccessCount(object):
    def __init__(self, blog_id):
        self._blog_id = blog_id

    async def increment_blogview_count(self, blog_id):
        pass

    async def save_to_database(self, blog_id=None):
        pass
