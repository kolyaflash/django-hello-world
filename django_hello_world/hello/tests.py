"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import sys
from cStringIO import StringIO
from contextlib import contextmanager
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django_hello_world.hello.models import MyData
from django_hello_world.hello.models import RequestLog, PriorityRule


@contextmanager
def capture_out(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    _out, sys.stderr = sys.stderr, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class HttpTest(TestCase):

    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello!')

    def test_home_edit(self):
        # Get request protected
        response = self.client.get(reverse('home_pages:edit'))
        self.assertEqual(response.status_code, 302)

        # Get request protected
        response = self.client.post(reverse('home_pages:edit'))
        self.assertEqual(response.status_code, 302)

    def test_requests(self):
        response = self.client.get(reverse('requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Requests')


class CommandsTest(TestCase):

    def test_models_stat(self):
        with capture_out(call_command, 'modelstat') as stat_output:
            self.assertTrue('MyData\t%d' %
                            MyData.objects.count() in stat_output)


class CommonTest(TestCase):
    fixtures = ['initial_data.json', ]

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        profile = response.context["profile"]
        self.assertTrue('profile' in response.context)
        profile = response.context['profile']
        self.assertTrue(isinstance(profile, MyData))
        self.assertContains(response, profile.first_name)
        self.assertContains(response,
                            profile.contacts_set.get(
                                contact_type='email').value)

    def test_requests_logging(self):
        self.client.get(reverse('home'))
        self.assertEqual(RequestLog.objects.all().count(), 1)
        log = RequestLog.objects.all()[0]
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.path, reverse('home'))
        self.assertIsNotNone(log.date)
        self.assertIsNone(log.user)

    def test_request_page(self):
        response = self.client.get(reverse('requests') + '?priority=')
        self.assertTrue('requests' in response.context)
        self.assertEqual(len(response.context['requests']), 1)

    def test_context(self):
        response = self.client.get(reverse('home'))
        self.assertTrue('django_settings' in response.context)
        context_settings = response.context['django_settings']
        self.assertEqual(context_settings.ROOT_URLCONF, settings.ROOT_URLCONF)
        self.assertFalse(hasattr(context_settings, 'SECRET_KEY'))

    def _get_test_form_data(self):
        self.assertTrue(self.client.login(username="admin", password="admin"))
        response = self.client.get(reverse('home_pages:edit'))
        form = response.context['form']
        test_data = form.initial
        test_data['photo'] = None

        return test_data

    def test_home_edit(self):
        response = self.client.get(reverse('home_pages:edit'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [
                         ('http://testserver/accounts/login/?next=/home/edit/',
                          302)])

        self.assertTrue(self.client.login(username="admin", password="admin"))
        response = self.client.get(reverse('home_pages:edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

        test_data = self._get_test_form_data()
        self.assertTrue('email' in test_data)

        # Saves valid data
        response = self.client.post(reverse('home_pages:edit'), test_data)
        self.assertTrue(response.context['form'].is_valid())

        # Form contains errors
        response = self.client.post(reverse('home_pages:edit'),
                                    dict(test_data, **{"email": ""}))
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue("email" in response.context['form'].errors)
        self.assertContains(response, 'has-errors')

        # Valid changes in form
        response = self.client.post(reverse('home_pages:edit'),
                                    dict(test_data,
                                         **{"email": "valid@email.com"}))
        self.assertTrue(response.context['form'].is_valid())
        mydata = MyData.objects.get(id=1)
        self.assertEqual(mydata.contacts_set.get(
            contact_type="email").value, "valid@email.com")

    def test_calendar_widget(self):
        from django_hello_world.hello.forms import CalendarWidget

        self.assertTrue(self.client.login(username="admin", password="admin"))
        response = self.client.get(reverse('home_pages:edit'))

        for excepted_str in CalendarWidget.Media.js:
            self.assertContains(response, excepted_str)

        for excepted_str in CalendarWidget.Media.css['all']:
            self.assertContains(response, excepted_str)

    def test_home_edit_photo(self):
        from django.contrib.staticfiles import finders
        test_data = self._get_test_form_data()
        file_name = 'avatar.jpg'

        test_file = finders.find(file_name)
        with open(test_file) as fp:
            try:
                response = self.client.post(reverse('home_pages:edit'),
                                            dict(test_data, **{"photo": fp}))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].is_valid())
                self.assertContains(response, file_name)

                mydata = MyData.objects.get(id=1)
                self.assertTrue(mydata.photo)
            finally:
                try:
                    mydata.photo.delete()
                except:
                    pass

    def test_home_edit_ajax(self):
        test_data = self._get_test_form_data()

        self.assertTrue(self.client.login(username="admin", password="admin"))
        response = self.client.post(reverse('home_pages:edit'),
                                    test_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, "fieldset")
        self.assertNotContains(response, "</body>")

    def test_admin_url_templ_tag(self):
        from django.contrib.auth.models import User
        from django.template import Template, Context
        mydata = MyData.objects.get(id=1)

        def get_out(test_obj):
            out = Template(
                "{% load admin_url %}"
                "{% admin_url test_obj %}"
            ).render(Context({"test_obj": test_obj}))
            return out

        test_obj = User.objects.get(id=1)
        excepted_result = "/admin/auth/user/1/"
        self.assertEqual(get_out(test_obj), excepted_result)

        with self.assertRaises(TypeError):
            get_out("JustAString")

        self.assertEqual(get_out(mydata), 'None')

    def test_logging_models(self):
        from django_hello_world.hello.models import ModelActionLog
        from django.conf import settings

        # Test create log

        with self.assertRaises(ModelActionLog.DoesNotExist):
            ModelActionLog.objects.get(instance_id=9999, model_name="MyData")

        test_my_data = {
            "id": 9999,
            "first_name": "Unit",
            "last_name": "Test",
            "birth_date": "2014-03-29",
        }

        test_obj = MyData(**test_my_data)
        test_obj.save()

        test_obj_log = ModelActionLog.objects.get(
            instance_id=9999, model_name="MyData")
        self.assertEqual(test_obj_log.action, "CREATE")
        self.assertTrue(test_obj_log.datetime)

        # Test update log
        test_obj.first_name = "Super"
        test_obj.save()

        test_obj_log = ModelActionLog.objects.get(
            instance_id=9999, model_name="MyData", action="UPDATE")

        # Test delete log
        test_obj.delete()
        ModelActionLog.objects.get(
            instance_id=9999, model_name="MyData", action="DELETE")

    @override_settings(APPS_TO_LOG_DB_CHANGES=[])
    def test_logging_models_ingore(self):
        from django_hello_world.hello.models import ModelActionLog
        prev_count = ModelActionLog.objects.count()

        mydata = MyData.objects.all()[0]
        mydata.first_name = "test"
        mydata.save()

        # No update record
        self.assertEqual(prev_count, ModelActionLog.objects.count())


class RequestsTest(TestCase):

    def setUp(self):
        self.log1 = RequestLog(path="/test/", method="GET")
        self.log1.save()
        self.log2 = RequestLog(path="/test/2/", method="GET")
        self.log2.save()
        self.log3 = RequestLog(path="/test/2/", method="GET")
        self.log3.save()
        self.log4 = RequestLog(path="/test/2/", method="POST")
        self.log4.save()
        self.log5 = RequestLog(path="/test/post/", method="POST")
        self.log5.save()
        super(RequestsTest, self).setUp()

    def test_default_state(self):
        self.assertEqual(RequestLog.objects.all().count(),
                         RequestLog.objects.filter(priority=0).count())

    def test_detect_priority(self):
        self.assertEqual(self.log1.priority, 0)
        rule1 = PriorityRule(
            path=self.log1.path,
            method=self.log1.method,
            priority=PriorityRule.PRIOR_HIGH)
        rule1.save()

        self.assertEqual(self.log1.detect_priority(), rule1.priority)
        self.assertEqual(self.log1.priority, PriorityRule.PRIOR_HIGH)

    def test_apply_to_existed(self):
        rule1 = PriorityRule(
            path="/test/2/",
            method="GET",
            priority=PriorityRule.PRIOR_HIGH)
        rule1.save()

        rule1.apply_to_existed()
        self.assertEqual(list(RequestLog.high_priority.all().order_by('id')),
                         [self.log2, self.log3])

        rule2 = PriorityRule(
            path="/test/2/",
            method="POST",
            priority=PriorityRule.PRIOR_HIGH)
        rule2.save()
        rule2.apply_to_existed()
        self.assertEqual(list(RequestLog.high_priority.all().order_by('id')),
                         [self.log2, self.log3, self.log4])

    def test_priority_on_create(self):
        rule1 = PriorityRule(
            path="/",
            method="GET",
            priority=PriorityRule.PRIOR_HIGH)
        rule1.save()

        self.client.get("/")

        self.assertTrue(
            RequestLog.high_priority.filter(path="/")
        )

    def test_prior_all_post(self):
        rule1 = PriorityRule(
            method="POST",
            priority=PriorityRule.PRIOR_HIGH)
        rule1.save()
        rule1.apply_to_existed()
        self.assertEqual(list(RequestLog.high_priority.all().order_by('id')),
                         [self.log4, self.log5])

    def test_requests_page(self):
        resp = self.client.get(reverse("requests"))
        self.assertEqual(resp.status_code, 200)

        rule1 = PriorityRule(
            method="GET",
            priority=PriorityRule.PRIOR_HIGH)
        rule1.save()
        rule1.apply_to_existed()

        # Show only high priority

        resp = self.client.get(reverse("requests") + '?priority=1')
        self.assertEqual(resp.status_code, 200)

        real = sorted(resp.context['requests'].values_list('id', flat=True))
        expected = sorted(
            RequestLog.high_priority.all()[:10].values_list('id', flat=True))

        self.assertEqual(real, expected)

        # Show only default priority

        resp = self.client.get(reverse("requests") + '?priority=0')
        self.assertEqual(resp.status_code, 200)

        real = sorted(resp.context['requests'].values_list('id', flat=True))
        expected = sorted(
            RequestLog.default_priority.all()[:10].values_list('id', flat=True))

        self.assertEqual(real, expected)

        # Show all priority
        resp = self.client.get(reverse("requests") + '?priority=')
        self.assertEqual(resp.status_code, 200)

        real = sorted(resp.context['requests'].values_list('id', flat=True))
        expected = sorted(
            RequestLog.objects.all()[:10].values_list('id', flat=True))

        self.assertEqual(real, expected)
