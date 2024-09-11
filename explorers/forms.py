from django import forms
from .models import Event, Comment


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date', 'start_time', 'end_time', 'image', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}), 
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
    
        
        self.fields['title'].widget.attrs.update({'placeholder': 'Event Title'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Event Description'})
        self.fields['location'].widget.attrs.update({'placeholder': 'Event Location'})
        self.fields['start_time'].widget.attrs.update({'placeholder': 'Start Time'})
        self.fields['end_time'].widget.attrs.update({'placeholder': 'End Time'})
    
    def clean(self):
        # Get cleaned data
        cleaned_data = super().clean()
    
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        
        if end_time and start_time and end_time <= start_time:
            raise ValidationError("End time must be after the start time.")

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