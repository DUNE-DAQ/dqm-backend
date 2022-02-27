from django.shortcuts import render

from Platform import data
from .dash_display import create_display as new_display

# Create your views here.
def display(request):
    displaysls = data.get_displays()

    return render(request, 'index_display.dtl', context={'displays': displaysls})



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
            print('Creating form with name {form.name}')
            print(form.cleaned_data['name'])
            data.create_display(form.cleaned_data['name'], {form.cleaned_data['source'][0] : form.cleaned_data['choices']})
            # return HttpResponseRedirect('/thanks/')
        else:
            print('Form is not valid')
    else:
        form = ExampleForm()
    return render(request, 'create_display.dtl', context={'form': form})
