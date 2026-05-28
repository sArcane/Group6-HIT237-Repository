# Entity Relationship Diagram (ERD)

Includes the application tables and the Django auth tables that back role-based access control (Users → Groups → Permissions). Custom permissions (`view_all_recordings`, `review_recordings`, `view_species_analytics`, `view_all_anomaly_flags`) are stored as rows in `auth_permission` and linked to users/groups through the standard Django many-to-many join tables.

```mermaid
erDiagram

    %% ── DJANGO AUTH ─────────────────────────────────────────────────────────
    USER {
        int id PK
        varchar username
        varchar email
        varchar password
        bool is_superuser
        bool is_staff
        bool is_active
        datetime date_joined
    }

    GROUP {
        int id PK
        varchar name
    }

    PERMISSION {
        int id PK
        int content_type_id FK
        varchar codename
        varchar name
    }

    %% ── APPLICATION TABLES ──────────────────────────────────────────────────
    SPECIES {
        int id PK
        varchar name
        varchar scientific_name
        varchar conservation_status
    }

    LOCATION {
        int id PK
        varchar name
    }

    RECORDING {
        int id PK
        int user_id FK
        int species_id FK
        int location_id FK
        varchar audio_file
        datetime date_recorded
        float confidence_score
        bool flagged
        datetime created_at
    }

    ANOMALYFLAG {
        int id PK
        int recording_id FK
        int flagged_by_id FK
        varchar anomaly_type
        text description
        datetime flagged_at
    }

    %% ── DJANGO AUTH RELATIONSHIPS ────────────────────────────────────────────
    USER }|--|{ GROUP        : "auth_user_groups"
    USER }|--|{ PERMISSION   : "auth_user_user_permissions"
    GROUP }|--|{ PERMISSION  : "auth_group_permissions"

    %% ── APPLICATION RELATIONSHIPS ────────────────────────────────────────────
    USER     ||--o{ RECORDING   : "creates"
    USER     ||--o{ ANOMALYFLAG : "flags"
    SPECIES  ||--o{ RECORDING   : "recorded as"
    LOCATION ||--o{ RECORDING   : "recorded at"
    RECORDING ||--o{ ANOMALYFLAG : "has"
```
