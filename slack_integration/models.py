from django.db import models


class Application(models.Model):
    name = models.CharField(max_length=50)
    signing_secret = models.CharField()
    bot_user_oauth_access_token = models.CharField()


class Template(models.Model):
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    related_name='templates')
    name = models.CharField(max_length=50)
    channel_name = models.CharField(max_length=15)
    text = models.TextField()


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
