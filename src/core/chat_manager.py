"""
Chat manager for handling conversation state and message flow.
Integrates with the database for persistence.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Optional

from .database import DatabaseError, DatabaseManager

logger = logging.getLogger(__name__)


class ChatManager:
    """Manages chat conversations and integrates with the database."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_thread_id: Optional[int] = None
        self.message_callbacks: list[Callable[[dict], None]] = []
        self.thread_callbacks: list[Callable[[dict], None]] = []

        # Initialize with default thread if none exists
        self._ensure_default_thread()

    def _ensure_default_thread(self) -> None:
        """Ensure there's at least one default thread."""
        try:
            threads = self.db.get_threads()
            if not threads:
                self.create_thread("New Chat", "💬")
                logger.info("Created default thread")
        except DatabaseError as e:
            logger.error(f"Failed to ensure default thread: {e}")

    def register_message_callback(self, callback: Callable[[dict], None]) -> None:
        """Register a callback to be called when messages are added."""
        self.message_callbacks.append(callback)

    def register_thread_callback(self, callback: Callable[[dict], None]) -> None:
        """Register a callback to be called when threads are modified."""
        self.thread_callbacks.append(callback)

    def _notify_message_callbacks(self, message: dict) -> None:
        """Notify all registered message callbacks."""
        for callback in self.message_callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")

    def _notify_thread_callbacks(self, thread: dict) -> None:
        """Notify all registered thread callbacks."""
        for callback in self.thread_callbacks:
            try:
                callback(thread)
            except Exception as e:
                logger.error(f"Error in thread callback: {e}")

    def create_thread(
        self,
        name: str,
        icon: str = "💬",
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        settings: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Create a new conversation thread.

        Args:
            name: Thread name
            icon: Thread icon
            description: Thread description (optional)
            tags: list of tags (optional)
            metadata: Additional metadata (optional)
            settings: Thread-specific settings (optional)

        Returns:
            Thread ID
        """
        try:
            thread_id = self.db.create_thread(name, icon, description, tags, metadata, settings)
            thread = self.db.get_thread(thread_id)

            if thread:
                self._notify_thread_callbacks(thread)

            return thread_id
        except DatabaseError as e:
            logger.error(f"Failed to create thread: {e}")
            raise

    def get_threads(
        self,
        active_only: bool = True,
        include_archived: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get all active threads."""
        try:
            return self.db.get_threads(active_only, include_archived, limit, offset)
        except DatabaseError as e:
            logger.error(f"Failed to get threads: {e}")
            return []

    def get_thread(self, thread_id: int) -> Optional[dict[str, Any]]:
        """Get a specific thread."""
        try:
            return self.db.get_thread(thread_id)
        except DatabaseError as e:
            logger.error(f"Failed to get thread {thread_id}: {e}")
            return None

    def find_threads_by_name(self, name: str, active_only: bool = True) -> list[dict[str, int]]:
        """
        Find threads by name (case-insensitive partial match).

        Args:
            name: Thread name to search for
            active_only: Only search active threads

        Returns:
            List of matching thread dictionaries
        """
        try:
            return self.db.find_threads_by_name(name, active_only)
        except DatabaseError as e:
            logger.error(f"Failed to find threads by name '{name}': {e}")
            return []

    def switch_thread(self, thread_id: int) -> bool:
        """
        Switch to a different thread.

        Args:
            thread_id: Thread ID to switch to

        Returns:
            True if successful
        """
        try:
            thread = self.db.get_thread(thread_id)
            if thread:
                self.current_thread_id = thread_id
                logger.info(f"Switched to thread: {thread['name']}")
                return True
            return False
        except DatabaseError as e:
            logger.error(f"Failed to switch to thread {thread_id}: {e}")
            return False

    def get_current_thread(self) -> Optional[dict[str, Any]]:
        """Get the current active thread."""
        if self.current_thread_id:
            return self.get_thread(self.current_thread_id)
        return None

    def get_current_thread_id(self) -> Optional[int]:
        """Get the current thread ID."""
        return self.current_thread_id

    def get_thread_message_counts(self) -> dict[int, int]:
        """
        Get message counts for all threads.

        Returns:
            Dictionary mapping thread_id to message count
        """
        try:
            return self.db.get_thread_message_counts()
        except DatabaseError as e:
            logger.error(f"Failed to get thread message counts: {e}")
            return {}

    def get_messages(
        self,
        thread_id: Optional[int] = None,
        limit: Optional[int] = None,
        include_attachments: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Get messages for a thread.

        Args:
            thread_id: Thread ID (uses current thread if None)
            limit: Maximum number of messages
            include_attachments: Include attachment data

        Returns:
            List of messages
        """
        if thread_id is None:
            thread_id = self.current_thread_id

        if thread_id is None:
            return []

        try:
            return self.db.get_messages(thread_id, limit, include_attachments=include_attachments)
        except DatabaseError as e:
            logger.error(f"Failed to get messages for thread {thread_id}: {e}")
            return []

    def add_user_message(
        self,
        content: str,
        content_type: str = "text",
        metadata: Optional[dict[str, Any]] = None,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> int:
        """
        Add a user message to the current thread.

        Args:
            content: Message content
            content_type: Type of content ('text', 'image', 'file', etc.)
            metadata: Additional metadata
            attachments: list of attachment dictionaries

        Returns:
            Message ID
        """
        if not self.current_thread_id:
            # Create a new thread if none exists
            self.current_thread_id = self.create_thread("New Chat", "💬")

        try:
            message_id = self.db.add_message(
                self.current_thread_id,
                "user",
                content,
                content_type,
                metadata,
                attachments,
            )

            # Get the full message data
            messages = self.db.get_messages(self.current_thread_id, limit=1)
            if messages:
                message = messages[-1]
                self._notify_message_callbacks(message)

            return message_id
        except DatabaseError as e:
            logger.error(f"Failed to add user message: {e}")
            raise

    def add_ai_message(
        self,
        content: str,
        content_type: str = "text",
        metadata: Optional[dict[str, Any]] = None,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> int:
        """
        Add an AI message to the current thread.

        Args:
            content: Message content
            content_type: Type of content ('text', 'image', 'file', etc.)
            metadata: Additional metadata
            attachments: list of attachment dictionaries

        Returns:
            Message ID
        """
        if not self.current_thread_id:
            logger.error("No current thread for AI message")
            return -1

        try:
            message_id = self.db.add_message(
                self.current_thread_id,
                "ai",
                content,
                content_type,
                metadata,
                attachments,
            )

            # Get the full message data
            messages = self.db.get_messages(self.current_thread_id, limit=1)
            if messages:
                message = messages[-1]
                self._notify_message_callbacks(message)

            return message_id
        except DatabaseError as e:
            logger.error(f"Failed to add AI message: {e}")
            raise

    def add_system_message(self, content: str, content_type: str = "text", metadata: Optional[dict[str, Any]] = None) -> int:
        """
        Add a system message to the current thread.

        Args:
            content: Message content
            content_type: Type of content
            metadata: Additional metadata

        Returns:
            Message ID
        """
        if not self.current_thread_id:
            logger.error("No current thread for system message")
            return -1

        try:
            message_id = self.db.add_message(self.current_thread_id, "system", content, content_type, metadata)

            # Get the full message data
            messages = self.db.get_messages(self.current_thread_id, limit=1)
            if messages:
                message = messages[-1]
                self._notify_message_callbacks(message)

            return message_id
        except DatabaseError as e:
            logger.error(f"Failed to add system message: {e}")
            raise

    def update_thread(self, thread_id: int, **kwargs: Any) -> bool:
        """
        Update a thread with flexible field updates.

        Args:
            thread_id: Thread ID
            **kwargs: Fields to update

        Returns:
            True if successful
        """
        try:
            success = self.db.update_thread(thread_id, **kwargs)
            if success:
                thread = self.db.get_thread(thread_id)
                if thread:
                    self._notify_thread_callbacks(thread)
            return success
        except DatabaseError as e:
            logger.error(f"Failed to update thread {thread_id}: {e}")
            return False

    def update_thread_name(self, thread_id: int, name: str) -> bool:
        """
        Update a thread's name.

        Args:
            thread_id: Thread ID
            name: New name

        Returns:
            True if successful
        """
        return self.update_thread(thread_id, name=name)

    def delete_thread(self, thread_id: int, soft_delete: bool = True) -> bool:
        """
        Delete a thread.

        Args:
            thread_id: Thread ID
            soft_delete: If True, mark as archived instead of hard delete

        Returns:
            True if successful
        """
        try:
            success = self.db.delete_thread(thread_id, soft_delete)

            # If we deleted the current thread, switch to another one
            if success and thread_id == self.current_thread_id:
                threads = self.db.get_threads()
                if threads:
                    self.current_thread_id = threads[0]["id"]
                else:
                    self.current_thread_id = None

            return success
        except DatabaseError as e:
            logger.error(f"Failed to delete thread {thread_id}: {e}")
            return False

    def search_messages(
        self,
        query: str,
        thread_id: Optional[int] = None,
        limit: int = 50,
        include_attachments: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Search messages.

        Args:
            query: Search query
            thread_id: Limit to specific thread (optional)
            limit: Maximum results
            include_attachments: Include attachment data

        Returns:
            List of matching messages
        """
        if thread_id is None:
            thread_id = self.current_thread_id

        try:
            return self.db.search_messages(query, thread_id, limit, include_attachments)
        except DatabaseError as e:
            logger.error(f"Failed to search messages: {e}")
            return []

    def get_conversation_summary(self, thread_id: Optional[int] = None) -> dict[str, Any]:
        """
        Get a summary of the current conversation.

        Args:
            thread_id: Thread ID (uses current thread if None)

        Returns:
            Conversation summary
        """
        if thread_id is None:
            thread_id = self.current_thread_id

        if thread_id is None:
            return {}

        try:
            thread = self.db.get_thread(thread_id)
            messages = self.db.get_messages(thread_id)

            if not messages:
                return {
                    "thread": thread,
                    "message_count": 0,
                    "last_message": None,
                    "user_messages": 0,
                    "ai_messages": 0,
                    "system_messages": 0,
                }

            # Count messages by sender
            sender_counts: dict[str, int] = {}
            for message in messages:
                sender = message["sender"]
                sender_counts[sender] = sender_counts.get(sender, 0) + 1

            return {
                "thread": thread,
                "message_count": len(messages),
                "last_message": messages[-1] if messages else None,
                "user_messages": sender_counts.get("user", 0),
                "ai_messages": sender_counts.get("ai", 0),
                "system_messages": sender_counts.get("system", 0),
                "other_messages": sum(count for sender, count in sender_counts.items() if sender not in ["user", "ai", "system"]),
            }
        except DatabaseError as e:
            logger.error(f"Failed to get conversation summary for thread {thread_id}: {e}")
            return {}

    def export_conversation(self, thread_id: Optional[int] = None, format: str = "json") -> str:
        """
        Export a conversation to a file.

        Args:
            thread_id: Thread ID (uses current thread if None)
            format: Export format ('json' or 'txt')

        Returns:
            Path to exported file
        """
        if thread_id is None:
            thread_id = self.current_thread_id

        if thread_id is None:
            raise ValueError("No thread to export")

        try:
            thread = self.db.get_thread(thread_id)
            messages = self.db.get_messages(thread_id)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Ensure thread is not None before accessing 'name'
            thread_name = thread["name"] if thread else "unknown_thread"
            filename = f"conversation_{thread_name.replace(' ', '_')}_{timestamp}.{format}"

            if format == "json":
                import json

                data = {
                    "thread": thread,
                    "messages": messages,
                    "exported_at": datetime.now().isoformat(),
                }
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            elif format == "txt":
                with open(filename, "w", encoding="utf-8") as f:
                    # Ensure thread is not None before accessing 'name'
                    f.write(f"Conversation: {thread['name'] if thread else 'Unknown'}\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")

                    for message in messages:
                        sender_icon = {"user": "👤", "ai": "🤖", "system": "⚙️"}.get(message["sender"], "💬")

                        f.write(f"{sender_icon} {message['sender'].upper()}\n")
                        f.write(f"{message['content']}\n\n")

            logger.info(f"Exported conversation to {filename}")
            return filename
        except DatabaseError as e:
            logger.error(f"Failed to export conversation: {e}")
            raise

    def get_user_settings(self, key: Optional[str] = None) -> Any:
        """
        Get user settings.

        Args:
            key: Specific setting key (optional)

        Returns:
            Setting value or all settings
        """
        try:
            return self.db.get_user_settings(key)
        except DatabaseError as e:
            logger.error(f"Failed to get user settings: {e}")
            return {} if key is None else None

    def set_user_setting(self, key: str, value: Any, value_type: str = "string", description: Optional[str] = None) -> bool:
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
        try:
            return self.db.set_user_setting(key, value, value_type, description)
        except DatabaseError as e:
            logger.error(f"Failed to set user setting {key}: {e}")
            return False

    def add_analytics(self, thread_id: int, analytics_type: str, data: dict[str, Any]) -> int:
        """
        Add conversation analytics data.

        Args:
            thread_id: Thread ID
            analytics_type: Type of analytics
            data: Analytics data

        Returns:
            Analytics record ID
        """
        try:
            return self.db.add_analytics(thread_id, analytics_type, data)
        except DatabaseError as e:
            logger.error(f"Failed to add analytics: {e}")
            raise

    def get_analytics(self, thread_id: int, analytics_type: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get conversation analytics.

        Args:
            thread_id: Thread ID
            analytics_type: Specific analytics type (optional)

        Returns:
            List of analytics records
        """
        try:
            return self.db.get_analytics(thread_id, analytics_type)
        except DatabaseError as e:
            logger.error(f"Failed to get analytics: {e}")
            return []

    def get_stats(self) -> dict[str, Any]:
        """Get chat statistics."""
        try:
            return self.db.get_database_stats()
        except DatabaseError as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.

        Args:
            backup_path: Path for the backup file

        Returns:
            True if backup successful
        """
        try:
            return self.db.backup_database(backup_path)
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False

    def cleanup_old_messages(self, days_old: int = 30) -> int:
        """
        Clean up messages older than specified days.

        Args:
            days_old: Delete messages older than this many days

        Returns:
            Number of messages deleted
        """
        try:
            return self.db.cleanup_old_messages(days_old)
        except DatabaseError as e:
            logger.error(f"Failed to cleanup old messages: {e}")
            return 0

    def vacuum_database(self) -> bool:
        """
        Vacuum the database to reclaim space and optimize performance.

        Returns:
            True if successful
        """
        try:
            return self.db.vacuum_database()
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            return False

    def close(self) -> None:
        """Close the chat manager and database connections."""
        try:
            self.db.close_connections()
            logger.info("Chat manager closed")
        except Exception as e:
            logger.error(f"Error closing chat manager: {e}")
