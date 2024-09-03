from django.urls import path, include
from .views import Home, EventCreateView, EventUpdateView, SavedEventsView, EventList, EventDetail, save_event_to_calendar, rate_event, BrowseEventsView, EventDeleteView, MyEventsView, remove_event_from_calendar

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('browse-events/', BrowseEventsView.as_view(), name='browse_events'),
    path('event/<slug:slug>/', EventDetail.as_view(), name='event_detail'),
    path('summernote/', include('django_summernote.urls')),
    path('save-event/<int:event_id>/', save_event_to_calendar, name='save_event_to_calendar'),
    path('my-calendar/', SavedEventsView.as_view(), name='my_calendar'),
    path('rate-event/<int:event_id>/', rate_event, name='rate_event'),
    path('add-event/', EventCreateView.as_view(), name='add_event'),
    path('event/<int:pk>/edit/', EventUpdateView.as_view(), name='edit_event'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='delete_event'),
    path('my-events/', MyEventsView.as_view(), name='my_events'),
    path('remove-event/<int:event_id>/', remove_event_from_calendar, name='remove_event_from_calendar'),
]