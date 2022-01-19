"""Initialize Flask app."""
from ddtrace import patch_all
from flask import Flask
from flask_assets import Environment

from config import Config

if Config.FLASK_ENV == "production" and Config.DD_SERVICE:
    patch_all()

from .display import dash_display


def init_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    assets = Environment()
    assets.init_app(app)

    with app.app_context():

        app = dash_display.add_dash(app)
        # Import parts of our application
        from .assets import compile_static_assets
        from .home import home
        from .display import display

        # Register Blueprints
        app.register_blueprint(home.home_bp)
        app.register_blueprint(display.display_bp)

        from .DashExample import routes
        app.register_blueprint(routes.blueprint)

        # Compile static assets
        compile_static_assets(assets)


        return app
