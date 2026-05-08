# Spiegazione JavaScript — Editor Canvas (edit_slide.html)

Tutto il JavaScript si trova dentro un unico blocco:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    // tutto il codice qui dentro
});
```
`DOMContentLoaded` significa: "esegui questo codice solo dopo che la pagina HTML
è stata caricata completamente". Senza questo, gli `getElementById` troverebbero
elementi che non esistono ancora e darebbero `null`.

---

## 1. Variabili globali (lo "stato" dell'editor)

```javascript
const CANVAS_W = 960;   // larghezza interna fissa del canvas in pixel
const CANVAS_H = 540;   // altezza interna fissa (rapporto 16:9)

const slideId        = 5;   // ID della slide nel DB (iniettato da Flask/Jinja)
const presentationId = 2;   // ID della presentazione (iniettato da Flask/Jinja)

const canvas     = document.getElementById('slide-canvas');   // il div canvas
const canvasWrap = document.getElementById('canvas-wrap');    // il wrapper
const canvasArea = document.getElementById('canvas-area');    // la zona esterna
```

### Stato dell'editor

```javascript
let components = [ /* array di oggetti componente, caricato dal server */ ];
let selectedId = null;   // ID del componente selezionato (null = nessuno)
let tempId     = -1;     // ID temporaneo negativo per nuovi componenti non ancora salvati
```

Ogni volta che aggiungi un nuovo componente prima di salvarlo, gli viene dato
un ID temporaneo negativo (-1, -2, -3...). Quando salvi, il server risponde
con i veri ID del database, e `components` viene aggiornato.

### Stato del mouse

```javascript
let isDragging  = false;         // true mentre stai trascinando un componente
let isResizing  = false;         // true mentre stai ridimensionando
let resizeDir   = '';            // direzione della maniglia ('nw', 'se', ecc.)
let dragOffPct  = { x: 0, y: 0 };  // offset del click rispetto al bordo del componente
let resizeStart = {};            // valori iniziali al momento di iniziare il resize
```

---

## 2. Scala del canvas — `scaleCanvas()`

### Il problema
Il canvas internamente è sempre 960×540 pixel. Ma lo schermo può essere
più piccolo (laptop) o più grande. Dobbiamo ridimensionarlo visivamente
senza cambiare le coordinate interne.

### La soluzione: CSS transform
```javascript
function scaleCanvas() {
    const availW = canvasArea.clientWidth  - 32;  // spazio disponibile in larghezza
    const availH = canvasArea.clientHeight - 32;  // spazio disponibile in altezza

    // scegli il fattore più piccolo per non sforare in nessuna direzione
    const scale = Math.min(availW / CANVAS_W, availH / CANVAS_H);
    //            Math.min(800/960, 500/540) = Math.min(0.833, 0.925) = 0.833

    // applica la scala visiva — il canvas sembra più piccolo ma internamente è 960×540
    canvas.style.transform = `scale(${scale})`;

    // ridimensiona il wrapper per occupare lo spazio giusto nella pagina
    // (transform non cambia il layout, serve il wrapper per "tenere il posto")
    canvasWrap.style.width  = (960 * 0.833) + 'px';  // 800px
    canvasWrap.style.height = (540 * 0.833) + 'px';  // 450px
}

scaleCanvas();                                  // esegui subito al caricamento
window.addEventListener('resize', scaleCanvas); // riesegui quando la finestra cambia
```

**Effetto concreto:** se il canvas è scalato a 0.8, un componente con
`font-size: 48px` appare come se fosse 38px sullo schermo. Ma internamente
rimane 48px, e verrà salvato come 48px nel database.

---

## 3. Funzioni di utilità

### `esc(s)` — escape HTML
```javascript
function esc(s) {
    return String(s ?? '')                    // converte null/undefined in stringa vuota
        .replace(/&/g, '&amp;')             // & → &amp;
        .replace(/</g, '&lt;')              // < → &lt;
        .replace(/>/g, '&gt;')             // > → &gt;
        .replace(/\n/g, '<br>');            // a capo → <br>
}
```
Serve per sicurezza: se l'utente scrive `<script>alert('xss')</script>`
nel titolo, questa funzione lo trasforma in testo innocuo invece di
eseguirlo come codice HTML.

### `mousePct(e)` — posizione mouse in percentuale
```javascript
function mousePct(e) {
    const r = canvas.getBoundingClientRect();
    // getBoundingClientRect restituisce la posizione e dimensione VISIVA
    // del canvas (dopo la scala CSS), in coordinate dello schermo
    return {
        x: (e.clientX - r.left) / r.width  * 100,
        y: (e.clientY - r.top)  / r.height * 100,
    };
}
```

**Esempio concreto:**
- Canvas visivo: parte da x=100px sullo schermo, largo 800px
- Mouse a x=300px sullo schermo
- `(300 - 100) / 800 * 100` = `200 / 800 * 100` = **25%**
- Significa: il mouse è al 25% della larghezza del canvas

Usando percentuali invece di pixel, i risultati sono sempre corretti
indipendentemente dalla scala del canvas.

### `round1(v)` — arrotonda a 1 decimale
```javascript
function round1(v) { return Math.round(v * 10) / 10; }
// round1(25.347) → 25.3
```
Evita che le posizioni abbiano 10 decimali inutili (es. 25.347281938...).

### `clamp(v, lo, hi)` — blocca un valore in un intervallo
```javascript
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
// clamp(110, 0, 100) → 100   (non esce oltre 100%)
// clamp(-5, 0, 100)  → 0     (non va sotto 0%)
// clamp(50, 0, 100)  → 50    (valore normale, non cambia)
```

---

## 4. Rendering — `renderAll()` e `renderComp()`

### `renderAll()`
```javascript
function renderAll() {
    canvas.innerHTML = '';   // cancella tutto quello che c'è nel canvas

    // ordina per z_index (componenti con z_index basso vanno sotto)
    // e poi ridisegna tutto
    [...components]
        .sort((a, b) => (a.z_index || 0) - (b.z_index || 0))
        .forEach(renderComp);
}
```

Il `...` (spread operator) crea una copia dell'array prima di ordinarlo,
così l'array originale non viene modificato.

### `renderComp(comp)` — crea un componente nel DOM

```javascript
function renderComp(comp) {
    // 1. Crea un div vuoto
    const el = document.createElement('div');

    // 2. Aggiungi le classi CSS
    el.className = 'comp-el' + (comp.id === selectedId ? ' comp-selected' : '');
    //                          ^ se è selezionato, aggiunge il bordo arancione

    // 3. Memorizza l'ID nell'attributo data-id per recuperarlo negli eventi
    el.dataset.id = comp.id;

    // 4. Applica posizione e dimensioni come percentuali
    el.style.cssText = `left:${comp.x}%; top:${comp.y}%; width:${comp.width}%; height:${comp.height}%; ...`;

    // 5. Riempi l'interno in base al tipo
    if (comp.type === 'title') {
        el.innerHTML = `<div style="font-size:${comp.font_size}px; font-weight:700; ...">Testo titolo</div>`;
    } else if (comp.type === 'image') {
        el.innerHTML = `<img src="${comp.image}" ...>`;  // o placeholder se nessuna immagine
    }
    // ecc. per text e link

    // 6. Se è selezionato, aggiungi le 8 maniglie di ridimensionamento
    if (comp.id === selectedId) {
        ['nw','n','ne','e','se','s','sw','w'].forEach(dir => {
            const h = document.createElement('div');
            h.className = `rh rh-${dir}`;   // classe CSS che posiziona la maniglia
            h.dataset.dir = dir;             // memorizza la direzione
            el.appendChild(h);              // aggiunge la maniglia dentro il componente
        });
    }

    // 7. Aggiunge l'evento mousedown e inserisce nel canvas
    el.addEventListener('mousedown', onCompDown);
    canvas.appendChild(el);
}
```

---

## 5. Gestione del mouse — il cuore dell'editor

### Evento 1: `onCompDown(e)` — click su un componente

```javascript
function onCompDown(e) {

    // CASO A: ha cliccato su una maniglia di ridimensionamento
    if (e.target.classList.contains('rh')) {
        e.preventDefault();      // evita comportamenti default del browser
        e.stopPropagation();     // evita che l'evento arrivi al canvas (deseleziona)

        const comp = getComp(+e.currentTarget.dataset.id);
        selectComp(comp.id);
        isResizing = true;
        resizeDir  = e.target.dataset.dir;   // 'nw', 'se', ecc.

        const mp = mousePct(e);
        resizeStart = {
            mx: mp.x, my: mp.y,        // posizione mouse al click
            x: comp.x, y: comp.y,      // posizione componente al click
            w: comp.width, h: comp.height  // dimensioni componente al click
        };
        return;   // esce, non eseguire il codice del drag
    }

    // CASO B: ha cliccato sul corpo del componente → inizia drag
    e.preventDefault();
    e.stopPropagation();

    const id   = +e.currentTarget.dataset.id;   // il + converte stringa in numero
    selectComp(id);
    const comp = getComp(id);
    const mp   = mousePct(e);

    // calcola l'offset: dove nel componente ha cliccato l'utente
    dragOffPct = {
        x: mp.x - comp.x,    // es: mouse al 30%, componente inizia al 25% → offset 5%
        y: mp.y - comp.y
    };
    isDragging = true;
}
```

**Perché `e.stopPropagation()`?**
Gli eventi DOM "risalgono" dall'elemento cliccato verso l'alto (bubbling).
Se clicchi su un componente, l'evento arriva anche al canvas.
Il canvas ha un listener che deseleziona tutto quando si clicca su di esso.
`stopPropagation()` blocca questa risalita.

**Perché l'offset nel drag?**
Senza offset, quando inizi a trascinare, il bordo in alto a sinistra del
componente "salta" sotto il cursore. Con l'offset, il componente rimane
esattamente dove l'hai cliccato.

```
Senza offset:           Con offset:
[   |comp   ]           [  co|mp   ]
       ^cursore              ^cursore
→ il componente salta   → il componente rimane fermo
```

---

### Evento 2: `mousemove` su `document`

```javascript
document.addEventListener('mousemove', e => {
    if (!isDragging && !isResizing) return;   // esci subito se non stai facendo niente

    const mp   = mousePct(e);
    const comp = getComp(selectedId);
    if (!comp) return;
    const el   = canvas.querySelector(`[data-id="${selectedId}"]`);

    // ── DRAG ──
    if (isDragging) {
        // nuova posizione = posizione mouse - offset iniziale
        comp.x = round1(clamp(mp.x - dragOffPct.x, 0, 100 - comp.width));
        //                     ^ dove sarebbe il bordo sx   ^ non uscire a destra
        comp.y = round1(clamp(mp.y - dragOffPct.y, 0, 100 - comp.height));

        // aggiorna SOLO left e top nel DOM (più veloce che rifare tutto il componente)
        if (el) {
            el.style.left = comp.x + '%';
            el.style.top  = comp.y + '%';
        }
        updatePosDisplay(comp);   // aggiorna X/Y nel pannello
    }

    // ── RESIZE ──
    if (isResizing) {
        // spostamento del mouse dall'inizio del resize
        const dx = mp.x - resizeStart.mx;
        const dy = mp.y - resizeStart.my;
        const MIN = 5;   // dimensione minima 5% del canvas
        let {x, y, w, h} = resizeStart;   // parti dai valori iniziali

        // maniglia EST → aumenta larghezza verso destra
        if (resizeDir.includes('e')) w = Math.max(MIN, resizeStart.w + dx);

        // maniglia SUD → aumenta altezza verso il basso
        if (resizeDir.includes('s')) h = Math.max(MIN, resizeStart.h + dy);

        // maniglia OVEST → aumenta larghezza verso sinistra E sposta il bordo sinistro
        if (resizeDir.includes('w')) {
            w = Math.max(MIN, resizeStart.w - dx);
            x = resizeStart.x + resizeStart.w - w;   // bordo destro fermo = x_inizio + w_inizio
        }

        // maniglia NORD → aumenta altezza verso l'alto E sposta il bordo superiore
        if (resizeDir.includes('n')) {
            h = Math.max(MIN, resizeStart.h - dy);
            y = resizeStart.y + resizeStart.h - h;   // bordo inferiore fermo
        }

        // impedisce di uscire fuori dal canvas
        x = clamp(x, 0, 100);
        y = clamp(y, 0, 100);
        w = Math.min(100 - x, w);   // non sforare a destra
        h = Math.min(100 - y, h);   // non sforare in basso

        comp.x = round1(x); comp.y = round1(y);
        comp.width = round1(w); comp.height = round1(h);

        if (el) {
            el.style.left   = comp.x + '%';
            el.style.top    = comp.y + '%';
            el.style.width  = comp.width + '%';
            el.style.height = comp.height + '%';
        }
        updatePosDisplay(comp);
    }

    // aggiorna la barra delle coordinate in basso
    document.getElementById('coords-bar').textContent =
        `X:${comp.x.toFixed(1)}%  Y:${comp.y.toFixed(1)}%  ...`;
});
```

**Perché `mousemove` è su `document` e non sul canvas?**
Se muovi il mouse rapidamente, il cursore può uscire dal canvas prima che
il componente lo raggiunga. Mettendo l'evento su `document`, il drag
continua a funzionare anche fuori dal canvas.

**Perché aggiorno solo `left/top` invece di `renderAll()`?**
`renderAll()` ricrea tutto il DOM del canvas (cancella e riscrive ogni div).
Durante il movimento del mouse questo avviene decine di volte al secondo:
se ricreassi tutto ogni volta, l'animazione sarebbe scattosa.
Aggiornare solo `el.style.left` è molto più veloce.

---

### Evento 3: `mouseup` su `document`

```javascript
document.addEventListener('mouseup', () => {
    if (isDragging || isResizing) {
        isDragging = false;
        isResizing = false;
        renderAll();   // ora posso rifare tutto il DOM con le posizioni finali corrette
    }
});
```

`renderAll()` viene chiamato solo al rilascio del mouse (non durante il drag)
per ridisegnare le maniglie nella posizione finale.

---

## 6. Selezione componenti

```javascript
function getComp(id) {
    return components.find(c => c.id === id) || null;
    // cerca nell'array il componente con quell'ID
    // se non esiste, ritorna null invece di undefined
}

function selectComp(id) {
    selectedId = id;
    renderAll();      // ridisegna tutto (aggiunge bordo arancione + maniglie)
    updateProps();    // aggiorna il pannello delle proprietà
}

function deselectAll() {
    selectedId = null;
    renderAll();
    updateProps();    // nasconde il pannello proprietà
}

// click sul canvas vuoto → deseleziona
canvas.addEventListener('mousedown', e => {
    if (e.target === canvas) deselectAll();
    //  ^ solo se ha cliccato direttamente sul canvas, non su un componente
});
```

---

## 7. Pannello proprietà

### `updateProps()` — aggiorna il pannello quando si seleziona qualcosa

```javascript
function updateProps() {
    if (!selectedId) {
        // nessun componente selezionato → mostra messaggio "seleziona elemento"
        propsEmpty.style.display = 'block';
        propsBody.style.display  = 'none';
        return;
    }

    const comp = getComp(selectedId);
    propsEmpty.style.display = 'none';
    propsBody.style.display  = 'flex';

    // mostra il nome del tipo (es. "Titolo", "Testo")
    propTypeLabel.textContent = { title:'Titolo', text:'Testo', image:'Immagine', link:'Link' }[comp.type];

    // per le immagini nasconde font/colore, mostra upload
    const isImg = comp.type === 'image';
    prContent.style.display  = isImg ? 'none' : 'flex';
    prImage.style.display    = isImg ? 'flex' : 'none';
    prFontsize.style.display = isImg ? 'none' : 'flex';
    prColor.style.display    = isImg ? 'none' : 'flex';

    // popola i campi con i valori attuali del componente
    propContent.value         = comp.content   || '';
    propFs.value              = comp.font_size || 24;
    propFsVal.textContent     = comp.font_size || 24;
    propColor.value           = comp.color     || '#333333';

    // sfondo: se transparent, checkbox "Trasparente" è spuntata
    const isTransp = !comp.bg_color || comp.bg_color === 'transparent';
    propBgTr.checked = isTransp;
    propBgColor.style.display = isTransp ? 'none' : 'inline-block';
}
```

### Modifiche in tempo reale (live update)

Ogni campo del pannello ha un listener che:
1. Aggiorna l'oggetto in `components[]`
2. Aggiorna il DOM del componente direttamente (senza `renderAll()`)

```javascript
// Esempio: campo testo
propContent.addEventListener('input', () => {
    const comp = getComp(selectedId);
    comp.content = propContent.value;               // 1. aggiorna array

    const inner = canvas.querySelector(`[data-id="${selectedId}"] div`);
    if (inner) inner.innerHTML = esc(comp.content); // 2. aggiorna DOM
});

// Esempio: slider font size
propFs.addEventListener('input', () => {
    const v = +propFs.value;               // converte stringa in numero
    propFsVal.textContent = v;             // aggiorna il numero mostrato accanto allo slider
    const comp = getComp(selectedId);
    comp.font_size = v;
    const inner = canvas.querySelector(`[data-id="${selectedId}"] div`);
    if (inner) inner.style.fontSize = v + 'px';
});
```

---

## 8. Upload immagine

```javascript
propImgFile.addEventListener('change', async () => {
    const comp = getComp(selectedId);
    if (!comp || comp.type !== 'image') return;  // sicurezza: solo per componenti immagine

    const fd = new FormData();
    fd.append('image', propImgFile.files[0]);    // aggiunge il file al form

    // manda il file al server con una richiesta POST multipart
    const res = await apiFetch(`/api/slides/${slideId}/upload_image`, {
        method: 'POST',
        body: fd   // nota: NON impostare Content-Type, lo fa FormData automaticamente
    });

    comp.image = res.path;   // es. '/static/uploads/foto.png'
    renderAll();             // ridisegna il componente con la nuova immagine
    updateProps();           // aggiorna l'anteprima nel pannello
});
```

Il server salva il file nella cartella `static/uploads/` e risponde con
il percorso del file. Questo percorso viene salvato nell'oggetto componente
in memoria (e poi nel DB quando si salva).

---

## 9. Aggiungere un componente — dropdown

```javascript
const DEFAULTS = {
    title: { content:'Titolo', x:5, y:5, width:90, height:18, font_size:48, color:'#ff6600', ... },
    text:  { content:'Testo',  x:5, y:28, width:60, height:40, font_size:22, color:'#333333', ... },
    image: { content:'',       x:63, y:5, width:32, height:60, ... },
    link:  { content:'https://...', x:5, y:75, ... },
};

addMenu.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', e => {
        e.stopPropagation();  // evita che il click chiuda il dropdown immediatamente
        const type = btn.dataset.type;   // 'title', 'text', 'image' o 'link'

        const comp = {
            id: tempId--,    // ID temporaneo negativo: -1, poi -2, poi -3...
            type,
            z_index: 0,
            ...DEFAULTS[type]  // copia tutte le proprietà default per quel tipo
        };

        components.push(comp);   // aggiunge all'array in memoria
        selectComp(comp.id);     // seleziona subito il nuovo componente
        addMenu.classList.remove('open');  // chiude il dropdown
    });
});
```

**L'operatore spread `...DEFAULTS[type]`** copia tutte le proprietà dell'oggetto
default nel nuovo componente. Equivale a scrivere:
```javascript
const comp = {
    id: tempId--,
    type: 'title',
    z_index: 0,
    content: 'Titolo',
    x: 5,
    y: 5,
    // ecc. tutti i campi di DEFAULTS.title
};
```

---

## 10. Tasti rapidi

```javascript
document.addEventListener('keydown', e => {
    const tag = e.target.tagName;
    // NON intercettare i tasti se l'utente sta scrivendo in un campo di testo
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;

    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId !== null) {
        e.preventDefault();
        // rimuove il componente dall'array con filter (crea nuovo array senza quell'elemento)
        components = components.filter(c => c.id !== selectedId);
        selectedId = null;
        renderAll();
        updateProps();
        return;
    }

    if (e.key === 'Escape') { deselectAll(); return; }

    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key) && selectedId !== null) {
        e.preventDefault();
        const comp = getComp(selectedId);
        const step = e.shiftKey ? 5 : 1;  // Shift = 5%, normale = 1%

        if (e.key === 'ArrowLeft')  comp.x = clamp(comp.x - step, 0, 100 - comp.width);
        if (e.key === 'ArrowRight') comp.x = clamp(comp.x + step, 0, 100 - comp.width);
        if (e.key === 'ArrowUp')    comp.y = clamp(comp.y - step, 0, 100 - comp.height);
        if (e.key === 'ArrowDown')  comp.y = clamp(comp.y + step, 0, 100 - comp.height);

        comp.x = round1(comp.x);
        comp.y = round1(comp.y);
        renderAll();
        updatePosDisplay(comp);
    }
});
```

---

## 11. Salvataggio — il bottone "Salva"

```javascript
document.getElementById('save-btn').addEventListener('click', async () => {

    // costruisce l'oggetto da mandare al server
    const data = {
        bg_color: document.getElementById('bg-input').value,   // colore sfondo slide
        components: components.map(c => ({    // mappa ogni componente in un oggetto pulito
            type:      c.type,
            content:   c.content   || '',
            x:         c.x,
            y:         c.y,
            width:     c.width,
            height:    c.height,
            font_size: c.font_size || 0,
            color:     c.color     || '#333333',
            bg_color:  c.bg_color  || 'transparent',
            z_index:   c.z_index   || 0,
            image:     c.image     || null,
            // NON include l'id: il server li riassegna
        }))
    };

    const res = await apiFetch(`/api/slides/${slideId}/components/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),   // converte l'oggetto in stringa JSON
    });

    // il server risponde con i componenti salvati e i loro ID reali del database
    components = res.components;   // sostituisce gli ID temporanei con quelli reali
    selectedId = null;
    renderAll();
    updateProps();
    showToast('Slide salvata!');
});
```

**Cosa succede lato server:**
1. Riceve il JSON
2. Cancella tutti i componenti esistenti per quella slide (`DELETE FROM slide_components WHERE slide_id = ?`)
3. Reinserisce tutti i componenti dell'array
4. Risponde con i componenti salvati (con i nuovi ID del database)

---

## 12. Schema riassuntivo del flusso eventi

```
Utente preme "Aggiungi → Titolo"
    → clic su bottone dropdown
    → crea oggetto con id=-1, type='title', x=5, y=5, ...
    → push in components[]
    → selectComp(-1) → renderAll() → appare nel canvas con bordo arancione
    → updateProps() → pannello mostra "Titolo", textarea, slider font...

Utente trascina il titolo
    → mousedown sul div → isDragging=true, calcola dragOffPct
    → mousemove → aggiorna comp.x e comp.y, sposta il div con style.left/top
    → mouseup → isDragging=false, renderAll() (ridisegna maniglie)

Utente scrive "Benvenuti!" nella textarea del pannello
    → input event → comp.content = "Benvenuti!" → inner.innerHTML aggiornato

Utente clicca "Salva"
    → POST /api/slides/5/components/save con JSON
    → server cancella e reinserisce → risponde con id=23 (ID reale)
    → components[0].id diventa 23 (sostituisce -1)
    → showToast("Slide salvata!")
```
