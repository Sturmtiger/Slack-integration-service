from django.test import TestCase
from slack_integration.models import (SlackApplication, Template, ActionsBlock)
from .mixins import *


class AppListViewTest(LoginRequiredTestMixin, LoggedInTestMixin,
                      TemplateUsedTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-list')
    template_name = 'slack_integration/list/app.html'


class AppDetailViewTest(LoginRequiredTestMixin, LoggedInTestMixin,
                        TemplateUsedTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-detail',
                         args=(SlackApplication.objects.first().pk,))
    template_name = 'slack_integration/detail/app.html'


class CreateAppViewTest(LoginRequiredTestMixin, TemplateUsedTestMixin,
                        LoggedInAdminAndNotAdminTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-registration')
    template_name = 'slack_integration/create/app.html'


class UpdateAppViewTest(LoginRequiredTestMixin, TemplateUsedTestMixin,
                        LoggedInAdminAndNotAdminTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('app-update',
                         args=(SlackApplication.objects.first().pk,))
    template_name = 'slack_integration/update/app.html'


class DeleteAppViewTest(LoginRequiredTestMixin, DeleteTestMixin, TestCase):
    fixtures = ('dump.json',)
    model = SlackApplication
    object = model.objects.first()
    tested_url = reverse('app-delete',
                         args=(object.pk,))


class CreateTemplateViewTest(LoginRequiredTestMixin, TemplateUsedTestMixin,
                             LoggedInAdminAndNotAdminTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('template-create',
                         args=(SlackApplication.objects.first().pk,))
    template_name = 'slack_integration/create/template.html'


class TemplateDetailViewTest(LoginRequiredTestMixin, LoggedInTestMixin,
                             TemplateUsedTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('template-detail',
                         args=(Template.objects.first().pk,))
    template_name = 'slack_integration/detail/template.html'


class UpdateTemplateViewTest(LoginRequiredTestMixin, TemplateUsedTestMixin,
                             LoggedInAdminAndNotAdminTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('template-update',
                         args=(Template.objects.first().pk,))
    template_name = 'slack_integration/update/template.html'


class DeleteTemplateViewTest(LoginRequiredTestMixin, DeleteTestMixin,
                             TestCase):
    fixtures = ('dump.json',)
    model = Template
    object = model.objects.first()
    tested_url = reverse('template-delete',
                         args=(object.pk,))


class CreateActionsBlockViewTest(LoginRequiredTestMixin, TemplateUsedTestMixin,
                                 LoggedInAdminAndNotAdminTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('actions-block-create',
                         args=(ActionsBlock.objects.first().pk,))
    template_name = 'slack_integration/create/actions_block.html'


class ActionsBlockDetailViewTest(LoginRequiredTestMixin, LoggedInTestMixin,
                                 TemplateUsedTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('actions-block-detail',
                         args=(ActionsBlock.objects.first().pk,))
    template_name = 'slack_integration/detail/actions_block.html'


class UpdateActionsBlockViewTest(LoginRequiredTestMixin, TemplateUsedTestMixin,
                                 LoggedInAdminAndNotAdminTestMixin, TestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('actions-block-update',
                         args=(ActionsBlock.objects.first().pk,))
    template_name = 'slack_integration/update/actions_block.html'


class DeleteActionsBlockViewTest(LoginRequiredTestMixin, TestCase):
    fixtures = ('dump.json',)
    model = ActionsBlock
    object = model.objects.first()
    tested_url = reverse('actions-block-delete',
                         args=(object.pk,))
