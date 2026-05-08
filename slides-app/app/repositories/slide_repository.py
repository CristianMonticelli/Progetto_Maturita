from app.db import get_db


def get_slides_by_presentation_id(presentation_id):
    db = get_db()
    rows = db.execute('SELECT * FROM slides WHERE presentation_id = ? ORDER BY position', (presentation_id,)).fetchall()
    return [dict(row) for row in rows]


def create_slide(presentation_id, position, bg_color='#ffffff'):
    db = get_db()
    cursor = db.execute(
        'INSERT INTO slides (presentation_id, position, bg_color) VALUES (?, ?, ?)',
        (presentation_id, position, bg_color)
    )
    db.commit()
    return get_slide_by_id(cursor.lastrowid)


def get_slide_by_id(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return None
    row = get_db().execute('SELECT * FROM slides WHERE id = ?', (slide_id,)).fetchone()
    return dict(row) if row else None


def update_slide(slide_id, position, bg_color='#ffffff'):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False
    db = get_db()
    db.execute('UPDATE slides SET position=?, bg_color=? WHERE id=?', (position, bg_color, slide_id))
    db.commit()
    return get_slide_by_id(slide_id)


def delete_slide(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False
    db = get_db()
    db.execute('DELETE FROM slides WHERE id = ?', (slide_id,))
    db.commit()
    return True


def move_slide_up(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False
    slide = get_slide_by_id(slide_id)
    if not slide:
        return False
    slides = get_slides_by_presentation_id(slide['presentation_id'])
    index = next((i for i, s in enumerate(slides) if s['id'] == slide_id), None)
    if index is None or index == 0:
        return False
    slides[index], slides[index - 1] = slides[index - 1], slides[index]
    for i, s in enumerate(slides):
        update_slide(s['id'], i + 1, s.get('bg_color', '#ffffff'))
    return True


def move_slide_down(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False
    slide = get_slide_by_id(slide_id)
    if not slide:
        return False
    slides = get_slides_by_presentation_id(slide['presentation_id'])
    index = next((i for i, s in enumerate(slides) if s['id'] == slide_id), None)
    if index is None or index == len(slides) - 1:
        return False
    slides[index], slides[index + 1] = slides[index + 1], slides[index]
    for i, s in enumerate(slides):
        update_slide(s['id'], i + 1, s.get('bg_color', '#ffffff'))
    return True
