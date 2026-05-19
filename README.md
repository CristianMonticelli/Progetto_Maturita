# SlidesApp

Applicazione web per la creazione e gestione di presentazioni digitali, sviluppata con Python e Flask.

> Autore: **Cristian Monticelli** | Classe 5M | A.S. 2025/2026

---

## Indice

1. [Installazione e avvio](#installazione-e-avvio)
2. [Configurazione email](#configurazione-email)
3. [Come usare l'applicazione](#come-usare-lapplicazione)

---

## Installazione e avvio

**Prerequisiti:** Python 3.10 o superiore, pip.

```bash
# 1. Clona il repository
git clone https://github.com/CristianMonticelli/Progetto_Maturita.git
cd Progetto_Maturita/slides-app

# 2. Crea e attiva l'ambiente virtuale
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Crea il file delle credenziali
cp .env.example .env
# Apri .env e inserisci le tue credenziali (vedi sezione successiva)

# 5. Inizializza il database
python setup_db.py

# 6. Compila le traduzioni
pybabel compile -d app/translations

# 7. (Opzionale) Popola il database con un account e contenuto demo
python seed_demo.py
# Username: demo | Password: demo1234

# 8. Avvia l'applicazione
python run.py
```

L'app sarà disponibile su `http://127.0.0.1:5000`.

---

## Configurazione email

Necessaria per il recupero password. Senza questa configurazione l'app funziona normalmente; solo l'invio email non è attivo.

Apri `.env` e compila i campi:

```
MAIL_USERNAME=tua-email@gmail.com
MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
SECRET_KEY=una-stringa-casuale-lunga
```

`MAIL_PASSWORD` deve essere una **App Password Gmail**, non la password dell'account:

1. Vai su [Account Google](https://myaccount.google.com) → **Sicurezza**
2. Abilita **Verifica in 2 passaggi**
3. Torna su **Sicurezza** → **Password per le app**
4. Genera una password per "Posta" e incollala nel file `.env`

---

## Come usare l'applicazione

### Registrazione e login

1. Aprire `http://127.0.0.1:5000`
2. Cliccare **Registrati** nella barra in alto e inserire username, email e password
3. Effettuare il **Login** con le credenziali create
4. Per recuperare la password, cliccare **Password dimenticata** nella pagina di login e inserire l'email registrata — verrà inviato un link di reset valido per 1 ora

### Navigazione principale

- La **home** (`/`) mostra tutte le presentazioni di tutti gli utenti ed è accessibile senza login
- Dopo il login si viene reindirizzati all'elenco delle proprie presentazioni

### Creare una presentazione

1. Cliccare **Crea presentazione** nella barra di navigazione in alto
2. Inserire titolo e descrizione, poi confermare
3. La nuova presentazione apparirà nell'elenco personale

### Aprire una presentazione

- Cliccare sul titolo della presentazione nell'elenco per aprire la pagina di dettaglio
- Nella pagina di dettaglio sono visibili tutte le slide in ordine con anteprima

### Eliminare una presentazione

- Nella pagina di dettaglio cliccare **Elimina presentazione** (l'operazione è irreversibile e rimuove anche tutte le slide)

### Aggiungere una slide

- Nella pagina di dettaglio cliccare **Aggiungi slide**
- Selezionare il template desiderato tra:
  - **Vuota** — canvas bianco senza componenti
  - **Titolo + Testo** — due caselle di testo preposizionate
  - **Titolo + Testo + Immagine** — casella titolo, testo e area immagine

### Riordinare le slide

- Usare i pulsanti **Sposta su** e **Sposta giù** accanto a ogni slide nella pagina di dettaglio

### Eliminare una slide

- Cliccare **Elimina** accanto alla slide nella pagina di dettaglio

### Modificare una slide — editor canvas

Cliccare **Modifica** accanto a una slide per aprire l'editor visuale.

**Aggiungere componenti:**
Usare i pulsanti nella barra laterale sinistra per aggiungere:
- **Titolo** — testo grande centrato
- **Testo** — casella di testo libera
- **Immagine** — area per un'immagine caricata da file
- **Link** — testo cliccabile con URL

**Selezionare un componente:**
Cliccare su un componente nella canvas per selezionarlo. Comparirà un bordo di selezione con 8 handle di ridimensionamento.

**Spostare un componente:**
Tenere premuto il mouse sul componente e trascinarlo nella posizione desiderata. In alternativa, usare i **tasti freccia** (spostamento 1%) oppure **Shift + tasti freccia** (spostamento 5%).

**Ridimensionare un componente:**
Trascinare uno degli 8 handle ai bordi/angoli del componente (nw, n, ne, e, se, s, sw, w).

**Modificare le proprietà:**
Con un componente selezionato, il **pannello proprietà** a destra mostra:
- Contenuto testuale (modificabile direttamente)
- Dimensione del font
- Colore del testo
- Colore di sfondo del componente

**Caricare un'immagine:**
Cliccare su un componente di tipo immagine, poi nel pannello proprietà usare il pulsante **Carica immagine** per selezionare un file dal proprio computer.

**Eliminare un componente:**
Selezionare il componente e premere il tasto **Canc** oppure cliccare **Elimina componente** nel pannello proprietà.

**Cambiare il colore di sfondo della slide:**
Nel pannello laterale, usare il selettore **Sfondo slide** per scegliere il colore.

**Salvare:**
Cliccare **Salva** in alto a destra. Il salvataggio avviene senza ricaricare la pagina.

### Modalità presentazione

- Nella pagina di dettaglio cliccare **Presenta** per avviare la modalità slideshow a schermo intero
- Navigare tra le slide con i pulsanti **Precedente** e **Successivo**

### Esportare in PowerPoint

- Nella pagina di dettaglio cliccare **Esporta .pptx** per scaricare la presentazione in formato PowerPoint

### Importare un file PowerPoint

- Nella pagina delle presentazioni personali cliccare **Importa .pptx**
- Selezionare un file `.pptx` dal proprio computer
- Verrà creata automaticamente una nuova presentazione con le slide e i contenuti (testi e immagini) del file importato

### Cambiare lingua

- In alto a destra nella barra di navigazione sono disponibili i selettori **IT**, **EN**, **ES**
- La lingua scelta viene mantenuta per tutta la sessione, anche attraverso login e logout

### Logout

- Cliccare **Logout** in alto a destra per uscire dall'account
