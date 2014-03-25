from django_hello_world.hello.models import RequestLog


class RequestsLoggingMiddleware(object):

    def process_request(self, request):
        log = RequestLog(_request=request)
        log.save()
