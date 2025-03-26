import json
import logging
import os

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from blog.models import BlogCategory
from eblog import settings
from .forms import PubBlogForm
from .models import Blog, BlogComment
from .utils import BlogViewCountSingleton

logger = logging.getLogger("django")


# Create your views here.

def handle_markdown(coententList: list = []) -> list:
    # 对blog实例进行处理
    for type, content in coententList:
        if type == "markdown":
            pass

    return coententList

# @cache_page(60*10)
@require_http_methods(["GET"])
def index(request):
    # 获取category_id参数，如果没有则默认为空字符串
    category_id = request.GET.get("category_id", '')

    # 如果category_id为空或无效，查询所有博客
    if category_id == '' or not category_id.isdigit():
        logger.info('获取全部博客信息')
        blogs = Blog.objects.filter(is_delete=False).order_by("-pub_time",).all()
    else:
        # 否则，按照category_id筛选博客
        try:
            category = BlogCategory.objects.get(id=int(category_id))
            blogs = category.blogs.filter(is_delete=False)
        except BlogCategory.DoesNotExist:
            # 如果category_id无效（即没有找到对应的分类），则查询所有博客
            logger.error(f"无效的category_id: {category_id}")
            blogs = Blog.objects.filter(is_delete=False).all()

    # 分页
    paginator = Paginator(blogs, 10)  # 每页显示10篇博客
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 获取所有博客分类，供筛选使用
    categories = BlogCategory.objects.all()

    return render(request, "blog_index.html", {"blogs": page_obj, 'categories': categories})


class blog_detail(View):
    def get_nested_comments(self, parent_comment=None, blog_id=None):
        logger.info(f"获取博客的评论列表")
        # 获取父评论的所有子评论
        comments = BlogComment.objects.filter(parent_comment=parent_comment, blog_id=blog_id, is_delete=False).order_by('pub_time')

        # 遍历评论，构建嵌套数据结构
        comment_data = [
            {
                'comment': {
                    'id': comment.id,
                    'author': comment.author,
                    'content': comment.content,
                    'pub_time': comment.pub_time,
                },
                'replies': self.get_nested_comments(comment, blog_id)  # 递归调用，获取该评论的回复
            }
            for comment in comments
        ]
        return comment_data

    def get(self, request, blog_id):
        logger.info(f"获取博客详情, blog_id: {blog_id}")

        # 获取博客详情
        try:
            blogDetail = Blog.objects.get(id=blog_id)
            logger.info(f"查询到博客信息: {blogDetail.title}-{blogDetail.pub_time}-{blogDetail.author}")
        except Blog.DoesNotExist:
            blogDetail = None
            logger.warning(f"Blog with id {blog_id} does not exist")
            return render(request, "404.html", status=404)

        # 增加访问计数
        logger.info(f"更新计数器")
        blog_counter = BlogViewCountSingleton()
        blog_counter.increment_blogview_count(blog_id)
        logger.info(f"更新计数器完成")

        # 获取评论树
        comment_tree = self.get_nested_comments(parent_comment=None, blog_id=blog_id)
        logger.info(f"获取到评论树: {comment_tree}")

        # 获取评论数量
        comment_count = blogDetail.comments.filter(is_delete=False).count()

        # 渲染博客详情模板
        return render(request, "blog_detail.html", context={
            "blogDetail": blogDetail,
            "comment_tree": comment_tree,
            "comment_count": comment_count,
        })


@require_http_methods(['GET', 'POST'])
@login_required(login_url=reverse_lazy('auth:login'))
def pub_blog(request):
    if request.method == 'GET':
        categories = BlogCategory.objects.all()
        return render(request, 'blog_pub.html', context={'categories': categories})
    if request.method == 'POST':
        form = PubBlogForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            category_id = form.cleaned_data.get('category')
            category = BlogCategory.objects.filter(id=category_id).first()
            image = form.cleaned_data.get('image')
            blog = Blog.objects.create(title=title, content=content, category=category, author=request.user,
                                       image=image)
            return JsonResponse({'code': 200, 'message': '博客发布成功', 'data': {'blog_id': blog.id}})
        else:
            logger.error(f'博客发布失败，错误: {form.errors}')
            return JsonResponse({'code': 400, 'message': 'POST参数错误'})




class coment_management(View):

    @staticmethod
    def delete(request, comment_id):
        if comment_id is None:
            logger.info(f'没有收到comment_id')
            return JsonResponse({'error': '没有权限删除该评论'}, status=403)

        # 验证权限
        comment = BlogComment.objects.get(id=comment_id)

        if request.user.is_authenticated:
            if comment.author == request.user:
                logger.info(f'当前登陆用户是评论作者，有权限删除...正在删除')
                comment.delete()
                return JsonResponse({'success': True})

            if request.user.is_superuser:
                logger.info(f'当前登陆用户是超级管理员，有权限删除...正在删除')
                comment.delete()
                return JsonResponse({'success': True})

            if request.user == comment.blog.author:
                logger.info(f'当前登陆用户是博客作者，有权限删除...正在删除')
                comment.delete()
                return JsonResponse({'success': True})

        return JsonResponse({'error': '没有权限删除该评论'}, status=403)

    def post(self, request):
        try:
            logger.info(f'尝试获取 blog 信息')

            # 获取表单数据
            blog_id = request.POST.get('blog_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')  # 获取是否是回复评论的父评论 ID

            # 检查评论内容是否合法
            if not content.strip():  # 判断评论内容是否为空
                return JsonResponse({"error": "评论内容不能为空"}, status=400)

            # 获取博客信息
            blog = get_object_or_404(Blog, id=blog_id)

            # 判断是否是回复评论
            if parent_id:
                # 获取父评论
                parent_comment = get_object_or_404(BlogComment, id=parent_id)

                # 创建回复评论
                new_comment = BlogComment.objects.create(
                    blog=blog,
                    content=content,
                    author=request.user if request.user.is_authenticated else None,
                    parent_comment=parent_comment
                )
                logger.info(f'{request.user.username} 回复评论：{content}')

                # 返回 JSON 响应（例如页面不刷新）
                return JsonResponse({
                    "message": "评论回复成功",
                    "comment": {
                        "author": new_comment.author.username,
                        "content": new_comment.content,
                        "pub_time": new_comment.pub_time.strftime("%Y年%m月%d日 %H:%M"),
                        "new_comment_user_pic": new_comment.author.profile_picture.url,
                    }
                })
            else:
                # 创建普通评论
                new_comment = BlogComment.objects.create(
                    blog=blog,
                    content=content,
                    author=request.user
                )
                logger.info(f'{request.user.username} 发布评论：{content}')

                # 返回 JSON 响应
                return JsonResponse({
                    "message": "评论发布成功",
                    "comment": {
                        "author": new_comment.author.username,
                        "content": new_comment.content,
                        "pub_time": new_comment.pub_time.strftime("%Y年%m月%d日 %H:%M"),
                        "new_comment_user_pic": new_comment.author.profile_picture.url
                    }
                })

        except Exception as e:
            # 捕获并记录异常
            logger.error(f"{request.user.username} 发布评论失败: {content}, 错误信息: {str(e)}")
            return JsonResponse({"error": "评论发布失败，请稍后再试。"}, status=500)

        # 若不使用 AJAX，可以继续使用原来的重定向
        return redirect('blog:blog_detail', blog_id=blog_id)


@require_http_methods(['GET'])
def search(request):
    # 查找url http://host/blog/search?q=xxx
    q = request.GET.get('q')
    if not q:
        q = ''

    categories = BlogCategory.objects.all()
    blogs = Blog.objects.filter(
        ((Q(title__icontains=q) | Q(content__icontains=q)) & Q(is_delete=0))).order_by('-id').all()

    paginator = Paginator(blogs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "blog_list.html", {"blogs": page_obj, 'categories': categories, 'query_string': q})


# q = request.GET.get('q')
# blogs = Blog.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).order_by('-id')
# return render(request, 'blog_index.html', {'blogs': blogs})

def blog_list(request):
    blogs = Blog.objects.filter(is_delete=0).order_by('-pub_time').all()
    categories = BlogCategory.objects.all()

    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog_list.html', {"blogs": page_obj, 'categories': categories})

@require_http_methods(['GET'])
def get_blog_details(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        blog_data = {
            'title': blog.title,
            'content': blog.content,
            'category': blog.category.id if blog.category else None  # 假设博客有一个类别
        }
        return JsonResponse(blog_data)
    except Blog.DoesNotExist:
        return JsonResponse({'error': 'Blog not found'}, status=404)


def get_categories(request):
    categories = BlogCategory.objects.all()
    category_data = [{'id': category.id, 'name': category.name} for category in categories]
    return JsonResponse({'categories': category_data})


@require_http_methods(['GET', 'POST'])
def edit_blog(request, blog_id):
    logger.info(f'尝试读取博客信息, blog_id: {blog_id}')
    blog = get_object_or_404(Blog, id=blog_id)

    # 确保只有博主可以编辑
    if request.user != blog.author:
        logger.info(f"校验权限...")
        return redirect('blog:blog_details', blog_id=blog_id)
    logger.info(f"权限校验完成，符合条件")
    # 获取分类信息
    categories = BlogCategory.objects.all()

    if request.method == 'POST':
        form = PubBlogForm(request.POST, request.FILES)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            category_id = form.cleaned_data['category']
            image = form.cleaned_data['image']
            # 验证id是否存在
            category = BlogCategory.objects.get(id=category_id)
            if category is None:
                logger.info('id不存在')

            blog.title = title
            blog.content = content
            blog.category = category
            if image:
                # 仅当选择了image时候更新
                blog.image = image
            blog.save()
            logger.info(f'写入信息完成')
        logger.info('表单校验错误，')
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'blog_id': blog_id
            }
        })
    logger.info(f'跳转到编辑页面')
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     # 返回编辑页面 URL 作为 JSON 响应
    #     edit_url = reverse('blog:edit_blog', kwargs={'blog_id': blog.id})
    #     logger.debug(f'重定向到编辑url: {edit_url}')
    #     return JsonResponse({"redirect_url": edit_url})

    logger.debug(f'title: {blog.title}-content: {blog.content}')
    return render(request, 'blog_edit.html', {'blog': blog, 'categories': categories})


@require_http_methods(['DELETE'])
@login_required(login_url=reverse_lazy('auth:login'))
def delete_blog(request, blog_id: int = None):
    login_user = request.user
    # blog查询
    blog = Blog.objects.get(id=blog_id)

    # 如果是超级管理员，可以删除
    if login_user.is_superuser:
        blog.logic_delete()
        logger.info(f'超级管理员：{login_user} 删除了博客{login_user.email}')
        return JsonResponse({
            'code': 200,
            'message': '操作成功',
            'data': {
                'title': blog.title,
            }
        }, status=200)

    # 验证是否是作者本人
    blog_author_email = blog.author.email
    login_user_email = login_user.email
    if blog_author_email == login_user_email:
        try:
            blog.logic_delete()
        except Exception as e:
            logger.error(f'删除博客失败, error:{e}')
            return JsonResponse(data={
                'code': 500,
                'message': '后端数据错误',
                'errors': {
                    'detail': e
                }
            }, status=500)

        logger.info(f'用户：{login_user} 删除了博客{login_user.email}')
        return JsonResponse({
            'code': 200,
            'message': '操作成功',
            'data': {
                'title': blog.title,
            }
        }, status=200)

    logger.info(f'用户:{login_user.email}无权限操作此博客(《{blog.title}》)')
    return JsonResponse({
        'code': 403,
        'message': '权限不足',
        'detail': '您无权执行此操作'
    }, status=403)


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        logger.info(f'upload image...')
        image = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images/'), base_url='/blog/media/images/')
        filename = fs.save(image.name, image)
        file_url = fs.url(filename)
        logger.info(f'upload image... name={filename}, url={file_url}')
        return JsonResponse({
            'errno': 0,
            'data': [{'url': file_url, 'alt': image.name}]
        })
    logger.info(f'get')
    return JsonResponse({'errno': 1, 'message': '上传失败'})


@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('file'):
        video = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos/'), base_url='/blog/media/videos/')
        filename = fs.save(video.name, video)
        file_url = fs.url(filename)
        logger.info(f'upload video save succeed! name={filename}, url={file_url}')
        return JsonResponse({
            'errno': 0,
            'data': {'url': file_url, 'poster': ''}
        })
    logger.info('上传视频失败')
    return JsonResponse({'errno': 1, 'message': '上传失败'})


@csrf_exempt
def requestDebugger(request):
    if request.method == "POST":
        # 获取请求的头部信息
        headers = dict(request.headers)

        # 检查 Content-Type，判断是表单数据还是 JSON 数据
        content_type = request.META.get('CONTENT_TYPE', '')

        # 如果是 multipart/form-data 请求
        if 'multipart/form-data' in content_type:
            post_data = dict(request.POST)  # 获取表单数据
            files_data = {key: [file.name for file in request.FILES.getlist(key)] for key in request.FILES}  # 获取文件数据
        else:
            # 处理 JSON 数据
            if request.body:
                try:
                    post_data = json.loads(request.body.decode('utf-8'))  # 解码 JSON 数据
                except json.JSONDecodeError:
                    post_data = {}  # 如果解码失败，返回空字典
            else:
                post_data = {}

        request_data = {
            'method': request.method,
            'path': request.path,
            'headers': headers,
            'GET': dict(request.GET),
            'POST': post_data,
            'FILES': files_data if 'files_data' in locals() else {}
        }
    else:
        request_data = {
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'GET': dict(request.GET),
            'POST': {},
            'FILES': {}
        }

    return JsonResponse(request_data)

