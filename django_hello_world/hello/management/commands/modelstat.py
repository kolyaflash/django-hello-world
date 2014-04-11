from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Dumps the models summary.'
    args = 'None'

    def handle(self, *app_labels, **options):
        for model, objs_count in _models_iterator():
            res_str = "\t".join((model.__name__, unicode(objs_count)))
            print res_str
            self.stderr.write("error: %s\n" % res_str)


def _models_iterator():
    """ Gets a list of models and count of objects in them.
    Returns list of tuples (model, objects count).
    """
    from django.contrib.contenttypes.models import ContentType

    EXCLUDED_MODELS = ('ContentType', )

    content_types = ContentType.objects.all()
    models = []

    for ct in content_types:
        model = ct.model_class()
        if model.__name__ in EXCLUDED_MODELS:
            continue

        yield (model, model._default_manager.count())
