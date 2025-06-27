"""
Database layer for Jeeves AI Assistant using SQLite.
Handles persistence of threads, messages, and conversation history.
Enhanced with durability, migrations, and future-proofing.
"""

import hashlib
import json
import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generator, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

_RetType = TypeVar("_RetType")


class DatabaseError(Exception):
    """Custom database exception."""

    pass


class MessageType(Enum):
    """Message types for extensibility."""

    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class DatabaseManager:
    """Manages SQLite database operations for the Jeeves AI Assistant."""

    def __init__(self, db_path: str = "jeeves.db", max_retries: int = 3, timeout: float = 30.0):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.timeout = timeout
        self._lock = threading.RLock()
        self._connection_pool: dict[int, sqlite3.Connection] = {}
        self._migrations_applied = False

        # Initialize database with migrations
        self._init_database()
        self._apply_migrations()

    def _init_database(self) -> None:
        """Initialize the database with required tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Enable foreign keys and WAL mode for better performance and
            # durability
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = 10000")
            cursor.execute("PRAGMA temp_store = MEMORY")

            # Create threads table with enhanced fields
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    icon TEXT,
                    description TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    is_archived BOOLEAN DEFAULT 0,
                    metadata TEXT,
                    settings TEXT,
                    UNIQUE(name, created_at)
                )
            """
            )

            # Create messages table with flexible sender field and enhanced
            # structure
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    edited_at TIMESTAMP,
                    is_edited BOOLEAN DEFAULT 0,
                    metadata TEXT,
                    attachments TEXT,
                    parent_message_id INTEGER,
                    reply_to_message_id INTEGER,
                    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_message_id) REFERENCES messages (id) ON DELETE SET NULL,
                    FOREIGN KEY (reply_to_message_id) REFERENCES messages (id) ON DELETE SET NULL
                )
            """
            )

            # Create attachments table for file handling
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    mime_type TEXT,
                    hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
                )
            """
            )

            # Create user_settings table for user preferences
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT,
                    value_type TEXT DEFAULT 'string',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create conversation_analytics table for insights
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER NOT NULL,
                    analytics_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
                )
            """
            )

            # Create search_index table for full-text search
            cursor.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
                    message_id,
                    content,
                    sender,
                    timestamp,
                    thread_id
                )
            """
            )

            # Create indexes for better performance
            self._create_indexes(cursor)

            conn.commit()
            logger.info("Database initialized successfully")

    def _create_indexes(self, cursor: sqlite3.Cursor) -> None:
        """Create database indexes for performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages (thread_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages (sender)",
            "CREATE INDEX IF NOT EXISTS idx_messages_parent ON messages (parent_message_id)",
            "CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON threads (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_threads_last_activity ON threads (last_activity)",
            "CREATE INDEX IF NOT EXISTS idx_threads_is_active ON threads (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_message_id ON attachments (message_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_thread_type ON conversation_analytics (thread_id, analytics_type)",
            "CREATE INDEX IF NOT EXISTS idx_settings_key ON user_settings (key)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

    def _apply_migrations(self) -> None:
        """Apply database migrations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get applied migrations
            applied_migrations = set()
            try:
                cursor.execute("SELECT name FROM migrations")
                for row in cursor.fetchall():
                    applied_migrations.add(row[0])
            except sqlite3.OperationalError:
                # Migrations table doesn't exist yet, which is fine
                pass

            # Find and apply new migrations
            migrations_path = Path(__file__).parent / "migrations"
            if migrations_path.exists():
                for migration_file in sorted(migrations_path.glob("*.sql")):
                    migration_name = migration_file.name
                    if migration_name not in applied_migrations:
                        logger.info(f"Applying migration: {migration_name}")

                        with open(migration_file, "r") as f:
                            cursor.executescript(f.read())

                        # Record migration
                        checksum = hashlib.sha256(migration_name.encode()).hexdigest()
                        cursor.execute(
                            "INSERT INTO migrations (name, applied_at, checksum) VALUES (?, CURRENT_TIMESTAMP, ?)",
                            (migration_name, checksum),
                        )
                        conn.commit()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections with retry logic."""
        thread_id = threading.get_ident()

        # Check if we have a connection for this thread
        if thread_id in self._connection_pool:
            conn = self._connection_pool[thread_id]
            try:
                # Test if connection is still valid
                conn.execute("SELECT 1")
                yield conn
                return
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Connection is invalid, remove it
                del self._connection_pool[thread_id]

        # Create new connection with retry logic
        for attempt in range(self.max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=self.timeout, check_same_thread=False)
                conn.row_factory = sqlite3.Row

                # Configure connection for better performance and durability
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")

                # Store connection for this thread
                self._connection_pool[thread_id] = conn

                try:
                    yield conn
                finally:
                    # Don't close the connection, keep it in the pool
                    pass

                return

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < self.max_retries - 1:
                    wait_time = (2**attempt) * 0.1  # Exponential backoff
                    logger.warning(f"Database locked, retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise DatabaseError(f"Database operation failed: {e}")
            except Exception as e:
                raise DatabaseError(f"Database connection failed: {e}")

        raise DatabaseError("Failed to connect to database after maximum retries")

    def _execute_with_retry(self, operation: Callable[..., _RetType], *args: Any, **kwargs: Any) -> _RetType:
        """Execute database operation with retry logic."""
        for attempt in range(self.max_retries):
            try:
                with self._lock:
                    return operation(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < self.max_retries - 1:
                    wait_time = (2**attempt) * 0.1
                    logger.warning(f"Database locked, retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise DatabaseError(f"Database operation failed: {e}")
            except Exception as e:
                raise DatabaseError(f"Database operation failed: {e}")

        raise DatabaseError("Failed to execute database operation after maximum retries")

    def create_thread(
        self,
        name: str,
        icon: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        settings: Optional[dict] = None,
    ) -> int:
        """
        Create a new conversation thread.

        Args:
            name: Thread name
            icon: Thread icon (optional)
            description: Thread description (optional)
            tags: list of tags (optional)
            metadata: Additional metadata (optional)
            settings: Thread-specific settings (optional)

        Returns:
            Thread ID
        """

        def _create() -> int:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO threads (name, icon, description, tags, metadata, settings,
                                       created_at, updated_at, last_activity)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    (
                        name,
                        icon,
                        description,
                        json.dumps(tags) if tags else None,
                        json.dumps(metadata) if metadata else None,
                        json.dumps(settings) if settings else None,
                    ),
                )
                thread_id_raw = cursor.lastrowid
                if thread_id_raw is None:
                    raise DatabaseError("Failed to retrieve thread ID after insertion.")
                thread_id: int = thread_id_raw
                conn.commit()
                return thread_id

        thread_id = self._execute_with_retry(_create)
        logger.info(f"Created thread: {name} (ID: {thread_id})")
        return thread_id

    def get_threads(
        self,
        active_only: bool = True,
        include_archived: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[dict]:
        """
        Get all threads with enhanced filtering.

        Args:
            active_only: Only return active threads
            include_archived: Include archived threads
            limit: Maximum number of threads
            offset: Number of threads to skip

        Returns:
            List of thread dictionaries
        """

        def _get() -> list[dict]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Use parameterized queries to prevent SQL injection
                where_conditions: list[str] = []
                params: list[Union[str, int]] = []

                if active_only:
                    where_conditions.append("is_active = ?")
                    params.append(1)

                if not include_archived:
                    where_conditions.append("is_archived = ?")
                    params.append(0)

                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

                query = f"""
                    SELECT id, name, icon, description, tags, created_at, updated_at,
                           last_activity, is_active, is_archived, metadata, settings
                    FROM threads
                    WHERE {where_clause}
                    ORDER BY last_activity DESC
                """  # nosec B608

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                if offset:
                    query += " OFFSET ?"
                    params.append(offset)

                cursor.execute(query, params)

                threads: list[dict] = []
                for row in cursor.fetchall():
                    threads.append(
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "icon": row["icon"],
                            "description": row["description"],
                            "tags": json.loads(row["tags"]) if row["tags"] else [],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"],
                            "last_activity": row["last_activity"],
                            "is_active": bool(row["is_active"]),
                            "is_archived": bool(row["is_archived"]),
                            "metadata": (json.loads(row["metadata"]) if row["metadata"] else {}),
                            "settings": (json.loads(row["settings"]) if row["settings"] else {}),
                        }
                    )

                return threads

        return self._execute_with_retry(_get)

    def get_thread_message_counts(self) -> dict[int, int]:
        """
        Get message counts for all threads.

        Returns:
            Dictionary mapping thread_id to message count
        """

        def _get_counts() -> dict[int, int]:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT thread_id, COUNT(*) as message_count
                    FROM messages
                    GROUP BY thread_id
                """
                )

                counts: dict[int, int] = {}
                for row in cursor.fetchall():
                    counts[row["thread_id"]] = row["message_count"]

                return counts

        return self._execute_with_retry(_get_counts)

    def get_thread(self, thread_id: int) -> Optional[dict]:
        """
        Get a specific thread by ID.

        Args:
            thread_id: Thread ID

        Returns:
            Thread dictionary or None if not found
        """

        def _get() -> Optional[dict]:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, name, icon, description, tags, created_at, updated_at,
                           last_activity, is_active, is_archived, metadata, settings
                    FROM threads
                    WHERE id = ?
                """,
                    (thread_id,),
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "id": row["id"],
                        "name": row["name"],
                        "icon": row["icon"],
                        "description": row["description"],
                        "tags": json.loads(row["tags"]) if row["tags"] else [],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "last_activity": row["last_activity"],
                        "is_active": bool(row["is_active"]),
                        "is_archived": bool(row["is_archived"]),
                        "metadata": (json.loads(row["metadata"]) if row["metadata"] else {}),
                        "settings": (json.loads(row["settings"]) if row["settings"] else {}),
                    }
                return None

        return self._execute_with_retry(_get)

    def find_threads_by_name(self, name: str, active_only: bool = True) -> list[dict]:
        """
        Find threads by name (case-insensitive partial match).

        Args:
            name: Thread name to search for
            active_only: Only search active threads

        Returns:
            List of matching thread dictionaries
        """

        def _find() -> list[dict]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                where_conditions: list[str] = ["LOWER(name) LIKE LOWER(?)"]
                params: list[Union[str, int]] = [f"%{name}%"]

                if active_only:
                    where_conditions.append("is_active = ?")
                    params.append(1)

                where_clause = " AND ".join(where_conditions)

                query = (
                    "SELECT id, name, icon, description, tags, created_at, updated_at, "
                    "last_activity, is_active, is_archived, metadata, settings "
                    "FROM threads "
                    "WHERE " + where_clause + " "  # nosec B608
                    "ORDER BY last_activity DESC"
                )
                cursor.execute(query, params)

                threads: list[dict] = []
                for row in cursor.fetchall():
                    threads.append(
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "icon": row["icon"],
                            "description": row["description"],
                            "tags": json.loads(row["tags"]) if row["tags"] else [],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"],
                            "last_activity": row["last_activity"],
                            "is_active": bool(row["is_active"]),
                            "is_archived": bool(row["is_archived"]),
                            "metadata": (json.loads(row["metadata"]) if row["metadata"] else {}),
                            "settings": (json.loads(row["settings"]) if row["settings"] else {}),
                        }
                    )

                return threads

        return self._execute_with_retry(_find)

    def update_thread(self, thread_id: int, **kwargs: Any) -> bool:
        """
        Update a thread with the given key-value arguments.

        Args:
            thread_id: Thread ID
            kwargs: Key-value pairs to update

        Returns:
            True if successful
        """

        def _update() -> bool:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Whitelist of allowed columns to prevent SQL injection
                allowed_columns = [
                    "name",
                    "icon",
                    "description",
                    "tags",
                    "is_active",
                    "is_archived",
                    "metadata",
                    "settings",
                ]

                updates: list[str] = []
                params: list[Any] = []

                for key, value in kwargs.items():
                    if key in allowed_columns:
                        updates.append(f"{key} = ?")
                        params.append(json.dumps(value) if isinstance(value, (dict, list)) else value)

                if not updates:
                    return False

                params.append(thread_id)

                # Construct the query safely
                query = f"UPDATE threads SET {', '.join(updates)} WHERE id = ?"  # nosec B608
                cursor.execute(query, params)

                conn.commit()
                return cursor.rowcount > 0

        return self._execute_with_retry(_update)

    def delete_thread(self, thread_id: int, soft_delete: bool = True) -> bool:
        """
        Delete a thread.

        Args:
            thread_id: Thread ID
            soft_delete: If True, mark as archived instead of hard delete

        Returns:
            True if deleted successfully
        """

        def _delete() -> bool:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if soft_delete:
                    cursor.execute(
                        """
                        UPDATE threads
                        SET is_active = 0, is_archived = 1, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """,
                        (thread_id,),
                    )
                else:
                    cursor.execute("DELETE FROM threads WHERE id = ?", (thread_id,))

                conn.commit()
                return cursor.rowcount > 0

        success = self._execute_with_retry(_delete)
        if success:
            logger.info(f"{'Soft deleted' if soft_delete else 'Deleted'} thread {thread_id}")
        return success

    def add_message(
        self,
        thread_id: int,
        sender: str,
        content: str,
        content_type: str = "text",
        metadata: Optional[dict] = None,
        attachments: Optional[list[dict]] = None,
        parent_message_id: Optional[int] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> int:
        """
        Add a message to a thread with enhanced features.

        Args:
            thread_id: Thread ID
            sender: Message sender (any string)
            content: Message content
            content_type: Type of content ('text', 'image', 'file', etc.)
            metadata: Additional metadata
            attachments: list of attachment dictionaries
            parent_message_id: Parent message ID for threading
            reply_to_message_id: Message being replied to

        Returns:
            Message ID
        """

        def _add() -> int:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Add message
                cursor.execute(
                    """
                    INSERT INTO messages (thread_id, sender, content, content_type,
                                        metadata, parent_message_id, reply_to_message_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (
                        thread_id,
                        sender,
                        content,
                        content_type,
                        json.dumps(metadata) if metadata else None,
                        parent_message_id,
                        reply_to_message_id,
                    ),
                )

                message_id_raw = cursor.lastrowid
                if message_id_raw is None:
                    raise DatabaseError("Failed to retrieve message ID after insertion.")
                message_id: int = message_id_raw

                # Add attachments if provided
                if attachments:
                    for attachment in attachments:
                        cursor.execute(
                            """
                            INSERT INTO attachments (message_id, file_name, file_path,
                                                   file_size, mime_type, hash)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (
                                message_id,
                                attachment.get("file_name"),
                                attachment.get("file_path"),
                                attachment.get("file_size"),
                                attachment.get("mime_type"),
                                attachment.get("hash"),
                            ),
                        )

                # Update thread's last activity
                cursor.execute(
                    """
                    UPDATE threads
                    SET last_activity = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (thread_id,),
                )

                # Update search index
                cursor.execute(
                    """
                    INSERT INTO search_index (message_id, content, sender, timestamp, thread_id)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
                """,
                    (message_id, content, sender, thread_id),
                )

                conn.commit()
                return message_id

        message_id = self._execute_with_retry(_add)
        logger.info(f"Added message to thread {thread_id}: {sender}")
        return message_id

    def get_messages(
        self,
        thread_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        include_attachments: bool = True,
    ) -> list[dict]:
        """
        Get messages for a thread with enhanced options.

        Args:
            thread_id: Thread ID
            limit: Maximum number of messages
            offset: Number of messages to skip
            include_attachments: Include attachment data

        Returns:
            List of message dictionaries
        """

        def _get() -> list[dict]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT m.id, m.thread_id, m.sender, m.content, m.content_type,
                           m.timestamp, m.edited_at, m.is_edited, m.metadata,
                           m.parent_message_id, m.reply_to_message_id
                    FROM messages m
                    WHERE m.thread_id = ?
                    ORDER BY m.timestamp ASC
                """

                params: list[int] = [thread_id]

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                if offset:
                    query += " OFFSET ?"
                    params.append(offset)

                cursor.execute(query, params)

                messages: list[dict] = []
                for row in cursor.fetchall():
                    message: dict = {
                        "id": row["id"],
                        "thread_id": row["thread_id"],
                        "sender": row["sender"],
                        "content": row["content"],
                        "content_type": row["content_type"],
                        "timestamp": row["timestamp"],
                        "edited_at": row["edited_at"],
                        "is_edited": bool(row["is_edited"]),
                        "metadata": (json.loads(row["metadata"]) if row["metadata"] else None),
                        "parent_message_id": row["parent_message_id"],
                        "reply_to_message_id": row["reply_to_message_id"],
                        "attachments": [],
                    }

                    # Get attachments if requested
                    if include_attachments:
                        cursor.execute(
                            """
                            SELECT id, file_name, file_path, file_size, mime_type, hash
                            FROM attachments
                            WHERE message_id = ?
                        """,
                            (row["id"],),
                        )

                        for att_row in cursor.fetchall():
                            logger.debug(f"Adding attachment {att_row['id']} to message {row['id']}\n {att_row['file_name']}")
                            message["attachments"].append(
                                {
                                    "id": att_row["id"],
                                    "file_name": att_row["file_name"],
                                    "file_path": att_row["file_path"],
                                    "file_size": att_row["file_size"],
                                    "mime_type": att_row["mime_type"],
                                    "hash": att_row["hash"],
                                }
                            )

                    logger.debug(f"Retrieved message: {message['id']} from thread {thread_id}")
                    messages.append(message)

                return messages

        return self._execute_with_retry(_get)

    def search_messages(
        self,
        query: str,
        thread_id: Optional[int] = None,
        limit: int = 50,
        include_attachments: bool = False,
    ) -> list[dict]:
        """
        Search messages using full-text search.

        Args:
            query: Search query
            thread_id: Limit search to specific thread (optional)
            limit: Maximum number of results
            include_attachments: Include attachment data

        Returns:
            List of matching messages
        """

        def _search() -> list[dict]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                sql_query = """
                    SELECT m.id, m.thread_id, m.sender, m.content, m.content_type,
                           m.timestamp, m.edited_at, m.is_edited, m.metadata,
                           t.name as thread_name,
                           rank
                    FROM search_index s
                    JOIN messages m ON s.message_id = m.id
                    JOIN threads t ON m.thread_id = t.id
                    WHERE s.content MATCH ?
                """
                params = [query]

                if thread_id:
                    sql_query += " AND m.thread_id = ?"
                    params.append(str(thread_id))

                sql_query += " ORDER BY rank LIMIT ?"
                params.append(str(limit))

                cursor.execute(sql_query, params)

                messages: list[dict] = []
                for row in cursor.fetchall():
                    message: dict = {
                        "id": row["id"],
                        "thread_id": row["thread_id"],
                        "sender": row["sender"],
                        "content": row["content"],
                        "content_type": row["content_type"],
                        "timestamp": row["timestamp"],
                        "edited_at": row["edited_at"],
                        "is_edited": bool(row["is_edited"]),
                        "metadata": (json.loads(row["metadata"]) if row["metadata"] else None),
                        "thread_name": row["thread_name"],
                        "rank": row["rank"],
                        "attachments": [],
                    }

                    if include_attachments:
                        cursor.execute(
                            """
                            SELECT id, file_name, file_path, file_size, mime_type, hash
                            FROM attachments
                            WHERE message_id = ?
                        """,
                            (row["id"],),
                        )

                        for att_row in cursor.fetchall():
                            message["attachments"].append(
                                {
                                    "id": att_row["id"],
                                    "file_name": att_row["file_name"],
                                    "file_path": att_row["file_path"],
                                    "file_size": att_row["file_size"],
                                    "mime_type": att_row["mime_type"],
                                    "hash": att_row["hash"],
                                }
                            )

                    messages.append(message)

                return messages

        return self._execute_with_retry(_search)

    def update_message(
        self,
        message_id: int,
        content: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Update a message with new content or metadata.

        Args:
            message_id: Message ID
            content: New message content (optional)
            metadata: New metadata (optional)

        Returns:
            True if successful
        """

        def _update() -> bool:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                updates: list[str] = []
                params: list[Any] = []

                if content is not None:
                    updates.append("content = ?")
                    params.append(content)

                if metadata is not None:
                    updates.append("metadata = ?")
                    params.append(json.dumps(metadata))

                if not updates:
                    return False

                params.append(message_id)

                # Construct the query safely
                query = f"UPDATE messages SET {', '.join(updates)} WHERE id = ?"  # nosec B608
                cursor.execute(query, params)

                conn.commit()
                return cursor.rowcount > 0

        return self._execute_with_retry(_update)

    def get_user_settings(self, key: Optional[str] = None) -> Union[dict, Any]:
        """
        Get user settings.

        Args:
            key: Specific setting key (optional)

        Returns:
            Setting value or all settings
        """

        def _get() -> Union[dict, Any]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if key:
                    cursor.execute(
                        """
                        SELECT key, value, value_type, description
                        FROM user_settings
                        WHERE key = ?
                    """,
                        (key,),
                    )

                    row = cursor.fetchone()
                    if row:
                        value = row["value"]
                        if row["value_type"] == "json":
                            return json.loads(value) if value else None
                        elif row["value_type"] == "int":
                            return int(value) if value else 0
                        elif row["value_type"] == "float":
                            return float(value) if value else 0.0
                        elif row["value_type"] == "bool":
                            return value.lower() == "true" if value else False
                        else:
                            return value
                    return None
                else:
                    cursor.execute(
                        """
                        SELECT key, value, value_type, description
                        FROM user_settings
                        ORDER BY key
                    """
                    )

                    settings: dict[str, Any] = {}
                    for row in cursor.fetchall():
                        value = row["value"]
                        if row["value_type"] == "json":
                            settings[row["key"]] = json.loads(value) if value else None
                        elif row["value_type"] == "int":
                            settings[row["key"]] = int(value) if value else 0
                        elif row["value_type"] == "float":
                            settings[row["key"]] = float(value) if value else 0.0
                        elif row["value_type"] == "bool":
                            settings[row["key"]] = value.lower() == "true" if value else False
                        else:
                            settings[row["key"]] = value

                    return settings

        return self._execute_with_retry(_get)

    def set_user_setting(
        self,
        key: str,
        value: Any,
        value_type: str = "string",
        description: Optional[str] = None,
    ) -> bool:
        """
        Set a user setting.

        Args:
            key: Setting key
            value: Setting value
            value_type: Type of value ('string', 'int', 'float', 'bool', 'json')
            description: Setting description

        Returns:
            True if set successfully
        """

        def _set() -> bool:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Convert value to string for storage
                if value_type == "json":
                    str_value = json.dumps(value) if value else None
                else:
                    str_value = str(value) if value is not None else None

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_settings (key, value, value_type, description, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (key, str_value, value_type, description),
                )

                conn.commit()
                return True

        success = self._execute_with_retry(_set)
        if success:
            logger.info(f"Set user setting: {key}")
        return success

    def add_analytics(self, thread_id: int, analytics_type: str, data: dict) -> int:
        """
        Add conversation analytics data.

        Args:
            thread_id: Thread ID
            analytics_type: Type of analytics
            data: Analytics data

        Returns:
            Analytics record ID
        """

        def _add() -> int:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO conversation_analytics (thread_id, analytics_type, data)
                    VALUES (?, ?, ?)
                """,
                    (thread_id, analytics_type, json.dumps(data)),
                )

                analytics_id_raw = cursor.lastrowid
                if analytics_id_raw is None:
                    raise DatabaseError("Failed to retrieve analytics ID after insertion.")
                analytics_id: int = analytics_id_raw
                conn.commit()
                return analytics_id

        analytics_id = self._execute_with_retry(_add)
        logger.info(f"Added analytics for thread {thread_id}: {analytics_type}")
        return analytics_id

    def get_analytics(self, thread_id: int, analytics_type: Optional[str] = None) -> list[dict]:
        """
        Get conversation analytics.

        Args:
            thread_id: Thread ID
            analytics_type: Specific analytics type (optional)

        Returns:
            List of analytics records
        """

        def _get() -> list[dict]:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if analytics_type:
                    cursor.execute(
                        """
                        SELECT id, thread_id, analytics_type, data, created_at
                        FROM conversation_analytics
                        WHERE thread_id = ? AND analytics_type = ?
                        ORDER BY created_at DESC
                    """,
                        (thread_id, analytics_type),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, thread_id, analytics_type, data, created_at
                        FROM conversation_analytics
                        WHERE thread_id = ?
                        ORDER BY created_at DESC
                    """,
                        (thread_id,),
                    )

                analytics: list[dict] = []
                for row in cursor.fetchall():
                    analytics.append(
                        {
                            "id": row["id"],
                            "thread_id": row["thread_id"],
                            "analytics_type": row["analytics_type"],
                            "data": json.loads(row["data"]),
                            "created_at": row["created_at"],
                        }
                    )

                return analytics

        return self._execute_with_retry(_get)

    def get_database_stats(self) -> dict:
        """
        Get comprehensive database statistics.

        Returns:
            Dictionary with database statistics
        """

        def _get_stats() -> dict:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get thread counts
                cursor.execute("SELECT COUNT(*) FROM threads WHERE is_active = 1")
                active_threads: int = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM threads")
                total_threads: int = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM threads WHERE is_archived = 1")
                archived_threads: int = cursor.fetchone()[0]

                # Get message counts
                cursor.execute("SELECT COUNT(*) FROM messages")
                total_messages: int = cursor.fetchone()[0]

                cursor.execute("SELECT sender, COUNT(*) FROM messages GROUP BY sender")
                sender_counts: dict[str, int] = dict(cursor.fetchall())

                # Get attachment counts
                cursor.execute("SELECT COUNT(*) FROM attachments")
                total_attachments: int = cursor.fetchone()[0]

                # Get analytics counts
                cursor.execute("SELECT COUNT(*) FROM conversation_analytics")
                total_analytics: int = cursor.fetchone()[0]

                # Get database size
                db_size: int = self.db_path.stat().st_size if self.db_path.exists() else 0

                # Get WAL file size
                wal_size: int = 0
                wal_path = self.db_path.with_suffix(".db-wal")
                if wal_path.exists():
                    wal_size = wal_path.stat().st_size

                return {
                    "active_threads": active_threads,
                    "total_threads": total_threads,
                    "archived_threads": archived_threads,
                    "total_messages": total_messages,
                    "sender_breakdown": sender_counts,
                    "total_attachments": total_attachments,
                    "total_analytics": total_analytics,
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / (1024 * 1024), 2),
                    "wal_size_bytes": wal_size,
                    "wal_size_mb": round(wal_size / (1024 * 1024), 2),
                    "total_size_mb": round((db_size + wal_size) / (1024 * 1024), 2),
                }

        return self._execute_with_retry(_get_stats)

    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.

        Args:
            backup_path: Path for the backup file

        Returns:
            True if backup successful
        """
        try:
            import shutil

            # Ensure WAL mode is properly handled
            with self._get_connection() as conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")

            # Wait a moment for WAL to be checkpointed
            time.sleep(0.1)

            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False

    def cleanup_old_messages(self, days_old: int = 30) -> int:
        """
        Delete messages older than a certain number of days.

        Args:
            days_old: Age of messages to delete

        Returns:
            Number of deleted messages
        """

        def _cleanup() -> int:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM messages
                    WHERE timestamp < datetime('now', ?)
                """,
                    (f"-{days_old} days",),
                )

                deleted_count: int = cursor.rowcount
                conn.commit()
                return deleted_count

        deleted_count = self._execute_with_retry(_cleanup)
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old messages")
        return deleted_count

    def vacuum_database(self) -> bool:
        """
        Vacuum the database to reclaim space and optimize performance.

        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            return False

    def close_connections(self) -> None:
        """Close all active database connections."""
        with self._lock:
            for conn in list(self._connection_pool.values()):  # Iterate over a copy
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Failed to close a database connection: {e}")
            self._connection_pool.clear()
        logger.info("All database connections closed")
