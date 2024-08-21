from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.db import models

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    time = models.TimeField(auto_now_add=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    image = CloudinaryField('image', default='placeholder-image')

    def __str__(self):
        return self.title

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # Field to check if comment is approved

    def __str__(self):
        return f'Comment by {self.user.username} on {self.event.title}'

class Calendar(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendars')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='calendar_events')
    date = models.DateTimeField()

    def __str__(self):
        return f'Calendar for {self.user.username} - {self.event.title} on {self.date}'