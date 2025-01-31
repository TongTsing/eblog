from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', view=views.index, name='index'),
    path('detail/<blog_id:int>', view=views.blog_detail.as_view(), name='blog_detail'),
    path('pub/', view=views.pub_blog, name='pub_blog'),
    path('pub_comment/', view=views.coment_management.as_view(), name='pub_comment'),
    path('delete_comment/', view=views.coment_management.as_view(), name='delete_comment'),
    path('search/', view=views.search, name='search'),
    path('edit_blog/<int:blog_id>/', view=views.edit_blog, name='edit_blog'),
    path('<int:blog_id>/', views.get_blog_details, name='get_blog_details'),  # 获取博客详情
    path('categories/', views.get_categories, name='get_categories'),
    path('del_blog/<int:blog_id>/', view=views.delete_blog, name='delete_blog'),
    path('blog_list/', view=views.blog_list, name='blog_list'),
    # 图片上传路由
    path('upload_image/', views.upload_image, name='upload_image'),
    # 视频上传路由
    path('upload_video/', views.upload_video, name='upload_video'),
]