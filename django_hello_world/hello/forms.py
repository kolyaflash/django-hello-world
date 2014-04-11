from django import forms
from django.utils.formats import get_format
from .models import MyData, Contacts


class CalendarWidget(forms.DateInput):

    class Media:
        css = {
            'all': ('css/datepicker.css', )
        }
        js = ('js/bootstrap-datepicker.js', 'js/widgets.js')

    def __init__(self, attrs={}):

        date_format = get_format('DATE_INPUT_FORMATS')[0]

        attrs.update({'data-widget': 'calendar',
                     'data-format': date_format})
        super(CalendarWidget, self).__init__(attrs=attrs)


class ProfileForm(forms.ModelForm):
    email = forms.CharField(label="Email", required=True)
    skype = forms.CharField(label="Skype", required=False)
    JID = forms.CharField(label="Jabber", required=False)

    class Meta:
        model = MyData

        widgets = {
            'birth_date': CalendarWidget(),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        initial = kwargs.get("initial", {})

        if instance:
            contacts_initial = {}

            for contact_type in Contacts.CONTACT_TYPES:
                contact, created = instance.contacts_set.get_or_create(
                    contact_type=contact_type[0])
                contacts_initial[contact.contact_type] = contact.value

            initial.update(contacts_initial)
            kwargs['initial'] = initial

        super(ProfileForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        for contact_type in Contacts.CONTACT_TYPES:
            _type = contact_type[0]
            if not _type in self.cleaned_data:
                continue
            self.instance.contacts_set.filter(
                contact_type=_type).update(value=self.cleaned_data.get(_type))
        return super(ProfileForm, self).save(*args, **kwargs)
