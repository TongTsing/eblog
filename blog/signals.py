# _*_ coding:utf-8 _*_
# Author: Tongqing
# Date Created: 2025/2/1
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import *
from blog.views import logger


def cascade_delete_replies(comment):
    # 更新当前评论的所有回复
    comment.replies.update(is_delete=True)

    # 对所有回复的子回复也进行递归删除
    for reply in comment.replies.all():
        cascade_delete_replies(reply)

@receiver(post_save, sender=BlogComment)
def cascade_logical_delete(sender, instance, **kwargs):
    if instance and instance.is_delete:
        logger.info(f"Deleting {instance}")
        cascade_delete_replies(instance)


