import os
import sqlite3
from flask import Flask
from flask_mail import Mail
from flask_babel import Babel, _
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mail = Mail()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        DATABASE=os.environ.get(
            'DATABASE',
            os.path.join(app.instance_path, 'slides.sqlite')
        ),
        UPLOAD_FOLDER=os.environ.get(
            'UPLOAD_FOLDER',
            os.path.join(app.root_path, 'static', 'uploads')
        ),
        BABEL_DEFAULT_LOCALE='it',
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_DEBUG=False,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME', ''),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', ''),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_USERNAME', 'noreply@slidesapp.local'),
        BABEL_SUPPORTED_LOCALES=['it', 'en', 'es'],
        BABEL_TRANSLATION_DIRECTORIES='translations',
    )

    mail.init_app(app)
    # Flask-Babel setup
    babel = Babel()
    def get_locale():
        from flask import session
        return session.get('lang', 'it')
    babel.init_app(app, locale_selector=get_locale)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

    if not os.path.exists(app.config['DATABASE']):
        with app.open_resource('schema.sql') as f:
            conn = sqlite3.connect(app.config['DATABASE'])
            conn.executescript(f.read().decode('utf-8'))
            conn.close()

    from . import db
    db.init_app(app)

    from .blueprints import presentations, slides, api
    app.register_blueprint(presentations.bp)
    app.register_blueprint(slides.bp)
    app.register_blueprint(api.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)

    return app
