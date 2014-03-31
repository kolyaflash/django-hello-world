from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings


class MyData(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    bio = models.TextField(blank=True)
    contacts_additional = models.TextField(blank=True)
    photo = models.ImageField(upload_to='my_photos/', null=True, blank=True)


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

        super(RequestLog, self).__init__(*args, **kwargs)

        if request:
            if isinstance(request.user, User):
                self.user = request.user
            self.path = request.get_full_path()
            self.method = request.method


class ModelActionLog(models.Model):
    ACTIONS = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    )
    action = models.CharField(
        max_length=20, null=False, default=None, choices=ACTIONS)
    datetime = models.DateTimeField(auto_now_add=True)

    model_name = models.CharField(max_length=128)
    instance_id = models.CharField(max_length=128)


@receiver(models.signals.post_save)
@receiver(models.signals.post_delete)
def log_models(sender, **kwargs):
    INGORED_SENDERS = [ModelActionLog, ]
    app_labels_whitelist = getattr(settings, "APPS_TO_LOG_DB_CHANGES", [])

    instance = kwargs.get("instance")
    model_name = sender.__name__

    if model_name in INGORED_SENDERS or sender in INGORED_SENDERS:
        return

    if not sender._meta.app_label in app_labels_whitelist:
        return

    if not 'created' in kwargs:
        # It's probably a deletion (quacks like a duck)
        action = "DELETE"
    elif kwargs['created']:
        # It's a creation
        action = "CREATE"
    else:
        # It's probably an update
        action = "UPDATE"

    log = ModelActionLog()
    log.action = action
    if instance and hasattr(instance, 'id'):
        log.instance_id = instance.id
    log.model_name = model_name
    log.save()
