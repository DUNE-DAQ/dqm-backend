from flask import Blueprint

blueprint = Blueprint(
    'Displays blueprint',
    __name__,
    url_prefix='/displays',
    template_folder='templates',
    static_folder='static'
)
