import logging
import random
import string

import redis
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views import View
from urllib3 import request

from utils.utils import redisMixin
from .forms import registerForm, LoginForm, EditProfileForm, ChangePasswordForm

User = get_user_model()
logger = logging.getLogger("django")


# Create your views here.

class blog_login(View):

    # 覆盖View的dispatch方法，并且使用装饰器
    @method_decorator(require_http_methods(["GET", "POST"]))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'blog_login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        logger.info("验证表单值")
        if login_form.is_valid():
            logger.info("正在尝试获取登陆信息")
            try:
                email = login_form.cleaned_data['email']
                password = login_form.cleaned_data['password']
                remember = login_form.cleaned_data['remember']
                logger.info(f"获取到的登陆信息: {email}.")

                user = User.objects.get(email=email)
                if user and user.check_password(password):
                    logger.info("密码验证成功")
                    login(request, user)
                    if not remember:
                        request.session.set_expiry(60 * 60)
                    # 设置过期时间为1周
                    request.session.set_expiry(604800)
                    request.session.save()
                    return HttpResponseRedirect(reverse("blog:index"))
                else:
                    logger.info(f'用户{email}尝试登录，密码校验失败')
                    messages.error(request, f'登录失败，请检查邮箱和密码')
                    return redirect('auth:login')
            except Exception as e:
                messages.error(request, f'登录失败，请检查邮箱和密码')
                logger.error(f"登录失败，错误：{e}")
                return redirect('auth:login')
        # 表单验证异常
        logger.info(f"表单验证不通过，请查看表单信息")




class blog_logout(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        logger.info(f'user {request.user.username} logged out!')
        logout(request)
        return redirect('blog:index')


class register_view(redisMixin, View):
    @method_decorator(require_http_methods(["GET", "POST"]))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'blog_register.html')

    def post(self, request):
        register_form = registerForm(request.POST, request.FILES)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']
            captcha = register_form.cleaned_data['captcha']  # 获取验证码
            profile_picture = register_form.cleaned_data['profile_picture']
            # 验证码验证逻辑
            captcha_in_redis = self.get_redis_cache(email)
            logger.info(f'头像地址：{profile_picture}')
            if not captcha_in_redis:
                logger.warning("没有在redis中找到key")
                # 在验证码无效时返回错误信息
                messages.error(request, "验证码无效，请重新输入")
                return redirect(reverse('auth:register'))  # 重定向到注册页面
            if captcha_in_redis != captcha:
                logger.info(f'输入的验证码不正确')
                messages.error(request, message=f'验证码不正确，请重新输入')
                return redirect(reverse('auth:register'))

            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.profile_picture = profile_picture
            user.save()
            logger.info(f"registered new user: {username} successfully")
            # 清理验证码

            return redirect(reverse('auth:login'))

        # 表单验证失败时返回
        messages.error(request, f"请检查表单填写项, error:{register_form.errors}")
        return redirect(reverse('auth:register'))


def set_redis_cache(key: str = "", value: str = "", timeout: int = 60, db=1) -> int:
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


def get_redis_cache(key: str = "", db=1) -> str:
    redis_client = redis.StrictRedis(
        host='ip.hwserver.cn',  # Redis 主机地址
        port=6379,  # Redis 端口
        password='tq113211',
        db=db,  # 数据库编号
        decode_responses=True  # 确保返回的数据是字符串
    )
    try:
        result = redis_client.get(key)  # Correct the key variable
        if result is None:
            return ""
    except Exception as e:
        logger.error(f"getting Redis cache failed: {e}")
        return ""
    return result


def generate_capture(length: int = 0) -> str:
    captcha = "".join(random.sample(string.ascii_letters + string.digits, length))
    logger.info(f'Captcha generated: {captcha}')
    return captcha


# This could be removed if you switch to POST and handle CSRF token on frontend
def send_captcha(request):
    if request.method == 'GET':  # You may consider changing to POST
        email = request.GET.get('email')
        logger.info(f'Trying to send captcha to email: {email}')
        if email is None:
            return JsonResponse({'code': 400, 'msg': '必须输入邮箱!'})

        captcha = generate_capture(6)
        if set_redis_cache(email, captcha, 300):  # Cache for 5 minutes
            mailInfo = f"【易博客】本次注册验证码：{captcha}"
            logger.info(f"Sending captcha to {email}: {mailInfo}")
            sendMailResult = send_mail(
                subject="易博客注册验证码",
                message=mailInfo,
                recipient_list=[email],
                from_email=None
            )
            if sendMailResult > 0:
                logger.info(f"Sending mail success: {email}")
                return JsonResponse({"code": 200, "msg": "验证码发送成功"})
            else:
                logger.error("Failed to send email.")
                return JsonResponse({"code": 500, "msg": "验证码发送失败"})
        else:
            return JsonResponse({"code": 500, "msg": "缓存设置失败"})

    return JsonResponse({"code": 400, "msg": "请求方式错误，必须为 GET"})


@require_http_methods(['GET'])
def profile(request):
    userins = request.user
    logger.info(f"username: {userins.username}, email: {userins.email}")
    # userinfo = User.objects.filter(username=userins.username)
    return render(request, 'blog_profile.html', {'user': userins})


@require_http_methods(['GET', "POST"])
@login_required(login_url='auth:login')
def edit_profile(request):
    if request.method == 'GET':
        userins = request.user
        return render(request, 'profile_edit.html', {'user': userins})

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            username = form.cleaned_data.get('username')
            profile = form.cleaned_data.get('profile')
            profile_picture = form.cleaned_data.get('profile_picture')
            email = form.cleaned_data.get('email')
            if not user.is_authenticated:
                logger.info("未登录， 请登录后再修改个人信息")
                return redirect('auth:login')
            if user.email != email:
                messages.error(request, '无法修改邮箱')
                return render(request, 'blog_profile.html', {'user': user})
            user.username = username
            user.profile = profile
            # 如果没上传，则不修改头像
            if profile_picture:
                user.profile_picture = profile_picture
            logger.info(f'要修改的个人信息：{username}-{profile}')
            user.save()
            return redirect('auth:profile')
        messages.error(request, f'修改个人信息表单校验不通过, error:{form.errors}')
        return redirect('auth:profile')


@require_http_methods(['GET', "POST"])
def delete_profile(request):
    pass


@require_http_methods(['GET', "POST"])
@login_required(login_url='auth:login')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password')
            # 判断旧秘密是否正确
            user = request.user
            if not user.check_password(old_password):
                logger.info(
                    f'user {user.username}-{user.email} trying to change password, but old password is not match!')
                messages.error(request, '旧密码不正确')
                return redirect('auth:change_password')

            if new_password == old_password:
                messages.error(request, f'新密码不能和旧秘密相同')
                return redirect('auth:change_password')

            user.set_password(new_password)
            messages.success(request, '修改密码成功！')
            return redirect('auth:profile')
        logger.error(f'表单校验失败')
        messages.error(request, f'表单校验失败')
        return redirect('auth:change_password')
    if request.method == 'GET':
        form = ChangePasswordForm()
        return render(request, 'change_passwd.html', {'form': form})
