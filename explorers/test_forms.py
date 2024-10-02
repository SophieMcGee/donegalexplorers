from django.test import TestCase
from explorers.forms import EventForm, CommentForm, NotificationPreferencesForm, NotificationSettingsForm
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
            'start_date': timezone.make_aware(datetime(2024, 10, 10)),  # Timezone-aware datetime
            'end_date': timezone.make_aware(datetime(2024, 10, 11)),    # Timezone-aware datetime
            'start_time': '10:00',
            'end_time': '14:00',
            'status': 'published'
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid(), msg="Form should be valid with all correct fields")

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
        self.assertFalse(form.is_valid(), msg="Form should be invalid when required fields are missing")

    def test_event_form_date_validation(self):
        form_data = {
            'title': 'Beach Cleanup',
            'description': 'Join us for a day of cleaning the beach!',
            'location': 'Bundoran Beach',
            'start_date': timezone.make_aware(datetime(2024, 10, 15)),  # Timezone-aware datetime
            'end_date': timezone.make_aware(datetime(2024, 10, 14)),    # End date before start date
            'start_time': '10:00',
            'end_time': '14:00',
            'status': 'published'
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when end_date is before start_date")

    def test_event_form_time_validation(self):
        form_data = {
            'title': 'Beach Cleanup',
            'description': 'Join us for a day of cleaning the beach!',
            'location': 'Bundoran Beach',
            'start_date': timezone.make_aware(datetime(2024, 10, 15)),  # Timezone-aware datetime
            'end_date': timezone.make_aware(datetime(2024, 10, 15)),    # Same start and end date
            'start_time': '14:00',
            'end_time': '10:00',  # End time before start time
            'status': 'published'
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when end_time is before start_time")

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
        form_data = {}  # No data provided
        form = NotificationPreferencesForm(data=form_data)
        
        # Form should still be valid even if no data is provided since BooleanField defaults to False
        self.assertTrue(form.is_valid(), msg="Form should be valid as Boolean fields default to False")
        
        # Confirm that the default value is False
        self.assertFalse(form.cleaned_data.get('receive_comment_notifications'), "The default value should be False")

class TestNotificationSettingsForm(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user_profile = UserProfile.objects.create(user=self.user, receive_comment_notifications=True)

    def test_notification_settings_form_valid(self):
        form_data = {'receive_comment_notifications': False}
        form = NotificationSettingsForm(data=form_data, instance=self.user_profile)
        self.assertTrue(form.is_valid(), msg="Form should be valid with correct data")

    def test_notification_settings_form_invalid(self):
        form_data = {}  # No data provided
        form = NotificationSettingsForm(data=form_data, instance=self.user_profile)
    
        # The form should be valid even if no data is provided because BooleanField defaults to False
        self.assertTrue(form.is_valid(), msg="Form should be valid even when no data is provided")