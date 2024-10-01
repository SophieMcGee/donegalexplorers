from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.urls import reverse
from autoslug import AutoSlugField
from django.db.models import Avg

class Event(models.Model):

    EVENT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    event_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255, null=False, blank=False)  
    slug = AutoSlugField(populate_from='title', unique=True, null=True, blank=True)
    description = models.TextField(null=False, blank=False)  
    location = models.CharField(max_length=255, null=False, blank=False)  
    start_date = models.DateTimeField(null=False, blank=False)  
    end_date = models.DateTimeField(null=False, blank=False)  
    start_time = models.TimeField(null=False, blank=False)  
    end_time = models.TimeField(null=False, blank=False)  
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    image = CloudinaryField('image', default='https://res.cloudinary.com/dsojbqe7b/image/upload/v1726670855/bmecfws82yver9zuiq8u.jpg')  
    status = models.CharField(max_length=10, choices=EVENT_STATUS_CHOICES, default='draft', null=False, blank=False)

    def average_rating(self) -> float:
        return Rating.objects.filter(event=self).aggregate(Avg("rating"))["rating__avg"] or 0

    def total_ratings(self) -> int:
        return Rating.objects.filter(event=self).count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})

    def clean(self):
        # Ensure that end date is not before start date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after the start date.")
        
        # Ensure that end time is after start time if the event is on the same day
        if self.start_date == self.end_date and self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after the start time for events on the same day.")

    class Meta:
        ordering = ['-start_date'] # Orders by start_date descending by default

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.user.is_authenticated:  # Auto-approve if the user is authenticated
            self.approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.event.title}'

    class Meta:
        ordering = ['created_on']  # Orders by 'created_on' ascending by default

class Calendar(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendars')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='calendar_events')
    date = models.DateTimeField()
    saved_on = models.DateTimeField(auto_now_add=True)  # The date the event was saved to the calendar

    def __str__(self):
        return f'Calendar for {self.user.username} - {self.event.title} on {self.date}'

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event.title}: {self.rating}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    receive_comment_notifications = models.BooleanField(default=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message