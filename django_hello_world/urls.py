from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', 'django_hello_world.hello.views.home', name='home'),
    url(r'^home/', include('django_hello_world.hello.urls',
        namespace="home_pages")),
    url(r'^requests/$', 'django_hello_world.hello.views.requests',
        name='requests'),
    url(r'^requests/remove/(?P<log_id>\d+)/$',
        'django_hello_world.hello.views.request_remove_handler',
        name='request_remove'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'},
        name="login_page"),
    url(r'^accounts/logout/$',
        'django.contrib.auth.views.logout', name="logout_url"),
    # url(r'^django_hello_world/', include('django_hello_world.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
