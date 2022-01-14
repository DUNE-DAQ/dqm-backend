"""General page routes."""
from flask import Blueprint
from flask import current_app as app
from flask import render_template
from flask import request
from wtforms import Form, StringField, SelectField, SelectMultipleField, SubmitField
from flask_wtf import FlaskForm
from wtforms import RadioField, widgets

from Platform import data

# from flask_blueprint_tutorial.api import fetch_products

# Blueprint Configuration
home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates", static_folder="static"
)

class musicsearchform(Form):
    choices = [('artist', 'artist'),
               ('album', 'album'),
               ('publisher', 'publisher')]
    select = SelectField('search for music:', choices=choices)
    search = StringField('')


class SimpleForm(FlaskForm):
    sources = data.get_sources()
    example = SelectField('Label', choices=[(i,s) for i,s in enumerate(sources)], default=1, coerce=int)

class SimpleForm2(FlaskForm):
    streams = data.get_streams()
    streamsls = []
    for key in streams:
        streamsls.extend(list(streams[key]))

    example = SelectMultipleField('Label', choices=[(i,s) for i,s in enumerate(streamsls)], default=-1, coerce=int)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ExampleForm(FlaskForm):
    name = StringField()
    choices = MultiCheckboxField([['a', 'Routes', 'b']], coerce=str)
    submit = SubmitField('Create display')


@home_bp.route("/", methods=["GET"])
def home():
    """Homepage."""
    # products = fetch_products(app)
    return render_template(
        "index.jinja2",
        title="DUNE-DAQ DQM Web Platform",
        subtitle="Demonstration of Flask blueprints in action.",
        template="home-template",
        # products=products,
    )


@home_bp.route("/create-display", methods=["GET", 'POST'])
def create_display():
    ls = ['A', 'B', 'C', 'D']
    search = musicsearchform(request.form)
    form = SimpleForm()
    print(f'{form.example.data=}')
    form_streams = ExampleForm()
    streams = data.get_streams()
    streamsls = []
    for key in streams:
        streamsls.extend(list(streams[key]))
    form_streams.choices.choices = [(elem, elem) for i, elem in enumerate (streamsls)]
    print(f'{form_streams.choices.data=}')
    # print(f'{form_streams.example.data=}')
    # if form_streams.example.data == 1:
    #     print('Creating new display')
    #     # data.create_display(
    """About page."""
    if form_streams.choices.name:
        print('Creating new display')
        print(f'{form_streams.choices.data=}')
        data.create_display(form_streams.name.data, 'testsource', form_streams.choices.data)

    return render_template(
        "create_display.jinja2",
        title="Create displays",
        template="home-template page",
        form=form_streams,
        # form_streams=form_streams,
    )



@home_bp.route("/contact", methods=["GET"])
def contact():
    """Contact page."""
    return render_template(
        "index.jinja2",
        title="Contact",
        subtitle="This is an example contact page.",
        template="home-template page",
    )
