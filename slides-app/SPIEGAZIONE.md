# SlidesApp — Spiegazione completa del progetto

---

## 1. Struttura generale

```
slides-app/
├── run.py                        ← avvia il server Flask
├── setup_db.py                   ← ricrea il database da zero
├── app/
│   ├── __init__.py               ← crea l'app Flask, registra i blueprint
│   ├── db.py                     ← connessione al database SQLite
│   ├── auth.py                   ← login, register, decoratore @login_required
│   ├── schema.sql                ← struttura delle tabelle
│   ├── blueprints/
│   │   ├── presentations.py      ← rotte pagine presentazioni
│   │   ├── slides.py             ← rotta editor slide
│   │   └── api.py                ← API JSON (usate da JavaScript)
│   ├── repositories/
│   │   ├── presentation_repository.py
│   │   ├── slide_repository.py
│   │   └── slide_component_repository.py
│   └── templates/
│       ├── base.html             ← layout base (navbar, stili, toast, apiFetch)
│       ├── presentations/
│       │   ├── index.html        ← lista presentazioni utente
│       │   ├── presentation_datail.html  ← gestione slide di una presentazione
│       │   └── presenta.html     ← modalità presentazione fullscreen
│       └── slides/
│           └── edit_slide.html   ← EDITOR CANVAS (il file più complesso)
```

---

## 2. Database

### Tabelle principali

```
user
  id, username, password(hash), email, mfa_enabled, mfa_secret

presentations
  id, title, description, author_id → user(id), created_at

slides
  id, presentation_id → presentations(id), position, bg_color

slide_components
  id, slide_id → slides(id),
  type          TEXT  ('title' | 'text' | 'image' | 'link')
  content       TEXT  (testo scritto dall'utente)
  x             REAL  (posizione orizzontale, in % del canvas 0-100)
  y             REAL  (posizione verticale, in % del canvas 0-100)
  width         REAL  (larghezza in % del canvas)
  height        REAL  (altezza in % del canvas)
  font_size     INT   (pixel, riferiti al canvas 960×540)
  color         TEXT  (colore testo, es. '#ff6600')
  bg_color      TEXT  (sfondo elemento, 'transparent' o colore hex)
  z_index       INT   (ordine di sovrapposizione, 0 = sotto)
  image         TEXT  (percorso file immagine, es. '/static/uploads/foto.png')
```

### Relazioni a cascata
- Cancellare una `presentation` → cancella tutte le sue `slides`
- Cancellare una `slide` → cancella tutti i suoi `slide_components`

### Perché le posizioni sono in percentuale?
Perché il canvas viene mostrato a dimensioni diverse (piccolo nell'editor,
grande in modalità presenta). Usando % invece di pixel fissi, un componente
al 5% da sinistra rimane al 5% da sinistra qualunque sia la dimensione dello schermo.

---

## 3. Blueprint e rotte

### presentations.py (pagine HTML)
| Rotta | Cosa fa |
|-------|---------|
| `GET /presentations/` | lista presentazioni dell'utente |
| `GET /presentations/presentazione/<id>` | dettaglio con anteprima slide |
| `GET /presentations/presentazione/<id>/presenta` | modalità presentazione |
| `GET /presentations/presentazione/<id>/delete` | elimina presentazione |

### slides.py (pagine HTML)
| Rotta | Cosa fa |
|-------|---------|
| `GET /slides/<id>/modifica` | apre l'editor canvas per quella slide |

### api.py (JSON, usate da fetch() in JavaScript)
| Rotta | Metodo | Cosa fa |
|-------|--------|---------|
| `/api/presentations/create` | POST | crea presentazione |
| `/api/presentations/<id>` | DELETE | elimina presentazione |
| `/api/presentations/<id>/slides` | POST | aggiunge slide vuota |
| `/api/slides/<id>/move_up` | POST | sposta slide su |
| `/api/slides/<id>/move_down` | POST | sposta slide giù |
| `/api/slides/<id>` | DELETE | elimina slide |
| `/api/slides/<id>/components/save` | POST | salva tutti i componenti |
| `/api/slides/<id>/upload_image` | POST | carica immagine, ritorna il path |

---

## 4. Repository pattern

Ogni repository è un file Python che contiene solo funzioni che parlano con il database.
Il blueprint chiama il repository, il repository chiama il database.

```
blueprint (gestisce HTTP)
    └── repository (gestisce SQL)
            └── db.get_db() (connessione SQLite)
```

Esempio reale:
```python
# slides.py (blueprint)
slide = slide_repository.get_slide_by_id(slide_id)
components = slide_component_repository.get_components_by_slide(slide_id)
return render_template('slides/edit_slide.html', slide=slide, components=components)

# slide_repository.py
def get_slide_by_id(slide_id):
    row = get_db().execute('SELECT * FROM slides WHERE id = ?', (slide_id,)).fetchone()
    return dict(row) if row else None
```

---

## 5. L'editor canvas (edit_slide.html) — spiegazione dettagliata

### 5.1 Struttura HTML dell'editor

```
editor-wrap
├── ed-toolbar          ← barra in alto (Torna, Sfondo, Aggiungi, Salva)
├── ed-main
│   ├── ed-canvas-area  ← zona sinistra (sfondo scuro che contiene il canvas)
│   │   └── ed-canvas-wrap  ← div con le dimensioni SCALATE del canvas
│   │       └── slide-canvas    ← IL CANVAS VERO (960×540 px, scalato con transform)
│   └── ed-props        ← pannello destro proprietà elemento selezionato
└── ed-coords           ← barra in basso con X/Y/W/H correnti
```

### 5.2 Il sistema di coordinate — perché 960×540?

Il canvas è sempre 960×540 pixel internamente (16:9, come HD).
Viene poi ridimensionato visivamente con CSS `transform: scale(fattore)` per
adattarsi allo spazio disponibile sullo schermo.

```javascript
function scaleCanvas() {
    const availW = canvasArea.clientWidth  - 32;  // larghezza disponibile
    const availH = canvasArea.clientHeight - 32;  // altezza disponibile

    // fattore di scala: il più piccolo tra larghezza e altezza
    const scale = Math.min(availW / 960, availH / 540);

    canvas.style.transform = `scale(${scale})`;

    // ridimensiona il wrapper per occupare lo spazio giusto nella pagina
    canvasWrap.style.width  = (960 * scale) + 'px';
    canvasWrap.style.height = (540 * scale) + 'px';
}
```

Se lo schermo ha 800px di larghezza disponibile:
- scale = 800 / 960 = 0.833
- Il canvas appare largo 800px ma internamente è ancora 960px
- Un font da 48px nel canvas appare come 48 × 0.833 = ~40px sullo schermo

In modalità presentazione (presenta.html) lo stesso meccanismo scala il canvas
per riempire lo schermo intero.

### 5.3 I componenti — come sono rappresentati

Ogni componente è un `<div>` con `position: absolute` dentro il canvas:

```javascript
el.style.cssText = [
    `left:${comp.x}%`,      // posizione dal bordo sinistro del canvas
    `top:${comp.y}%`,       // posizione dall'alto del canvas
    `width:${comp.width}%`, // larghezza
    `height:${comp.height}%`,
    `background:${comp.bg_color}`,
    'border-radius:4px',
    'padding:4px 8px',
].join(';');
```

Quando viene selezionato, vengono aggiunti 8 `<div>` piccoli arancioni negli
angoli e nei lati → le maniglie di ridimensionamento.

### 5.4 Il DRAG (trascinamento con il mouse)

**Fase 1 — mousedown sul componente:**
```javascript
function onCompDown(e) {
    selectComp(id);

    // calcola dove nel componente ha cliccato l'utente (in % del canvas)
    const mp = mousePct(e);           // posizione mouse in % canvas
    dragOffPct = {
        x: mp.x - comp.x,            // offset X: mouse - bordo sinistro componente
        y: mp.y - comp.y             // offset Y: mouse - bordo superiore componente
    };
    isDragging = true;
}
```

**Perché l'offset?** Se clicchi al centro di un componente (non sul suo angolo
in alto a sinistra), senza offset il componente "salterebbe" con il bordo
in alto a sinistra sotto il cursore. L'offset compensa questo.

**Fase 2 — mousemove (su `document`, non sul canvas):**
```javascript
if (isDragging) {
    const mp = mousePct(e);
    comp.x = clamp(mp.x - dragOffPct.x, 0, 100 - comp.width);
    comp.y = clamp(mp.y - dragOffPct.y, 0, 100 - comp.height);
    // aggiorna solo left/top per performance (senza rifare tutto il DOM)
    el.style.left = comp.x + '%';
    el.style.top  = comp.y + '%';
}
```

`clamp(valore, min, max)` impedisce che il componente esca fuori dal canvas.

**Perché mousemove è su `document` e non sul canvas?**
Se muovi il mouse velocemente, il cursore può uscire dal canvas prima che il
componente lo raggiunga. Con l'evento su `document`, il drag continua anche fuori.

**Fase 3 — mouseup:** `isDragging = false`, poi `renderAll()` per ridisegnare
tutto (compresi gli angoli di ridimensionamento nella posizione corretta).

### 5.5 Il RESIZE (ridimensionamento)

Ogni maniglia ha una direzione: `nw`, `n`, `ne`, `e`, `se`, `s`, `sw`, `w`
(Nord-Ovest, Nord, Nord-Est, Est, Sud-Est, Sud, Sud-Ovest, Ovest).

```javascript
if (isResizing) {
    const dx = mp.x - resizeStart.mx;  // spostamento mouse X dall'inizio
    const dy = mp.y - resizeStart.my;  // spostamento mouse Y dall'inizio

    let {x, y, w, h} = resizeStart;  // valori iniziali al momento del click

    // maniglia destra (e) → allarga verso destra
    if (resizeDir.includes('e')) w = Math.max(MIN, resizeStart.w + dx);
    // maniglia basso (s) → allunga verso il basso
    if (resizeDir.includes('s')) h = Math.max(MIN, resizeStart.h + dy);
    // maniglia sinistra (w) → allarga verso sinistra E sposta il bordo sinistro
    if (resizeDir.includes('w')) {
        w = Math.max(MIN, resizeStart.w - dx);
        x = resizeStart.x + resizeStart.w - w;  // il bordo destro rimane fermo
    }
    // maniglia alto (n) → allunga verso l'alto E sposta il bordo superiore
    if (resizeDir.includes('n')) {
        h = Math.max(MIN, resizeStart.h - dy);
        y = resizeStart.y + resizeStart.h - h;  // il bordo inferiore rimane fermo
    }
}
```

**Esempio:** Se trascini la maniglia `nw` (angolo in alto a sinistra):
- la direzione contiene sia `n` che `w`
- il bordo destro e quello inferiore rimangono fermi
- il bordo sinistro e quello superiore seguono il mouse

### 5.6 Calcolo posizione mouse in % canvas

```javascript
function mousePct(e) {
    const r = canvas.getBoundingClientRect();
    // getBoundingClientRect restituisce le dimensioni SCALATE visivamente
    // quindi r.width = 960 * scale, r.height = 540 * scale
    return {
        x: (e.clientX - r.left) / r.width  * 100,
        y: (e.clientY - r.top)  / r.height * 100,
    };
}
```

Dividendo per `r.width` (dimensione visiva del canvas) si ottiene già la
percentuale corretta, indipendente dal fattore di scala CSS.

### 5.7 Il pannello proprietà (destra)

Quando si seleziona un componente:
1. Appare il pannello con i campi rilevanti per il tipo
2. Ogni modifica aggiorna `components[]` in memoria E l'elemento nel DOM in tempo reale
3. Il salvataggio finale avviene solo quando si clicca "Salva"

Campi mostrati per tipo:
| Tipo | Contenuto | Font size | Colore | Immagine |
|------|-----------|-----------|--------|----------|
| title | ✓ | ✓ | ✓ | — |
| text | ✓ | ✓ | ✓ | — |
| image | — | — | — | ✓ |
| link | ✓ | ✓ | ✓ | — |

### 5.8 Il salvataggio

Quando l'utente clicca "Salva":
```javascript
const data = {
    bg_color: '#ffffff',        // colore sfondo slide
    components: [               // array di tutti i componenti attuali
        { type, content, x, y, width, height, font_size, color, bg_color, z_index, image },
        ...
    ]
};

await apiFetch(`/api/slides/${slideId}/components/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
});
```

Lato server (`api.py`), la funzione `save_slide_components`:
1. Aggiorna `bg_color` sulla slide
2. Cancella TUTTI i componenti esistenti della slide (`DELETE FROM slide_components WHERE slide_id = ?`)
3. Reinserisce tutti i componenti dell'array ricevuto
4. Restituisce i componenti con i nuovi ID del database

Dopo il salvataggio, JavaScript aggiorna `components[]` con i nuovi ID
(quelli temporanei negativi vengono sostituiti con gli ID reali del DB).

### 5.9 Tasti rapidi nell'editor

| Tasto | Azione |
|-------|--------|
| `Delete` / `Backspace` | Elimina elemento selezionato |
| `Escape` | Deseleziona |
| `←` `→` `↑` `↓` | Sposta di 1% |
| `Shift + freccia` | Sposta di 5% |

---

## 6. Modalità presentazione (presenta.html)

Ogni slide è un `<div class="slide-frame">` con dimensioni fisse 960×540px,
scalato con `transform: scale()` per riempire lo schermo.

```javascript
function scaleSlides() {
    const scale = Math.min(vw / 960, vh / 540);
    const offX = (vw - 960 * scale) / 2;  // centra orizzontalmente
    const offY = (vh - 540 * scale) / 2;  // centra verticalmente

    frame.style.transform = `scale(${scale})`;
    frame.style.left = offX + 'px';
    frame.style.top  = offY + 'px';
}
```

I componenti vengono renderizzati dal server (Jinja2) direttamente nell'HTML
con i loro stili inline — nessuna chiamata AJAX in modalità presenta.

Navigazione: frecce, spazio, click zone laterali, puntini in basso.

---

## 7. apiFetch — la funzione globale per chiamate AJAX

Definita in `base.html`, disponibile in tutte le pagine:

```javascript
async function apiFetch(url, options = {}) {
    const response = await fetch(url, { credentials: 'same-origin', ...options });

    // se la risposta non è JSON (es. redirect al login), mostra errore
    if (!contentType.includes('application/json')) {
        showToast('Sessione scaduta.', true);
        throw error;
    }

    const data = await response.json();

    // se il server risponde con errore (4xx/5xx), mostra il messaggio
    if (!response.ok) {
        showToast(data.error, true);
        throw data;
    }

    return data;  // ritorna il JSON di successo
}
```

Uso tipico:
```javascript
const result = await apiFetch('/api/slides/5/components/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bg_color: '#fff', components: [...] })
});
// result.components contiene i componenti salvati con ID reali
```

---

## 8. Flusso completo — da zero a presentazione

1. **Registrazione/Login** → `/auth/register`, `/auth/login`
2. **Crea presentazione** → modal in `/presentations/` → `POST /api/presentations/create`
3. **Aggiungi slide** → bottone in `/presentations/presentazione/<id>` → `POST /api/presentations/<id>/slides`
4. **Modifica slide** → click "Modifica slide" → `/slides/<id>/modifica` → editor canvas
   - Aggiungi componenti dal dropdown
   - Trascina per posizionare
   - Ridimensiona con le maniglie
   - Modifica testo/colori nel pannello dx
   - Clicca "Salva" → `POST /api/slides/<id>/components/save`
5. **Presenta** → bottone "▶ Presenta" → `/presentations/presentazione/<id>/presenta`
   - Navigazione con frecce / spazio / click
   - Fullscreen con `F`
   - Esci con `ESC`
