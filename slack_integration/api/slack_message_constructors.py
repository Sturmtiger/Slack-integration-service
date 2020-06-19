from django.core.exceptions import ObjectDoesNotExist

from ..models import SlackApplication, Template


class PostSlackMessageConstructor:
    """Constructs the message for Slack API."""

    def __init__(self, **kwargs):
        self.app_name = kwargs['app_name']
        self.template_name = kwargs['template_name']
        self.message_text = kwargs['text']

        self.template_obj = self._get_template_object()

    def get_message_payload(self):
        message = {
            'channel': self.template_obj.channel_name,
            # 'text' works as fallback
            'text': self.template_obj.fallback_text,
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': self._get_concated_message()
                    }
                },
                {
                    'type': 'divider'
                },
            ]
        }

        actions_block = self._get_actions_block()
        if actions_block:
            message['blocks'].append(actions_block)

        return message

    def _get_template_object(self):
        app_obj = self._get_application_object()

        try:
            template_obj = Template.objects.get(application=app_obj,
                                                name=self.template_name)
            return template_obj

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                'This application does not have a template with this name.')

    def _get_actions_block(self):
        if hasattr(self.template_obj, 'actions_block'):
            actions_block_obj = self.template_obj.actions_block

            actions_block = {
                'block_id': actions_block_obj.block_id,
                'type': 'actions',
                'elements': self._get_buttons(actions_block_obj)
            }
            return actions_block

        return None

    def _get_buttons(self, actions_block):
        buttons = [
            {
                'type': 'button',
                'action_id': button.action_id,
                'text': {
                    'type': 'plain_text',
                    'text': button.text
                },
            } for button in actions_block.buttons.all()
        ]

        return buttons

    def _get_application_object(self):
        try:
            app_obj = SlackApplication.objects.get(name=self.app_name)
            return app_obj

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                'Application with this name does not exist.')

    def _get_concated_message(self):
        """
        Concatenates the sent message with the template message.
        """
        completed_message = (f"{self.template_obj.message_text}\n\n"
                             f"{self.message_text}")
        return completed_message


class UpdateSlackMessageConstructor(PostSlackMessageConstructor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ts = kwargs['ts']

    def get_message_payload(self):
        message = super().get_message_payload()
        message['ts'] = self.ts

        return message
