from django.contrib import messages
from annoying.decorators import render_to
from .models import MyData


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
