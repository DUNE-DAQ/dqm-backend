from django.shortcuts import render
from django.views.generic import ListView

from .models import *

# Create your views here.

# Person.objects.create(name='p1')
# print(Person.objects.all())

class PersonView(ListView):
    model = Person
