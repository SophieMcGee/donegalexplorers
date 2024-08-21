from django.contrib import admin
from .models import Event, Comment
from django_summernote.admin import SummernoteModelAdmin

# Register the Event model
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'location', 'date', 'time', 'created_on')
    search_fields = ('title', 'description', 'location')
    list_filter = ('date', 'author')
    ordering = ('-date',)
    summernote_fields = ('description',)  # Enable Summernote for the description field

# Register the Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'created_on', 'content')
    search_fields = ('content', 'user__username', 'event__title')
    list_filter = ('created_on', 'user')
    ordering = ('-created_on',)
