from . import blueprint
from flask import render_template
from flask_login import login_required
from ..display import dash1, dash2 

@blueprint.route('/app1')
# @login_required
def app1_template():
    return render_template('app1.html', dash_url = dash1.url_base)

@blueprint.route('/app2')
# @login_required
def app2_template():
    return render_template('app2.html', dash_url = dash2.url_base)
