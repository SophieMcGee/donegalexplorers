from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Comment
from django.core.mail import send_mail
from django.conf import settings

# Automatically create a UserProfile for new users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Automatically save the UserProfile whenever the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Check if the user has a profile, and save it if it exists
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# Send notification when a comment is posted on an event
@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        author = event.author

        # Check if the user has a profile and wants to receive notifications
        if hasattr(author, 'userprofile') and author.userprofile.receive_comment_notifications:
            send_mail(
                'New Comment on Your Event',
                f'A new comment has been posted on your event "{event.title}". Check it out!',
                settings.DEFAULT_FROM_EMAIL,
                [author.email],  # Send the email to the event's author
                fail_silently=False,
            )