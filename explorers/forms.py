from django import forms
from .models import Event, Comment, UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'location', 'start_date', 'end_date',
            'start_time', 'end_time', 'image', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure that end date is after start date
        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                _('End date must be after the start date.'),
                code='invalid'
            )

        # Continue to clean the data as necessary
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '',
        }
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter your comment here...'
                }
            ),
        }


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['receive_comment_notifications']


class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['receive_comment_notifications']
        labels = {
            'receive_comment_notifications': (
                'Receive notifications for comments'
            ),
        }