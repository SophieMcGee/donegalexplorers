from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Event, Calendar


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