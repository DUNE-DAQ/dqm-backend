from . import blueprint
from flask import render_template
from flask_login import login_required
from ..display import dash_display

@blueprint.route('/<pathname>')
# @login_required
def app3_template(pathname):
    return render_template('app3.html', dash_url=f'/dash/{pathname}', pathname=pathname)
