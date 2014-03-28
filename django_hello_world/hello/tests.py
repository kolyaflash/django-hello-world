"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django_hello_world.hello.models import MyData


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class HttpTest(TestCase):

    def test_home(self):
        c = Client()
        response = c.get(reverse('home'))
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
        c = Client()
        response = c.get(reverse('requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Requests')


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
        from django_hello_world.hello.models import RequestLog
        self.client.get(reverse('home'))
        self.assertEqual(RequestLog.objects.all().count(), 1)
        log = RequestLog.objects.all()[0]
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.path, reverse('home'))
        self.assertIsNotNone(log.date)
        self.assertIsNone(log.user)

    def test_request_page(self):
        response = self.client.get(reverse('requests'))
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

        form = response.context['form']
        test_data = self._get_test_form_data()

        response = self.client.post(reverse('home_pages:edit'), test_data)
        self.assertTrue(response.context['form'].is_valid())

        response = self.client.post(reverse('home_pages:edit'),
                                    dict(test_data, **{"email": ""}))
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue("email" in response.context['form'].errors)

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
                                    test_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, "fieldset")
        self.assertNotContains(response, "</body>")
