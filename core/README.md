# Core Package

This package provides essential, shared utilities and plugin abstractions used throughout the Ultimate AI Web Navigator system.

## Submodules

*   **`database/`**: 
    *   Manages database connections, schema definitions (SQLAlchemy models), and session handling for the SQLite database.
    *   Used for storing persistent information like learned content, API requests, and semantic embeddings (though embeddings might ideally move to a vector store).
    *   See `core/database/README.md` for details.
*   **`plugins/`**: 
    *   Contains wrappers and managers for external tools, services, and APIs that the system interacts with.
    *   Promotes modularity by abstracting the direct interaction logic with these external components.
    *   See `core/plugins/README.md` for details. 