import logging

import redis
from django import forms
from django.core.exceptions import ValidationError

from blog_auth.models import User

logging.basicConfig(level=logging.INFO)


def get_redis_cache(key: str = "", db=1) -> str:
    redis_client = redis.StrictRedis(
        host='127.0.0.1',  # Redis 主机地址
        port=6379,  # Redis 端口
        db=db,  # 数据库编号
        decode_responses=True  # 确保返回的数据是字符串
    )
    try:
        result = redis_client.get(key)  # Correct the key variable
        if result is None:
            return ""
    except Exception as e:
        logging.error(f"Error getting Redis cache: {e}")
        return ""
    return result


class registerForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, min_length=4, error_messages={
        'required': '请输入用户名',
        'max_length': '用户名长度在4-100之间',
        'min_length': '用户名长度在4-100之间'
    })
    email = forms.EmailField(error_messages={
        "required": "请输入邮箱",
        'invalid': '请输入正确的邮箱'
    })
    captcha = forms.CharField(max_length=6, min_length=6, error_messages={
        'required': '请输入验证码',
        'max_length': '验证码长度为6位',
        'min_length': '验证码长度为6位'
    })
    password = forms.CharField(max_length=16, min_length=8, error_messages={
        'required': '<PASSWORD>',
        'max_length': '密码长度为8-16位',
        'min_length': '密码长度为8-16位'
    })

    profile_picture = forms.ImageField()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("用户名称已存在，请重新输入")
        else:
            return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith('@163.com'):
            raise ValidationError('邮箱必须是163邮箱')
        if User.objects.filter(email=email).exists():
            raise ValidationError('邮箱已被注册，请重新输入邮箱')
        return email

    # def clean_captcha(self):
    #     captcha = self.cleaned_data.get('captcha')
    #     email = self.cleaned_data.get('email')
    #     captcha_in_redis=get_redis_cache(email)
    #     if not captcha_in_redis:
    #         raise ValidationError('验证码无效，请重新获取')
    #
    #     return captcha


class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={
        "requeird": "请输入邮箱",
        'invalid': '请输入正确的邮箱'
    })
    password = forms.CharField(max_length=16, min_length=8, error_messages={
        'required': '<PASSWORD>',
        'max_length': '密码长度为8-16位',
        'min_length': '密码长度为8-16位'
    })
    remember = forms.IntegerField(required=False)


class EditProfileForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, min_length=4, error_messages={
        'required': '请输入用户名',
        'max_length': '用户名长度在4-100之间',
        'min_length': '用户名长度在4-100之间'
    })
    email = forms.EmailField()
    profile_picture = forms.ImageField(required=False)
    profile = forms.CharField(max_length=500, required=False)


class ChangePasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'first_name' in self.fields:
            del self.fields['first_name']
        if 'last_name' in self.fields:
            del self.fields['last_name']

    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm new Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")
