from django.shortcuts import render

# Create your views here.

import django_tables2 as tables

def sources(request):

    sources = ['source1', 'source2']

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
