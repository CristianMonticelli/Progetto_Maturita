from flask import Blueprint, request, jsonify, g, current_app
from flask_babel import _
import os
from werkzeug.utils import secure_filename
from app.repositories import presentation_repository, slide_repository
from app.auth import login_required

bp = Blueprint('api', __name__, url_prefix='/api')

def save_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return f'/static/uploads/{filename}'
    return None

@bp.route('/presentations')
@login_required
def get_presentations():
    presentations = presentation_repository.get_presentations_by_author(g.user['id'])
    return jsonify({'presentations': presentations})

@bp.route('/presentations/create', methods=['POST'])
@login_required
def create_presentation():
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()

    if not title:
        return jsonify({'ok': False, 'error': _('Il titolo è obbligatorio.')}), 400

    presentation = presentation_repository.create_presentation(title, description, g.user['id'])
    return jsonify({'ok': True, 'presentation': presentation})

@bp.route('/presentations/<int:presentation_id>', methods=['DELETE'])
@login_required
def delete_presentation(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentation or presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': _('Presentazione non trovata.')}), 404

    presentation_repository.delete_presentation(presentation_id)
    return jsonify({'ok': True})

@bp.route('/presentations/<int:presentation_id>/slides')
@login_required
def get_slides(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentation or presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': _('Presentazione non trovata.')}), 404

    slides = slide_repository.get_slides_by_presentation_id(presentation_id)
    return jsonify({'slides': slides})

@bp.route('/presentations/<int:presentation_id>/slides', methods=['POST'])
@login_required
def create_slide(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentation or presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': 'Presentazione non trovata.'}), 404

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    bg_color = request.form.get('bg_color', '#ffffff').strip()
    image_file = request.files.get('image')
    image_path = save_image(image_file)

    if not title:
        return jsonify({'ok': False, 'error': 'Il titolo della slide è obbligatorio.'}), 400

    slides = slide_repository.get_slides_by_presentation_id(presentation_id)
    position = len(slides) + 1
    slide = slide_repository.create_slide(presentation_id, title, content, position, image_path, bg_color)
    return jsonify({'ok': True, 'slide': slide})

@bp.route('/slides/<int:slide_id>/update', methods=['POST'])
@login_required
def update_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        return jsonify({'ok': False, 'error': 'Slide non trovata.'}), 404

    presentation = presentation_repository.get_presentation_by_id(slide['presentation_id'])
    if presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': 'Non autorizzato.'}), 403

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    bg_color = request.form.get('bg_color', '#ffffff').strip()
    remove_image = request.form.get('remove_image')
    image_file = request.files.get('image')
    if remove_image:
        image_path = None
    else:
        image_path = save_image(image_file) if image_file and image_file.filename else slide.get('image')

    if not title:
        return jsonify({'ok': False, 'error': 'Il titolo della slide è obbligatorio.'}), 400

    position = slide['position']
    updated_slide = slide_repository.update_slide(slide_id, title, content, position, image_path, bg_color)
    if not updated_slide:
        return jsonify({'ok': False, 'error': 'Errore nell\'aggiornamento della slide.'}), 500
    return jsonify({'ok': True, 'slide': updated_slide})

@bp.route('/slides/<int:slide_id>/move_up', methods=['POST'])
@login_required
def move_slide_up(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        return jsonify({'ok': False, 'error': 'Slide non trovata.'}), 404

    presentation = presentation_repository.get_presentation_by_id(slide['presentation_id'])
    if presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': 'Non autorizzato.'}), 403

    if slide_repository.move_slide_up(slide_id):
        slides = slide_repository.get_slides_by_presentation_id(slide['presentation_id'])
        return jsonify({'ok': True, 'slides': slides})
    return jsonify({'ok': False, 'error': 'Impossibile spostare la slide.'}), 400

@bp.route('/slides/<int:slide_id>/move_down', methods=['POST'])
@login_required
def move_slide_down(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        return jsonify({'ok': False, 'error': 'Slide non trovata.'}), 404

    presentation = presentation_repository.get_presentation_by_id(slide['presentation_id'])
    if presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': 'Non autorizzato.'}), 403

    if slide_repository.move_slide_down(slide_id):
        slides = slide_repository.get_slides_by_presentation_id(slide['presentation_id'])
        return jsonify({'ok': True, 'slides': slides})
    return jsonify({'ok': False, 'error': 'Impossibile spostare la slide.'}), 400

@bp.route('/slides/<int:slide_id>', methods=['DELETE'])
@login_required
def delete_slide(slide_id):
    slide = slide_repository.get_slide_by_id(slide_id)
    if not slide:
        return jsonify({'ok': False, 'error': 'Slide non trovata.'}), 404

    presentation = presentation_repository.get_presentation_by_id(slide['presentation_id'])
    if presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': 'Non autorizzato.'}), 403

    slide_repository.delete_slide(slide_id)
    return jsonify({'ok': True, 'presentation_id': slide['presentation_id']})

@bp.route('/presentations/<int:presentation_id>/change_bg_color', methods=['POST'])
@login_required
def change_all_slides_bg_color(presentation_id):
    presentation = presentation_repository.get_presentation_by_id(presentation_id)
    if not presentation or presentation['author_id'] != g.user['id']:
        return jsonify({'ok': False, 'error': 'Presentazione non trovata.'}), 404

    data = request.get_json()
    bg_color = data.get('bg_color', '#ffffff').strip()
    slides = slide_repository.get_slides_by_presentation_id(presentation_id)
    for slide in slides:
        slide_repository.update_slide(
            slide['id'], slide['title'], slide['content'], slide['position'], slide.get('image'), bg_color
        )
    return jsonify({'ok': True})

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    from app.repositories import user_repository
    user = user_repository.authenticate_user(username, password)
    if user:
        from flask import session
        session.clear()
        session['user_id'] = user['id']
        return jsonify({'ok': True, 'username': username})
    return jsonify({'ok': False, 'error': 'Credenziali errate.'}), 401

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'ok': False, 'error': 'Username e password obbligatori.'}), 400

    from werkzeug.security import generate_password_hash
    from app.repositories import user_repository
    try:
        hashed_pwd = generate_password_hash(password)
        user_repository.create_user(username, hashed_pwd)
        return jsonify({'ok': True})
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@bp.route('/auth/logout', methods=['POST'])
def logout():
    from flask import session
    session.clear()
    return jsonify({'ok': True})