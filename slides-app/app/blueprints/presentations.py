from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from app.repositories import presentation_repository, slide_repository

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
def list_presentations():
    presentations = presentation_repository.get_presentations()
    print(presentations)
    return render_template('presentations/index.html', lista_presentazioni=presentations)

@bp.route('/create', methods=('GET', 'POST'))
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
            presentation_repository.create_presentation(title, description)
            return redirect(url_for('presentations.list_presentations'))

    return render_template('presentations/create.html')

@bp.route('/presentazione/<id>', methods=('GET', 'POST'))
def presentazione(id):
    presentazione = presentation_repository.get_presentation_by_id(id)
    slides = slide_repository.get_slides_by_presentation_id(id)

    # Reorder positions to ensure they are 1,2,3,...
    for i, slide in enumerate(slides):
        slide_repository.update_slide(
            slide['id'], slide['title'], slide['content'], i + 1, slide.get('image')
        )

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        image_file = request.files.get('image')
        image_path = save_image(image_file)

        error = None
        if not title:
            error = 'Il titolo della slide è obbligatorio.'

        if error is not None:
            flash(error)
        else:
            position = len(slides) + 1
            slide_repository.create_slide(id, title, content, position, image_path)
            return redirect(url_for('presentations.presentazione', id=id))

    return render_template('presentations/presentation_datail.html', presentazione=presentazione, slides=slides)


@bp.route('/slide/<slide_id>/modifica', methods=('GET', 'POST'))
def modifi_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        flash('Slide non trovata.')
        return redirect(url_for('presentations.list_presentations'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        remove_image = request.form.get('remove_image')
        image_file = request.files.get('image')
        if remove_image:
            image_path = None
        else:
            image_path = save_image(image_file) if image_file and image_file.filename else slide.get('image')

        error = None
        if not title:
            error = 'Il titolo della slide è obbligatorio.'

        if error is not None:
            flash(error)
        else:
            position = slide['position']
            slide_repository.update_slide(slide_id, title, content, position, image_path)
            if remove_image:
                flash('Immagine rimossa.')
                return redirect(url_for('presentations.modifi_slide', slide_id=slide_id))
            return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))

    return render_template('presentations/edit_slide.html', slide=slide)


@bp.route('/slide/<int:slide_id>/move_up')
def move_slide_up(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        if slide_repository.move_slide_up(slide_id):
            flash('Slide spostata verso l\'alto.')
        else:
            flash('Impossibile spostare la slide verso l\'alto.')
        return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/slide/<int:slide_id>/move_down')
def move_slide_down(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        if slide_repository.move_slide_down(slide_id):
            flash('Slide spostata verso il basso.')
        else:
            flash('Impossibile spostare la slide verso il basso.')
        return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/slide/<int:slide_id>/delete')
def delete_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        slide_repository.delete_slide(slide_id)
        flash('Slide eliminata.')
        return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))
    flash('Slide non trovata.')
    return redirect(url_for('presentations.list_presentations'))


@bp.route('/presentazione/<int:presentation_id>/delete')
def delete_presentation(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if presentation:
        presentation_repository.delete_presentation(presentation_id)
        flash('Presentazione eliminata.')
    else:
        flash('Presentazione non trovata.')
    return redirect(url_for('presentations.list_presentations'))
