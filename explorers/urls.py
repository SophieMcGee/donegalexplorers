from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.my_blog, name='my_blog'),
    path('summernote/', include('django_summernote.urls')),
]