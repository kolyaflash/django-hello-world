from django.conf.urls import url, patterns

urlpatterns = patterns(
    'django_hello_world.hello.views',
    url(r'^edit/$', 'home_edit', name='edit'),
)
