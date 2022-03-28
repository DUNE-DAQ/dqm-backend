from django.db import models

# Create your models here.

class Text(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name

class OverviewDisplay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    data = models.JSONField()
    source = models.CharField(max_length=30)

    def get_absolute_url(self):
        return f'/overview/{self.name}'

class SystemDisplay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    data = models.JSONField()

    def get_absolute_url(self):
        return f'/displays/{self.name}'

