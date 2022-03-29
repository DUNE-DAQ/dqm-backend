from django.shortcuts import render

from Platform import utils
from .dash_display import create_display as new_display
from .overview_display import create_overview_display

import django_tables2 as tables

from .models import OverviewDisplay, SystemDisplay
from templates.models import OverviewTemplate, SystemTemplate

from django import forms
from .models import Text
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset

class NameTable(tables.Table):
    name = tables.Column(attrs={'td': {'class': 'col-6'}}, linkify=True)
    description = tables.Column()

# Create your views here.
def system_display_index(request):

    # newnames = Display.objects.create(name='roland', description='this is a description')
    # obj = Display.objects.filter(name='this is a test')
    # obj.delete()
    newnames = SystemDisplay.objects.all()
    # print(newnames[0].get_absolute_url)
    ls = []
    for s in newnames:
        ls.append(s)

    table = NameTable(ls)

    return render(request, 'index_display.html', context={'table': table})

def overview_display_index(request):

    newnames = OverviewDisplay.objects.all()
    ls = []
    for s in newnames:
        ls.append(s)

    table = NameTable(ls)

    return render(request, 'index_display.html', context={'table': table})


displays = {}
def show_display(request, partition, displayname):
    if (partition, displayname) not in displays:
        app = new_display(partition, displayname)
        displays[(partition, displayname)] = app
    return render(request, 'display.dtl', context={'displayname': displayname})

overview_displays = {}
def show_overview_display(request, partition):
    if partition not in overview_displays:
        app = create_overview_display(partition)
        overview_displays[partition] = app
    return render(request, 'overview.dtl', context={'displayname': partition})



def create_display(request):

    def get_form():

        overview_templates = OverviewTemplate.objects.all()
        system_templates = SystemTemplate.objects.all()

        # Create templates if there isn't any in the database
        if not OverviewTemplate.objects.all():
            OverviewTemplate.objects.create(name='TPC Charge Template',
                                            description='test',
                                            display={})

        if not SystemTemplate.objects.all():
            SystemTemplate.objects.create(name='TPC Charge Template',
                                           display={'rmsm_display0': {'plot_type': 'scatter', 'pos': 1},
                                                    'rmsm_display1': {'plot_type': 'scatter', 'pos': 0},
                                                    'rmsm_display2': {'plot_type': 'scatter', 'pos': 2},
                                                    'raw_display0':  {'plot_type': 'heatmap', 'pos': 3},
                                                    'raw_display1':  {'plot_type': 'heatmap', 'pos': 4},
                                                    'raw_display2':  {'plot_type': 'heatmap', 'pos': 5}
                                                   })

        partitions = utils.get_partitions()
        possible_names = utils.get_streams()
        # This is a hack to find all the available streams and pass them as possible choices
        # otherwise the form will complain that an invalid choice was chosen
        tmp = []
        for val in possible_names.values():
            tmp.extend(val)
        tmp = list(set(tmp))

        class ExampleForm(forms.Form):
            name = forms.CharField(label='Name of the display')
            description = forms.CharField(label='Short description')
            overview_template = forms.ChoiceField(label='Overview Template', choices= [(None, None)] + [(overview_templates[i].name, overview_templates[i].name) for i in range(len(overview_templates))])
            system_template = forms.ChoiceField(label='Template', choices= [(None, None)] + [(system_templates[i].name, system_templates[i].name) for i in range(len(system_templates))])

            source = forms.ChoiceField(label='Source', choices= [(elem, elem) for elem in partitions])

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
                        'Create a data display',
                        'name',
                        'description',
                        'overview_template',
                        'system_template',
                        'source',
                        # 'choices',
                    )
                    )
        return ExampleForm

    Form = get_form()

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Form(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(f'Creating form with name {form.cleaned_data["name"]}')
            # data.create_display(form.cleaned_data['name'], {form.cleaned_data['source'][0] : form.cleaned_data['choices']})
            obj = OverviewDisplay.objects.filter(name=form.cleaned_data['name'])
            if not obj:
                displays = {}
                if form.cleaned_data['overview_template'] is not None:
                    _ = OverviewTemplate.objects.filter(name=form.cleaned_data['overview_template'])[0].display
                if form.cleaned_data['system_template'] is not None:
                    displays = SystemTemplate.objects.filter(name=form.cleaned_data['system_template'])[0].display
                else:
                    for d in form.cleaned_data['choices']:
                        if 'raw_display' in d:
                            displays[d] = 'heatmap'
                        elif 'rmsm_display' in d:
                            displays[d] = 'scatter'
                        elif 'fft_sums_display' in d:
                            displays[d] = 'line'
                dataa = {form.cleaned_data['source']: displays}
                OverviewDisplay.objects.create(name=form.cleaned_data['name'],
                                               description=form.cleaned_data['description'],
                                               data=dataa,
                                               source=form.cleaned_data['source']
                                               )
            else:
                print(f'Panel with name {form.cleaned_data["name"]} already exists')

            # return HttpResponseRedirect('/thanks/')
        else:
            print('Form is not valid')
    else:
        form = Form()
    return render(request, 'create_display.dtl', context={'form': form})
