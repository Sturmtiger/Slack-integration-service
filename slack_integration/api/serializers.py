from rest_framework import serializers
from rest_framework import fields
from slack_integration.models import (SlackApplication, Template,
                                      ActionsBlock, Button,)


class SlackApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackApplication
        fields = ('id', 'name', 'signing_secret',
                  'bot_user_oauth_access_token',)


class SlackApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackApplication
        fields = ('id', 'name',)


class TemplateSerializer(serializers.ModelSerializer):
    actions_block = serializers.IntegerField(read_only=True,
                                             source='actions_block.pk')

    class Meta:
        model = Template
        fields = ('application', 'id', 'channel_name', 'name',
                  'message_text', 'fallback_text', 'actions_block',
                  'thread_subscription', 'endpoint')

    def validate(self, attrs):
        errors = {}

        request_method = self.context['request'].method

        thread_subscription = attrs.get('thread_subscription')
        endpoint = attrs.get('endpoint')

        # In case if a user erases the endpoint when
        # `thread_subscription` is True
        if thread_subscription is None and endpoint == '':
            attrs['thread_subscription'] = False

        elif thread_subscription is True and not endpoint:
            if request_method in ['PATCH', 'PUT']:
                if not self.instance.endpoint:
                    errors['endpoint'] = 'Endpoint cannot be empty when ' \
                                         '`thread_subscription` field is true'
            elif request_method == 'POST':
                errors['endpoint'] = 'Endpoint is required when ' \
                                 '`thread_subscription` field is true'

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class TemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ('application', 'id', 'name',)


class ActionsBlockSerializer(serializers.ModelSerializer):
    application = serializers.IntegerField(read_only=True,
                                           source='template.application.pk')

    class Meta:
        model = ActionsBlock
        fields = ('application', 'template', 'id', 'block_id',
                  'action_subscription', 'endpoint')

    def validate(self, attrs):
        errors = {}

        request_method = self.context['request'].method

        action_subscription = attrs.get('action_subscription')
        endpoint = attrs.get('endpoint')

        # In case if a user erases the endpoint when
        # `action_subscription` is True
        if action_subscription is None and endpoint == '':
            attrs['action_subscription'] = False

        elif action_subscription is True and not endpoint:
            if request_method in ['PATCH', 'PUT']:
                if not self.instance.endpoint:
                    errors['endpoint'] = 'Endpoint cannot be empty when ' \
                                         '`action_subscription` field is true'
            elif request_method == 'POST':
                errors['endpoint'] = 'Endpoint is required when ' \
                                 '`action_subscription` field is true'

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class ButtonSerializer(serializers.ModelSerializer):
    application = serializers.IntegerField(
        read_only=True,
        source='actions_block.template.application.pk')
    template = serializers.IntegerField(
        read_only=True,
        source='actions_block.template.pk')

    class Meta:
        model = Button
        fields = ('application', 'template', 'actions_block', 'id',
                  'action_id', 'text',)


class PostMessageSerializer(serializers.Serializer):
    app_name = fields.CharField()
    template_name = fields.CharField()
    text = fields.CharField()

    def validate(self, attrs):
        errors = dict()

        app = SlackApplication.objects.filter(name=attrs['app_name'])
        if not app.exists():
            errors['app_name'] = 'Application with this name does not exist.'

        # In case the application is found
        if not errors:
            app = app.get()
            template = Template.objects.filter(application=app,
                                               name=attrs['template_name'])
            if not template.exists():
                errors['template_name'] = 'Template with this name ' \
                                          'does not exist.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class UpdateMessageSerializer(PostMessageSerializer):
    ts = fields.CharField()


class DeleteMessageSerializer(serializers.Serializer):
    app_name = fields.CharField()
    channel = fields.CharField()
    ts = fields.CharField()
