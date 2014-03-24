from django.db import models


class MyData(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    bio = models.TextField()
    contacts = models.TextField()
