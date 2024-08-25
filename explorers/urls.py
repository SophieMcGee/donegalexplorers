from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Enables the admin interface and login page
    path('', views.my_blog, name='my_blog'),
    path('summernote/', include('django_summernote.urls')),
]