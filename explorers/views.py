from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views import View, generic
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event, Calendar, Rating, Comment
from .forms import EventForm, CommentForm

# View to list events with filters (homepage)
class EventList(generic.ListView):
    model = Event
    queryset = Event.objects.all().order_by('-created_on')
    template_name = 'event_list.html'
    paginate_by = 6

# View to save an event to the user's calendar
@login_required
def save_event_to_calendar(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    Calendar.objects.get_or_create(user=request.user, event=event, date=event.date)
    return redirect('event_detail', slug=event.slug)

# View to display the user's saved events
class SavedEventsView(LoginRequiredMixin, ListView):
    model = Calendar
    template_name = 'saved_events.html'
    context_object_name = 'saved_events'
    
    def get_queryset(self):
        return Calendar.objects.filter(user=self.request.user).order_by('-saved_on')

# View to display the rating submission
@login_required
def rate_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
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

        return render(request, 'event_detail.html', {
            'event': event,
            'comments': comments,
            'comment_form': comment_form,
        })

    @login_required
    def post(self, request, slug, *args, **kwargs):
        event = get_object_or_404(Event, slug=slug)
        comments = event.comments.filter(approved=True).order_by('created_on')
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.event = event
            comment.user = request.user
            comment.save()
            return redirect('event_detail', slug=event.slug)
        
        return render(request, 'event_detail.html', {
            'event': event,
            'comments': comments,
            'comment_form': comment_form,
        })

# View to browse events
class BrowseEventsView(View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.all()
        return render(request, 'browse_events.html', {'events': events})

# View to add an event
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'add_event.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the logged-in user to the event
        return super().form_valid(form)  # Call the original form_valid method

# View to update an event
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'edit_event.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        event = super().get_object(queryset)
        
        # Check if the user is the author or an admin
        if not self.request.user.is_superuser and event.user != self.request.user:
            # Return a forbidden response if the user is not authorised
            raise HttpResponseForbidden("You are not allowed to edit this event.")
        
        return event

# View to delete an event

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        event = super().get_object(queryset)
        
        # Check if the user is the author or an admin
        if not self.request.user.is_superuser and event.author != self.request.user:
            # Return a forbidden response if the user is not authorised
            raise HttpResponseForbidden("You are not allowed to delete this event.")
        
        return event

# View to display the events created by the logged-in user
class MyEventsView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'my_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(author=self.request.user).order_by('-created_on')

