from django.contrib import admin
from korek import models

admin.site.register(models.Category)
admin.site.register(models.Product)
admin.site.register(models.Profile)
admin.site.register(models.ProfileImage)
admin.site.register(models.GroupAcknowlegment)
admin.site.register(models.PasswordReset)
admin.site.register(models.Comment)