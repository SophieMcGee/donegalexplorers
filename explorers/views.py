from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import Event, Calendar, Rating


def my_blog(request):
    return HttpResponse("Hello, Blog!")

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
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

# View to list events with filters
class EventList(generic.ListView):
    model = Event
    queryset = Event.objects.all().order_by('-created_on')
    template_name = 'event_list.html'
    paginate_by = 6