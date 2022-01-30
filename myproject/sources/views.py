from django.shortcuts import render

# Create your views here.

from Platform import data

import django_tables2 as tables


def sources(request):

    sources = data.get_sources()

    # data = [
    #     {"name": "Bradley"},
    #     {"name": "Stevie"},
    # ]
    ls = []
    for s in sources:
        ls.append({'name': s, 'description': ' ', 'menu': ' '})
        

    class NameTable(tables.Table):
        name = tables.Column(attrs={'td': {'class': 'col-6'}})
        description = tables.Column()
        menu = tables.Column()
        class Meta:
            attrs = {'class': 'table table-striped table-hover'}

    table = NameTable(ls)

    return render(request, 'sources.dtl', context={'table': table, 'title': 'hello'})
