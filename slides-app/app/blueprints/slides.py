from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from flask_babel import _
from werkzeug.utils import secure_filename
import os
from app.repositories import slide_repository
from app.auth import login_required

bp = Blueprint('slides', __name__, url_prefix='/slides')

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
def index():
    return render_template('slides/index.html')

@bp.route('/<int:slide_id>/modifica', methods=('GET', 'POST'))
@login_required
def modifica_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        flash(_('Slide non trovata.'), 'error')
        return redirect(url_for('presentations.list_presentations'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        bg_color = request.form.get('bg_color', '#ffffff').strip()
        box_color = request.form.get('box_color', '').strip() or None
        title_font_size = int(request.form.get('title_font_size', 48) or 48)
        content_font_size = int(request.form.get('content_font_size', 20) or 20)
        remove_image = request.form.get('remove_image')
        image_file = request.files.get('image')
        if remove_image:
            image_path = None
        else:
            image_path = save_image(image_file) if image_file and image_file.filename else slide.get('image')

        error = None
        if not title:
            error = _('Il titolo della slide è obbligatorio.')

        if error is not None:
            flash(error, 'error')
        else:
            position = slide['position']
            slide_repository.update_slide(slide_id, title, content, position, image_path, bg_color, box_color, title_font_size, content_font_size)
            if remove_image:
                flash(_('Immagine rimossa.'), 'success')
                return redirect(url_for('slides.modifica_slide', slide_id=slide_id))
            return redirect(url_for('presentations.presentazione', id=slide['presentation_id']))

    hex_color = (slide.get('bg_color', '#ffffff') or '#ffffff').lstrip('#')
    if len(hex_color) != 6:
        hex_color = 'ffffff'
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        r, g, b = 255, 255, 255

    return render_template('slides/edit_slide.html', slide=slide, r=r, g=g, b=b)

@bp.route('/<int:slide_id>/move_up')
@login_required
def move_slide_up(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if slide:
        if slide_repository.move_slide_up(slide_id):
            flash(_('Slide spostata verso l\'alto.'), 'success')
        else:
            flash(_('Impossibile spostare la slide verso l\'alto.'), 'error')
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



