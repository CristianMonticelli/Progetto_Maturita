from flask import Blueprint, redirect, url_for

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def index():
    return redirect(url_for('presentations.list_presentations'))
