# Documento dei Requisiti – SlidesApp v3

> Versione aggiornata con diagramma casi d'uso dalla screenshot + UML ricreato. Data: oggi.

[Contenuto originale fino sezione 6.3 invariato...]

### 6.3 Diagramma dei casi d'uso

**Screenshot originale fornito:**

![Diagramma casi d'uso dalla screenshot](Screenshot 2026-04-28 093957.png)

**UML ricreato con PlantUML (omini + nuvolette, esempio adattato):**

```plantuml
@startuml casi_uso_slidesapp
left to right direction
actor Visitatore
actor Utente
Visitatore <|-- Utente

Visitatore --> (Visualizza elenco presentazioni)
Visitatore --> (Visualizza dettaglio presentazione)

Utente --> (Registrazione utente)
Utente --> (Login)
Utente --> (Logout)
Utente --> (Crea presentazione)
Utente --> (Aggiungi slide)
Utente --> (Modifica slide)
Utente --> (Sposta slide)
Utente --> (Cambia colore slide)

(Crea presentazione) .> (Verifica autenticazione) : <<include>>
(Aggiungi slide) .> (Verifica autenticazione) : <<include>>
(Modifica slide) .> (Verifica autenticazione) : <<include>>

(Logout) .> (Login) : <<extend>>
(Modifica slide) .> (Upload immagine) : <<extend>>
@enduml
```

**[Resto documento invariato...]**

**v3 completa con foto integrata + diagramma ricreato da screenshot!** Renderizza con PlantUML extension o online.
