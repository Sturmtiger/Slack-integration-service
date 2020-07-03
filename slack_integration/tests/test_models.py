from django.test import TestCase
from django.db import IntegrityError
from slack_integration.models import (SlackApplication, Template,
                                      ActionsBlock, Button)


class SlackApplicationModelTest(TestCase):

    def test_unique_app_name(self):
        SlackApplication.objects.create(
            name='app_name',
            signing_secret='111',
            bot_user_oauth_access_token='111')
        with self.assertRaises(IntegrityError):
            SlackApplication.objects.create(
                name='app_name',
                signing_secret='111',
                bot_user_oauth_access_token='111')


class TemplateModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app1 = SlackApplication.objects.create(
            name='app1',
            signing_secret='111',
            bot_user_oauth_access_token='111')
        cls.app2 = SlackApplication.objects.create(
            name='app2',
            signing_secret='111',
            bot_user_oauth_access_token='111')

    def test_unique_template_name_with_same_app(self):
        Template.objects.create(application=self.app1,
                                name='template_name',
                                channel_id='channel',
                                message_text='asasasas',
                                fallback_text='sadasdas')

        with self.assertRaises(IntegrityError):
            Template.objects.create(application=self.app1,
                                    name='template_name',
                                    channel_id='channel',
                                    message_text='asasasas',
                                    fallback_text='sadasdas')

    def test_different_apps_can_have_templates_with_same_name(self):
        Template.objects.create(application=self.app1,
                                name='template_name',
                                channel_id='channel',
                                message_text='asasasas',
                                fallback_text='sadasdas')

        try:
            Template.objects.create(application=self.app2,
                                    name='template_name',
                                    channel_id='channel',
                                    message_text='asasasas',
                                    fallback_text='sadasdas')
        except IntegrityError:
            self.fail('IntegrityError raised unexpectedly. '
                      'For some reasons different applications cannot have '
                      'a template with the same name.')


class ActionsBlockModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = SlackApplication.objects.create(
            name='app_name',
            signing_secret='111',
            bot_user_oauth_access_token='111')
        cls.template = Template.objects.create(
            application=cls.app,
            name='template_name',
            channel_id='channel',
            message_text='asasasas',
            fallback_text='sadasdas')

    def test_one_app_can_have_one_actions_block(self):
        ActionsBlock.objects.create(template=self.template,
                                    block_id='first_id')

        with self.assertRaises(IntegrityError):
            ActionsBlock.objects.create(template=self.template,
                                        block_id='second_id')

    def test_actions_block_block_id_is_unique(self):
        ActionsBlock.objects.create(template=self.template,
                                    block_id='first_id')
        with self.assertRaises(IntegrityError):
            ActionsBlock.objects.create(template=self.template,
                                        block_id='first_id')


class ButtonModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = SlackApplication.objects.create(
            name='app_name',
            signing_secret='111',
            bot_user_oauth_access_token='111')
        cls.template = Template.objects.create(application=cls.app,
                                               name='template_name',
                                               channel_id='channel',
                                               message_text='asasasas',
                                               fallback_text='sadasdas')
        cls.actions_block = ActionsBlock.objects.create(template=cls.template,
                                                        block_id='first_id')

    def test_must_have_unique_action_id(self):
        Button.objects.create(actions_block=self.actions_block,
                              action_id='act_id',
                              text='rerf')

        with self.assertRaises(IntegrityError):
            Button.objects.create(actions_block=self.actions_block,
                                  action_id='act_id',
                                  text='qweetr')

    def test_must_have_unique_text(self):
        Button.objects.create(actions_block=self.actions_block,
                              action_id='act_id1',
                              text='rerf')

        with self.assertRaises(IntegrityError):
            Button.objects.create(actions_block=self.actions_block,
                                  action_id='act_id2',
                                  text='rerf')
