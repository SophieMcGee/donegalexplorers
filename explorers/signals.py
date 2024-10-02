from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Notification
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        author = event.author

        # Check if the author has a UserProfile and has opted in for notifications
        if hasattr(author, 'userprofile') and author.userprofile.receive_comment_notifications:
            # Create the notification
            Notification.objects.create(
                user=author,
                message=f"A new comment was posted on your event '{event.title}'"
            )
            # Send email
            send_mail(
                'New Comment on Your Event',
                f'A new comment has been posted on your event "{event.title}". Check it out!',
                settings.DEFAULT_FROM_EMAIL,
                [author.email],
                fail_silently=False,
            )
        else:
            print(f"User {author.username} has not opted in for notifications.")