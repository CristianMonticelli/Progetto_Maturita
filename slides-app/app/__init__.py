import os
import sqlite3
from flask import Flask
from flask_babel import Babel, _


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'slides.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
        BABEL_DEFAULT_LOCALE='it',
        BABEL_SUPPORTED_LOCALES=['it', 'en', 'es'],
    )

    # Flask-Babel setup
    babel = Babel()
    def get_locale():
        from flask import session
        return session.get('lang', 'it')
    babel.init_app(app, locale_selector=get_locale)

    # Assicurati che instance esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
