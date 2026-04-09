from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.repositories import slide_repository, presentation_repository

bp = Blueprint('slides', __name__, url_prefix='/slides')

@bp.route('/')
def index():
    return render_template('slides/index.html')



