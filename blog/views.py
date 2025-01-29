import logging
import os

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page

from blog.models import BlogCategory
from eblog import settings
from .forms import PubBlogForm
from .models import Blog, BlogComment
from .utils import BlogViewCountSingleton

logging.basicConfig(level=logging.DEBUG)


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
    category_id = request.GET.get("category_id")
    if category_id == None or category_id == '0':
        logging.info(f'获取全部博客信息')
        blogs = Blog.objects.filter(is_delete=False).all()[:10]
        categories = BlogCategory.objects.all()
    else:
        logging.info(f'筛选博客类别id为{category_id}的博客')
        blogs = BlogCategory.objects.get(id=int(category_id)).blogs.filter(is_delete=0).all()[:10]
        categories = BlogCategory.objects.all()
    return render(request, "blog_index.html", {"blogs": blogs, 'categories': categories})


def blog_detail(request, blog_id: int):
    logging.info(f"获取博客详情, blog_id: {blog_id}")
    # Get blog details
    try:
        blogDetail = Blog.objects.get(id=blog_id)
        logging.info(f"查询到到博客信息: {blogDetail.title}-{blogDetail.pub_time}-{blogDetail.author}")
    except Blog.DoesNotExist:
        blogDetail = None
        logging.warning(f"Blog with id {blog_id} does not exist")
        return render(request, "404.html", status=404)

    # 访问计数
    blog_counter = BlogViewCountSingleton()
    blog_counter.increment_blogview_count(blog_id)
    blog_counter.save_to_database(blog_id)
    # Blog.objects.filter(id=blog_id).update(access_times=F('access_times') + 1)
    # logging.debug(f'博客{blog_id} 访问量增加1')

    # Organize comments and their replies
    parent_comments = blogDetail.comments.filter(parent_comment=None, is_delete=False)
    replies = blogDetail.comments.filter(parent_comment__isnull=False, is_delete=False)

    # Organize replies by parent comment id
    parent_comments_dict = {}
    for parent_comment in parent_comments:
        parent_comments_dict[parent_comment.id] = replies.filter(parent_comment=parent_comment)

    # Render the blog detail template with the comments and replies
    return render(request, "blog_detail.html", context={
        "blogDetail": blogDetail,
        "parent_comments_dict": parent_comments_dict
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
            logging.error(f'博客发布失败，错误: {form.errors}')
            return JsonResponse({'code': 400, 'message': 'POST参数错误'})


@require_http_methods(['POST'])
def pub_comment(request):
    try:
        logging.info(f'尝试获取 blog 信息')
        blog_id = request.POST.get('blog_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')  # 获取是否是回复评论的父评论 ID

        blog = get_object_or_404(Blog, id=blog_id)  # 获取博客信息

        # 判断是否是回复评论
        if parent_id:
            parent_comment = get_object_or_404(BlogComment, id=parent_id)
            BlogComment.objects.create(
                blog=blog,
                content=content,
                author=request.user,
                parent_comment=parent_comment
            )
            logging.info(f'{request.user.username} 回复评论：{content}')
        else:
            # 普通评论
            BlogComment.objects.create(
                blog=blog,
                content=content,
                author=request.user
            )
            logging.info(f'{request.user.username} 发布评论：{content}')

    except Exception as e:
        logging.error(f"{request.user.username} 发布评论失败: {content}, 错误信息: {str(e)}")
        return JsonResponse({"error": "评论发布失败，请稍后再试。"}, status=500)

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

    return render(request, "blog_list.html", {"blogs": page_obj, 'categories': categories})


# q = request.GET.get('q')
# blogs = Blog.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).order_by('-id')
# return render(request, 'blog_index.html', {'blogs': blogs})

def blog_list(request):
    blogs = Blog.objects.filter(is_delete=0)
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
    logging.info(f'尝试读取博客信息, blog_id: {blog_id}')
    blog = get_object_or_404(Blog, id=blog_id)

    # 确保只有博主可以编辑
    if request.user != blog.author:
        logging.info(f"校验权限...")
        return redirect('blog:blog_details', blog_id=blog_id)
    logging.info(f"权限校验完成，符合条件")
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
                logging.info('id不存在')

            blog.title = title
            blog.content = content
            blog.category = category
            if image:
                # 仅当选择了image时候更新
                blog.image = image
            blog.save()
            logging.info(f'写入信息完成')
        logging.info('表单校验错误，')
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'blog_id': blog_id
            }
        })
    logging.info(f'跳转到编辑页面')
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     # 返回编辑页面 URL 作为 JSON 响应
    #     edit_url = reverse('blog:edit_blog', kwargs={'blog_id': blog.id})
    #     logging.debug(f'重定向到编辑url: {edit_url}')
    #     return JsonResponse({"redirect_url": edit_url})

    logging.debug(f'title: {blog.title}-content: {blog.content}')
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
        logging.info(f'超级管理员：{login_user} 删除了博客{login_user.email}')
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
            logging.error(f'删除博客失败, error:{e}')
            return JsonResponse(data={
                'code': 500,
                'message': '后端数据错误',
                'errors': {
                    'detail': e
                }
            }, status=500)

        logging.info(f'用户：{login_user} 删除了博客{login_user.email}')
        return JsonResponse({
            'code': 200,
            'message': '操作成功',
            'data': {
                'title': blog.title,
            }
        }, status=200)

    logging.info(f'用户:{login_user.email}无权限操作此博客(《{blog.title}》)')
    return JsonResponse({
        'code': 403,
        'message': '权限不足',
        'detail': '您无权执行此操作'
    }, status=403)


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        logging.info(f'upload image...')
        image = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images/'), base_url='/blog/media/images/')
        filename = fs.save(image.name, image)
        file_url = fs.url(filename)
        logging.info(f'upload image... name={filename}, url={file_url}')
        return JsonResponse({
            'errno': 0,
            'data': [{'url': file_url, 'alt': image.name}]
        })
    logging.info(f'get')
    return JsonResponse({'errno': 1, 'message': '上传失败'})


@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video = request.FILES['video']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos/'), base_url='/blog/media/videos/')
        filename = fs.save(video.name, video)
        file_url = fs.url(filename)
        return JsonResponse({
            'errno': 0,
            'data': {'url': file_url, 'poster': ''}
        })
    logging.info('上传视频失败')
    return JsonResponse({'errno': 1, 'message': '上传失败'})
