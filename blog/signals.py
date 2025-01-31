# _*_ coding:utf-8 _*_
# Author: Tongqing
# Date Created: 2025/2/1
from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import *
from blog.views import logger


@receiver(post_delete, sender=BlogComment)
def cascade_logical_delete(sender, instance, **kwargs):
    if not instance.is_delete:
        logger.info(f"Deleting {instance}")
        instance.replies.delete(is_delete=True)