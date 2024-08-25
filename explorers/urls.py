from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.my_blog, name='my_blog'),
    path('summernote/', include('django_summernote.urls')),
    path('save-event/<int:event_id>/', views.save_event_to_calendar, name='save_event_to_calendar'),
    path('saved-events/', views.view_saved_events, name='view_saved_events'),
    path('rate-event/<int:event_id>/', views.rate_event, name='rate_event'),
    path('event/<int:event_id>/', views.event_detail, name='view_event'),
]