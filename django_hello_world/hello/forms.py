from django import forms
from .models import MyData
from django.utils.formats import get_format


class CalendarWidget(forms.DateInput):

    class Media:
        css = {
            'all': ('datepicker/css/datepicker.css', )
        }
        js = ('datepicker/js/bootstrap-datepicker.js', 'widgets.js')

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
