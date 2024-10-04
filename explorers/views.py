from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.contrib.auth.decorators import login_required
from django.views import View, generic
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, TemplateView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.views import LoginView
from django.contrib import messages
from .models import Event, Calendar, Rating, Comment, Notification, UserProfile
from .forms import EventForm, CommentForm, NotificationPreferencesForm
from django.utils import timezone
from datetime import datetime


# View for homepage

class Home(View):
    def get(self, request):
        upcoming_events = Event.objects.filter(
            status='published', start_date__gte=timezone.now()
        ).order_by('start_date')[:3]  # Get next 3 upcoming events
        return render(
            request, 'index.html', {'upcoming_events': upcoming_events}
        )

# View to list events with filters (homepage)


class EventList(generic.ListView):
    model = Event
    template_name = 'event_list.html'
    paginate_by = 6

    def get_queryset(self):
        return Event.objects.filter(status='published').order_by('-created_on')

# View to save an event to the user's calendar


@login_required
def save_event_to_calendar(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    event.start_date = (timezone.make_aware(event.start_date)
                        if timezone.is_naive(event.start_date)
                        else event.start_date)
    Calendar.objects.get_or_create(
        user=request.user, event=event, date=event.start_date
    )
    return redirect('event_detail', slug=event.slug)

# View to display the user's saved events in their calendar


class SavedEventsView(LoginRequiredMixin, ListView):
    model = Calendar
    template_name = 'saved_events.html'
    context_object_name = 'saved_events'

    def get_queryset(self):
        # Get the filtered month & default to current month
        selected_month = self.request.GET.get('month', None)
        current_month = timezone.now().month
        current_year = timezone.now().year
        current_date = timezone.now()

        if selected_month:
            month, year = map(int, selected_month.split('-'))
        else:
            month, year = current_month, current_year

        # Filter events and only show events from today onwards
        return Calendar.objects.filter(
            user=self.request.user,
            event__start_date__month=month,
            event__start_date__year=year,
            event__end_date__gte=current_date
        ).order_by('event__start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month = timezone.now().strftime('%m-%Y')

        # Get the selected month from query params if available
        selected_month = self.request.GET.get('month', current_month)
        context['selected_month'] = selected_month

        # Pass months available for filtering
        context['months'] = Calendar.objects.dates(
            'event__start_date', 'month', order='DESC'
        )
        return context

# View to remove an event from users calendar


@login_required
def remove_event_from_calendar(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    Calendar.objects.filter(user=request.user, event=event).delete()
    return redirect('event_detail', slug=event.slug)

# View to display the rating submission


@login_required
def rate_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    # Check if the user has already rated this event
    existing_rating = Rating.objects.filter(
        user=request.user, event=event
    ).first()
    if existing_rating:
        # If user has already rated the event, show an error message
        messages.error(request, "You have already rated this event.")
        return redirect('event_detail', slug=event.slug)
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        # Create the new rating
        rating, created = Rating.objects.get_or_create(
            user=request.user, event=event
        )
        rating.rating = rating_value
        rating.save()

        # Show a success message after rating
        messages.success(request, "Thank you for rating this event!")
        return redirect('event_detail', slug=event.slug)
    return render(request, 'rate_event.html', {'event': event})

# View to display event details


class EventDetail(View):
    def get(self, request, slug, *args, **kwargs):
        event = get_object_or_404(Event, slug=slug)
        comments = event.comments.filter(approved=True).order_by('created_on')
        comment_form = CommentForm()
        saved_to_calendar = False

        if request.user.is_authenticated:
            saved_to_calendar = Calendar.objects.filter(
                user=request.user, event=event
            ).exists()

        return render(
            request,
            'event_detail.html',
            {
                'event': event,
                'comments': comments,
                'comment_form': comment_form,
                'saved_to_calendar': saved_to_calendar,
                'user': request.user
            },
        )

    def post(self, request, slug, *args, **kwargs):
        event = get_object_or_404(Event, slug=slug)
        comments = event.comments.filter(approved=True).order_by('created_on')
        comment_form = CommentForm(data=request.POST)
        saved_to_calendar = False

        if request.user.is_authenticated:
            saved_to_calendar = Calendar.objects.filter(
                user=request.user, event=event
            ).exists()

        if comment_form.is_valid():
            comment_form.instance.user = request.user
            comment = comment_form.save(commit=False)
            comment.event = event
            comment.save()
            return redirect('event_detail', slug=event.slug)

        return render(
            request,
            'event_detail.html',
            {
                'event': event,
                'comments': comments,
                'comment_form': comment_form,
                'saved_to_calendar': saved_to_calendar
            },
        )

# View to browse events


class BrowseEventsView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort_by', 'start_date')
        current_date = timezone.now()
        # Fetch only events that have a future or current start date
        events = Event.objects.filter(start_date__gte=current_date)

        # Apply search filter
        if search_query:
            events = events.filter(
                title__icontains=search_query
            ) | events.filter(description__icontains=search_query)

        # Apply sorting
        if sort_by == 'location':
            events = events.order_by('location')
        elif sort_by == 'title':
            events = events.order_by('title')
        else:
            events = events.order_by('start_date')

        return render(request, 'browse_events.html', {'events': events})

# View to add an event


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'add_event.html'
    success_url = reverse_lazy('event_confirmation')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.start_date = timezone.make_aware(
            form.instance.start_date) if timezone.is_naive(
            form.instance.start_date) else form.instance.start_date
        form.instance.end_date = timezone.make_aware(
            form.instance.end_date) if timezone.is_naive(
            form.instance.end_date) else form.instance.end_date
        return super().form_valid(form)  # Call the original form_valid method

# View to update an event


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'edit_event.html'

    def form_valid(self, form):
        form.instance.user = self.request.user  # Ensure the author is set
        form.instance.start_date = timezone.make_aware(
            form.instance.start_date) if timezone.is_naive(
            form.instance.start_date) else form.instance.start_date
        form.instance.end_date = timezone.make_aware(
            form.instance.end_date) if timezone.is_naive(
            form.instance.end_date) else form.instance.end_date
        messages.success(
            self.request, "Your event has been updated successfully!"
        )
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the event detail page after a successful update
        return reverse_lazy('event_detail', kwargs={'slug': self.object.slug})

    def test_func(self):
        event = self.get_object()
        return (
            self.request.user.is_superuser or event.author == self.request.user
        )

# View to delete an event


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        event = self.get_object()
        return (
            event.author == self.request.user or self.request.user.is_superuser
        )

# View to display the events created by the logged-in user


class MyEventsView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'my_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Get search and sorting parameters from the request
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'start_date')

        # Filter events created by the logged-in user
        queryset = Event.objects.filter(author=self.request.user)

        # Apply search filter if a query is provided
        if search_query:
            queryset = queryset.filter(
                title__icontains=search_query
            ) | queryset.filter(description__icontains=search_query)

        # Apply sorting logic based on the sort_by parameter
        if sort_by == 'title':
            queryset = queryset.order_by('title')
        elif sort_by == 'location':
            queryset = queryset.order_by('location')
        else:
            queryset = queryset.order_by('start_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass search and sorting values back to the template to maintain state
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'start_date')
        return context

# View to display message for too many login attempts


class CustomLoginView(LoginView):
    def form_invalid(self, form):
        return super().form_invalid(form)

# View to test signup closed page


def signup_closed(request):
    return render(request, 'account/signup_closed.html')

# View for editing a comment


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['content']
    template_name = 'edit_comment.html'

    def get_success_url(self):
        return self.object.event.get_absolute_url()

    def test_func(self):
        comment = self.get_object()
        return (
            self.request.user == comment.user or self.request.user.is_superuser
        )

# View for deleting a comment


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'delete_comment.html'

    def get_success_url(self):
        return self.object.event.get_absolute_url()

    def test_func(self):
        comment = self.get_object()
        return (
            self.request.user == comment.user or self.request.user.is_superuser
        )

# View for managing emails


class ManageEmailView(LoginRequiredMixin, TemplateView):
    template_name = 'account/email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_add_email'] = True
        return context

# View to display notifications on user dashboard


@login_required
def notifications_view(request):
    # Get or create the user's profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    # Fetch notifications
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Handle POST request to update preferences
    if request.method == 'POST':
        preferences_form = NotificationPreferencesForm(
            request.POST, instance=user_profile
        )
        if preferences_form.is_valid():
            preferences_form.save()
            return redirect('notifications')
    else:
        preferences_form = NotificationPreferencesForm(instance=user_profile)

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'preferences_form': preferences_form,
    })


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect('notifications')

# custom 404 view


def custom_404(request, exception):
    return render(request, '404.html', status=404)