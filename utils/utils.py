import logging

import redis

logger = logging.getLogger('django')


class redisMixin():
    def set_redis_cache(self, key: str = "", value: str = "", timeout: int = 60, db=1) -> int:
        redis_client = redis.StrictRedis(
            host='ip.hwserver.cn',  # Redis 主机地址
            port=6379,  # Redis 端口
            password='tq113211',
            db=db,  # 数据库编号
            decode_responses=True  # 确保返回的数据是字符串
        )
        try:
            redis_client.set(key, value, timeout)
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            return 0
        return 1

    def get_redis_cache(self, key: str = "", db=1) -> str:
        redis_client = redis.StrictRedis(
            host='ip.hwserver.cn',  # Redis 主机地址
            port=6379,  # Redis 端口
            password='tq113211',
            db=db,  # 数据库编号
            decode_responses=True  # 确保返回的数据是字符串
        )
        try:
            logger.info(f"get redis key: {key}")
            result = redis_client.get(key)  # Correct the key variable
            if result is None:
                logger.info("test")
                result = ""
        except Exception as e:
            logger.error(f"getting Redis cache failed: {e}")
            result = ""
        logger.info(f"get capcher {result}")
        return result