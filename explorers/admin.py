from django.contrib import admin
from .models import Event, Comment
from django_summernote.admin import SummernoteModelAdmin

# Register the Event model
@admin.register(Event)
class EventAdmin(SummernoteModelAdmin):
    list_display = ('title', 'author', 'location', 'date', 'time', 'created_on')
    search_fields = ('title', 'description', 'location')
    list_filter = ('date', 'author')
    ordering = ('-date',)
    summernote_fields = ('description',)  # Enable Summernote for the description field

# Register the Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'created_on', 'approved']
    search_fields = ('content', 'user__username', 'event__title')
    list_filter = ('created_on', 'user')
    ordering = ('-created_on',)
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)

    approve_comments.short_description = "Mark selected comments as approved"
