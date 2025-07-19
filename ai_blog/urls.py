from django.contrib import admin
from django.contrib.auth import views as auth_view
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name= 'index'),
    path('signup/', views.signup_page, name= 'signup'),
    path('login/', auth_view.LoginView.as_view(template_name="login.html"), name= 'login'),
    path('logout/', auth_view.LogoutView.as_view(template_name="logout.html"), name= 'logout'),
    path('generate-blog/', views.generate_blog, name= 'generate-blog'),
    path('blog-list/', views.blog_list, name= 'blog-list'),
    path('blog-details/<int:pk>/', views.blog_details, name= 'blog-details'),
    path('blog-delete/<int:pk>/', views.blog_delete, name= 'blog-delete'),
    path('download-audio/<int:pk>/', views.download_audio_file, name='download-audio'),
    path('download-video/<int:pk>/', views.download_video_file, name='download-video'),
    path('check-status/<str:task_id>/', views.check_status, name='check-status'),
]
