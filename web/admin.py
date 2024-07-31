from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Board)
admin.site.register(models.Room)
admin.site.register(models.Variant)
admin.site.register(models.VRel)
