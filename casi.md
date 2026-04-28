# Casi d'Uso - lidesApp

## Diagramma dei Casi d'Uso

```plantuml
@startuml
left to right direction
skinparam actorBackgroundColor #FFE6E6
skinparam usecaseBackgroundColor #FFFACD

actor Visitatore
actor Utente

rectangle lidesApp {
    usecase "Visualizza home\npubblica" as UC1
    usecase "Registrazione\nutente" as UC2
    usecase "Login" as UC3
    usecase "Cambio lingua" as UC4
    usecase "Verifica secondo\nfattore" as UC5
    usecase "Crea\npresentazione" as UC6
    usecase "Modifica\npresentazione" as UC7
    usecase "Aggiungi slide" as UC8
    usecase "Modifica slide" as UC9
    usecase "Elimina slide" as UC10
    usecase "Cambia colore\ne titolo slide" as UC11
    usecase "Verifica\nautenticazione" as UC12
}

Visitatore --> UC1
Visitatore --> UC2
Visitatore --> UC3
Visitatore --> UC4
UC3 ..> UC5 : <<extend>>

Utente --> UC6
Utente --> UC7
Utente --> UC8
Utente --> UC9
Utente --> UC10
UC7 ..> UC11 : <<extend>>
UC9 ..> UC12 : <<extend>>
UC10 ..> UC12 : <<extend>>

UC3 ..> Utente : <<after login>>

@enduml
```

## Legenda
- **→** Associazione (l'attore utilizza il caso d'uso)
- **..>** Estensione (relazione include/extend)

## Descrizione Casi d'Uso

### Visitatore
| Caso d'Uso | Descrizione |
|-----------|-------------|
| Visualizza home pubblica | Accesso alla pagina principale |
| Registrazione utente | Creazione nuovo account |
| Login | Accesso con credenziali |
| Cambio lingua | Personalizzazione lingua |
| Verifica secondo fattore | Autenticazione 2FA |

### Utente
| Caso d'Uso | Descrizione |
|-----------|-------------|
| Crea presentazione | Creazione nuova presentazione |
| Modifica presentazione | Modifica proprietà |
| Aggiungi slide | Aggiunta slide |
| Modifica slide | Modifica contenuto slide |
| Elimina slide | Rimozione slide |
| Cambia colore e titolo slide | Personalizzazione slide |
| Verifica autenticazione | Verifica accesso |