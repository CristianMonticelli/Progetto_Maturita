from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from flask_babel import _
from app.repositories import presentation_repository, slide_repository, slide_component_repository
from app.auth import login_required

bp = Blueprint('presentations', __name__, url_prefix='/presentations')


@bp.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['it', 'en', 'es']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('presentations.list_presentations'))


@bp.route('/')
@login_required
def list_presentations():
    presentations = presentation_repository.get_presentations_by_author(g.user['id'])
    return render_template('presentations/index.html', lista_presentazioni=presentations)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_presentation():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash(_('Il titolo è obbligatorio.'), 'error')
        else:
            presentation_repository.create_presentation(title, description, g.user['id'])
            flash(_('Presentazione creata con successo.'), 'success')
            return redirect(url_for('presentations.list_presentations'))
    return render_template('presentations/create.html')


@bp.route('/presentazione/<int:id>', methods=('GET',))
@login_required
def presentazione(id):
    presentazione = presentation_repository.get_presentation_by_id(id)
    if not presentazione:
        flash(_('Presentazione non trovata.'), 'error')
        return redirect(url_for('presentations.list_presentations'))

    slides = slide_repository.get_slides_by_presentation_id(id)

    # Normalize positions
    for i, slide in enumerate(slides):
        if slide['position'] != i + 1:
            slide_repository.update_slide(slide['id'], i + 1, slide.get('bg_color', '#ffffff'))

    slides_with_components = []
    for slide in slides:
        components = slide_component_repository.get_components_by_slide(slide['id'])
        slides_with_components.append({**slide, 'components': components})

    return render_template('presentations/presentation_datail.html',
                           presentazione=presentazione,
                           slides=slides_with_components)


@bp.route('/presentazione/<int:presentation_id>/presenta')
@login_required
def presenta(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentation:
        flash(_('Presentazione non trovata.'), 'error')
        return redirect(url_for('presentations.list_presentations'))
    slides = slide_repository.get_slides_by_presentation_id(presentation_id)
    slides_with_components = []
    for slide in slides:
        components = slide_component_repository.get_components_by_slide(slide['id'])
        slides_with_components.append({**slide, 'components': components})
    return render_template('presentations/presenta.html',
                           presentation=presentation,
                           slides=slides_with_components)


@bp.route('/presentazione/<int:presentation_id>/delete')
@login_required
def delete_presentation(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentation:
        flash(_('Presentazione non trovata.'), 'error')
    elif presentation['author_id'] != g.user['id']:
        flash(_('Non autorizzato.'), 'error')
    else:
        presentation_repository.delete_presentation(presentation_id)
        flash(_('Presentazione eliminata.'), 'success')
    return redirect(url_for('presentations.list_presentations'))
