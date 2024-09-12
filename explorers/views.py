from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views import View, generic
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.views import LoginView
from django.contrib import messages
from .models import Event, Calendar, Rating, Comment
from .forms import EventForm, CommentForm

# View for homepage

class Home(View):
    def get(self, request):
        return render(request, 'index.html')

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
    Calendar.objects.get_or_create(user=request.user, event=event, date=event.start_date)
    return redirect('event_detail', slug=event.slug)

# View to display the user's saved events in their calendar
class SavedEventsView(LoginRequiredMixin, ListView):
    model = Calendar
    template_name = 'saved_events.html'
    context_object_name = 'saved_events'
    
    def get_queryset(self):
        return Calendar.objects.filter(user=self.request.user).order_by('-saved_on')

# View to remove an event from users calendar
@login_required
def remove_event_from_calendar(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    Calendar.objects.filter(user=request.user, event=event).delete()
    return redirect('event_detail', slug=event.slug)

# View to display the rating submission
@login_required
def rate_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        rating, created = Rating.objects.get_or_create(user=request.user, event=event)
        rating.rating = rating_value
        rating.save()
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
            saved_to_calendar = Calendar.objects.filter(user=request.user, event=event).exists()

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
            saved_to_calendar = Calendar.objects.filter(user=request.user, event=event).exists()

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
        
        events = Event.objects.all()

        # Apply search filter
        if search_query:
            events = events.filter(title__icontains=search_query) | events.filter(description__icontains=search_query)

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
        form.instance.author = self.request.user  # Assign the logged-in user to the event
        return super().form_valid(form)  # Call the original form_valid method

# View to update an event
class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'edit_event.html'
    

    def form_valid(self, form):
        form.instance.user = self.request.user  # Ensure the author is set
        messages.success(self.request, "Your event has been updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the event detail page after a successful update
        return reverse_lazy('event_detail', kwargs={'slug': self.object.slug})

    def test_func(self):
        event = self.get_object()
        return self.request.user.is_superuser or event.user == self.request.user

# View to delete an event

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        event = self.get_object()
        return event.author == self.request.user or self.request.user.is_superuser

# View to display the events created by the logged-in user
class MyEventsView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'my_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(author=self.request.user).order_by('-created_on')

# View to display message for too many login attempts

class CustomLoginView(LoginView):
    def form_invalid(self, form):
        # Check if throttling is triggered
        if self.request.session.get('login_attempts') > ACCOUNT_LOGIN_ATTEMPTS_LIMIT:
            messages.error(self.request, "Too many login attempts. Try again later.")
            return render(self.request, 'account/login_attempt.html')
        return super().form_invalid(form)

# View to test signup closed page

def signup_closed(request):
    return render(request, 'account/signup_closed.html')