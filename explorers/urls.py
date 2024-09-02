from django.urls import path, include
from . import views
from .views import EventCreateView, EventUpdateView

urlpatterns = [
    path('', views.EventList.as_view(), name='home'),
    path('event/<slug:slug>/', views.EventDetail.as_view(), name='event_detail'),
    path('summernote/', include('django_summernote.urls')),
    path('save-event/<int:event_id>/', views.save_event_to_calendar, name='save_event_to_calendar'),
    path('my-calendar/', views.view_saved_events, name='my_calendar'),
    path('rate-event/<int:event_id>/', views.rate_event, name='rate_event'),
    path('browse-events/', views.BrowseEventsView.as_view(), name='browse_events'),
    path('add-event/', EventCreateView.as_view(), name='add_event'),
    path('event/<int:pk>/edit/', EventUpdateView.as_view(), name='edit_event'),
]