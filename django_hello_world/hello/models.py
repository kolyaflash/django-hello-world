from django.db import models
from django.contrib.auth.models import User


class MyData(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    bio = models.TextField(null=True)
    contacts_additional = models.TextField(null=True)


class Contacts(models.Model):
    CONTACT_TYPES = (
        ('email', 'Email'),
        ('skype', 'Skype'),
        ('JID', 'Jabber'),
    )
    data = models.ForeignKey(MyData, on_delete=models.CASCADE)
    contact_type = models.CharField(max_length=100, choices=CONTACT_TYPES)
    value = models.CharField(max_length=100)


class RequestLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)

    class Meta:
        ordering = ['-date']

    def __init__(self, *args, **kwargs):
        """
        Pass `_request` as kwarg for fill objects with data.
        `_request` should be request instance.
        """

        request = kwargs.pop("_request", None)
        if request:
            if isinstance(request.user, User):
                self.user = request.user
            self.path = request.get_full_path()
            self.method = request.method

        super(RequestLog, self).__init__(*args, **kwargs)
