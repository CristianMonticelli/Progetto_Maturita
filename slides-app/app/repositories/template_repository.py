from app.db import get_db


def get_templates():
    db = get_db()
    query = 'SELECT * FROM templates ORDER BY id'
    rows = db.execute(query).fetchall()
    return [dict(row) for row in rows]
