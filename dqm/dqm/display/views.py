from django.shortcuts import render

from Platform import utils
from .system_display import create_display as new_display
from .overview_display import create_overview_display

import django_tables2 as tables

from .models import OverviewDisplay, SystemDisplay
from templates.models import OverviewTemplate, SystemTemplate

from django import forms
from .models import Text
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset

from django.utils.html import format_html

class NameTable(tables.Table):
    name = tables.Column(attrs={'td': {'class': 'col-6'}}, linkify=True)
    description = tables.Column()

class OverviewTable(tables.Table):
    name = tables.Column(attrs={'td': {'class': 'col-4'}}, linkify=lambda record: record['object'].get_absolute_url())
    description = tables.Column(attrs={'td': {'class': 'col-4'}})
    template = tables.Column(attrs={'td': {'class': 'col-4'}})
    options = tables.Column(attrs={'td': {'class': 'col-4'}},)
    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_options(self, record):
        return format_html(f'<a href={record["object"].get_edit_url()}>Edit</a> <a href={record["object"].get_delete_url()}>Delete</a>')

# Create your views here.
def system_display_index(request):

    # newnames = Display.objects.create(name='roland', description='this is a description')
    # obj = Display.objects.filter(name='this is a test')
    # obj.delete()
    newnames = SystemDisplay.objects.all()
    # print(newnames[0].get_absolute_url)
    ls = []
    for s in newnames:
        ls.append({'name': s.name, 'description': s.description, 'object': s, 'options': '_'})

    table = NameTable(ls)

    return render(request, 'index_display.html', context={'table': table})

def overview_display_index(request):
    """
    Renders the page with the list of displays
    """

    partitions = utils.get_partitions()
    displays = list(OverviewDisplay.objects.all())
    partitions_in_default_displays = set([d.partition for d in displays if d.default])

    # Create default display if there isn't one
    for p in partitions:
        if p not in partitions_in_default_displays:
            obj = OverviewDisplay.objects.create(name=f'{p}_default',
                                           description=f'Default display for partition {p}',
                                           data={},
                                           partition=p,
                                           default=True)
            displays.append(obj)


    ls = []

    for d in displays:
        # The options field is needed for it to be rendered
        ls.append({'name': d.name, 'description': d.description, 'object': d,
                   'template': 'test', 'options': '_'})

    table = OverviewTable(ls)

    return render(request, 'index_display.html', context={'table': table})


def edit_overview_display(request, name):
    obj = OverviewDisplay.objects.all().filter(name=name)[0]

def delete_overview_display(request, name):
    OverviewDisplay.objects.all().filter(name=name).delete()
    return overview_display_index(request)

displays = {}
def show_display(request, overview_name, displayname):
    if (overview_name, displayname) not in displays:
        app = new_display(overview_name, displayname)
        displays[(overview_name, displayname)] = app
    app_name = overview_name + displayname
    return render(request, 'display.html', context={'app_name': app_name, 'displayname': displayname})

overview_displays = {}
def show_overview_display(request, display_name):
    if display_name not in overview_displays:
        app = create_overview_display(display_name)
        overview_displays[display_name] = app
    return render(request, 'overview.html', context={'displayname': display_name})

channel_displays = {}
def show_channel_display(request, overview_name, displayname, channel):
    partition = OverviewDisplay.objects.filter(name=overview_name)[0].partition
    app_name = displayname
    name = f'channel-{partition}-{displayname}'
    if name not in channel_displays:
        app = create_channel_display(partition, displayname)
        channel_displays[name] = app
    else:
        app = channel_displays[name]
    return render(request, 'channel.html', context={'displayname': name})


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
                                           display={
                                                    'fft_sums_display0': {'plot_type': 'line'   , 'pos': 0, 'size': 3},
                                                    'fft_sums_display1': {'plot_type': 'line'   , 'pos': 1, 'size': 3},
                                                    'fft_sums_display2': {'plot_type': 'line'   , 'pos': 2, 'size': 3},
                                                    'fft_sums_display3': {'plot_type': 'line'   , 'pos': 3, 'size': 3},
                                                    'rmsm_display0':     {'plot_type': 'scatter', 'pos': 4, 'size': 4},
                                                    'rmsm_display1':     {'plot_type': 'scatter', 'pos': 5, 'size': 4},
                                                    'rmsm_display2':     {'plot_type': 'scatter', 'pos': 6, 'size': 4},
                                                    'raw_display0':      {'plot_type': 'heatmap', 'pos': 7, 'size': 4},
                                                    'raw_display1':      {'plot_type': 'heatmap', 'pos': 8, 'size': 4},
                                                    'raw_display2':      {'plot_type': 'heatmap', 'pos': 9, 'size': 4}
                                                   })

            SystemTemplate.objects.create(name='TPC Charge Template (WIB2)',
                                           display={
                                                    'fft_sums_display0':          {'plot_type': 'line'   , 'pos': 0, 'size': 3},
                                                    'fft_sums_display1':          {'plot_type': 'line'   , 'pos': 1, 'size': 3},
                                                    'fft_sums_display2':          {'plot_type': 'line'   , 'pos': 2, 'size': 3},
                                                    'fft_sums_display3':          {'plot_type': 'line'   , 'pos': 3, 'size': 3},
                                                    'rmsm_display0':              {'plot_type': 'scatter', 'pos': 4, 'size': 4},
                                                    'rmsm_display1':              {'plot_type': 'scatter', 'pos': 5, 'size': 4},
                                                    'rmsm_display2':              {'plot_type': 'scatter', 'pos': 6, 'size': 4},
                                                    'raw_display0':               {'plot_type': 'heatmap', 'pos': 7, 'size': 4},
                                                    'raw_display1':               {'plot_type': 'heatmap', 'pos': 8, 'size': 4},
                                                    'raw_display2':               {'plot_type': 'heatmap', 'pos': 9, 'size': 4},
                                                    'channel_mask_display0':      {'plot_type': 'scatter', 'pos': 10, 'size': 4},
                                                    'channel_mask_display1':      {'plot_type': 'scatter', 'pos': 11, 'size': 4},
                                                    'channel_mask_display2':      {'plot_type': 'scatter', 'pos': 12, 'size': 4},
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
    return render(request, 'create_display.html', context={'form': form})
