from app.db import get_db


def get_components_by_slide(slide_id):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM slide_components WHERE slide_id = ? ORDER BY z_index, id',
        (slide_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def get_component_by_id(comp_id):
    row = get_db().execute('SELECT * FROM slide_components WHERE id = ?', (comp_id,)).fetchone()
    return dict(row) if row else None


def create_component(slide_id, type, content='', x=5.0, y=5.0, width=90.0, height=20.0,
                     font_size=24, color='#333333', bg_color='transparent', z_index=0, image=None):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO slide_components
           (slide_id, type, content, x, y, width, height, font_size, color, bg_color, z_index, image)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (slide_id, type, content, x, y, width, height, font_size, color, bg_color, z_index, image)
    )
    db.commit()
    return get_component_by_id(cursor.lastrowid)


def delete_all_components(slide_id):
    db = get_db()
    db.execute('DELETE FROM slide_components WHERE slide_id = ?', (slide_id,))
    db.commit()


def save_all_components(slide_id, components):
    delete_all_components(slide_id)
    result = []
    for comp in components:
        c = create_component(
            slide_id=slide_id,
            type=comp.get('type', 'text'),
            content=comp.get('content', ''),
            x=float(comp.get('x', 5)),
            y=float(comp.get('y', 5)),
            width=float(comp.get('width', 90)),
            height=float(comp.get('height', 20)),
            font_size=int(comp.get('font_size', 24) or 24),
            color=comp.get('color', '#333333'),
            bg_color=comp.get('bg_color', 'transparent'),
            z_index=int(comp.get('z_index', 0) or 0),
            image=comp.get('image'),
        )
        result.append(c)
    return result
