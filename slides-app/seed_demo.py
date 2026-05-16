"""
Script per creare un account demo con presentazioni e slide di esempio.
Eseguire DOPO setup_db.py:
    python setup_db.py
    python seed_demo.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash

def seed():
    from app import create_app
    from app.db import get_db

    app = create_app()
    with app.app_context():
        db = get_db()

        # Check if demo user already exists
        existing = db.execute(
            "SELECT id FROM user WHERE username = 'demo'"
        ).fetchone()
        if existing:
            print("Account demo già esistente. Nessuna modifica.")
            return

        # Create demo user
        db.execute(
            "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
            ('demo', generate_password_hash('demo1234'), 'demo@slidesapp.local')
        )
        db.commit()
        user_id = db.execute(
            "SELECT id FROM user WHERE username = 'demo'"
        ).fetchone()['id']
        print(f"Utente demo creato (id={user_id})")

        # Create presentation 1
        db.execute(
            "INSERT INTO presentations (title, description, author_id) VALUES (?, ?, ?)",
            ('Benvenuto in SlidesApp', 'Presentazione di esempio con i componenti principali', user_id)
        )
        db.commit()
        pres1_id = db.execute(
            "SELECT id FROM presentations WHERE author_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()['id']

        # Slide 1 — Title + Text
        db.execute(
            "INSERT INTO slides (presentation_id, position, bg_color) VALUES (?, ?, ?)",
            (pres1_id, 1, '#1a1a2e')
        )
        db.commit()
        slide1_id = db.execute(
            "SELECT id FROM slides WHERE presentation_id = ? ORDER BY id DESC LIMIT 1",
            (pres1_id,)
        ).fetchone()['id']

        db.executemany(
            """INSERT INTO slide_components
               (slide_id, type, content, x, y, width, height,
                font_size, color, bg_color, z_index, image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (slide1_id, 'title', 'Benvenuto in SlidesApp 🎞️',
                 5, 20, 90, 22, 52, '#ff6600', 'transparent', 0, None),
                (slide1_id, 'text',
                 'Crea presentazioni con editor canvas drag & drop.\nAggiungi testi, immagini e link.',
                 5, 50, 90, 30, 22, '#e0e0e0', 'transparent', 0, None),
            ]
        )
        db.commit()

        # Slide 2 — Title + Text + Image placeholder
        db.execute(
            "INSERT INTO slides (presentation_id, position, bg_color) VALUES (?, ?, ?)",
            (pres1_id, 2, '#ffffff')
        )
        db.commit()
        slide2_id = db.execute(
            "SELECT id FROM slides WHERE presentation_id = ? ORDER BY id DESC LIMIT 1",
            (pres1_id,)
        ).fetchone()['id']

        db.executemany(
            """INSERT INTO slide_components
               (slide_id, type, content, x, y, width, height,
                font_size, color, bg_color, z_index, image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (slide2_id, 'title', 'Funzionalità principali',
                 5, 5, 90, 18, 40, '#ff6600', 'transparent', 0, None),
                (slide2_id, 'text',
                 '✓ Drag & drop dei componenti\n✓ Ridimensionamento con 8 handle\n✓ Import/Export PowerPoint\n✓ 3 lingue disponibili',
                 5, 28, 55, 65, 20, '#333333', 'transparent', 0, None),
            ]
        )
        db.commit()

        # Slide 3 — Dark with link
        db.execute(
            "INSERT INTO slides (presentation_id, position, bg_color) VALUES (?, ?, ?)",
            (pres1_id, 3, '#16213e')
        )
        db.commit()
        slide3_id = db.execute(
            "SELECT id FROM slides WHERE presentation_id = ? ORDER BY id DESC LIMIT 1",
            (pres1_id,)
        ).fetchone()['id']

        db.executemany(
            """INSERT INTO slide_components
               (slide_id, type, content, x, y, width, height,
                font_size, color, bg_color, z_index, image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (slide3_id, 'title', 'Inizia subito!',
                 10, 30, 80, 22, 52, '#ff6600', 'transparent', 0, None),
                (slide3_id, 'link', 'github.com/CristianMonticelli/Progetto_Maturita',
                 15, 62, 70, 12, 18, '#64b5f6', 'transparent', 0, None),
            ]
        )
        db.commit()

        # Create presentation 2 — shorter
        db.execute(
            "INSERT INTO presentations (title, description, author_id) VALUES (?, ?, ?)",
            ('Esempio Import/Export', 'Prova a scaricare questa presentazione come .pptx', user_id)
        )
        db.commit()
        pres2_id = db.execute(
            "SELECT id FROM presentations WHERE author_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()['id']

        db.execute(
            "INSERT INTO slides (presentation_id, position, bg_color) VALUES (?, ?, ?)",
            (pres2_id, 1, '#f5f5f5')
        )
        db.commit()
        slide4_id = db.execute(
            "SELECT id FROM slides WHERE presentation_id = ? ORDER BY id DESC LIMIT 1",
            (pres2_id,)
        ).fetchone()['id']

        db.executemany(
            """INSERT INTO slide_components
               (slide_id, type, content, x, y, width, height,
                font_size, color, bg_color, z_index, image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (slide4_id, 'title', 'Export in PowerPoint',
                 5, 5, 90, 18, 44, '#333333', 'transparent', 0, None),
                (slide4_id, 'text',
                 'Clicca "Scarica .pptx" nella pagina della presentazione\nper scaricare questa presentazione come file PowerPoint.',
                 5, 28, 90, 40, 20, '#555555', 'transparent', 0, None),
            ]
        )
        db.commit()

        print("Contenuto demo creato:")
        print("  Username: demo")
        print("  Password: demo1234")
        print(f"  2 presentazioni con {3+1} slide totali")

if __name__ == '__main__':
    seed()
