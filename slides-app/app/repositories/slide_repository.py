from app.db import get_db


def get_slides_by_presentation(presentation_id):
    db = get_db()
    rows = db.execute('SELECT * FROM slides WHERE presentation_id = ? ORDER BY position', (presentation_id,)).fetchall()
    return [dict(row) for row in rows]


def create_slide(presentation_id, title, content, position, image=None, bg_color='#ffffff', box_color=None, title_font_size=48, content_font_size=20):
    db = get_db()
    query = '''INSERT INTO slides
               (presentation_id, title, content, position, image, bg_color, box_color, title_font_size, content_font_size)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor = db.execute(query, (presentation_id, title, content, position, image, bg_color, box_color, title_font_size, content_font_size))
    db.commit()
    return get_slide_by_id(cursor.lastrowid)


def get_slides_by_presentation_id(presentation_id):
    db = get_db()
    rows = db.execute('SELECT * FROM slides WHERE presentation_id = ? ORDER BY position', (presentation_id,)).fetchall()
    return [dict(row) for row in rows]


def get_slide_by_id(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return None
    row = get_db().execute('SELECT * FROM slides WHERE id = ?', (slide_id,)).fetchone()
    return dict(row) if row else None


def update_slide(slide_id, title, content, position, image=None, bg_color='#ffffff', box_color=None, title_font_size=48, content_font_size=20):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False
    db = get_db()
    db.execute(
        '''UPDATE slides SET title=?, content=?, position=?, image=?, bg_color=?, box_color=?,
           title_font_size=?, content_font_size=? WHERE id=?''',
        (title, content, position, image, bg_color, box_color, title_font_size, content_font_size, slide_id)
    )
    db.commit()
    return get_slide_by_id(slide_id)


def delete_slide(slide_id):
    try:
        slide_id = int(slide_id)
    except (TypeError, ValueError):
        return False
    get_db().execute('DELETE FROM slides WHERE id = ?', (slide_id,))
    get_db().commit()
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
        update_slide(s['id'], s['title'], s['content'], i + 1, s.get('image'),
                     s.get('bg_color', '#ffffff'), s.get('box_color'),
                     s.get('title_font_size', 48), s.get('content_font_size', 20))
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
        update_slide(s['id'], s['title'], s['content'], i + 1, s.get('image'),
                     s.get('bg_color', '#ffffff'), s.get('box_color'),
                     s.get('title_font_size', 48), s.get('content_font_size', 20))
    return True
