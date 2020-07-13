from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework import fields
from slack_integration.models import (SlackApplication, Template,
                                      ActionsBlock, Button,)

from django_celery_beat.models import CrontabSchedule

from .mixins.serializers.validate import ValidateSubsCallbackUrlMixin


class SlackApplicationBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackApplication
        fields = ('id', 'name',)


class SlackApplicationSerializer(SlackApplicationBaseSerializer):
    class Meta(SlackApplicationBaseSerializer.Meta):
        fields = (SlackApplicationBaseSerializer.Meta.fields +
                  ('signing_secret', 'bot_user_oauth_access_token',
                   'templates'))
        extra_kwargs = {
            'templates': {'read_only': True},
        }


class TemplateBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ('application', 'id', 'name',)


class TemplateSerializer(ValidateSubsCallbackUrlMixin,
                         TemplateBaseSerializer):
    subs_field_name = 'thread_subscription'

    class Meta(TemplateBaseSerializer.Meta):
        fields = (TemplateBaseSerializer.Meta.fields +
                  ('channel_id', 'message_text', 'fallback_text',
                   'actions_block', 'thread_subscription', 'callback_url'))
        extra_kwargs = {
            'actions_block': {'read_only': True},
        }


class CrontabScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = ('minute', 'hour', 'day_of_week',
                  'day_of_month', 'month_of_year')

    def validate(self, attrs):
        if attrs == {}:
            error = {'crontab': 'crontab fields are not specified'}
            raise serializers.ValidationError(error)

        return attrs

    def create(self, validated_data):
        validated_data['timezone'] = settings.TIME_ZONE
        return CrontabSchedule.objects.get_or_create(**validated_data)[0]


class ActionsBlockBaseSerializer(serializers.ModelSerializer):
    application = serializers.IntegerField(read_only=True,
                                           source='template.application.pk')

    class Meta:
        model = ActionsBlock
        fields = ('application', 'template', 'id', 'block_id')


class ActionsBlockSerializer(ValidateSubsCallbackUrlMixin,
                             ActionsBlockBaseSerializer):
    subs_field_name = 'action_subscription'

    class Meta(ActionsBlockBaseSerializer.Meta):
        fields = (ActionsBlockBaseSerializer.Meta.fields +
                  ('action_subscription', 'callback_url', 'buttons'))
        extra_kwargs = {
            'buttons': {'read_only': True},
        }


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
                  'action_id', 'text')


class PostMessageSerializer(serializers.Serializer):
    app_name = fields.CharField()
    template_name = fields.CharField()
    text = fields.CharField()

    def validate(self, attrs):
        errors = dict()

        try:
            app = SlackApplication.objects.get(name=attrs['app_name'])
        except ObjectDoesNotExist:
            errors['app_name'] = 'Application with this name does not exist.'
            raise serializers.ValidationError(errors)

        # In case the application is found
        try:
            Template.objects.get(application=app,
                                 name=attrs['template_name'])
        except ObjectDoesNotExist:
            errors['template_name'] = 'Template with this name does not exist.'
            raise serializers.ValidationError(errors)

        return attrs


class UpdateMessageSerializer(PostMessageSerializer):
    ts = fields.CharField()


class DeleteMessageSerializer(serializers.Serializer):
    app_name = fields.CharField()
    channel_id = fields.CharField()
    ts = fields.CharField()
