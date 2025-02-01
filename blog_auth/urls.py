from django.conf.urls.static import static
from django.urls import path

from eblog import settings
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', view=views.blog_login.as_view(), name='login'),
    path('logout', view=views.blog_logout.as_view(), name='logout'),
    path('register/', view=views.register_view.as_view(), name='register'),
    path('captcha/', view=views.send_captcha, name='send_capcha'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('change_password/', views.change_password, name='change_password')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)