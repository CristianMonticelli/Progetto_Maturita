from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from werkzeug.utils import secure_filename
import os
from app.repositories import presentation_repository, slide_repository
from app.auth import login_required

bp = Blueprint('presentations', __name__, url_prefix='/presentations')

def save_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return f'/static/uploads/{filename}'
    return None

@bp.route('/')
@login_required
def list_presentations():
    # Mostra solo le presentazioni dell'utente loggato
    presentations = presentation_repository.get_presentations_by_author(g.user['id'])
    print(presentations)
    return render_template('presentations/index.html', lista_presentazioni=presentations)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_presentation():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        error = None
        if not title:
            error = 'Il titolo è obbligatorio.'

        if error is not None:
            flash(error)
        else:
            # Passa l'ID dell'autore all'atto della creazione
            presentation_repository.create_presentation(title, description, g.user['id'])
            return redirect(url_for('presentations.list_presentations'))

    return render_template('presentations/create.html')

@bp.route('/presentazione/<id>', methods=('GET', 'POST'))
@login_required
def presentazione(id):
    presentazione = presentation_repository.get_presentation_by_id(id)
    slides = slide_repository.get_slides_by_presentation_id(id)

    # Reorder positions to ensure they are 1,2,3,...
    for i, slide in enumerate(slides):
        slide_repository.update_slide(
            slide['id'], slide['title'], slide['content'], i + 1, slide.get('image'), slide.get('bg_color', '#ffffff')
        )

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        image_file = request.files.get('image')
        image_path = save_image(image_file)
        bg_color = request.form.get('bg_color', '#ffffff').strip()

        error = None
        if not title:
            error = 'Il titolo della slide è obbligatorio.'

        if error is not None:
            flash(error)
        else:
            position = len(slides) + 1
            slide_repository.create_slide(id, title, content, position, image_path, bg_color)
            return redirect(url_for('presentations.presentazione', id=id))

    return render_template('presentations/presentation_datail.html', presentazione=presentazione, slides=slides)


@bp.route('/presentazione/<int:presentation_id>/change_bg_color', methods=('POST',))
@login_required
def change_all_slides_bg_color(presentation_id):
    presentazione = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentazione:
        flash('Presentazione non trovata.')
        return redirect(url_for('presentations.list_presentations'))

    bg_color = request.form.get('bg_color_all', '#ffffff').strip()
    slides = slide_repository.get_slides_by_presentation_id(presentation_id)
    for slide in slides:
        slide_repository.update_slide(
            slide['id'], slide['title'], slide['content'], slide['position'], slide.get('image'), bg_color
        )

    flash('Colore sfondo aggiornato a tutte le slide.')
    return redirect(url_for('presentations.presentazione', id=presentation_id))


@bp.route('/presentazione/<int:presentation_id>/delete')
@login_required
def delete_presentation(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if presentation:
        presentation_repository.delete_presentation(presentation_id)
        flash('Presentazione eliminata.')
    else:
        flash('Presentazione non trovata.')
    return redirect(url_for('presentations.list_presentations'))
