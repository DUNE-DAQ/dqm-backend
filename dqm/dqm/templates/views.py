from django.shortcuts import render

from .models import OverviewTemplate, SystemTemplate

import django_tables2 as tables

class TemplateTable(tables.Table):
    name = tables.Column(attrs={'td': {'class': 'col-6'}})
    description = tables.Column()
    menu = tables.Column()
    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

def show_templates(request):
    overview_templates = OverviewTemplate.objects.all()
    system_templates = SystemTemplate.objects.all()

    ls = []
    for s in overview_templates:
        ls.append({'name': s.name, 'description': ' ', 'menu': ' '})

    overview_templates_table = TemplateTable(ls)

    ls = []
    for s in system_templates:
        ls.append({'name': s.name, 'description': ' ', 'menu': ' '})

    system_templates_table = TemplateTable(ls)

    return render(request, 'templates_list.html',
                  context={'overview_templates_table': overview_templates_table,
                           'system_templates_table': system_templates_table})
