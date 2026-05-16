from flask import Blueprint, render_template, redirect, url_for, flash, g
from flask_babel import _
from app.repositories import slide_repository, slide_component_repository
from app.auth import login_required

bp = Blueprint('slides', __name__, url_prefix='/slides')


@bp.route('/')
@login_required
def index():
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/<int:slide_id>/modifica')
@login_required
def modifica_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        flash(_('Slide non trovata.'), 'error')
        return redirect(url_for('presentations.list_presentations'))
    components = slide_component_repository.get_components_by_slide(slide_id)
    return render_template('slides/edit_slide.html', slide=slide, components=components)


@bp.route('/<int:slide_id>/move_up')
@login_required
def move_slide_up(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        if slide_repository.move_slide_up(slide_id):
            flash(_("Slide spostata verso l'alto."), 'success')
        else:
            flash(_("Impossibile spostare la slide verso l'alto."), 'error')
        return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/<int:slide_id>/move_down')
@login_required
def move_slide_down(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        if slide_repository.move_slide_down(slide_id):
            flash(_('Slide spostata verso il basso.'), 'success')
        else:
            flash(_('Impossibile spostare la slide verso il basso.'), 'error')
        return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/<int:slide_id>/delete')
@login_required
def delete_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        slide_repository.delete_slide(slide_id)
        flash(_('Slide eliminata.'), 'success')
        return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))
    flash(_('Slide non trovata.'), 'error')
    return redirect(url_for('presentations.list_presentations'))
