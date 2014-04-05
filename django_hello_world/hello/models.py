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


class PriorityDefaultManager(models.Manager):

    def get_query_set(self):
        return super(PriorityDefaultManager, self).get_query_set().filter(
            priority=PriorityRule.PRIOR_DEFAULT)


class PriorityHighManager(models.Manager):

    def get_query_set(self):
        return super(PriorityHighManager, self).get_query_set().filter(
            priority=PriorityRule.PRIOR_HIGH)


class PriorityRule(models.Model):
    ALLOWED_METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
    )

    PRIOR_DEFAULT = 0
    PRIOR_HIGH = 1

    PRIORITIES = (
        (PRIOR_DEFAULT, "Default"),
        (PRIOR_HIGH, "High"),
    )

    priority = models.IntegerField(default=PRIOR_DEFAULT, choices=PRIORITIES)
    method = models.CharField(max_length=10, choices=ALLOWED_METHODS)
    path = models.CharField(max_length=500)

    class Meta:
        unique_together = (("method", "path"), )

    def apply_to_existed(self):
        lookup_params = {}
        if self.method:
            lookup_params['method'] = self.method
        if self.path:
            lookup_params['path'] = self.path

        if lookup_params:
            RequestLog.objects.filter(
                **lookup_params).update(priority=self.priority)


class RequestLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    priority = models.IntegerField(default=PriorityRule.PRIOR_DEFAULT)
    date = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)

    objects = models.Manager()
    default_priority = PriorityDefaultManager()
    high_priority = PriorityHighManager()

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
            self.detect_priority(auto_set_priority=True)

    def detect_priority(self, auto_set_priority=True):
        """
        With this method you can get and/or set priority for this
        request. It will try to find prioritize rule for this kind of requests
        based on such attributes as path and method. When there is no any rule
        the priority will be set to default.
        """
        try:
            rule = PriorityRule.objects.get(path=self.path, method=self.method)
        except PriorityRule.DoesNotExist:
            return PriorityRule.PRIOR_DEFAULT

        if auto_set_priority:
            self.priority = rule.priority
        return rule.priority


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
