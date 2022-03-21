from django.db import models
from display.models import Display

class OverviewTemplate(models.Model):
    name = models.CharField(max_length=30)
    display = models.JSONField()

class SystemTemplate(models.Model):
    name = models.CharField(max_length=30)
    display = models.JSONField()
