from django.db import models

class OverviewTemplate(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    display = models.JSONField()

class SystemTemplate(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    display = models.JSONField()
