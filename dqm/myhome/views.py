from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.dtl', context={'title': 'DUNEDAQ DQM Web Platform'})
