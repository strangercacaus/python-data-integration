# Python Data Integration

## Diagrama ER

```mermaid
erDiagram

    Table {
        int id
        int origin
        string email
    }
    Column {
        string id
        date created_at
        float total_amount
    }
    Origin {
        string id
        int quantity
        float price
    }
    Stream {
        string id
        int quantity
        float price
    }
    Destination {
        string id
        int quantity
        float price
    }
    Source {
        string id
        int quantity
        float price
    }
    Job {
        string id
        string name
        float price
        string description
    }
    Origin ||--|| Source : representa
    Table ||--|{ Column : Possui
    Table }o--|| Origin : Pertence
    Table ||--o{ Stream : "É Processado Por"
    Stream }o--|| Job : "É Montorado Com"
    Stream ||--|| Destination : "Envia Para"
    Stream ||--|| Source : "Extrai de"
```

## Description
This Entity Relationship Diagram shows:
- A Customer can place multiple Orders
- Each Order can contain multiple Order Items
- Each Order Item is associated with a Product
- The attributes of each entity are listed within the entity boxes