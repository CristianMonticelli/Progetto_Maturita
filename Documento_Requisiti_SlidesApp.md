# Documento dei Requisiti – SlidesApp

> Questo documento descrive i requisiti per il progetto **SlidesApp**, un'applicazione web per la creazione e gestione di presentazioni digitali, sviluppata come elaborato di fine anno del modulo `03_Sviluppo_Web_e_Database`.

---

## 1. Introduzione

### 1.1 Scopo del documento

Lo scopo di questo documento è:

- descrivere in modo chiaro il prodotto **SlidesApp** che si intende realizzare;
- raccogliere i requisiti funzionali e non funzionali del sistema;
- fornire una prima progettazione concettuale tramite diagrammi ER, UML e casi d'uso;
- definire una roadmap di lavoro con milestone e attività principali.

### 1.2 Contesto

Il progetto nasce nell'ambito del quinto anno del corso di informatica. L'obiettivo è realizzare un'applicazione web completa con backend in **Python/Flask** e database relazionale **SQLite**, rispettando i seguenti criteri tecnici:

- gestione dati persistente tramite database relazionale;
- interfaccia web con visualizzazione dinamica lato server (Jinja2), senza utilizzo di JavaScript;
- organizzazione del codice con pattern **Blueprint** (separazione delle route) e pattern **Repository** (separazione della logica di accesso ai dati);
- relazioni tra più tabelle nel database (presentazioni → slide → template).

Il progetto può essere eseguito localmente tramite ambiente virtuale Python ed è versionato su GitHub.

### 1.3 Tema

Tema scelto: **SlidesApp**.

SlidesApp è un'applicazione web che permette agli utenti di creare e gestire **presentazioni digitali** composte da slide. Ogni slide ha un titolo, un contenuto testuale, una posizione ordinata all'interno della presentazione e la possibilità di includere un'immagine. Le slide seguono dei **template predefiniti** che definiscono la struttura del layout.

L'ispirazione viene da strumenti come PowerPoint o Google Slides, ma con un approccio volutamente semplificato: nessun editor visuale, nessun JavaScript, tutto il rendering avviene lato server tramite Flask e Jinja2.

> Il progetto prevede in futuro l'aggiunta di un sistema di autenticazione per associare le presentazioni a un account utente specifico.

---

## 2. Obiettivi generali

Gli obiettivi principali dell'applicazione SlidesApp sono:

- Permettere la **creazione di presentazioni** con titolo e descrizione.
- Consentire l'**aggiunta, modifica ed eliminazione di slide** all'interno di una presentazione, con gestione automatica dell'ordine (posizione).
- Supportare l'**upload di immagini** da associare alle singole slide.
- Permettere la **visualizzazione** di una presentazione con tutte le sue slide in ordine.
- Consentire l'**eliminazione di una presentazione** insieme a tutte le sue slide (cascade delete).
- Utilizzare **template predefiniti** per definire il layout delle slide e guidare l'utente nella compilazione dei contenuti.
- Fornire un'interfaccia web **semplice e accessibile**, funzionante senza JavaScript.
- Strutturare il codice in modo modulare e manutenibile tramite Blueprint e Repository.
