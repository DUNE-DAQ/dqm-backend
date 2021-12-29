"""General page routes."""
from flask import Blueprint
from flask import current_app as app
from flask import render_template

# from flask_blueprint_tutorial.api import fetch_products

# Blueprint Configuration
display_bp = Blueprint(
    "display_bp", __name__, template_folder="templates", static_folder="static"
)


list_displays = ['A', 'B', 'Display 3']

@display_bp.route("/display", methods=["GET"])
def display():
    """Homepage."""
    # products = fetch_products(app)
    return render_template(
        "index_display.jinja2",
        title="DUNE-DAQ DQM Web Platform",
        subtitle="Demonstration of Flask blueprints in action.",
        template="display-template",
        displays=list_displays,
        # products=products,
    )



