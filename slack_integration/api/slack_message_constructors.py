from django.core.exceptions import ObjectDoesNotExist


class PostSlackMessageConstructor:
    """Constructs the message for Slack API."""

    def __init__(self, template_obj, message_text=None):
        self.template_obj = template_obj
        self.message_text = message_text

    def get_message_payload(self):
        message = {
            'channel': self.template_obj.channel_id,
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

    def _get_actions_block(self):
        try:
            actions_block_obj = self.template_obj.actions_block
            buttons = self._get_buttons(actions_block_obj)

            # Do not return the empty `action block` if
            # there are no `buttons`.
            if buttons:
                actions_block = {
                    'block_id': actions_block_obj.block_id,
                    'type': 'actions',
                    'elements': buttons
                }
                return actions_block
        # If the actions_block does not exist
        except ObjectDoesNotExist:
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

    def _get_concated_message(self):
        """
        Concatenates the sent message with the template message.
        """
        if self.message_text:
            return (f"{self.template_obj.message_text}\n\n"
                    f"{self.message_text}")

        return self.template_obj.message_text


class UpdateSlackMessageConstructor(PostSlackMessageConstructor):
    def __init__(self, template_obj, message_text, ts):
        super().__init__(template_obj, message_text)
        self.ts = ts

    def get_message_payload(self):
        message = super().get_message_payload()
        message['ts'] = self.ts

        return message
