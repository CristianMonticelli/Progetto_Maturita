# Report del Progetto — SlidesApp

> Progetto di fine anno — Modulo 03: Sviluppo Web e Database
> Autore: **Cristian Monticelli** | Classe 5M | A.S. 2025/2026

---

## Indice

1. [Descrizione del progetto](#descrizione-del-progetto)
2. [Funzionalità implementate](#funzionalità-implementate)
3. [Stack tecnologico](#stack-tecnologico)
4. [Architettura del progetto](#architettura-del-progetto)
5. [Schema del database](#schema-del-database)
6. [Scelte progettuali](#scelte-progettuali)
7. [Sviluppi futuri](#sviluppi-futuri)
8. [Fonti e riferimenti](#fonti-e-riferimenti)

---

## Descrizione del progetto

SlidesApp è un'applicazione web per la creazione e la gestione di presentazioni
digitali, sviluppata con Python e Flask. Permette di comporre ogni slide tramite
un editor canvas visuale con componenti liberamente posizionabili (titolo, testo,
immagine, link), esportare presentazioni in PowerPoint e importare file `.pptx`
esistenti.

La pagina iniziale è pubblica: chiunque può sfogliare le presentazioni di tutti
gli utenti senza registrarsi. Per creare e modificare le proprie presentazioni
è necessario autenticarsi.

---

## Funzionalità implementate

### Gestione account
- Registrazione con username, email e password hashata (Werkzeug)
- Login e logout con sessioni Flask
- **Recupero password** via link monouso inviato all'indirizzo email registrato
- Validazione email con espressione regolare lato server

### Presentazioni e slide
- Pagina pubblica nella home: tutte le presentazioni visibili senza login
- Creazione, visualizzazione ed eliminazione di presentazioni personali
- Aggiunta di slide con tre template predefiniti: **Vuota**, **Titolo + Testo**,
  **Titolo + Testo + Immagine**
- Riordinamento slide (sposta su / sposta giù)
- Modalità presentazione a schermo intero (slideshow)

### Editor canvas visuale
- Canvas fisso 960×540 px, scalato via CSS transform in base alla finestra
- Aggiunta di componenti: **Titolo**, **Testo**, **Immagine**, **Link**
- **Drag & drop** per spostare i componenti con il mouse
- **Ridimensionamento** tramite 8 handle direzionali (nw, n, ne, e, se, s, sw, w)
- **Pannello proprietà** laterale: testo, font, colore, sfondo
- Spostamento fine con i tasti freccia (1%; con Shift 5%)
- Eliminazione componente con tasto Canc o dal pannello
- Salvataggio tramite AJAX senza ricaricare la pagina

### Import / Export PowerPoint
- **Esportazione** in formato `.pptx` scaricabile, con coordinate EMU
- **Importazione** di file `.pptx`: testi e immagini convertiti in componenti

### Internazionalizzazione
- Interfaccia in **italiano**, **inglese** e **spagnolo**
- Selettore a bandiera nella topbar, lingua persistente tra pagine e sessioni

---

## Stack tecnologico

| Layer | Tecnologia |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (modulo `sqlite3`) |
| Autenticazione | Werkzeug (hashing), Flask sessions |
| Email | Flask-Mail (Gmail SMTP) |
| Internazionalizzazione | Flask-Babel (GNU gettext) |
| Import/Export pptx | python-pptx |
| Frontend | HTML, CSS, Jinja2, JavaScript (AJAX con `fetch()`) |
| Variabili d'ambiente | python-dotenv |

---

## Architettura del progetto

Il codice è organizzato seguendo il **pattern Blueprint + Repository**,
che separa le responsabilità in moduli indipendenti.

```
slides-app/
├── run.py
├── setup_db.py
├── seed_demo.py
├── requirements.txt
├── .env.example
├── babel.cfg
│
└── app/
    ├── __init__.py
    ├── auth.py
    ├── db.py
    ├── main.py
    ├── schema.sql
    │
    ├── blueprints/
    │   ├── presentations.py
    │   ├── slides.py
    │   └── api.py
    │
    ├── repositories/
    │   ├── user_repository.py
    │   ├── presentation_repository.py
    │   ├── slide_repository.py
    │   └── slide_component_repository.py
    │
    ├── templates/
    │   ├── base.html
    │   ├── main/index.html
    │   ├── auth/
    │   ├── presentations/
    │   └── slides/
    │
    ├── static/
    │   ├── css/style.css
    │   ├── js/
    │   └── uploads/
    │
    └── translations/
```

### Blueprint e responsabilità

| Blueprint | Prefisso | Responsabilità |
|---|---|---|
| `main` | `/` | Home pubblica con tutte le presentazioni |
| `presentations` | `/presentations` | CRUD presentazioni, dettaglio, slideshow |
| `slides` | `/slides` | Editor canvas visuale |
| `api` | `/api` | Endpoint JSON per AJAX, export/import pptx |
| `auth` | `/auth` | Login, register, logout, reset password |

I **Repository** incapsulano tutto l'accesso al database: ogni Blueprint chiama
solo funzioni del repository corrispondente, senza scrivere SQL direttamente
nei controller. In questo modo sostituire il DBMS non richiederebbe di toccare
le route.

---

## Schema del database

```
USER
  id            INTEGER PK
  username      TEXT
  password      TEXT    (hash Werkzeug)
  email         TEXT
  mfa_enabled   INTEGER
  mfa_secret    TEXT

PRESENTATIONS
  id            INTEGER PK
  title         TEXT
  description   TEXT
  author_id     INTEGER FK → USER.id
  created_at    DATETIME

SLIDES
  id            INTEGER PK
  presentation_id INTEGER FK → PRESENTATIONS.id
  position      INTEGER
  bg_color      TEXT

SLIDE_COMPONENTS
  id            INTEGER PK
  slide_id      INTEGER FK → SLIDES.id
  type          TEXT    (title | text | image | link)
  content       TEXT
  x             REAL    (% rispetto al canvas)
  y             REAL
  width         REAL
  height        REAL
  font_size     INTEGER
  color         TEXT
  bg_color      TEXT
  z_index       INTEGER
  image         TEXT    (nome file in static/uploads/)

PASSWORD_RESET_TOKENS
  id            INTEGER PK
  user_id       INTEGER FK → USER.id
  token         TEXT
  expires_at    DATETIME
  used          INTEGER
```

La tabella `SLIDE_COMPONENTS` è il cuore del sistema: ogni componente memorizza
posizione e dimensione come percentuale (0–100) rispetto al canvas 960×540,
permettendo il ridimensionamento responsive senza perdere le proporzioni.

Le eliminazioni a cascata sono gestite tramite `ON DELETE CASCADE` sulle chiavi
esterne, così cancellare una presentazione rimuove automaticamente tutte le slide
e i relativi componenti.

---

## Scelte progettuali

### Pattern Blueprint + Repository
I Blueprint raggruppano le route per area funzionale; i Repository incapsulano
tutto l'accesso al database. Questa separazione rende ogni modulo testabile
indipendentemente e facilita la manutenzione.

### AJAX con `fetch()` e API JSON
Le operazioni di modifica (crea presentazione, aggiungi slide, sposta, elimina,
salva componenti) usano chiamate AJAX verso endpoint `/api/...` che rispondono
in JSON. La pagina non si ricarica: il DOM viene aggiornato direttamente in
JavaScript. Il rendering iniziale resta lato server con Jinja2.

### Editor canvas in percentuale
Posizioni e dimensioni dei componenti sono memorizzate come percentuali (0–100)
rispetto a un canvas virtuale 960×540. Il canvas reale viene scalato tramite
`CSS transform: scale()` in base alla finestra disponibile. Questo permette di
visualizzare le slide in modo identico nell'editor, nella preview e nel presenter
su qualsiasi schermo.

### CSS e JS separati dai template
Tutti gli stili sono raccolti in un unico file `static/css/style.css`, suddiviso
per area con selettori `body.editor-mode` e `body.pres-mode` per isolare i layout
specifici. La logica JavaScript è in file esterni (`base.js`, `edit-slide.js`,
`presenta.js`, ecc.); le variabili Jinja2 vengono passate tramite un piccolo
blocco `<script>` inline con costanti `window.*` prima di ogni `<script src>`.

### Punto di ingresso unico per la creazione
La creazione di una nuova presentazione avviene esclusivamente tramite il pulsante
"Crea presentazione" nella barra di navigazione in alto, sempre visibile.
In una versione precedente esisteva un secondo pulsante con modal AJAX nella
pagina delle presentazioni personali — è stato rimosso per semplificare
l'interfaccia ed evitare duplicazioni.

### Internazionalizzazione GNU gettext
Le stringhe dell'interfaccia sono avvolte con `_()` di Flask-Babel. I file `.po`
(leggibili) vengono compilati in `.mo` (binari) che Flask-Babel legge a runtime.
La lingua è salvata in `session['lang']` e viene preservata esplicitamente
durante `session.clear()` al login e logout.

---

## Sviluppi futuri

- Autenticazione a due fattori (MFA): via app TOTP con QR code (Google
  Authenticator) oppure via codice OTP via email. Lo schema del database è già
  predisposto con le colonne `mfa_enabled` e `mfa_secret` nella tabella utenti.
- Condivisione di presentazioni con altri utenti tramite link
- Modalità collaborativa in tempo reale (WebSocket)
- Esportazione in PDF
- Più template predefiniti per le slide
- Supporto a forme geometriche come componente aggiuntivo

---

## Fonti e riferimenti

Il progetto include funzionalità non affrontate a scuola. Il codice è stato
adattato dalle seguenti risorse esterne.

### Editor canvas: drag & drop

- **Algoritmo drag & drop** (mousedown / mousemove / mouseup con offset):
  https://javascript.info/mouse-drag-and-drop

- **Posizione relativa al canvas** (getBoundingClientRect):
  https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect

### Editor canvas: resize con handle direzionali

- **Concetto degli 8 handle di resize** (nw, n, ne, e, se, s, sw, w):
  https://github.com/taye/interact.js

### Chiamate AJAX

- **Chiamate AJAX con fetch**:
  https://javascript.info/fetch

### Modalità presentazione fullscreen

- **API fullscreen del browser**:
  https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API

### Import/Export PowerPoint

- **Creazione file .pptx — python-pptx quickstart**:
  https://python-pptx.readthedocs.io/en/latest/user/quickstart.html
  Fonte principale per export: aggiunta slide, caselle di testo (add_textbox),
  immagini (add_picture), colore sfondo e RGBColor.

- **Unità di misura EMU in python-pptx**:
  https://python-pptx.readthedocs.io/en/latest/user/units.html
  Usato per convertire le posizioni percentuali del canvas nelle coordinate EMU
  richieste da PowerPoint (9 144 000 × 5 143 500).

- **Lettura file .pptx — python-pptx shapes**:
  https://python-pptx.readthedocs.io/en/latest/user/shapes.html
  Usato per iterare forme, riconoscere testi (has_text_frame), immagini
  (MSO_SHAPE_TYPE.PICTURE) e leggerne font e colori.

- **Repository ufficiale python-pptx con esempi**:
  https://github.com/scanny/python-pptx
  Consultato per il pattern BytesIO + send_file (generazione del file in memoria
  senza salvarlo su disco prima di inviarlo al browser).

### Validazione email lato server

- **Regex validazione email — RFC 5322 semplificato**:
  https://emailregex.com
  Usato come riferimento per costruire l'espressione regolare che verifica il
  formato dell'indirizzo email durante la registrazione
  (`r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'`).
