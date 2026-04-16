from app.db import get_db


def get_presentations():
    db = get_db()
    query = 'SELECT * FROM presentations ORDER BY id'
    rows = db.execute(query).fetchall()
    return [dict(row) for row in rows]


def get_presentations_by_author(author_id):
    """Restituisce solo le presentazioni dell'autore specificato."""
    db = get_db()
    query = 'SELECT * FROM presentations WHERE author_id = ? ORDER BY id'
    rows = db.execute(query, (author_id,)).fetchall()
    return [dict(row) for row in rows]


def create_presentation(title, description, author_id):
    db = get_db()
    query = 'INSERT INTO presentations (title, description, author_id) VALUES (?, ?, ?)'
    cursor = db.execute(query, (title, description, author_id))
    db.commit()
    presentation_id = cursor.lastrowid
    return get_presentation_by_id(presentation_id)

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
