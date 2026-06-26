"""
Script per creare l'account cristian con la presentazione PCTO per la maturità.
Eseguire DOPO setup_db.py:
    python setup_db.py
    python seed_pcto.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash


def add_slide(db, pres_id, pos, bg, comps):
    db.execute(
        "INSERT INTO slides (presentation_id, position, bg_color) VALUES (?, ?, ?)",
        (pres_id, pos, bg)
    )
    db.commit()
    slide_id = db.execute(
        "SELECT id FROM slides WHERE presentation_id = ? ORDER BY id DESC LIMIT 1",
        (pres_id,)
    ).fetchone()['id']
    db.executemany(
        """INSERT INTO slide_components
           (slide_id, type, content, x, y, width, height,
            font_size, color, bg_color, z_index, image)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (slide_id, c['type'], c['content'], c['x'], c['y'],
             c['w'], c['h'], c['font_size'], c['color'],
             c.get('bg_color', 'transparent'), c.get('z_index', i), c.get('image', None))
            for i, c in enumerate(comps)
        ]
    )
    db.commit()


def seed():
    from app import create_app
    from app.db import get_db

    app = create_app()
    with app.app_context():
        db = get_db()

        # Check if user already exists
        existing = db.execute(
            "SELECT id FROM user WHERE username = 'cristian'"
        ).fetchone()
        if existing:
            user_id = existing['id']
            print("Account cristian già esistente.")
        else:
            db.execute(
                "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
                ('cristian', generate_password_hash('pcto2026'), 'cristian@slidesapp.local')
            )
            db.commit()
            user_id = db.execute(
                "SELECT id FROM user WHERE username = 'cristian'"
            ).fetchone()['id']
            print(f"Utente cristian creato (id={user_id})")

        # Check if presentation already exists
        pres_title = 'Il mio percorso — PCTO e Capolavori'
        existing_pres = db.execute(
            "SELECT id FROM presentations WHERE title = ? AND author_id = ?",
            (pres_title, user_id)
        ).fetchone()
        if existing_pres:
            print("Presentazione già esistente. Nessuna modifica.")
            return

        # Create presentation
        db.execute(
            "INSERT INTO presentations (title, description, author_id) VALUES (?, ?, ?)",
            (pres_title, 'Presentazione personale per il colloquio di maturità', user_id)
        )
        db.commit()
        pres_id = db.execute(
            "SELECT id FROM presentations WHERE author_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()['id']

        # Slide 1
        add_slide(db, pres_id, 1, '#1a1a2e', [
            {'type': 'title', 'content': 'Il mio percorso',
             'x': 5, 'y': 8, 'w': 90, 'h': 15, 'font_size': 52, 'color': '#ff6600'},
            {'type': 'text',
             'content': 'Monticelli Cristian — Classe 5M\nI.S.I.S.S. Gobetti-De Gasperi',
             'x': 5, 'y': 26, 'w': 90, 'h': 10, 'font_size': 22, 'color': '#e0e0e0'},
            {'type': 'text',
             'content': '2023-24          ●──────────●          2024-25          ●──────────●          2025-26',
             'x': 5, 'y': 55, 'w': 90, 'h': 18, 'font_size': 18, 'color': '#ff6600'},
            {'type': 'text',
             'content': '  Olimpiadi Informatica               PCTO + Certificati               Attestato + Armi',
             'x': 5, 'y': 72, 'w': 90, 'h': 12, 'font_size': 15, 'color': '#aaaaaa'},
        ])

        # Slide 2
        add_slide(db, pres_id, 2, '#0f3460', [
            {'type': 'title', 'content': '\U0001f3c5 2023-24 — Olimpiadi di Informatica',
             'x': 5, 'y': 5, 'w': 90, 'h': 14, 'font_size': 36, 'color': '#ff6600'},
            {'type': 'text',
             'content': 'Partecipazione alla Fase Territoriale delle\nOlimpiadi Italiane di Informatica\npresso I.I.S. Pascal Comandini di Cesena\n\n23 Aprile 2024',
             'x': 5, 'y': 22, 'w': 52, 'h': 55, 'font_size': 20, 'color': '#e0e0e0'},
            {'type': 'image', 'content': '',
             'x': 60, 'y': 18, 'w': 35, 'h': 58,
             'font_size': 0, 'color': '#555555', 'bg_color': '#1e3a5f', 'image': None},
            {'type': 'text', 'content': '[ foto attestato ]',
             'x': 60, 'y': 77, 'w': 35, 'h': 8, 'font_size': 13, 'color': '#888888'},
            {'type': 'text',
             'content': '\U0001f3c5  Prima esperienza in competizione informatica',
             'x': 5, 'y': 80, 'w': 52, 'h': 12, 'font_size': 16, 'color': '#ff9944'},
            {'type': 'image', 'content': '', 'x': 3,  'y': 84, 'w': 20, 'h': 13, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 5,  'image': None},
            {'type': 'image', 'content': '', 'x': 27, 'y': 84, 'w': 20, 'h': 13, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 6,  'image': None},
            {'type': 'image', 'content': '', 'x': 51, 'y': 84, 'w': 20, 'h': 13, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 7,  'image': None},
            {'type': 'image', 'content': '', 'x': 75, 'y': 84, 'w': 20, 'h': 13, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 8,  'image': None},
        ])

        # Slide 3
        add_slide(db, pres_id, 3, '#16213e', [
            {'type': 'title', 'content': '\U0001f4bc 2024-25 — PCTO: Reale Mutua Assicurazioni',
             'x': 5, 'y': 5, 'w': 90, 'h': 14, 'font_size': 34, 'color': '#ff6600'},
            {'type': 'text',
             'content': '\U0001f4cd Viale Liguria 27, Riccione\n\U0001f4c5 7 Aprile 2024 → 4 Maggio 2024\n\U0001f464 Ruolo: Assistente',
             'x': 5, 'y': 22, 'w': 52, 'h': 35, 'font_size': 20, 'color': '#e0e0e0'},
            {'type': 'image', 'content': '',
             'x': 60, 'y': 18, 'w': 35, 'h': 45,
             'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'image': None},
            {'type': 'text', 'content': '[ logo / foto azienda ]',
             'x': 60, 'y': 64, 'w': 35, 'h': 8, 'font_size': 13, 'color': '#888888'},
            {'type': 'text',
             'content': 'Obiettivo: comprendere il funzionamento di un\nufficio assicurativo e acquisire competenze pratiche.',
             'x': 5, 'y': 62, 'w': 52, 'h': 25, 'font_size': 17, 'color': '#aaddff'},
        ])

        # Slide 4
        add_slide(db, pres_id, 4, '#16213e', [
            {'type': 'title', 'content': '\U0001f4bc PCTO — Attività svolte',
             'x': 5, 'y': 5, 'w': 90, 'h': 12, 'font_size': 36, 'color': '#ff6600'},
            {'type': 'text',
             'content': '\U0001f4c1  Archiviazione fisica delle polizze\n\n\U0001f4f2  Avvisi ai clienti via WhatsApp\n\n\U0001f4bb  Archiviazione digitale e scansioni\n\n\U0001f4de  Contatti telefonici con i clienti\n\n\U0001f5c2️  Segreteria e gestione chiamate',
             'x': 5, 'y': 20, 'w': 58, 'h': 72, 'font_size': 19, 'color': '#e0e0e0'},
            {'type': 'image', 'content': '',
             'x': 66, 'y': 18, 'w': 30, 'h': 55,
             'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'image': None},
            {'type': 'text', 'content': '[ foto stage ]',
             'x': 66, 'y': 74, 'w': 30, 'h': 8, 'font_size': 13, 'color': '#888888'},
        ])

        # Slide 5
        add_slide(db, pres_id, 5, '#16213e', [
            {'type': 'title', 'content': '\U0001f4bc PCTO — Competenze acquisite',
             'x': 5, 'y': 5, 'w': 90, 'h': 12, 'font_size': 36, 'color': '#ff6600'},
            {'type': 'text',
             'content': '\U0001f5e3️  Relazionali: gestione clienti, telefonate,\n       situazioni difficili con calma\n\n⚙️  Tecniche: software gestionale Asseasy,\n       SIC, archiviazione digitale\n\n\U0001f9e0  Organizzative: gestione scadenze,\n       pianificazione attività quotidiane\n\n\U0001f4a1  Personali: autonomia, comunicazione\n       efficace, lavoro in team',
             'x': 5, 'y': 20, 'w': 60, 'h': 72, 'font_size': 18, 'color': '#e0e0e0'},
            {'type': 'text',
             'content': '"Questa esperienza mi ha aperto gli occhi\nsulle possibilità future e mi ha motivato\na continuare a crescere professionalmente."',
             'x': 63, 'y': 25, 'w': 33, 'h': 45,
             'font_size': 16, 'color': '#ff9944', 'bg_color': '#1e2d4a'},
            {'type': 'text',
             'content': 'Grazie a: Denis Perugini (tutor aziendale),\nAngelo Berlini (compagno di stage)',
             'x': 63, 'y': 74, 'w': 33, 'h': 18, 'font_size': 14, 'color': '#aaaaaa'},
            {'type': 'image', 'content': '', 'x': 5,  'y': 75, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'z_index': 6,  'image': None},
            {'type': 'image', 'content': '', 'x': 37, 'y': 75, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'z_index': 7,  'image': None},
            {'type': 'image', 'content': '', 'x': 69, 'y': 75, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'z_index': 8,  'image': None},
            {'type': 'image', 'content': '', 'x': 5,  'y': 87, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'z_index': 9,  'image': None},
            {'type': 'image', 'content': '', 'x': 37, 'y': 87, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'z_index': 10, 'image': None},
            {'type': 'image', 'content': '', 'x': 69, 'y': 87, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e2d4a', 'z_index': 11, 'image': None},
        ])

        # Slide 6
        add_slide(db, pres_id, 6, '#0f3460', [
            {'type': 'title', 'content': '\U0001f4dc 2024-25 — Certificati',
             'x': 5, 'y': 5, 'w': 90, 'h': 12, 'font_size': 38, 'color': '#ff6600'},
            {'type': 'text', 'content': '\U0001f681  Corso sui Droni',
             'x': 5, 'y': 20, 'w': 44, 'h': 10, 'font_size': 22, 'color': '#e0e0e0'},
            {'type': 'text',
             'content': "Corso professionale sull'utilizzo\ndi droni, normativa e sicurezza\n— svolto a scuola",
             'x': 5, 'y': 32, 'w': 44, 'h': 25, 'font_size': 17, 'color': '#aaaaaa'},
            {'type': 'image', 'content': '',
             'x': 5, 'y': 58, 'w': 44, 'h': 32,
             'font_size': 0, 'color': '#555555', 'bg_color': '#1e3a5f', 'image': None},
            {'type': 'text', 'content': '\U0001f97d  Corso Visori 3D',
             'x': 52, 'y': 20, 'w': 44, 'h': 10, 'font_size': 22, 'color': '#e0e0e0'},
            {'type': 'text',
             'content': "Corso sull'utilizzo di visori\nper realtà virtuale e aumentata\n— svolto a scuola",
             'x': 52, 'y': 32, 'w': 44, 'h': 25, 'font_size': 17, 'color': '#aaaaaa'},
            {'type': 'image', 'content': '',
             'x': 52, 'y': 58, 'w': 44, 'h': 32,
             'font_size': 0, 'color': '#555555', 'bg_color': '#1e3a5f', 'image': None},
            {'type': 'image', 'content': '', 'x': 5,  'y': 88, 'w': 20, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 6,  'image': None},
            {'type': 'image', 'content': '', 'x': 27, 'y': 88, 'w': 20, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 7,  'image': None},
            {'type': 'image', 'content': '', 'x': 53, 'y': 88, 'w': 20, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 8,  'image': None},
            {'type': 'image', 'content': '', 'x': 75, 'y': 88, 'w': 20, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1e3060', 'z_index': 9,  'image': None},
        ])

        # Slide 7
        add_slide(db, pres_id, 7, '#1a1a2e', [
            {'type': 'title', 'content': '\U0001f393 2025-26 — Attestato di Merito',
             'x': 5, 'y': 5, 'w': 90, 'h': 14, 'font_size': 38, 'color': '#ff6600'},
            {'type': 'text',
             'content': 'Borsa di Studio\nDott. Giuseppe Montanari — Cav. Oreste Angelini\nXV Edizione\n\nClasse V^M — Settore Tecnologico\nIndirizzo: Informatica e Telecomunicazioni\n\nI.S.I.S.S. "Gobetti-De Gasperi" — A.S. 2025/26\n27 Maggio 2026',
             'x': 5, 'y': 22, 'w': 52, 'h': 65, 'font_size': 18, 'color': '#e0e0e0'},
            {'type': 'image', 'content': '',
             'x': 60, 'y': 18, 'w': 36, 'h': 68,
             'font_size': 0, 'color': '#555555', 'bg_color': '#2a1a4a', 'image': None},
            {'type': 'text', 'content': '[ foto attestato di merito ]',
             'x': 60, 'y': 87, 'w': 36, 'h': 8, 'font_size': 13, 'color': '#888888'},
            {'type': 'image', 'content': '', 'x': 3,  'y': 79, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 5,  'image': None},
            {'type': 'image', 'content': '', 'x': 25, 'y': 79, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 6,  'image': None},
            {'type': 'image', 'content': '', 'x': 47, 'y': 79, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 7,  'image': None},
            {'type': 'image', 'content': '', 'x': 69, 'y': 79, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 8,  'image': None},
            {'type': 'image', 'content': '', 'x': 11, 'y': 90, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 9,  'image': None},
            {'type': 'image', 'content': '', 'x': 36, 'y': 90, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 10, 'image': None},
            {'type': 'image', 'content': '', 'x': 61, 'y': 90, 'w': 19, 'h': 10, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a1040', 'z_index': 11, 'image': None},
        ])

        # Slide 8
        add_slide(db, pres_id, 8, '#1a1a2e', [
            {'type': 'title', 'content': '\U0001f3af 2025-26 — Certificato Maneggio Armi',
             'x': 5, 'y': 5, 'w': 90, 'h': 14, 'font_size': 36, 'color': '#ff6600'},
            {'type': 'text',
             'content': "\U0001f3af  Certificato di abilitazione\n      al maneggio delle armi\n\nCompetenza acquisita nel corso\ndell'anno scolastico 2025-26.",
             'x': 5, 'y': 22, 'w': 52, 'h': 55, 'font_size': 20, 'color': '#e0e0e0'},
            {'type': 'image', 'content': '',
             'x': 60, 'y': 18, 'w': 36, 'h': 60,
             'font_size': 0, 'color': '#555555', 'bg_color': '#2a1a2a', 'image': None},
            {'type': 'text', 'content': '[ foto certificato ]',
             'x': 60, 'y': 79, 'w': 36, 'h': 8, 'font_size': 13, 'color': '#888888'},
            {'type': 'image', 'content': '', 'x': 5,  'y': 78, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a0a1a', 'z_index': 4,  'image': None},
            {'type': 'image', 'content': '', 'x': 37, 'y': 78, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a0a1a', 'z_index': 5,  'image': None},
            {'type': 'image', 'content': '', 'x': 69, 'y': 78, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a0a1a', 'z_index': 6,  'image': None},
            {'type': 'image', 'content': '', 'x': 18, 'y': 90, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a0a1a', 'z_index': 7,  'image': None},
            {'type': 'image', 'content': '', 'x': 51, 'y': 90, 'w': 26, 'h': 11, 'font_size': 0, 'color': '#555555', 'bg_color': '#1a0a1a', 'z_index': 8,  'image': None},
        ])

        # Slide 9
        add_slide(db, pres_id, 9, '#0f3460', [
            {'type': 'title', 'content': '✨ Conclusioni',
             'x': 5, 'y': 8, 'w': 90, 'h': 14, 'font_size': 48, 'color': '#ff6600'},
            {'type': 'text',
             'content': 'Tre anni di crescita personale e professionale:\n\n\U0001f3c5  Competizione nelle Olimpiadi di Informatica\n\U0001f4bc  Esperienza lavorativa reale con Reale Mutua\n\U0001f4dc  Certificazioni pratiche (droni, visori, armi)\n\U0001f393  Riconoscimento scolastico come studente meritevole\n\U0001f4bb  Progetto SlidesApp — sviluppato con Python e Flask',
             'x': 5, 'y': 26, 'w': 90, 'h': 55, 'font_size': 20, 'color': '#e0e0e0'},
            {'type': 'text',
             'content': '...e questa presentazione è stata creata\ne mostrata con il mio stesso progetto. \U0001f39e️',
             'x': 10, 'y': 83, 'w': 80, 'h': 12, 'font_size': 18, 'color': '#ff9944'},
        ])

        print("Presentazione PCTO creata!")
        print("  username: cristian")
        print("  password: pcto2026")
        print("  9 slide con segnaposto per le immagini")
        print("  Sostituisci le emoji delle medagliette con quelle di Unica.")


if __name__ == '__main__':
    seed()
