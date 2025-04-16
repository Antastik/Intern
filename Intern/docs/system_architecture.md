graph TD
    Client[Client Browser/App] -->|HTTP Requests| API[FastAPI Application]
    API -->|Authentication| Auth[Authentication Module]
    API -->|Database Operations| CRUD[CRUD Operations]
    CRUD -->|ORM| DB[(SQLite Database)]
    
    subgraph "FastAPI Application"
        API
        Auth
        CRUD
        Models[Database Models]
        Schemas[Pydantic Schemas]
    end
    
    subgraph "Database"
        DB
        Users[(Users Table)]
        Tasks[(Tasks Table)]
        TimeLogs[(Time Logs Table)]
    end
    
    Models -.-> DB
    Users -.-> DB
    Tasks -.-> DB
    TimeLogs -.-> DB