from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from explorers.models import Event, Calendar, Comment, Notification, UserProfile
from django.utils import timezone
from datetime import datetime

class TestViews(TestCase):

    def setUp(self):
        # Set up a user, profile, and event to use for testing
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user_profile = UserProfile.objects.create(user=self.user, receive_comment_notifications=True)
        self.client.login(username='testuser', password='password123')

        # Use timezone-aware datetimes
        self.event = Event.objects.create(
            title="Test Event",
            description="Event description",
            location="Test Location",
            start_date=timezone.make_aware(datetime(2024, 10, 10)),
            end_date=timezone.make_aware(datetime(2024, 10, 11)),
            start_time="10:00",
            end_time="14:00",
            status="published",
            author=self.user
        )

    def test_home_page_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_browse_events_view(self):
        response = self.client.get(reverse('browse_events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'browse_events.html')

    def test_event_detail_view(self):
        response = self.client.get(reverse('event_detail', kwargs={'slug': self.event.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')

    def test_event_create_view(self):
        response = self.client.get(reverse('add_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_event.html')

    def test_event_update_view(self):
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_event.html')

    def test_event_delete_view(self):
        response = self.client.get(reverse('delete_event', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete.html')

    def test_my_events_view(self):
        response = self.client.get(reverse('my_events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_events.html')

    def test_save_event_to_calendar_view(self):
        response = self.client.post(reverse('save_event_to_calendar', kwargs={'event_id': self.event.event_id}))
        self.assertEqual(response.status_code, 302)  # Should redirect after saving event
        self.assertTrue(Calendar.objects.filter(user=self.user, event=self.event).exists())

    def test_remove_event_from_calendar_view(self):
        Calendar.objects.create(user=self.user, event=self.event, date=self.event.start_date)
        response = self.client.post(reverse('remove_event_from_calendar', kwargs={'event_id': self.event.event_id}))
        self.assertEqual(response.status_code, 302)  # Should redirect after removing event
        self.assertFalse(Calendar.objects.filter(user=self.user, event=self.event).exists())

    def test_notifications_view(self):
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications.html')

    def test_mark_notification_as_read_view(self):
        notification = Notification.objects.create(user=self.user, message="New notification")
        response = self.client.post(reverse('mark_notification_as_read', kwargs={'notification_id': notification.id}))
        self.assertEqual(response.status_code, 302)  # Should redirect after marking notification as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)