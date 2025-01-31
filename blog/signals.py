# _*_ coding:utf-8 _*_
# Author: Tongqing
# Date Created: 2025/2/1
from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import *


@receiver(post_delete, sender=BlogComment)
def cascade_logical_delete(sender, instance, **kwargs):
    if instance.parent_comment is None and not instance.is_delete:
        # 如果是父评论并且没有被删除，则级联逻辑删除子评论
        instance.replies.update(is_delete=True)