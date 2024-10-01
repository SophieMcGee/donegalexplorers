from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        author = event.author

        # Check if the user wants to receive notifications
        if author.userprofile.receive_comment_notifications:
            send_mail(
                'New Comment on Your Event',
                f'A new comment has been posted on your event "{event.title}". Check it out!',
                settings.DEFAULT_FROM_EMAIL,
                [author.email],  # Send the email to the event's author
                fail_silently=False,
            )