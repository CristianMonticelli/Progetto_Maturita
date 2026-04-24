from flask import Blueprint, render_template, g
from app.repositories import presentation_repository

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get ALL presentations from ALL users with author username
    presentations = presentation_repository.get_all_presentations_with_author()
    return render_template('main/index.html', presentations=presentations)
