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
    partition = models.CharField(max_length=30)
    default = models.BooleanField()
    creation_date = models.DateField()

    def get_absolute_url(self):
        return f'/overview/{self.name}'
    def get_edit_url(self):
        return f'/overview/{self.name}/edit'
    def get_delete_url(self):
        return f'/overview/{self.name}/delete'

class SystemDisplay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    data = models.JSONField()
    creation_date = models.DateField()

    def get_absolute_url(self):
        return f'/displays/{self.name}'

