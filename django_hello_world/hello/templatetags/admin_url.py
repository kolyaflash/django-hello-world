# reverse('admin_%s_%s_change' % (app_label, model_name), args=(object_id,))
from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
register = template.Library()


@register.simple_tag
def admin_url(obj):
    if not hasattr(obj, "_meta"):
        raise TypeError("You can't pass this object to admin_url")

    # Django templates supposed to fail silently.
    try:
        return reverse('admin:%s_%s_change' % (
            obj._meta.app_label, obj._meta.module_name), args=[obj.id,])
    except NoReverseMatch:
        return
