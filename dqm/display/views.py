from django.shortcuts import render

from Platform import data
from .dash_display import create_display as new_display

import django_tables2 as tables

from .models import Display

from django import forms
from .models import Text
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset

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
    



def create_display(request):

    def get_form():

        possible_names = data.get_streams()
        # This is a hack to find all the available streams and pass them as possible choices
        # otherwise the form will complain that an invalid choice was chosen
        tmp = []
        for val in possible_names.values():
            tmp.extend(val)
        tmp = list(set(tmp))

        class ExampleForm(forms.Form):
            name = forms.CharField(label='Name of the display')
            description = forms.CharField(label='Short description')
            template = forms.CharField(label='Use the same template as')

            source = forms.ChoiceField(label='Source', choices= [(list(possible_names.keys())[i], list(possible_names.keys())[i]) for i in range(len(possible_names))])

            default_choices = [[tmp[i], tmp[i]] for i in range(len(tmp))]
            choices = forms.MultipleChoiceField(choices=(default_choices), required=False)

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
        return ExampleForm

    Form = get_form();

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Form(request.POST)
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
                    elif 'rmsm_display' in d:
                        displays[d] = 'scatter'
                    elif 'fft_sums_display' in d:
                        displays[d] = 'line'
                dataa = {form.cleaned_data['source']: displays}
                Display.objects.create(name=form.cleaned_data['name'],
                                       description=form.cleaned_data['description'],
                                       data=dataa
                                       )
            else:
                print(f'Panel with name {form.cleaned_data["name"]} already exists')

            # return HttpResponseRedirect('/thanks/')
        else:
            print('Form is not valid')
    else:
        form = Form()
    return render(request, 'create_display.dtl', context={'form': form})
