from django.test import TestCase
from django.urls import reverse

class AppListViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-list')
    login_url = reverse('login')

    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_logged_in(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        # Checks the logged in user does not redirect to the login page
        self.assertEqual(response.status_code, 200)


class CreateAppViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-registration')
    login_url = reverse('login')

    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_logged_in_not_admin(self):
        self.client.login(username='dev', password='dev')
        response = self.client.get(self.tested_url)
        self.assertEqual(response.status_code, 403)

    def test_logged_in_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.tested_url)
        self.assertEqual(response.status_code, 200)
