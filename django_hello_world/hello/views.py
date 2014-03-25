from django.contrib import messages
from annoying.decorators import render_to
from .models import MyData, RequestLog


@render_to('hello/home.html')
def home(request):
    context = {}

    try:
        mydata = MyData.objects.get(id=1)
    except MyData.DoesNotExist:
        messages.error(request, "Run syncdb first")
        return {}

    context['profile'] = mydata
    context['contacts'] = mydata.contacts_set.all()
    return context


@render_to('hello/requests.html')
def requests(request):
    context = {}
    context['requests'] = RequestLog.objects.all().order_by('date')[:10]
    return context
