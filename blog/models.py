from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.

class BlogCategory(models.Model):
    name = models.CharField(max_length=20, verbose_name="分类")

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    category = models.ForeignKey(BlogCategory, related_name='blogs',on_delete=models.CASCADE, verbose_name="分类")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者", related_name='blogs')
    is_delete = models.BooleanField(default=False)
    image = models.ImageField(upload_to='blog_pics/', null=True, blank=True)
    access_times = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name

    def logic_delete(self):
        self.is_delete = True
        self.save()

    def logic_restore(self):
        self.is_delete = False
        self.save()


class BlogComment(models.Model):
    content = models.TextField(verbose_name="内容")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间" )
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments", verbose_name="所属博客")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    is_delete = models.BooleanField(default=False, verbose_name="是否已删除")
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name

    def delete(self):
        self.is_delete = True
        self.save()

    def restore(self):
        self.is_delete = False
        self.save()