from rest_framework.serializers import Serializer, ValidationError
from rest_framework import fields
from slack_integration.models import SlackApplication, Template


class PostMessageSerializer(Serializer):
    app_name = fields.CharField()
    template_name = fields.CharField()
    text = fields.CharField()

    def validate(self, data):
        errors = dict()

        app = SlackApplication.objects.filter(name=data['app_name'])
        if not app.exists():
            errors['app_name'] = 'Application with this name does not exist.'

        # In case the application is found
        if not errors:
            app = app.get()
            template = Template.objects.filter(application=app,
                                               name=data['template_name'])
            if not template.exists():
                errors['template_name'] = 'Template with this name ' \
                                          'does not exist.'

        if errors:
            raise ValidationError(errors)

        return data
