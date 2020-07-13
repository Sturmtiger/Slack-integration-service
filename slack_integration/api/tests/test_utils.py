from django.test import TestCase

from slack_integration.models import Template

from ..slack_message_constructors import PostSlackMessageConstructor


class PostSlackMessageConstructorTest(TestCase):
    fixtures = ('test_dump.json',)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.template_obj = Template.objects.first()

    def test_message_payload_is_dict(self):
        constructor = PostSlackMessageConstructor(self.template_obj,
                                                  'some text')
        message_payload = constructor.get_message_payload()

        self.assertIsInstance(message_payload, dict)
