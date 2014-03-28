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
    from django.db.models import get_apps
    from django.db.models import get_models
    EXCLUDED_MODELS = ('ContentType', )

    app_list = get_apps()
    models = []

    for app in app_list:
        # Get all models for each app, except any excluded ones
        models += [m for m in get_models(
            app) if m.__name__ not in EXCLUDED_MODELS]

    for model in models:
        # For lazy count execute
        yield (model, model.objects.count())
