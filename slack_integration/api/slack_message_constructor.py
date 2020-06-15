from ..models import Template
from django.core.exceptions import ObjectDoesNotExist


class SlackMessageConstructor:
    """Constructs the message."""

    def __init__(self, template_name, message_text):
        self.template_name = template_name
        self.message_text = message_text

        self._extract_template_object()

    def get_message_payload(self):
        message = {
            'channel': self.template_obj.channel_name,
            'text': self._concat_message(),
            'attachments': [
                self._get_attachment()
            ]
        }

        return message

    def _extract_template_object(self):
        """
        Extracts the template object and assigns it
        as an attribute of the class instance.
        """
        try:
            template_obj = Template.objects.get(name=self.template_name)
            self.template_obj = template_obj

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                'This application does not have a template with this name.')

    def _get_attachment(self):
        if hasattr(self.template_obj, 'attachment'):
            attachment_obj = self.template_obj.attachment

            attachment = {
                'fallback': attachment_obj.fallback,
                'fallback_id': attachment_obj.callback_id,
                'color': attachment_obj.color,
                'actions': self._get_buttons(attachment_obj)
            }

            return attachment

        return ''

    def _get_buttons(self, attachment):
        buttons = [
            {
                "name": button.name,
                "text": button.text,
                "type": button.type,
                "value": button.value,
            } for button in attachment.buttons.all()
        ]

        return buttons

    def _concat_message(self):
        """
        Concatenates the sent message with the template message.
        """
        completed_message = (f"{self.template_obj.message_text}\n\n"
                             f"{self.message_text}")
        return completed_message
