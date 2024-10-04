from django.test import TestCase
from explorers.forms import (
    EventForm, CommentForm, NotificationPreferencesForm, NotificationSettingsForm
)
from explorers.models import UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

class TestEventForm(TestCase):

    def test_event_form_valid(self):
        form_data = {
            'title': 'Beach Cleanup',
            'description': 'Join us for a day of cleaning the beach!',
            'location': 'Bundoran Beach',
            'start_date': timezone.make_aware(datetime(2024, 10, 10)),
            'end_date': timezone.make_aware(datetime(2024, 10, 11)),
            'start_time': '10:00',
            'end_time': '14:00',
            'status': 'published'
        }
        form = EventForm(data=form_data)
        self.assertTrue(
            form.is_valid(), msg="Form should be valid with all correct fields"
        )

    def test_event_form_missing_required_fields(self):
        form_data = {
            'title': '',  
            'description': '',
            'location': '',
            'start_date': '',
            'end_date': '',
            'start_time': '',
            'end_time': '',
            'status': ''
        }
        form = EventForm(data=form_data)
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid when fields are missing"
        )

    def test_event_form_date_validation(self):
        form_data = {
            'title': 'Beach Cleanup',
            'description': 'Join us for a day of cleaning the beach!',
            'location': 'Bundoran Beach',
            'start_date': timezone.make_aware(datetime(2024, 10, 15)),
            'end_date': timezone.make_aware(datetime(2024, 10, 14)),
            'start_time': '10:00',
            'end_time': '14:00',
            'status': 'published'
        }
        form = EventForm(data=form_data)
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid when end_date is before start"
        )

    def test_event_form_time_validation(self):
        form_data = {
            'title': 'Beach Cleanup',
            'description': 'Join us for a day of cleaning the beach!',
            'location': 'Bundoran Beach',
            'start_date': timezone.make_aware(datetime(2024, 10, 15)),
            'end_date': timezone.make_aware(datetime(2024, 10, 15)),
            'start_time': '14:00',
            'end_time': '10:00',
            'status': 'published'
        }
        form = EventForm(data=form_data)
        self.assertFalse(
            form.is_valid(), msg="Form should be invalid when end_time is before start"
        )

class TestCommentForm(TestCase):

    def test_comment_form_valid(self):
        form_data = {'content': 'Great event!'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        form_data = {'content': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())

class TestNotificationPreferencesForm(TestCase):

    def test_notification_preferences_valid(self):
        form_data = {'receive_comment_notifications': True}
        form = NotificationPreferencesForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_notification_preferences_defaults_to_false(self):
        form_data = {}
        form = NotificationPreferencesForm(data=form_data)

        self.assertTrue(
            form.is_valid(), msg="Form should be valid as Boolean fields default to False"
        )

        self.assertFalse(
            form.cleaned_data.get('receive_comment_notifications'),
            "The default value should be False"
        )

class TestNotificationSettingsForm(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='password123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user, receive_comment_notifications=True
        )

    def test_notification_settings_form_valid(self):
        form_data = {'receive_comment_notifications': False}
        form = NotificationSettingsForm(
            data=form_data, instance=self.user_profile
        )
        self.assertTrue(
            form.is_valid(), msg="Form should be valid with correct data"
        )

    def test_notification_settings_form_invalid(self):
        form_data = {}
        form = NotificationSettingsForm(
            data=form_data, instance=self.user_profile
        )

        self.assertTrue(
            form.is_valid(), msg="Form should be valid even when no data is provided"
        )