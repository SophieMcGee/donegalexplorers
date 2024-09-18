from django import forms
from .models import Event, Comment
from django.core.exceptions import ValidationError


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_date', 'end_date', 'start_time', 'end_time', 'image', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}), 
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
    
        
        self.fields['title'].widget.attrs.update({'placeholder': 'Event Title'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Event Description'})
        self.fields['location'].widget.attrs.update({'placeholder': 'Event Location'})
        self.fields['start_date'].widget.attrs.update({'placeholder': 'Start Date'})
        self.fields['end_date'].widget.attrs.update({'placeholder': 'End Date'})
        self.fields['start_time'].widget.attrs.update({'placeholder': 'Start Time'})
        self.fields['end_time'].widget.attrs.update({'placeholder': 'End Time'})

        # Set required attributes explicitly in the form fields
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['location'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['start_time'].required = True
        self.fields['end_time'].required = True
        self.fields['image'].required = True
        self.fields['status'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # Check that end date is not before start date
        if end_date and start_date and end_date < start_date:
            raise ValidationError("End date must be after the start date.")

        # Check that end time is not before start time (only for events happening on the same day)
        if start_date == end_date and end_time and start_time and end_time <= start_time:
            raise ValidationError("End time must be after the start time for events on the same day.")

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '',
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your comment here...'}),
        }