from django.conf import settings

from rest_framework import serializers
from rest_framework import fields
from slack_integration.models import (SlackApplication, Template,
                                      ActionsBlock, Button,)

from django_celery_beat.models import CrontabSchedule


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
        fields = ('application', 'id', 'channel_id', 'name',
                  'message_text', 'fallback_text', 'actions_block',
                  'thread_subscription', 'endpoint')

    def validate(self, attrs):
        request_method = self.context['request'].method

        endpoint = attrs.get('endpoint')

        if endpoint == '':
            attrs['thread_subscription'] = False
        if endpoint is None:
            if request_method == 'POST':
                attrs['thread_subscription'] = False
            elif (request_method in ['PUT', 'PATCH'] and not
                    self.instance.endpoint):
                attrs['thread_subscription'] = False

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
        request_method = self.context['request'].method

        endpoint = attrs.get('endpoint')

        if endpoint == '':
            attrs['action_subscription'] = False
        if endpoint is None:
            if request_method == 'POST':
                attrs['action_subscription'] = False
            elif (request_method in ['PUT', 'PATCH'] and not
                    self.instance.endpoint):
                attrs['action_subscription'] = False

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
    channel_id = fields.CharField()
    ts = fields.CharField()


class CrontabScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = ('minute', 'hour', 'day_of_week',
                  'day_of_month', 'month_of_year')

    def create(self, validated_data):
        validated_data['timezone'] = settings.TIME_ZONE
        return CrontabSchedule.objects.get_or_create(**validated_data)[0]
