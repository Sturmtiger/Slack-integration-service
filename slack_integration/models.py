from django.db import models
from django.core.validators import MinLengthValidator


class SlackApplication(models.Model):
    name = models.CharField(max_length=50, unique=True)
    signing_secret = models.CharField(max_length=32,
                                      validators=[
                                          MinLengthValidator(32),
                                      ])
    bot_user_oauth_access_token = models.CharField(max_length=57,
                                                   validators=[
                                                       MinLengthValidator(57),
                                                   ])


class Template(models.Model):
    application = models.ForeignKey(SlackApplication,
                                    on_delete=models.CASCADE,
                                    related_name='templates')
    name = models.CharField(max_length=50)
    channel_name = models.CharField(max_length=15)
    message_text = models.TextField()
    fallback_text = models.CharField(max_length=255)

    class Meta:
        unique_together = ('application', 'name')


class ActionsBlock(models.Model):
    template = models.OneToOneField(Template,
                                    on_delete=models.CASCADE,
                                    related_name='actions_block')
    block_id = models.CharField(max_length=255)


class Button(models.Model):
    actions_block = models.ForeignKey(ActionsBlock,
                                      on_delete=models.CASCADE,
                                      related_name='buttons')
    action_id = models.CharField(max_length=255)
    text = models.CharField(max_length=75)
    # value = models.CharField(max_length=2000)  # needed?

    class Meta:
        unique_together = (
            ('actions_block', 'action_id'),
            ('actions_block', 'text'),
        )
