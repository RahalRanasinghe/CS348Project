from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Custom Jinja filter for formatting dates as dd/mm/yyyy
    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        return value.strftime('%d/%m/%Y')

    from .routes import main
    app.register_blueprint(main)

    return app
