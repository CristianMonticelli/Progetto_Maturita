from app.db import get_db


def get_slides_by_presentation(presentation_id):
    db = get_db()
    query = 'SELECT * FROM slides WHERE presentation_id = ? ORDER BY position'
    rows = db.execute(query, (presentation_id,)).fetchall()
    return [dict(row) for row in rows]


def create_slide(presentation_id, title, content, position, image=None):
    db = get_db()
    query = 'INSERT INTO slides (presentation_id, title, content, position, image) VALUES (?, ?, ?, ?, ?)'
    db.execute(query, (presentation_id, title, content, position, image))
    db.commit()

def get_slides_by_presentation_id(presentation_id):
    db = get_db()
    query = 'SELECT * FROM slides WHERE presentation_id = ? ORDER BY position'
    rows = db.execute(query, (presentation_id,)).fetchall()
    return [dict(row) for row in rows]


def get_slide_by_id(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return None

    db = get_db()
    query = 'SELECT * FROM slides WHERE id = ?'
    row = db.execute(query, (slide_id,)).fetchone()
    return dict(row) if row else None


def update_slide(slide_id, title, content, position, image=None):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False

    db = get_db()
    query = 'UPDATE slides SET title = ?, content = ?, position = ?, image = ? WHERE id = ?'
    db.execute(query, (title, content, position, image, slide_id))
    db.commit()
    return True


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

    presentation_id = slide['presentation_id']
    slides = get_slides_by_presentation_id(presentation_id)
    index = None
    for i, s in enumerate(slides):
        if s['id'] == slide_id:
            index = i
            break
    if index is None or index == 0:
        return False

    slides[index], slides[index - 1] = slides[index - 1], slides[index]
    for i, s in enumerate(slides):
        update_slide(s['id'], s['title'], s['content'], i + 1, s.get('image'))
    return True


def move_slide_down(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False

    slide = get_slide_by_id(slide_id)
    if not slide:
        return False

    presentation_id = slide['presentation_id']
    slides = get_slides_by_presentation_id(presentation_id)
    index = None
    for i, s in enumerate(slides):
        if s['id'] == slide_id:
            index = i
            break
    if index is None or index == len(slides) - 1:
        return False

    slides[index], slides[index + 1] = slides[index + 1], slides[index]
    for i, s in enumerate(slides):
        update_slide(s['id'], s['title'], s['content'], i + 1, s.get('image'))
    return True