from django.shortcuts import render

from Platform import data
from .dash_display import create_display as new_display

import django_tables2 as tables

from .models import Display

class NameTable(tables.Table):
    name = tables.Column(attrs={'td': {'class': 'col-6'}}, linkify=True)
    description = tables.Column()

# Create your views here.
def display(request):

    # newnames = Display.objects.create(name='roland', description='this is a description')
    # obj = Display.objects.filter(name='this is a test')
    # obj.delete()
    newnames = Display.objects.all()
    # print(newnames[0].get_absolute_url)
    ls = []
    for s in newnames:
        ls.append(s)

    table = NameTable(ls)

    return render(request, 'index_display.dtl', context={'table': table})


displays = {}
def show_display(request, displayname):
    if displayname not in displays:
        app = new_display(displayname)
        displays[displayname] = app
    return render(request, 'display.dtl', context={'displayname': displayname})
    

from django import forms
from .models import Text
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset

# Text.objects.create(name='testttt')


possible_names = data.get_streams()

class ExampleForm(forms.Form):


    name = forms.CharField(label='Name of the display')
    description = forms.CharField(label='Short description')
    template = forms.CharField(label='Use the same template as')

    # source = forms.ModelChoiceField(label='Source', choices=['src1', 'src2'], queryset)
    source = forms.MultipleChoiceField(label='Source', choices= [(list(possible_names.keys())[i], list(possible_names.keys())[i]) for i in range(len(possible_names))] )
    choices = forms.MultipleChoiceField(choices=(['raw_display2', 'raw_display2'], [2, 'Test choice 2']), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        # self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.add_input(Submit('', 'Create display'))
        self.helper.layout = Layout(
                    Fieldset(
                'first arg is the legend of the fieldset',
                'name',
                'description',
                'template',
                'source',
                'choices',
            
            )
            )

    #     self.fields['foodkind'].queryset = ['a', 'b', 'c']

def create_display(request):
    print('CALLING create_display')
    print(f'{request.method=}')

    if request.method == 'POST':
        print('Request method is POST')
        # create a form instance and populate it with data from the request:
        form = ExampleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print(f'Creating form with name {form.cleaned_data["name"]}')
            print(form.cleaned_data['name'])
            # data.create_display(form.cleaned_data['name'], {form.cleaned_data['source'][0] : form.cleaned_data['choices']})
            obj = Display.objects.filter(name=form.cleaned_data['name'])
            if not obj:
                print(form.cleaned_data['source'])
                print(form.cleaned_data['choices'])
                displays = {}
                for d in form.cleaned_data['choices']:
                    if 'raw_display' in d:
                        displays[d] = 'heatmap'
                    else:
                        displays[d] = 'scatter'
                data = {form.cleaned_data['source'][0]: displays}
                Display.objects.create(name=form.cleaned_data['name'],
                                       description=form.cleaned_data['description'],
                                       data=data
                                       )
            else:
                print(f'Panel with name {form.cleaned_data["name"]} already exists')

            # return HttpResponseRedirect('/thanks/')
        else:
            print('Form is not valid')
    else:
        form = ExampleForm()
    return render(request, 'create_display.dtl', context={'form': form})
