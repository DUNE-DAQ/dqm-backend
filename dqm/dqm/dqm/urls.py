"""dqm-backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from django_plotly_dash.views import add_to_session

from home.views import index
from sources.views import sources
from test.views import PersonView
from display.views import system_display_index, overview_display_index, create_display, show_display, show_overview_display, delete_overview_display, edit_overview_display, show_channel_display, show_alarm_display, piptest
from templates.views import show_templates, edit_overview_template, edit_system_template
# from files.views import show_files_display

import json
from django.http import JsonResponse
from display.models import OverviewDisplay
from django.core.cache import cache

from Platform import utils

print('Clearing cache...')
cache.clear()

def ajax_view(request, choice):
    streams = utils.get_streams()
    if choice in streams:
        return JsonResponse(streams[choice], safe=False)
    else:
        return JsonResponse({})

def search_results(request, text):
    """
    Return the results for the live search
    It checks the name and description of the available displays
    """
    print(f'ajax_list {text=}')
    obj = OverviewDisplay.objects.all()
    showls = [False] * len(obj)
    for i in range(len(obj)):
        if text in obj[i].name or text in obj[i].description:
            showls[i] = True
    ret = [{'name': elem.name, 'description': elem.description, 'url': elem.get_absolute_url()} for elem, show in zip(obj, showls) if show]
    return JsonResponse(ret, safe=False)

from django.shortcuts import render
def render_test(request):
    return render(request, 'test.html')

def get_json(request):
    return JsonResponse(json.loads(open('./data.json').read()), safe=False)


# from dash_static.views import show_display_static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('display/', system_display_index, name='display'),
    path('overview/', overview_display_index, name='overview'),
    path('overview/<name>/delete', delete_overview_display, name='overview'),
    path('overview/<name>/edit', edit_overview_display, name='overview'),
    path('sources/', sources, name='sources'),
    path('create-display/', create_display, name='create display'),
    path('overview/<overview_name>/<displayname>/<channel>', show_channel_display, name='show channel display'),
    path('overview/<overview_name>/<displayname>', show_display, name='show display'),
    path('overview/<display_name>', show_overview_display, name='show display'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('test/', PersonView.as_view()),
    path('ajax/<choice>', ajax_view, name='ajax'),
    path('aj/<text>', search_results, name='ajax_search'),
    path('templates', show_templates, name='templates'),
    path('templates-overview/<name>/edit', edit_overview_template, name='edit_overview_template'),
    path('templates-system/<name>/edit', edit_system_template, name='edit_system_template'),
    path('test', render_test, name='test'),
    path('get_json', get_json, name='get_json'),
    #path('alarm/<overview_name>/<displayname>', show_alarm_display, name='test_alarm'),
    path('alarm/<display_name>', show_alarm_display, name='test_alarm'),
    # path('file-explorer', show_files_display, name='file explorer'),
]

# Add in static routes so daphne can serve files; these should
# be masked eg with nginx for production use

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
