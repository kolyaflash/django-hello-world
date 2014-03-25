from django.conf import settings


class SettingGetter(object):
    UNAVAILABLE_KEYS = ['SECRET_KEY', ]

    @classmethod
    def _is_valid_key(cls, key):
        return not key in cls.UNAVAILABLE_KEYS

    def __getattr__(cls, key):
        if not hasattr(settings, key) or not cls._is_valid_key(key):
            raise AttributeError(
                "Settings has no {0} or {0} isn't accesible".format(key))

        return getattr(settings, key)


def django_settings(request):
    context = {}
    settings_for_context = {}

    settings_for_context = SettingGetter()

    context.update({
        "django_settings": settings_for_context,
    })
    return context
