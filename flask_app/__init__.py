"""Initialize Flask app."""
from ddtrace import patch_all
from flask import Flask
from flask_assets import Environment

from config import Config

if Config.FLASK_ENV == "production" and Config.DD_SERVICE:
    patch_all()
from .display import dash1, dash2


def init_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    assets = Environment()
    assets.init_app(app)

    with app.app_context():
        # Import parts of our application
        from .assets import compile_static_assets
        from .home import home
        from .display import display
        # from .products import products
        # from .profile import profile

        from .display.dashboard import init_dashboard
        app = init_dashboard(app)

        # Register Blueprints
        # app.register_blueprint(profile.profile_bp)
        app.register_blueprint(home.home_bp)
        app.register_blueprint(display.display_bp)
        # app.register_blueprint(products.product_bp)

        from .DashExample import routes
        app.register_blueprint(routes.blueprint)

        # Compile static assets
        compile_static_assets(assets)

        app = dash1.Add_Dash(app)
        app = dash2.Add_Dash(app)


        return app
