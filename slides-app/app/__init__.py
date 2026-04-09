import os
import sqlite3
from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'slides.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
    )

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

    from .blueprints import presentations, slides
    app.register_blueprint(presentations.bp)
    app.register_blueprint(slides.bp)

    from . import main
    app.register_blueprint(main.bp)

    return app
