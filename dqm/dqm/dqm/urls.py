"""dqm URL Configuration

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

from django.contrib import admin
from django.urls import path, include
from myhome.views import index

from sources.views import sources
from display.views import display, create_display, show_display
from test.views import PersonView

import json
from django.http import JsonResponse

from Platform import data
def ajax_view(request, choice):
    streams = data.get_streams()
    if choice in streams:
        return JsonResponse(streams[choice], safe=False)
    else:
        return JsonResponse({})

# from dash_static.views import show_display_static

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),

    path('demo-session-var', add_to_session, name="session-variable-example"),
    path('dash_static/', TemplateView.as_view(template_name='display_static.html'), name='dash-static'),

    path('admin/', admin.site.urls),
    # path('hello/', hello, name='home'),
    path('', index, name='home'),
    path('display/', display, name='display'),
    path('sources/', sources, name='sources'),
    path('create-display/', create_display, name='create display'),
    path('displays/<displayname>', show_display, name='show display'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('test/', PersonView.as_view()),
    path('ajax/<choice>', ajax_view, name='ajax'),
    # path('dash_static/', show_display_static, name='static display')

]

# Add in static routes so daphne can serve files; these should
# be masked eg with nginx for production use

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)