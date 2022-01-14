"""General page routes."""
from flask import Blueprint
from flask import current_app as app
from flask import render_template

from Platform import data


# Blueprint Configuration
display_bp = Blueprint(
    "display_bp", __name__, template_folder="templates", static_folder="static"
)


@display_bp.route("/display", methods=["GET"])
def display():
    """Homepage."""
    displaysls = data.get_displays()
    print(displaysls)
    # products = fetch_products(app)
    return render_template(
        "index_display.jinja2",
        template="display-template",
        displays=displaysls,
        # products=products,
    )
