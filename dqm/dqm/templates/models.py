from django.db import models

class OverviewTemplate(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    display = models.JSONField()
    creation_date = models.DateField()

    def get_edit_url(self):
        return f'/templates-overview/{self.name}/edit'

    def get_delete_url(self):
        return f'/templates-overview/{self.name}/delete'

class SystemTemplate(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    display = models.JSONField()
    creation_date = models.DateField()

    def get_edit_url(self):
        return f'/templates-system/{self.name}/edit'

    def get_delete_url(self):
        return f'/templates-system/{self.name}/delete'
