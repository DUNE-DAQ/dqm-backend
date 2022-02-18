"""General page routes."""
from flask import Blueprint
from flask import current_app as app
from flask import render_template
from flask import request
from wtforms import Form, StringField, SelectField, SelectMultipleField, SubmitField, validators
from flask_wtf import FlaskForm
from wtforms import RadioField, widgets
import wtforms
from flask import jsonify
from flask_table import Table, Col

from Platform import data

# Blueprint Configuration
home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates", static_folder="static"
)

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

possible_names = data.get_streams()

class ExampleForm(FlaskForm):
    name = StringField()
    choices = MultiCheckboxField([['a', 'Routes', 'b']], coerce=str)
    submit = SubmitField('Create display')

    food = MultiCheckboxField(
                    choices=[],
                    validators=[validators.InputRequired()])

    foodkind = SelectField("Enter a Name",
                           choices=[''] + list(possible_names.keys()),
                    validators=[validators.InputRequired()])

@home_bp.route("/", methods=["GET"])
def home():
    """Homepage."""
    return render_template(
        "index.jinja2",
        title="DUNE-DAQ DQM Web Platform",
        # subtitle="Demonstration of Flask blueprints in action.",
        template="home-template",
    )

@home_bp.route("/create-display", methods=["GET", 'POST'])
def create_display():
    form_streams = ExampleForm()
    streams = data.get_streams()
    streamsls = []
    # for key in streams:
    #     streamsls.extend(list(streams[key]))
    form_streams.choices.choices = [(elem, elem) for i, elem in enumerate (streamsls)]
    # print(f'{form_streams.example.data=}')
    # if form_streams.example.data == 1:
    #     print('Creating new display')
    #     # data.create_display(
    """About page."""
    if form_streams.choices.name:
        print('Creating new display')
        print(f'{form_streams.choices.data=}')

        # source = form_streams.choices.food
        source = form_streams.foodkind.data
        displaystreams = {}
        displaystreams[source] = form_streams.choices.data
        print('STREAMS', displaystreams)
        data.create_display(form_streams.name.data, displaystreams)

    return render_template(
        "create_display.jinja2",
        title="Create displays",
        template="home-template page",
        form=form_streams,
    )

@home_bp.route('/create-display/get-streams/<streamname>')
def get_streams(streamname):
    streams = data.get_streams()
    import json
    if streamname not in streams:
        return jsonify([])
    else:
        return jsonify(streams[streamname])

class ItemTable(Table):
    name = Col('Name',
            column_html_attrs={
            'class': 'col-10'},
               )
    description = Col('Description')
    menu = Col('Menu')

class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.menu = ''


@home_bp.route("/sources", methods=["GET"])
def sources():
    """Sources"""

    sources = data.get_sources()
    items = [Item(s, '',) for s in sources]
    table = ItemTable(items, classes=['table', 'table-striped', 'table-hover'], thead_classes=['col-6', 'col-6'])
    print(table.__html__())

    return render_template(
        "sources.jinja2",
        title="Sources",
        # subtitle="This is an example contact page.",
        table=table.__html__()
    )
