from ..models import SlackApplication, Template
from django.core.exceptions import ObjectDoesNotExist


class SlackMessageConstructor:
    """Constructs the message."""

    def __init__(self, **kwargs):
        self.app_name = kwargs['app_name']
        self.template_name = kwargs['template_name']
        self.message_text = kwargs['text']

        self._extract_template_object()

    def get_message_payload(self):
        message = {
            'channel': self.template_obj.channel_name,
            'text': self._concat_message(),
            'attachments': self._get_attachments()
        }

        return message

    def _extract_template_object(self):
        """
        Extracts the template object and assigns it
        as an attribute of the class instance.
        """
        app_obj = self._get_application_object()

        try:
            template_obj = Template.objects.get(application=app_obj,
                                                name=self.template_name)
            self.template_obj = template_obj

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                'This application does not have a template with this name.')

    def _get_application_object(self):
        try:
            print(self.app_name)
            app_obj = SlackApplication.objects.get(name=self.app_name)
            return app_obj
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                'Application with this name does not exist.')

    def _get_attachments(self):
        attachments = []

        if hasattr(self.template_obj, 'attachment'):
            attachment_obj = self.template_obj.attachment

            attachment = {
                'fallback': attachment_obj.fallback,
                'fallback_id': attachment_obj.callback_id,
                'color': attachment_obj.color,
                'actions': self._get_buttons(attachment_obj)
            }
            attachments.append(attachment)

        return attachments

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
