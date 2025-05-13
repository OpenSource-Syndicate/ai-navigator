# Core Database Package

This package handles all database-related operations for the Ultimate AI system, primarily using SQLAlchemy for ORM capabilities with a SQLite backend.

## Components

*   **`database.py`:**
    *   Defines the SQLite database URL (`DATABASE_URL = "sqlite:///./ultimate_ai.db"`).
    *   Creates the SQLAlchemy `engine`.
    *   Creates the `SessionLocal` factory for generating database sessions.
    *   Defines the `Base` declarative base class for SQLAlchemy models.
    *   Includes the `init_db()` function to create all database tables defined by the models.
    *   Provides the `get_db()` dependency function, typically used with FastAPI, to manage session lifecycles within requests.
*   **`models.py`:**
    *   Defines the SQLAlchemy ORM models that map to database tables.
    *   **`LearnedInfo`:** Stores general learned information, potentially including UI analysis summaries, plans, or other text content. Also used by `SemanticIndexer` to store text content alongside its generated embedding (as a JSON string or potentially blob in the future).
    *   **`APIRequest`:** Stores details about captured API requests (method, URL, headers, body, etc.). This allows the `APIReverseEngineer` and `SemanticIndexer` to process and learn from network interactions.

## Usage

*   The database is initialized using `init_db()`, typically on application startup (see `main.py` or `init_db.py` script).
*   Database sessions are obtained using `SessionLocal()` or the `get_db` dependency.
*   Data is queried and manipulated using standard SQLAlchemy session operations on the defined models (`LearnedInfo`, `APIRequest`).
*   The `SemanticIndexer` interacts with the `LearnedInfo` table to store and potentially retrieve embeddings.

## Backend

Currently uses SQLite (`ultimate_ai.db` file in the project root), which is suitable for development and single-user scenarios. For production or multi-user environments, migrating to a more robust database system (e.g., PostgreSQL) might be necessary, which would involve updating the `DATABASE_URL` and potentially installing the appropriate database driver. 