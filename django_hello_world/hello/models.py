from django.db import models


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
    data = models.ForeignKey(MyData)
    contact_type = models.CharField(max_length=100, choices=CONTACT_TYPES)
    value = models.CharField(max_length=100)
