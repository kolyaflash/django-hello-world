from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from annoying.decorators import render_to
from .models import MyData, RequestLog, Contacts, PriorityRule
from .forms import ProfileForm


MY_DATA_ID = 1


@render_to('hello/home.html')
def home(request):
    context = {}

    try:
        mydata = MyData.objects.get(id=MY_DATA_ID)
    except MyData.DoesNotExist:
        messages.error(request, "Run syncdb first")
        return {}

    context['profile'] = mydata
    context['contacts'] = mydata.contacts_set.all()
    return context


@login_required
@render_to()
def home_edit(request):
    context = {}
    TEMPLATE = 'hello/home_edit.html'

    mydata = get_object_or_404(MyData, pk=MY_DATA_ID)
    contacts_initial = {}

    form = ProfileForm(instance=mydata)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=mydata)
        if form.is_valid():
            form.save()

    if request.is_ajax():
        TEMPLATE = 'hello/_home_fieldset.html'

    context['form'] = form
    context['TEMPLATE'] = TEMPLATE
    return context


@render_to('hello/requests.html')
def requests(request):
    context = {}
    qs = RequestLog.objects.all()

    _priority = request.GET.get("priority", 1)
    current_priority = ""

    try:
        filter_val = int(_priority)
    except ValueError:
        filter_val = None
    if filter_val is not None:
        current_priority = filter_val
        qs = qs.filter(priority=filter_val)

    context['requests'] = qs.order_by('date')[:10]
    context['priorities'] = PriorityRule.PRIORITIES
    context['current_priority'] = current_priority

    return context
