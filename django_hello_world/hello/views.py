from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from annoying.decorators import render_to
from .models import MyData, RequestLog, Contacts
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
@render_to('hello/home_edit.html')
def home_edit(request):
    context = {}

    mydata = get_object_or_404(MyData, pk=MY_DATA_ID)
    contacts_initial = {}

    for contact_type in Contacts.CONTACT_TYPES:
        contact, created = mydata.contacts_set.get_or_create(
            contact_type=contact_type[0])
        contacts_initial[contact_type[0]] = contact.value

    form = ProfileForm(instance=mydata, initial=contacts_initial)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=mydata)
        if form.is_valid():
            form.save()
            for contact_type in Contacts.CONTACT_TYPES:
                _type = contact_type[0]
                if not _type in form.cleaned_data:
                    continue
                mydata.contacts_set.filter(
                    contact_type=_type).update(
                        value=form.cleaned_data.get(_type))

    context['form'] = form
    return context


@render_to('hello/requests.html')
def requests(request):
    context = {}
    context['requests'] = RequestLog.objects.all().order_by('date')[:10]
    return context
