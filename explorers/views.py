from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View, generic
from django.views.generic import ListView, CreateView
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
    return redirect('view_event', event_id=event.id)  # Redirect to the event view or wherever you want

# View to display the user's saved events
@login_required
def view_saved_events(request):
    saved_events = Calendar.objects.filter(user=request.user).order_by('-saved_on')
    return render(request, 'saved_events.html', {'saved_events': saved_events})

# View to display the rating submission
@login_required
def rate_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        rating, created = Rating.objects.get_or_create(user=request.user, event=event)
        rating.rating = rating_value
        rating.save()
        return redirect('view_event', event_id=event_id)
    return render(request, 'rate_event.html', {'event': event})

# View to display event details
class EventDetail(View):
    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        comments = event.comments.filter(approved=True).order_by('created_on')

        return render(request, 'event_detail.html', {
            'event': event,
            'comments': comments,
            'comment_form': comment_form,
        })
        
    @login_required
    def post(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        comments = event.comments.filter(approved=True).order_by('created_on')
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.event = event
            comment.user = request.user
            comment.save()
            return redirect('event_detail', event_id=event.id)
        
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
