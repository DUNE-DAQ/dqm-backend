from django.db import models

# Create your models here.

class Text(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name


class Display(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    data = models.JSONField()
    # data = models.

    def get_absolute_url(self):
        return f'/displays/{self.name}'

