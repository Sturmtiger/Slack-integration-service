from django.test import TestCase
from django.urls import reverse
from slack_integration.models import (SlackApplication, Template, ActionsBlock)


class AppListViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-list')
    login_url = reverse('login')
    template_name = 'slack_integration/list/app.html'

    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_logged_in(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        # Checks the logged in user does not redirect to the login page
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class AppDetailViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-detail',
                         args=(SlackApplication.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/detail/app.html'

    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_logged_in(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        # Checks the logged in user does not redirect to the login page
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class CreateAppViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-registration')
    login_url = reverse('login')
    template_name = 'slack_integration/create/app.html'

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

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class UpdateAppViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-update',
                         args=(SlackApplication.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/update/app.html'

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

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class DeleteAppViewTest(TestCase):
    fixtures = ('dump.json',)
    object = SlackApplication.objects.first()
    tested_url = reverse('app-delete',
                         args=(object.pk,))
    login_url = reverse('login')

    def test_login_required(self):
        response = self.client.post(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_admin_can_delete_post(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.tested_url)
        self.assertRedirects(response, '/')

    def test_not_admin_cannot_delete_post(self):
        self.client.login(username='dev', password='dev')
        response = self.client.post(self.tested_url)
        self.assertEqual(response.status_code, 403)

    def test_obj_is_deleted_post(self):
        self.client.login(username='admin', password='admin')
        self.client.post(self.tested_url)
        # Check that object has been deleted.
        self.assertFalse(self.object in SlackApplication.objects.all())


class CreateTemplateViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('template-create',
                         args=(SlackApplication.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/create/template.html'

    def test_login_required(self):
        response = self.client.post(self.tested_url)
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

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class TemplateDetailViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('template-detail',
                         args=(Template.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/detail/template.html'

    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_logged_in(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        # Checks the logged in user does not redirect to the login page
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class UpdateTemplateViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('template-update',
                         args=(Template.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/update/template.html'

    def test_login_required(self):
        response = self.client.post(self.tested_url)
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

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class DeleteTemplateViewTest(TestCase):
    fixtures = ('dump.json',)
    object = Template.objects.first()
    tested_url = reverse('template-delete',
                         args=(object.pk,))
    login_url = reverse('login')

    def test_login_required(self):
        response = self.client.post(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_admin_can_delete_post(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.tested_url)
        self.assertRedirects(response, '/')

    def test_not_admin_cannot_delete_post(self):
        self.client.login(username='dev', password='dev')
        response = self.client.post(self.tested_url)
        self.assertEqual(response.status_code, 403)

    def test_obj_is_deleted_post(self):
        self.client.login(username='admin', password='admin')
        self.client.post(self.tested_url)
        # Check that object has been deleted.
        self.assertFalse(self.object in Template.objects.all())


class CreateActionsBlockViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('actions-block-create',
                         args=(ActionsBlock.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/create/actions_block.html'

    def test_login_required(self):
        response = self.client.post(self.tested_url)
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

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class ActionsBlockDetailViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('actions-block-detail',
                         args=(ActionsBlock.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/detail/actions_block.html'

    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_logged_in(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        # Checks the logged in user does not redirect to the login page
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class UpdateActionsBlockViewTest(TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('actions-block-update',
                         args=(ActionsBlock.objects.first().pk,))
    login_url = reverse('login')
    template_name = 'slack_integration/update/actions_block.html'

    def test_login_required(self):
        response = self.client.post(self.tested_url)
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

    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class DeleteActionsBlockViewTest(TestCase):
    fixtures = ('dump.json',)
    object = ActionsBlock.objects.first()
    tested_url = reverse('actions-block-delete',
                         args=(object.pk,))
    login_url = reverse('login')

    def test_login_required(self):
        response = self.client.post(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url,
                                                       self.tested_url))

    def test_admin_can_delete_post(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.tested_url)
        self.assertRedirects(response, '/')

    def test_not_admin_cannot_delete_post(self):
        self.client.login(username='dev', password='dev')
        response = self.client.post(self.tested_url)
        self.assertEqual(response.status_code, 403)

    def test_obj_is_deleted_post(self):
        self.client.login(username='admin', password='admin')
        self.client.post(self.tested_url)
        # Check that object has been deleted.
        self.assertFalse(self.object in ActionsBlock.objects.all())
