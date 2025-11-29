# Database Layer

This module provides the database layer for Maveric MiniPilot, including SQLAlchemy models, migrations, and a repository pattern for data access.

## Overview

The database layer consists of:
- **Models**: SQLAlchemy ORM models for User, Conversation, Message, and KnowledgeChunk
- **Configuration**: Database connection setup with support for SQLite (dev) and PostgreSQL (production)
- **Migrations**: Alembic-based database migrations
- **Repository**: High-level CRUD and query functions for all models

## Architecture

```
database/
├── db_config.py          # Database configuration and session management
├── models.py              # SQLAlchemy ORM models
├── repository.py          # Data access layer (CRUD functions)
├── migrations/            # Alembic migration scripts
│   ├── env.py            # Alembic environment configuration
│   ├── script.py.mako    # Migration template
│   └── versions/         # Generated migration files
├── tests/                 # Test scripts
│   └── test_database.py  # End-to-end database tests
└── README.md             # This file
```

## File Structure

### `db_config.py`

Database configuration and session management.

**Key Functions:**
- `get_database_url() -> str`: Get database URL from environment or use defaults
- `create_database_engine(url: Optional[str]) -> Engine`: Create SQLAlchemy engine
- `get_engine() -> Engine`: Get or create global engine instance
- `get_session() -> Generator[Session, None, None]`: Context manager for database sessions
- `init_db()`: Initialize database (create all tables)
- `drop_db()`: Drop all tables (WARNING: deletes all data)
- `reset_db()`: Reset database (drop and recreate)

**Environment Variables:**
- `DATABASE_URL`: Full database connection string (highest priority)
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: maveric_minipilot)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password
- `DB_PATH`: SQLite database path (default: data/maveric_minipilot.db)
- `DB_ECHO`: Enable SQLAlchemy query logging (default: false)

**Usage:**
```python
from database.db_config import get_session, init_db

# Initialize database (first time)
init_db()

# Use database session
with get_session() as session:
    # Your database operations here
    pass
```

### `models.py`

SQLAlchemy ORM models for all database tables.

#### `TimestampMixin`
Base mixin providing `created_at` and `updated_at` timestamp columns.

#### `User`
User model representing chatbot users.

**Attributes:**
- `id` (UUID, PK): Unique user identifier
- `external_id` (String, unique, nullable): External user ID from auth system
- `name` (String, nullable): User's display name
- `email` (String, unique, nullable): User's email address
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- `conversations`: One-to-many relationship with Conversation

**Example:**
```python
user = User(
    email="user@example.com",
    name="John Doe",
    external_id="auth_12345"
)
```

#### `Conversation`
Conversation model representing a chat session.

**Attributes:**
- `id` (UUID, PK): Unique conversation identifier
- `user_id` (UUID, FK, nullable): User who owns this conversation
- `title` (String, nullable): Conversation title
- `status` (String): Conversation status ("active" or "archived")
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- `user`: Many-to-one relationship with User
- `messages`: One-to-many relationship with Message

**Indexes:**
- `idx_conversation_user_status`: Composite index on (user_id, status)
- `idx_conversation_created`: Index on created_at

**Example:**
```python
conversation = Conversation(
    user_id=user.id,
    title="How to use the database?",
    status="active"
)
```

#### `Message`
Message model representing individual messages in a conversation.

**Attributes:**
- `id` (UUID, PK): Unique message identifier
- `conversation_id` (UUID, FK): Conversation this message belongs to
- `sender_type` (String): Type of sender ("user", "assistant", or "system")
- `content` (Text): Message content/text
- `role_metadata` (JSON, nullable): Additional metadata (tool calls, retrieved chunks, token counts, etc.)
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- `conversation`: Many-to-one relationship with Conversation

**Indexes:**
- `idx_message_conversation_created`: Composite index on (conversation_id, created_at)
- `idx_message_sender_type`: Index on sender_type

**Example:**
```python
message = Message(
    conversation_id=conversation.id,
    sender_type="user",
    content="Hello, how does the database work?",
    role_metadata={"tokens": 10}
)
```

#### `KnowledgeChunk`
KnowledgeChunk model representing chunks from the knowledge base.

**Attributes:**
- `id` (UUID, PK): Unique knowledge chunk identifier
- `source` (String): Source of the chunk (e.g., "enhanced_readme", "docs")
- `external_id` (String, nullable): External identifier (file path + chunk index, section ID)
- `title` (String, nullable): Chunk title or heading
- `content` (Text): Chunk content/text
- `chunk_metadata` (JSON, nullable): Additional metadata (section_type, module, line_numbers, etc.)
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Indexes:**
- `idx_knowledge_source`: Index on source
- `idx_knowledge_external_id`: Index on external_id
- `idx_knowledge_created`: Index on created_at

**Example:**
```python
chunk = KnowledgeChunk(
    source="enhanced_readme",
    external_id="readme_section_1",
    title="Installation Guide",
    content="To install the project, run: pip install -r requirements.txt",
    chunk_metadata={"section_type": "installation", "module": "readme_generator"}
)
```

### `repository.py`

Repository layer providing high-level CRUD and query functions for all models.

All functions accept a `Session` parameter to allow transaction management at the service layer.

#### User Functions

- `create_user(session, email=None, name=None, external_id=None) -> User`: Create a new user
- `get_user_by_id(session, user_id) -> Optional[User]`: Get user by ID
- `get_user_by_email(session, email) -> Optional[User]`: Get user by email
- `get_user_by_external_id(session, external_id) -> Optional[User]`: Get user by external ID
- `get_or_create_user_by_external_id(session, external_id, email=None, name=None) -> tuple[User, bool]`: Get or create user by external ID
- `list_users(session, limit=100, offset=0) -> List[User]`: List all users with pagination
- `update_user(session, user_id, email=None, name=None) -> Optional[User]`: Update user information
- `delete_user(session, user_id) -> bool`: Delete a user and all associated conversations

**Example:**
```python
from database.repository import create_user, get_user_by_email
from database.db_config import get_session

with get_session() as session:
    user = create_user(session, email="user@example.com", name="John Doe")
    retrieved = get_user_by_email(session, "user@example.com")
```

#### Conversation Functions

- `create_conversation(session, user_id=None, title=None, status="active") -> Conversation`: Create a new conversation
- `get_conversation_by_id(session, conversation_id) -> Optional[Conversation]`: Get conversation by ID
- `list_conversations_for_user(session, user_id, status=None, limit=100, offset=0) -> List[Conversation]`: List conversations for a user
- `list_all_conversations(session, status=None, limit=100, offset=0) -> List[Conversation]`: List all conversations
- `update_conversation(session, conversation_id, title=None, status=None) -> Optional[Conversation]`: Update conversation
- `archive_conversation(session, conversation_id) -> Optional[Conversation]`: Archive a conversation
- `delete_conversation(session, conversation_id) -> bool`: Delete a conversation and all associated messages

**Example:**
```python
from database.repository import create_conversation, list_conversations_for_user

with get_session() as session:
    conv = create_conversation(session, user_id=user.id, title="Test Chat")
    user_convs = list_conversations_for_user(session, user.id, status="active")
```

#### Message Functions

- `add_message(session, conversation_id, sender_type, content, role_metadata=None) -> Message`: Add a message to a conversation
- `get_message_by_id(session, message_id) -> Optional[Message]`: Get message by ID
- `list_messages_for_conversation(session, conversation_id, limit=100, offset=0, sender_type=None) -> List[Message]`: List messages for a conversation
- `get_conversation_message_count(session, conversation_id) -> int`: Get total message count for a conversation
- `delete_message(session, message_id) -> bool`: Delete a message

**Example:**
```python
from database.repository import add_message, list_messages_for_conversation
from database.models import MessageSenderType

with get_session() as session:
    msg = add_message(
        session,
        conversation_id=conv.id,
        sender_type=MessageSenderType.USER,
        content="Hello!",
        role_metadata={"tokens": 5}
    )
    messages = list_messages_for_conversation(session, conv.id)
```

#### KnowledgeChunk Functions

- `upsert_knowledge_chunk(session, source, content, external_id=None, title=None, chunk_metadata=None) -> KnowledgeChunk`: Insert or update a knowledge chunk
- `get_knowledge_chunk_by_id(session, chunk_id) -> Optional[KnowledgeChunk]`: Get knowledge chunk by ID
- `get_knowledge_chunk_by_external_id(session, external_id, source=None) -> Optional[KnowledgeChunk]`: Get knowledge chunk by external ID
- `search_knowledge_chunks_by_source(session, source, limit=100, offset=0) -> List[KnowledgeChunk]`: Search knowledge chunks by source
- `list_all_knowledge_chunks(session, limit=100, offset=0) -> List[KnowledgeChunk]`: List all knowledge chunks
- `bulk_upsert_knowledge_chunks(session, chunks) -> List[KnowledgeChunk]`: Bulk upsert knowledge chunks
- `delete_knowledge_chunk(session, chunk_id) -> bool`: Delete a knowledge chunk

**Example:**
```python
from database.repository import upsert_knowledge_chunk, bulk_upsert_knowledge_chunks

with get_session() as session:
    chunk = upsert_knowledge_chunk(
        session,
        source="enhanced_readme",
        external_id="section_1",
        title="Installation",
        content="Installation instructions...",
        chunk_metadata={"section_type": "installation"}
    )
    
    # Bulk upsert
    chunks = [
        {"source": "docs", "content": "Content 1", "external_id": "doc1"},
        {"source": "docs", "content": "Content 2", "external_id": "doc2"}
    ]
    bulk_upsert_knowledge_chunks(session, chunks)
```

## Alembic Migrations

Alembic is used for database migrations. The configuration is in `alembic.ini` (project root) and `database/migrations/env.py`.

### Setup

1. **Initialize Alembic** (already done):
   ```bash
   alembic init database/migrations
   ```

2. **Configure `alembic.ini`**:
   - Set `script_location = database/migrations`
   - The `sqlalchemy.url` in `alembic.ini` is ignored (we use `db_config.py`)

3. **Configure `database/migrations/env.py`**:
   - Imports `get_engine` from `db_config`
   - Imports `Base.metadata` from `models`
   - Uses application's engine and metadata for migrations

### Migration Commands

**Create a new migration:**
```bash
alembic revision --autogenerate -m "description_of_changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback one migration:**
```bash
alembic downgrade -1
```

**View current migration status:**
```bash
alembic current
```

**View migration history:**
```bash
alembic history
```

### Initial Schema Migration

The initial schema migration (`8678818e71a3_initial_schema.py`) creates all tables:
- `users`
- `conversations`
- `messages`
- `knowledge_chunks`

With all indexes, foreign keys, and constraints.

## Testing

### Test Script: `database/tests/test_database.py`

Comprehensive end-to-end test script that verifies:
1. **User Operations**: Create, retrieve, update, delete users
2. **Conversation Operations**: Create, list, update, archive conversations
3. **Message Operations**: Add, retrieve, list messages
4. **KnowledgeChunk Operations**: Upsert, retrieve, search chunks
5. **Relationships**: User-Conversation and Conversation-Message relationships
6. **Cascade Deletes**: Verify cascading deletes work correctly
7. **Edge Cases**: Non-existent records, empty pagination, etc.

**Running Tests:**
```bash
cd /Users/tanzimfarhan/Desktop/Maveric/maveric-minipilot
python database/tests/test_database.py
```

**Test Coverage:**
- All CRUD operations for each model
- Relationship queries
- Cascade delete behavior
- Pagination
- Filtering and searching
- Edge cases and error handling

**Example Output:**
```
============================================================
DATABASE LAYER END-TO-END TESTS
============================================================

============================================================
RESETTING DATABASE
============================================================
✓ Database reset complete

============================================================
TEST 1: User Operations
============================================================
...
✓ All tests passed
```

## Quick Start Guide

1. **Set up environment variables** (optional, defaults to SQLite):
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/maveric_minipilot"
   # OR
   export DB_HOST=localhost
   export DB_NAME=maveric_minipilot
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   ```

2. **Initialize database**:
   ```bash
   python -c "from database.db_config import init_db; init_db()"
   ```

3. **Run migrations** (if using Alembic):
   ```bash
   alembic upgrade head
   ```

4. **Run tests**:
   ```bash
   python database/tests/test_database.py
   ```

5. **Use in your code**:
   ```python
   from database.db_config import get_session
   from database.repository import create_user, create_conversation, add_message
   from database.models import MessageSenderType
   
   with get_session() as session:
       user = create_user(session, email="user@example.com", name="John")
       conv = create_conversation(session, user_id=user.id, title="Chat")
       msg = add_message(
           session,
           conversation_id=conv.id,
           sender_type=MessageSenderType.USER,
           content="Hello!"
       )
   ```

## Troubleshooting

### SQLAlchemy Errors

**Issue**: `Attribute name 'metadata' is reserved`
- **Solution**: Use `chunk_metadata` instead of `metadata` in KnowledgeChunk model

**Issue**: `DetachedInstanceError`
- **Solution**: Always use objects within the same session context, or pass UUIDs between functions

### SQLite Issues

**Issue**: `check_same_thread` error
- **Solution**: Already handled in `db_config.py` with `check_same_thread=False`

**Issue**: Database file not found
- **Solution**: Ensure `data/` directory exists, or set `DB_PATH` environment variable

### PostgreSQL Issues

**Issue**: Connection refused
- **Solution**: Verify PostgreSQL is running and connection details are correct

**Issue**: Database does not exist
- **Solution**: Create database: `CREATE DATABASE maveric_minipilot;`

### Migration Issues

**Issue**: `Target database is not up to date`
- **Solution**: Run `alembic upgrade head`

**Issue**: Migration conflicts
- **Solution**: Review migration history with `alembic history` and resolve conflicts manually

## Dependencies

- `sqlalchemy`: ORM and database toolkit
- `alembic`: Database migration tool
- `psycopg2` or `psycopg2-binary`: PostgreSQL adapter (for PostgreSQL)
- Python 3.8+

## Notes

- All models use UUID primary keys for better distributed system support
- Timestamps are automatically managed via `TimestampMixin`
- Cascade deletes ensure data consistency (deleting a user deletes their conversations, etc.)
- The repository pattern allows for easy testing and transaction management
- SQLite is used by default for development, PostgreSQL for production

