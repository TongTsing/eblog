# _*_ coding:utf-8 _*_
# Author: Tongqing
# Date Created: 2025/2/1
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import *
from blog.views import logger


@receiver(post_save, sender=BlogComment)
def cascade_logical_delete(sender, instance, **kwargs):
    if instance and instance.is_delete:
        logger.info(f"Deleting {instance}")
        # 获取与该评论相关的所有回复，并将它们标记为删除
        instance.replies.update(is_delete=True)

