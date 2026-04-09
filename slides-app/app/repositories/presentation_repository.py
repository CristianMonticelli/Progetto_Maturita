from app.db import get_db


def get_presentations():
    db = get_db()
    query = 'SELECT * FROM presentations ORDER BY id'
    rows = db.execute(query).fetchall()
    return [dict(row) for row in rows]


def create_presentation(title, description):
    db = get_db()
    query = 'INSERT INTO presentations (title, description) VALUES (?, ?)'
    db.execute(query, (title, description))
    db.commit()

def get_presentation_by_id(id):
    db = get_db()
    query = 'SELECT * FROM presentations WHERE id = ?'
    row = db.execute(query, (id,)).fetchone()
    return dict(row) if row else None


def delete_presentation(presentation_id):
    db = get_db()
    db.execute('DELETE FROM presentations WHERE id = ?', (presentation_id,))
    db.execute('DELETE FROM slides WHERE presentation_id = ?', (presentation_id,))
    db.commit()
