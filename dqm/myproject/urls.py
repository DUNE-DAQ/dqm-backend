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



urlpatterns = [
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
]

# @home_bp.route("/create-display", methods=["GET", 'POST'])
# def create_display():
#     form_streams = ExampleForm()
#     streams = data.get_streams()
#     streamsls = []
#     # for key in streams:
#     #     streamsls.extend(list(streams[key]))
#     form_streams.choices.choices = [(elem, elem) for i, elem in enumerate (streamsls)]
#     # print(f'{form_streams.example.data=}')
#     # if form_streams.example.data == 1:
#     #     print('Creating new display')
#     #     # data.create_display(
#     """About page."""
#     if form_streams.choices.name:
#         print('Creating new display')
#         print(f'{form_streams.choices.data=}')

#         # source = form_streams.choices.food
#         source = form_streams.foodkind.data
#         displaystreams = {}
#         displaystreams[source] = form_streams.choices.data
#         print('STREAMS', displaystreams)
#         data.create_display(form_streams.name.data, displaystreams)

#     return render_template(
#         "create_display.jinja2",
#         title="Create displays",
#         template="home-template page",
#         form=form_streams,
#     )

# @home_bp.route('/create-display/get-streams/<streamname>')
# def get_streams(streamname):
#     streams = data.get_streams()
#     import json
#     if streamname not in streams:
#         return jsonify([])
#     else:
#         return jsonify(streams[streamname])
