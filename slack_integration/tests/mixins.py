from django.urls import reverse


class LoggedInAdminAndNotAdminTestMixin:
    """
    Mixin to check views where only the user from 'Admin' group can access.
    """
    def test_logged_in_not_admin(self):
        self.client.login(username='dev', password='dev')
        response = self.client.get(self.tested_url)
        self.assertEqual(response.status_code, 403)

    def test_logged_in_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.tested_url)
        self.assertEqual(response.status_code, 200)


class LoggedInTestMixin:
    """
    Mixin to check views where user just need to be logged in to access.
    """
    def test_logged_in(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        # Checks the logged in user does not redirect to the login page
        self.assertEqual(response.status_code, 200)


class LoginRequiredTestMixin:
    """
    Mixin to check that user just need to be logged in to access view.
    """
    def test_login_required(self):
        response = self.client.get(self.tested_url)
        self.assertRedirects(response, '%s?next=%s' % (reverse('login'),
                                                       self.tested_url))


class TemplateUsedTestMixin:
    """
    Mixin to check that the expected HTML-template is being used.
    """
    def test_template_used(self):
        self.client.login(username='adm', password='adm')
        response = self.client.get(self.tested_url)
        self.assertTemplateUsed(response, self.template_name)


class DeleteTestMixin:
    """
    Mixin checks that only the user from 'Admin' group has access
    to delete the object and checks that the object is deleted from DB
    correctly.
    """
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
        self.assertFalse(self.object in self.model.objects.all())
