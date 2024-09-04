from django.contrib import admin
from .models import Event, Comment, Calendar, Rating
from django_summernote.admin import SummernoteModelAdmin

# Register the Event model
@admin.register(Event)
class EventAdmin(SummernoteModelAdmin):
    list_display = ('title', 'author', 'location', 'date', 'time', 'created_on')
    search_fields = ('title', 'description', 'location', 'slug')
    list_filter = ('date', 'author')
    ordering = ('-date',)
    summernote_fields = ('description',)  # Enable Summernote for the description field

    actions = ['publish_events']

    def publish_events(self, request, queryset):
        queryset.update(status='published')
    publish_events.short_description = "Mark selected events as published"

# Register the Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'created_on', 'approved']
    search_fields = ('content', 'user__username', 'event__title')
    list_filter = ('created_on', 'user', 'approved')
    ordering = ('-approved','-created_on',)
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)

    approve_comments.short_description = "Mark selected comments as approved"

# Register the Admin model
@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'date')  
    list_filter = ('user', 'date')  
    search_fields = ('user__username', 'event__title')  
    date_hierarchy = 'date'

# Register the Rating model
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'rating')
    search_fields = ('event__title', 'user__username')
    list_filter = ('rating',) 