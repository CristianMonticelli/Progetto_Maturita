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

def get_presentation_by_id(presentation_id):
    try:
        presentation_id = int(presentation_id)
    except (TypeError, ValueError):
        return None
    db = get_db()
    row = db.execute('SELECT * FROM presentations WHERE id = ?', (presentation_id,)).fetchone()
    return dict(row) if row else None


def delete_presentation(presentation_id):
    db = get_db()
    db.execute('DELETE FROM presentations WHERE id = ?', (presentation_id,))
    db.execute('DELETE FROM slides WHERE presentation_id = ?', (presentation_id,))
    db.commit()

def get_all_presentations_with_author():
    """Return all presentations from all users with their author username, ordered by newest first."""
    db = get_db()
    rows = db.execute(
        '''SELECT p.*, u.username as author_username
           FROM presentations p
           JOIN user u ON p.author_id = u.id
           ORDER BY p.created_at DESC'''
    ).fetchall()
    return [dict(row) for row in rows]
