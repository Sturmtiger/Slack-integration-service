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

    class Meta:
        unique_together = ('application', 'name')


class Attachment(models.Model):
    template = models.OneToOneField(Template,
                                    on_delete=models.CASCADE)
    fallback = models.CharField(max_length=100)
    callback_id = models.CharField(max_length=50)
    color = models.CharField(max_length=7, blank=True)


class Button(models.Model):
    attachment = models.ForeignKey(Attachment,
                                   on_delete=models.CASCADE,
                                   related_name='buttons')
    name = models.CharField(max_length=50)
    text = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
