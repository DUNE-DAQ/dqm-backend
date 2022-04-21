from django.shortcuts import render

from .models import OverviewTemplate, SystemTemplate

import django_tables2 as tables

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field
from django.utils.html import format_html

from django.forms import formset_factory

class TemplateTable(tables.Table):
    name = tables.Column(attrs={'td': {'class': 'col-6'}})
    description = tables.Column()
    menu = tables.Column()
    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_menu(self, record):
        return format_html(f'<a href="{record["object"].get_edit_url()}">Edit</a> <a href="{record["object"].get_delete_url()}">Delete</a>')

def show_templates(request):
    overview_templates = OverviewTemplate.objects.all()
    system_templates = SystemTemplate.objects.all()

    ls = []
    for s in overview_templates:
        ls.append({'name': s.name, 'description': ' ', 'object': s,
                   'menu': '_'})

    overview_templates_table = TemplateTable(ls)

    ls = []
    for s in system_templates:
        ls.append({'name': s.name, 'description': ' ', 'object': s, 'menu': '_'})

    system_templates_table = TemplateTable(ls)

    return render(request, 'templates_list.html',
                  context={'overview_templates_table': overview_templates_table,
                           'system_templates_table': system_templates_table})


def edit_overview_template(request, name):

    class OverviewTemplateForm(forms.Form):
        name = forms.CharField(label='Name of the template')
        data = forms.CharField(label='Data')
        # description = forms.CharField(label='Short description')
        # overview_template = forms.ChoiceField(label='Overview Template', choices= [(None, None)] + [(overview_templates[i].name, overview_templates[i].name) for i in range(len(overview_templates))])
        # system_template = forms.ChoiceField(label='Template', choices= [(None, None)] + [(system_templates[i].name, system_templates[i].name) for i in range(len(system_templates))])

        # source = forms.ChoiceField(label='Source', choices= [(elem, elem) for elem in partitions])

        # default_choices = [[tmp[i], tmp[i]] for i in range(len(tmp))]
        # choices = forms.MultipleChoiceField(choices=(default_choices), required=False)

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
                    'Edit a display template',
                    'name',
                    'data',
                    # 'description',
                    # 'overview_template',
                    # 'system_template',
                    # 'source',
                    # 'choices',
                )
                )

    Form = OverviewTemplateForm

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
                # OverviewDisplay.objects.create(name=form.cleaned_data['name'],
                #                                description=form.cleaned_data['description'],
                #                                data=dataa,
                #                                source=form.cleaned_data['source']
                #                                )
            else:
                print(f'Panel with name {form.cleaned_data["name"]} already exists')

            # return HttpResponseRedirect('/thanks/')
        else:
            print('Form is not valid')
    else:
        form = Form()
    return render(request, 'edit_overview_template.html', context={'form': form})


def edit_system_template(request, name):


    template = SystemTemplate.objects.filter(name=name)[0]

    class SystemTemplateForm(forms.Form):
        name = forms.CharField(label='Name of the template', initial=template.name)
        data = forms.CharField(label='Data', initial=template.display)
        # description = forms.CharField(label='Short description')
        # overview_template = forms.ChoiceField(label='Overview Template', choices= [(None, None)] + [(overview_templates[i].name, overview_templates[i].name) for i in range(len(overview_templates))])
        # system_template = forms.ChoiceField(label='Template', choices= [(None, None)] + [(system_templates[i].name, system_templates[i].name) for i in range(len(system_templates))])

        # source = forms.ChoiceField(label='Source', choices= [(elem, elem) for elem in partitions])

        # default_choices = [[tmp[i], tmp[i]] for i in range(len(tmp))]
        # choices = forms.MultipleChoiceField(choices=(default_choices), required=False)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            # self.helper.form_id = 'id-exampleForm'
            # self.helper.form_class = 'blueForms'
            self.helper.form_method = 'post'
            # self.helper.form_action = ''

            self.helper.form_tag = False
            self.helper.form_class = 'form-horizontal'
            # self.helper.add_input(Submit('', 'Create display'))
            # self.helper.label_class = 'col-md-3 create-label'
            # self.helper.field_class = 'col-md-9'
            self.helper.layout = Layout(
                        Div(
                    Field('name'),
                    Field('data'),
                    # 'description',
                    # 'overview_template',
                    # 'system_template',
                    # 'source',
                    # 'choices',
                )
                )

    class SystemTemplateForm(forms.ModelForm):
        class Meta:
            model = SystemTemplate
            exclude = []
        # name = forms.CharField(label='Name of the template', initial=template.name)
        # data = forms.CharField(label='Data', initial=template.display)
        # description = forms.CharField(label='Short description')
        # overview_template = forms.ChoiceField(label='Overview Template', choices= [(None, None)] + [(overview_templates[i].name, overview_templates[i].name) for i in range(len(overview_templates))])
        # system_template = forms.ChoiceField(label='Template', choices= [(None, None)] + [(system_templates[i].name, system_templates[i].name) for i in range(len(system_templates))])

        # source = forms.ChoiceField(label='Source', choices= [(elem, elem) for elem in partitions])

        # default_choices = [[tmp[i], tmp[i]] for i in range(len(tmp))]
        # choices = forms.MultipleChoiceField(choices=(default_choices), required=False)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            # self.helper.form_id = 'id-exampleForm'
            # self.helper.form_class = 'blueForms'
            self.helper.form_method = 'post'
            # self.helper.form_action = ''

            # self.helper.form_tag = True
            self.helper.form_class = 'row g-3'
            # self.helper.add_input(Submit('', 'Create display'))
            # self.helper.label_class = 'col-md-3 create-label'
            # self.helper.field_class = 'col-md-9'
            self.helper.layout = Layout(
                        Div(
                    Field('name', css_class='form-control col-md-6'),
                    Field('description', css_class='form-control col-md-6'),
                            css_class='row g-3',
                    # 'description',
                    # 'overview_template',
                    # 'system_template',
                    # 'source',
                    # 'choices',
                )
                )

    Form = SystemTemplateForm

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
                # OverviewDisplay.objects.create(name=form.cleaned_data['name'],
                #                                description=form.cleaned_data['description'],
                #                                data=dataa,
                #                                source=form.cleaned_data['source']
                #                                )
            else:
                print(f'Panel with name {form.cleaned_data["name"]} already exists')

            # return HttpResponseRedirect('/thanks/')
        else:
            print('Form is not valid')
    else:
        form = Form()
        # form = formset_factory(SystemTemplateForm, extra=3)
    return render(request, 'edit_system_template.html', context={'form': form})
