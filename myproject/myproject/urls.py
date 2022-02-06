"""myproject URL Configuration

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
from django.urls import path, include
# from myapp.views import hello
from myhome.views import index

from sources.views import sources
from display.views import display, create_display, show_display

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('hello/', hello, name='home'),
    path('', index, name='home'),
    path('display/', display, name='display'),
    path('sources/', sources, name='sources'),
    path('create-display/', create_display, name='create display'),
    path('displays/<displayname>', show_display, name='show display'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
