from django.contrib import admin

from . import models


admin.site.register(models.SlackApplication)
admin.site.register(models.Template)
admin.site.register(models.ActionsBlock)
admin.site.register(models.Button)
admin.site.register(models.MessageTimeStamp)
