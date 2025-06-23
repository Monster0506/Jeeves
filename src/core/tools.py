"""
Tools module for Jeeves AI Assistant.
Contains all available tools that can be called by the AI.

## Available Tools (13 total)

### 🗂️ Chat Management Tools (6)
1. **rename_chat_thread** - Rename chat threads for better organization
2. **search_chat_history** - Search through conversation history across threads
3. **get_available_threads** - List all chat threads with statistics
4. **get_current_thread_info** - Get detailed info about current thread
5. **export_current_conversation** - Export conversation to JSON/text format
6. **get_conversation_summary** - Get conversation statistics and summary

### 📝 File Management Tools (5)
7. **note_manager** - Manage personal notes in sandbox/notes/
8. **todo_list_manager** - Manage centralized todo list in sandbox/todo.md
9. **content_searcher** - Search files and content within sandbox directory
10. **read_file** - Read content from a file in the project directory
11. **list_directory** - List contents of a directory in the project

### 🧠 Memory & Logging Tools (2)
12. **persistent_memory_manager** - Manage Jeeves's long-term memory
13. **scratchpad_logger** - Log internal thoughts to session-specific files

## Tool Categories & Usage

### Chat Management
Tools for organizing and managing conversation threads:
- Thread renaming and organization
- Historical search and retrieval
- Conversation export and summaries

### File Management
Tools for managing personal files and data:
- Note creation, reading, and management
- Todo list with task tracking
- Content search across all files
- Safe file operations within sandbox

### Memory & Logging
Tools for persistent memory and session logging:
- Long-term memory storage and retrieval
- Session-specific thought logging
- Context preservation across conversations

## Security Features
- All tools operate within sandbox directory
- Input validation and parameter filtering
- Error handling with graceful fallbacks
- Soft deletes for file operations
- Comprehensive logging for audit trails

## Usage Examples

### Basic Tool Usage
```python
# Chat management
response = manager.generate_response("Rename this thread to 'Project Planning'")
response = manager.generate_response("Search for 'API' in chat history")

# File management
response = manager.generate_response("Create a note called 'ideas' with content 'Build a new app'")
response = manager.generate_response("Add 'Review code' to my todo list")

# Memory management
response = manager.generate_response("Remember that I prefer dark mode")
response = manager.generate_response("Log this thought: 'User needs help with authentication'")
```

### Complex Workflows
```python
# Multi-step process example
response = manager.generate_response(\"\"\"
1. Search my notes for 'database design'
2. If found, read the content
3. Add 'Review database schema' to todo list
4. Remember that I'm working on database optimization
\"\"\")
```

For detailed tool calling documentation, see TOOL_CALLING_GUIDE.md
"""

import logging
import os
import re
from datetime import datetime
from typing import Optional

from .chat_manager import ChatManager
from .file_handler import JeevesFileHandler

logger = logging.getLogger(__name__)


class JeevesTools:
    """
    Collection of tools available to Jeeves AI Assistant.

    This class provides 13 powerful tools organized into 3 categories:

    **Chat Management (6 tools):**
    - Thread organization and renaming
    - Historical search and retrieval
    - Conversation export and summaries

    **File Management (5 tools):**
    - Personal note management
    - Todo list with task tracking
    - Content search across files
    - Reading and listing project files

    **Memory & Logging (2 tools):**
    - Persistent memory storage
    - Session-specific thought logging

    Most tools operate within a secure sandbox directory, while some
    provide safe, read-only access to the project directory. All tools include
    comprehensive error handling, input validation, and logging.
    """

    def __init__(self, chat_manager: ChatManager):
        """
        Initialize the tools with required dependencies.

        Args:
            chat_manager: Chat manager instance for database operations
        """
        self.chat_manager = chat_manager
        self.file_handler = JeevesFileHandler()
        self.sandbox_root = self.file_handler.get_sandbox_root()
        logger.info(f"JeevesTools initialized. Sandbox root: {self.sandbox_root}")

    def _resolve_thread_identifier(self, thread_identifier: Optional[str]) -> Optional[int]:
        """
        Resolve a thread identifier to a thread ID.

        Args:
            thread_identifier: Thread ID (as string) or thread name (str), or None for current thread

        Returns:
            Thread ID if found, or None if not found or ambiguous
        """
        # Treat empty string or whitespace as None
        if thread_identifier is None or (isinstance(thread_identifier, str) and thread_identifier.strip() == ""):
            # If None, use current thread
            current_thread_id = self.chat_manager.get_current_thread_id()
            return current_thread_id

        if isinstance(thread_identifier, str):
            # Check if it's a numeric string (thread ID)
            if thread_identifier.isdigit():
                thread_id = int(thread_identifier)
                # Direct ID - verify it exists
                thread = self.chat_manager.get_thread(thread_id)
                return thread_id if thread else None

            # Name search
            matching_threads = self.chat_manager.find_threads_by_name(thread_identifier)

            if not matching_threads:
                return None

            if len(matching_threads) == 1:
                return matching_threads[0]["id"]

            # Multiple matches - raise error with details
            thread_details = []
            for thread in matching_threads:
                thread_details.append(f"ID {thread['id']}: '{thread['name']}' (last activity: {thread['last_activity']})")

            raise ValueError(f"Multiple threads found matching '{thread_identifier}':\n" + "\n".join(thread_details) + "\n\nPlease specify the exact thread ID or use a more specific name.")

        return None

    def rename_chat_thread(self, thread_identifier: Optional[str], new_name: str) -> str:
        """
        Rename a chat thread.

        Args:
            thread_identifier: Thread ID (as string) or thread name (str), or None for the current thread
            new_name: The new name for the thread

        Returns:
            Success or error message
        """
        logger.info(f"Tool called: rename_chat_thread(thread_identifier={thread_identifier}, new_name='{new_name}')")

        try:
            if not new_name or not new_name.strip():
                logger.warning("rename_chat_thread: New name is empty or whitespace only")
                return "Error: New name cannot be empty"

            # Resolve thread identifier
            try:
                thread_id = self._resolve_thread_identifier(thread_identifier)
            except ValueError as e:
                return f"Error: {str(e)}"

            if thread_id is None:
                if thread_identifier is None:
                    return "No active thread."
                else:
                    return f"Thread '{thread_identifier}' not found."

            logger.debug(f"Attempting to rename thread {thread_id} to '{new_name.strip()}'")

            success = self.chat_manager.update_thread_name(thread_id, new_name.strip())

            if success:
                logger.info(f"Successfully renamed thread {thread_id} to '{new_name}'")
                return f"Successfully renamed thread {thread_id} to '{new_name}'"
            else:
                logger.warning(f"Failed to rename thread {thread_id} - thread may not exist")
                return f"Error: Failed to rename thread {thread_id}. Thread may not exist."

        except Exception as e:
            logger.error(f"Error renaming thread {thread_identifier}: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def search_chat_history(self, query: str, thread_identifier: Optional[str] = None, limit: int = 10) -> str:
        """
        Search through chat history.

        Args:
            query: Search query string
            thread_identifier: Thread ID (as string) or thread name (str), or None for all threads
            limit: Maximum number of results to return

        Returns:
            Formatted search results or error message
        """
        logger.info(f"Tool called: search_chat_history(query='{query}', thread_identifier={thread_identifier}, limit={limit})")

        try:
            if not query or not query.strip():
                logger.warning("search_chat_history: Query is empty or whitespace only")
                return "Error: Search query cannot be empty"

            # Resolve thread identifier
            thread_id = None
            if thread_identifier is not None:
                try:
                    thread_id = self._resolve_thread_identifier(thread_identifier)
                except ValueError as e:
                    return f"Error: {str(e)}"

                if thread_id is None:
                    return f"Thread '{thread_identifier}' not found."

            logger.debug(f"Searching for '{query.strip()}' in thread {thread_id} with limit {limit}")
            results = self.chat_manager.search_messages(query.strip(), thread_id=thread_id, limit=limit)

            logger.info(f"Search returned {len(results)} results")

            if not results:
                thread_info = f" in thread {thread_id}" if thread_id else ""
                logger.debug(f"No messages found matching '{query}'{thread_info}")
                return f"No messages found matching '{query}'{thread_info}"

            # Format results
            formatted_results = []
            for i, message in enumerate(results, 1):
                sender = message.get("sender", "unknown")
                content = message.get("content", "")[:100]  # Truncate long messages
                timestamp = message.get("timestamp", "")
                thread_name = message.get("thread_name", "Unknown Thread")

                formatted_results.append(f"{i}. [{thread_name}] {sender}: {content}... ({timestamp})")

            logger.debug(f"Formatted {len(formatted_results)} search results")
            logger.debug(formatted_results)
            return f"Found {len(results)} messages matching '{query}':\n" + "\n".join(formatted_results)

        except Exception as e:
            logger.error(f"Error searching chat history: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def get_available_threads(self) -> str:
        """
        Get a list of all available chat threads.

        Returns:
            Formatted list of threads or error message
        """
        logger.info("Tool called: get_available_threads()")

        try:
            logger.debug("Retrieving all available threads")
            threads = self.chat_manager.get_threads()

            logger.info(f"Retrieved {len(threads)} threads")

            if not threads:
                logger.debug("No chat threads found")
                return "No chat threads found."

            # Get message counts for all threads
            logger.debug("Getting message counts for all threads")
            message_counts = self.chat_manager.get_thread_message_counts()

            formatted_threads = []
            for i, thread in enumerate(threads, 1):
                thread_id = thread.get("id", "Unknown")
                name = thread.get("name", "Unnamed")
                message_count = message_counts.get(thread_id, 0)
                last_activity = thread.get("last_activity", "Unknown")

                formatted_threads.append(f"{i}. Thread {thread_id}: '{name}' ({message_count} messages, last: {last_activity})")

            logger.debug(f"Formatted {len(formatted_threads)} thread entries")
            return f"Available chat threads:\n{"\n".join(formatted_threads)}"

        except Exception as e:
            logger.error(f"Error getting available threads: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def get_current_thread_info(self) -> str:
        """
        Get information about the current active thread.

        Returns:
            Formatted thread information or error message
        """
        logger.info("Tool called: get_current_thread_info()")

        try:
            logger.debug("Retrieving current thread information")
            current_thread = self.chat_manager.get_current_thread()

            if not current_thread:
                logger.warning("No active thread found")
                return "No active thread."

            thread_id = current_thread.get("id", "Unknown")
            name = current_thread.get("name", "Unnamed")

            # Get message count for current thread
            message_counts = self.chat_manager.get_thread_message_counts()
            message_count = message_counts.get(thread_id, 0)

            last_activity = current_thread.get("last_activity", "Unknown")
            created_at = current_thread.get("created_at", "Unknown")

            logger.info(f"Current thread: {thread_id} ('{name}') with {message_count} messages")

            return f"Current thread: {thread_id}\nName: {name}\nMessages: {message_count}\nCreated: {created_at}\nLast activity: {last_activity}"

        except Exception as e:
            logger.error(f"Error getting current thread info: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def export_current_conversation(self, thread_identifier: Optional[str] = None, format: str = "json") -> str:
        """
        Export a conversation to a file.

        Args:
            thread_identifier: Thread ID (as string) or thread name (str), or None for the current thread
            format: Export format ('json' or 'txt')

        Returns:
            Success message with file path or error message
        """
        logger.info(f"Tool called: export_current_conversation(thread_identifier={thread_identifier}, format='{format}')")

        try:
            # Resolve thread identifier
            thread_id = None
            if thread_identifier is not None:
                try:
                    thread_id = self._resolve_thread_identifier(thread_identifier)
                except ValueError as e:
                    return f"Error: {str(e)}"

                if thread_id is None:
                    return f"Thread '{thread_identifier}' not found."
            else:
                # Use current thread
                current_thread = self.chat_manager.get_current_thread()
                if not current_thread:
                    return "No active thread to export."
                thread_id = current_thread.get("id")

            logger.debug(f"Exporting conversation for thread {thread_id} in {format} format")
            export_path = self.chat_manager.export_conversation(thread_id=thread_id, format=format)

            logger.info(f"Successfully exported conversation to: {export_path}")
            return f"Successfully exported conversation to: {export_path}"

        except Exception as e:
            logger.error(f"Error exporting conversation: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def get_conversation_summary(self) -> str:
        """
        Get a summary of the current conversation.

        Returns:
            Formatted conversation summary or error message
        """
        logger.info("Tool called: get_conversation_summary()")

        try:
            logger.debug("Retrieving conversation summary")
            summary = self.chat_manager.get_conversation_summary()

            if not summary:
                logger.warning("No conversation to summarize")
                return "No conversation to summarize."

            thread = summary.get("thread", {})
            thread_name = thread.get("name", "Unknown")
            message_count = summary.get("message_count", 0)
            user_messages = summary.get("user_messages", 0)
            ai_messages = summary.get("ai_messages", 0)

            logger.info(f"Conversation summary: {thread_name} - {message_count} total messages ({user_messages} user, {ai_messages} AI)")

            return f"Conversation Summary:\nThread: {thread_name}\nTotal messages: {message_count}\nUser messages: {user_messages}\nAI messages: {ai_messages}"

        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def get_registered_tools(self) -> dict[str, callable]:
        """
        Get all registered tools with their descriptions.

        Returns:
            Dictionary mapping tool names to their functions
        """
        logger.debug("Getting registered tools")
        return {
            "rename_chat_thread": self.rename_chat_thread,
            "search_chat_history": self.search_chat_history,
            "get_available_threads": self.get_available_threads,
            "get_current_thread_info": self.get_current_thread_info,
            "export_current_conversation": self.export_current_conversation,
            "get_conversation_summary": self.get_conversation_summary,
            "note_manager": self.note_manager,
            "todo_list_manager": self.todo_list_manager,
            "content_searcher": self.content_searcher,
            "persistent_memory_manager": self.persistent_memory_manager,
            "scratchpad_logger": self.scratchpad_logger,
            "read_file": self.read_file,
            "list_directory": self.list_directory,
        }

    def get_tool_descriptions(self) -> dict[str, str]:
        """
        Get descriptions for all registered tools.

        Returns:
            Dictionary mapping tool names to their docstrings
        """
        logger.debug("Getting tool descriptions")
        descriptions = {name: func.__doc__ for name, func in self.get_registered_tools().items() if func.__doc__}
        logger.debug(f"Returning descriptions for {len(descriptions)} tools")
        return descriptions

    # File-based Tools

    def note_manager(
        self,
        action: str,
        filename: Optional[str] = None,
        content: Optional[str] = None,
        directory: str = "notes",
    ) -> str:
        """
        Manage personal notes within the sandbox/notes/ directory.

        Args:
            action: 'create', 'append', 'read', 'list', or 'delete'
            filename: Name of the note file (without .md extension)
            content: Content to write or append
            directory: Subdirectory within sandbox/ (default: 'notes')

        Returns:
            Success message or file content
        """
        logger.info(f"Tool called: note_manager(action='{action}', filename='{filename}', directory='{directory}')")

        try:
            logger.debug(f"Processing note manager action: {action}")

            # Ensure notes directory exists
            notes_dir = f"{directory}"
            logger.debug(f"Ensuring directory exists: {notes_dir}")
            self.file_handler.ensure_directory_exists(notes_dir)

            if action == "list":
                logger.debug("Listing notes in directory")
                # List all notes in directory
                files = self.file_handler.list_directory_contents(notes_dir, include_directories=False)
                if not files:
                    logger.debug(f"No files found in {directory}/ directory")
                    return f"No notes found in {directory}/ directory."
                print(files)
                note_list = []
                for file_info in files:
                    if file_info.get("path", "").endswith(".md"):
                        note_list.append(file_info["path"])

                logger.info(f"Found {len(note_list)} markdown notes in {directory}/")

                if note_list:
                    return f"Notes in {directory}/:\n" + "\n".join(f"- {note}" for note in note_list)
                else:
                    return f"No markdown notes found in {directory}/ directory."

            if not filename:
                logger.warning("note_manager: filename is required but not provided")
                return "Error: filename is required for create, append, read, and delete actions."

            # Add .md extension if not present
            if not filename.endswith(".md"):
                filename += ".md"
                logger.debug(f"Added .md extension to filename: {filename}")

            file_path = f"{notes_dir}/{filename}"
            logger.debug(f"Full file path: {file_path}")

            if action == "create":
                if not content:
                    logger.warning("note_manager: content is required for create action but not provided")
                    return "Error: content is required for create action."

                logger.debug(f"Creating note with content length: {len(content)} characters")
                success = self.file_handler.write_file(file_path, content, overwrite=True)
                if success:
                    logger.info(f"Successfully created note: {file_path}")
                    return f"Successfully created note '{filename}' in {directory}/ directory."
                else:
                    logger.error(f"Failed to create note: {file_path}")
                    return f"Error: Failed to create note '{filename}'."

            elif action == "append":
                if not content:
                    logger.warning("note_manager: content is required for append action but not provided")
                    return "Error: content is required for append action."

                logger.debug(f"Appending content with length: {len(content)} characters")
                success = self.file_handler.append_to_file(file_path, f"\n{content}")
                if success:
                    logger.info(f"Successfully appended to note: {file_path}")
                    return f"Successfully appended content to note '{filename}'."
                else:
                    logger.error(f"Failed to append to note: {file_path}")
                    return f"Error: Failed to append to note '{filename}'."

            elif action == "read":
                logger.debug(f"Reading note: {file_path}")
                if not self.file_handler.file_exists(file_path):
                    logger.warning(f"Note does not exist: {file_path}")
                    return f"Error: Note '{filename}' does not exist."

                content = self.file_handler.read_file_content(file_path)
                if content:
                    logger.info(f"Successfully read note: {file_path} ({len(content)} characters)")
                    return f"Content of '{filename}':\n\n{content}"
                else:
                    logger.debug(f"Note is empty: {file_path}")
                    return f"Note '{filename}' is empty."

            elif action == "delete":
                logger.debug(f"Deleting note: {file_path}")
                success = self.file_handler.delete_file(file_path, soft=True)
                if success:
                    logger.info(f"Successfully deleted note (moved to trash): {file_path}")
                    return f"Successfully deleted note '{filename}' (moved to trash)."
                else:
                    logger.error(f"Failed to delete note: {file_path}")
                    return f"Error: Failed to delete note '{filename}'."

            else:
                logger.warning(f"Unknown action in note_manager: {action}")
                return f"Error: Unknown action '{action}'. Valid actions: create, append, read, list, delete."

        except Exception as e:
            logger.error(f"Error in note_manager: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def todo_list_manager(
        self,
        action: str,
        task_content: Optional[str] = None,
        task_id: Optional[int] = None,
    ) -> str:
        """
        Manage the central sandbox/todo.md file.

        Args:
            action: 'add', 'list', 'complete', 'delete', or 'clear'
            task_content: Content of the task to add
            task_id: Numerical ID of the task to complete/delete

        Returns:
            Success message or current todo list
        """
        logger.info(f"Tool called: todo_list_manager(action='{action}', task_id={task_id})")

        try:
            todo_file = "todo.md"
            logger.debug(f"Using todo file: {todo_file}")

            if action == "list":
                logger.debug("Listing todo items")
                if not self.file_handler.file_exists(todo_file):
                    logger.debug("Todo file does not exist")
                    return "No todo list found. Use 'add' action to create your first task."

                content = self.file_handler.read_file_content(todo_file)
                if content.strip():
                    logger.info(f"Retrieved todo list with {len(content)} characters")
                    return f"Current Todo List:\n\n{content}"
                else:
                    logger.debug("Todo list is empty")
                    return "Todo list is empty."

            elif action == "add":
                if not task_content:
                    logger.warning("todo_list_manager: task_content is required for add action but not provided")
                    return "Error: task_content is required for add action."

                logger.debug(f"Adding new task: {task_content}")

                # Read existing content to get next ID
                existing_content = ""
                if self.file_handler.file_exists(todo_file):
                    existing_content = self.file_handler.read_file_content(todo_file)
                    logger.debug(f"Read existing todo content: {len(existing_content)} characters")

                # Find next available ID
                next_id = 1
                if existing_content:
                    id_pattern = r"^\d+\."
                    existing_ids = re.findall(id_pattern, existing_content, re.MULTILINE)
                    if existing_ids:
                        max_id = max(int(id_.rstrip(".")) for id_ in existing_ids)
                        next_id = max_id + 1
                        logger.debug(f"Found existing IDs, next ID will be: {next_id}")

                new_task = f"{next_id}. [ ] {task_content}\n"
                logger.debug(f"Created new task entry: {new_task.strip()}")

                if existing_content:
                    # Append to existing file
                    logger.debug("Appending to existing todo file")
                    success = self.file_handler.append_to_file(todo_file, new_task)
                else:
                    # Create new file
                    logger.debug("Creating new todo file")
                    success = self.file_handler.write_file(todo_file, new_task, overwrite=True)

                if success:
                    logger.info(f"Successfully added todo task {next_id}: {task_content}")
                    return f"Added task {next_id}: {task_content}"
                else:
                    logger.error(f"Failed to add todo task: {task_content}")
                    return "Error: Failed to add task."

            elif action == "complete":
                if not task_id:
                    logger.warning("todo_list_manager: task_id is required for complete action but not provided")
                    return "Error: task_id is required for complete action."

                logger.debug(f"Completing task ID: {task_id}")

                if not self.file_handler.file_exists(todo_file):
                    logger.warning("Todo file does not exist for completion")
                    return "Error: Todo list does not exist."

                content = self.file_handler.read_file_content(todo_file)
                lines = content.split("\n")
                logger.debug(f"Processing {len(lines)} lines in todo file")

                task_found = False
                for i, line in enumerate(lines):
                    if line.strip().startswith(f"{task_id}."):
                        # Mark as complete
                        if "[ ]" in line:
                            lines[i] = line.replace("[ ]", "[x]")
                            task_found = True
                            logger.debug(f"Marked task {task_id} as complete")
                        elif "[x]" in line:
                            logger.debug(f"Task {task_id} is already completed")
                            return f"Task {task_id} is already completed."
                        break

                if not task_found:
                    logger.warning(f"Task {task_id} not found in todo file")
                    return f"Error: Task {task_id} not found."

                new_content = "\n".join(lines)
                success = self.file_handler.write_file(todo_file, new_content, overwrite=True)

                if success:
                    logger.info(f"Successfully completed todo task {task_id}")
                    return f"Marked task {task_id} as complete."
                else:
                    logger.error(f"Failed to update todo task {task_id}")
                    return "Error: Failed to update task."

            elif action == "delete":
                if not task_id:
                    logger.warning("todo_list_manager: task_id is required for delete action but not provided")
                    return "Error: task_id is required for delete action."

                logger.debug(f"Deleting task ID: {task_id}")

                if not self.file_handler.file_exists(todo_file):
                    logger.warning("Todo file does not exist for deletion")
                    return "Error: Todo list does not exist."

                content = self.file_handler.read_file_content(todo_file)
                lines = content.split("\n")
                logger.debug(f"Processing {len(lines)} lines in todo file")

                task_found = False
                new_lines = []
                for line in lines:
                    if line.strip().startswith(f"{task_id}."):
                        task_found = True
                        logger.debug(f"Found task {task_id} to delete")
                        continue  # Skip this line
                    new_lines.append(line)

                if not task_found:
                    logger.warning(f"Task {task_id} not found in todo file")
                    return f"Error: Task {task_id} not found."

                new_content = "\n".join(new_lines)
                success = self.file_handler.write_file(todo_file, new_content, overwrite=True)

                if success:
                    logger.info(f"Successfully deleted todo task {task_id}")
                    return f"Deleted task {task_id}."
                else:
                    logger.error(f"Failed to delete todo task {task_id}")
                    return "Error: Failed to delete task."

            elif action == "clear":
                logger.debug("Clearing todo list")
                success = self.file_handler.write_file(todo_file, "", overwrite=True)
                if success:
                    logger.info("Successfully cleared todo list")
                    return "Todo list cleared."
                else:
                    logger.error("Failed to clear todo list")
                    return "Error: Failed to clear todo list."

            else:
                logger.warning(f"Unknown action in todo_list_manager: {action}")
                return f"Error: Unknown action '{action}'. Valid actions: add, list, complete, delete, clear."

        except Exception as e:
            logger.error(f"Error in todo_list_manager: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def content_searcher(
        self,
        query: str,
        search_type: str = "content",
        file_pattern: Optional[str] = None,
        recursive: bool = True,
    ) -> str:
        """
        Search for files and content within the sandbox directory.

        Args:
            query: Search query (keywords or regex pattern)
            search_type: 'content', 'filename', or 'both'
            file_pattern: Optional file pattern to limit search (e.g., "*.md")
            recursive: Whether to search recursively in subdirectories

        Returns:
            Search results
        """
        logger.info(f"Tool called: content_searcher(query='{query}', search_type='{search_type}', pattern='{file_pattern}', recursive={recursive})")

        try:
            logger.debug(f"Starting content search with query: '{query}'")
            results = []

            if search_type in ["filename", "both"]:
                logger.debug("Searching for files by name/pattern")
                # Search for files by name/pattern
                if file_pattern:
                    pattern = file_pattern
                    logger.debug(f"Using file pattern: {pattern}")
                else:
                    pattern = f"*{query}*"
                    logger.debug(f"Using query-based pattern: {pattern}")

                files = self.file_handler.find_files_by_pattern("", pattern, recursive)
                logger.debug(f"Found {len(files)} files matching pattern")
                for file_path in files:
                    results.append(f"File: {file_path}")

            if search_type in ["content", "both"]:
                logger.debug("Searching file contents")
                # Search file contents - search_file_contents requires relative_root_path as first parameter
                content_results = self.file_handler.search_file_contents("", query)
                logger.debug(f"Found {len(content_results)} content results")
                for result in content_results:
                    file_path = result.get("file_path", "Unknown")  # Changed from 'file' to 'file_path'
                    line_number = result.get("line_number", "Unknown")  # Changed from 'line' to 'line_number'
                    line_content = result.get("line_content", "")[:100]  # Changed from 'content' to 'line_content'
                    results.append(f"Content in {file_path}:{line_number} - {line_content}...")

            if not results:
                logger.debug(f"No results found for query: '{query}'")
                return f"No results found for query '{query}'."

            logger.info(f"Content search returned {len(results)} results for query: '{query}'")
            return f"Search results for '{query}':\n\n" + "\n".join(results)

        except Exception as e:
            logger.error(f"Error in content_searcher: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def persistent_memory_manager(self, action: str, content: Optional[str] = None, entry_id: Optional[int] = None) -> str:
        """
        Manage Jeeves's long-term persistent memory in sandbox/MEMORY.md.

        Args:
            action: 'add', 'list', 'remove', or 'clear'
            content: Memory entry to add
            entry_id: ID of entry to remove

        Returns:
            Success message or memory content
        """
        logger.info(f"Tool called: persistent_memory_manager(action='{action}', entry_id={entry_id})")

        try:
            memory_file = "MEMORY.md"
            logger.debug(f"Using memory file: {memory_file}")

            if action == "list":
                logger.debug("Listing persistent memory entries")
                if not self.file_handler.file_exists(memory_file):
                    logger.debug("Memory file does not exist")
                    return "No persistent memory found."

                content = self.file_handler.read_file_content(memory_file)
                if content.strip():
                    logger.info(f"Retrieved persistent memory with {len(content)} characters")
                    return f"Persistent Memory:\n\n{content}"
                else:
                    logger.debug("Persistent memory is empty")
                    return "Persistent memory is empty."

            elif action == "add":
                if not content:
                    logger.warning("persistent_memory_manager: content is required for add action but not provided")
                    return "Error: content is required for add action."

                logger.debug(f"Adding memory entry: {content}")

                # Read existing content to get next ID
                existing_content = ""
                if self.file_handler.file_exists(memory_file):
                    existing_content = self.file_handler.read_file_content(memory_file)
                    logger.debug(f"Read existing memory content: {len(existing_content)} characters")

                # Find next available ID
                next_id = 1
                if existing_content:
                    id_pattern = r"^\d+\."
                    existing_ids = re.findall(id_pattern, existing_content, re.MULTILINE)
                    if existing_ids:
                        max_id = max(int(id_.rstrip(".")) for id_ in existing_ids)
                        next_id = max_id + 1
                        logger.debug(f"Found existing IDs, next ID will be: {next_id}")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry = f"{next_id}. {content} (Added: {timestamp})\n"
                logger.debug(f"Created new memory entry: {new_entry.strip()}")

                if existing_content:
                    # Append to existing file
                    logger.debug("Appending to existing memory file")
                    success = self.file_handler.append_to_file(memory_file, new_entry)
                else:
                    # Create new file
                    logger.debug("Creating new memory file")
                    success = self.file_handler.write_file(memory_file, new_entry, overwrite=True)

                if success:
                    logger.info(f"Successfully added memory entry {next_id}: {content}")
                    return f"Added memory entry {next_id}: {content}"
                else:
                    logger.error(f"Failed to add memory entry: {content}")
                    return "Error: Failed to add memory entry."

            elif action == "remove":
                if not entry_id:
                    logger.warning("persistent_memory_manager: entry_id is required for remove action but not provided")
                    return "Error: entry_id is required for remove action."

                logger.debug(f"Removing memory entry ID: {entry_id}")

                if not self.file_handler.file_exists(memory_file):
                    logger.warning("Memory file does not exist for removal")
                    return "Error: Memory file does not exist."

                content = self.file_handler.read_file_content(memory_file)
                lines = content.split("\n")
                logger.debug(f"Processing {len(lines)} lines in memory file")

                entry_found = False
                new_lines = []
                for line in lines:
                    if line.strip().startswith(f"{entry_id}."):
                        entry_found = True
                        logger.debug(f"Found memory entry {entry_id} to remove")
                        continue  # Skip this line
                    new_lines.append(line)

                if not entry_found:
                    logger.warning(f"Memory entry {entry_id} not found")
                    return f"Error: Memory entry {entry_id} not found."

                new_content = "\n".join(new_lines)
                success = self.file_handler.write_file(memory_file, new_content, overwrite=True)

                if success:
                    logger.info(f"Successfully removed memory entry {entry_id}")
                    return f"Removed memory entry {entry_id}."
                else:
                    logger.error(f"Failed to remove memory entry {entry_id}")
                    return "Error: Failed to remove memory entry."

            elif action == "clear":
                logger.debug("Clearing persistent memory")
                success = self.file_handler.write_file(memory_file, "", overwrite=True)
                if success:
                    logger.info("Successfully cleared persistent memory")
                    return "Persistent memory cleared."
                else:
                    logger.error("Failed to clear persistent memory")
                    return "Error: Failed to clear persistent memory."

            else:
                logger.warning(f"Unknown action in persistent_memory_manager: {action}")
                return f"Error: Unknown action '{action}'. Valid actions: add, list, remove, clear."

        except Exception as e:
            logger.error(f"Error in persistent_memory_manager: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def scratchpad_logger(self, content: str, session_name: Optional[str] = None) -> str:
        """
        Log internal thought processes to session-specific scratchpad files.

        Args:
            content: Content to log
            session_name: Optional session name (uses current thread if None)

        Returns:
            Success message
        """
        logger.info(f"Tool called: scratchpad_logger(session_name='{session_name}')")

        try:
            logger.debug(f"Logging scratchpad content with length: {len(content)} characters")

            # Get current thread info if no session name provided
            if not session_name:
                logger.debug("No session name provided, getting current thread info")
                current_thread = self.chat_manager.get_current_thread()
                if current_thread:
                    thread_name = current_thread.get("name", "unknown")
                    thread_id = current_thread.get("id", "unknown")
                    session_name = f"{thread_name}_{thread_id}"
                    logger.debug(f"Generated session name from thread: {session_name}")
                else:
                    session_name = "unknown_session"
                    logger.warning("No current thread found, using 'unknown_session'")

            # Sanitize session name for filename
            original_session_name = session_name
            session_name = re.sub(r"[^\w\-_]", "_", session_name)
            if original_session_name != session_name:
                logger.debug(f"Sanitized session name: '{original_session_name}' -> '{session_name}'")

            # Ensure scratchpads directory exists
            logger.debug("Ensuring scratchpads directory exists")
            self.file_handler.ensure_directory_exists("scratchpads")

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scratchpads/{session_name}_{timestamp}.md"
            logger.debug(f"Created scratchpad filename: {filename}")

            # Add timestamp to content
            log_entry = f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{content}\n\n---\n\n"
            logger.debug("Created log entry with timestamp")

            # Append to scratchpad file
            success = self.file_handler.append_to_file(filename, log_entry)

            if success:
                logger.info(f"Successfully logged to scratchpad: {filename}")
                return f"Logged to scratchpad: {filename}"
            else:
                logger.error(f"Failed to log to scratchpad: {filename}")
                return "Error: Failed to log to scratchpad."

        except Exception as e:
            logger.error(f"Error in scratchpad_logger: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def read_file(self, path: str) -> str:
        """
        Read the content of a file within the sandbox directory.

        Args:
            path: The relative path to the file from the sandbox root.

        Returns:
            The content of the file or an error message.
            For files in the attachments directory, informs the user to use the attach file button.
        """
        logger.info(f"Tool called: read_file(path='{path}')")

        try:
            logger.debug(f"Processing read_file request for path: '{path}'")

            # Check if this is an attachment file
            is_attachment_path = path.startswith("attachments/") or path.startswith("/attachments/")
            logger.debug(f"Path '{path}' is attachment path: {is_attachment_path}")

            if is_attachment_path:
                logger.info(f"Detected attachment file: '{path}' - informing user to use attach button")

                # Get file info for better user feedback
                file_info = self.file_handler.get_file_info(path)
                if file_info:
                    # Simple MIME type detection
                    import mimetypes

                    mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
                    file_size = file_info.get("size_bytes", 0)
                    file_name = os.path.basename(path)

                    logger.info(f"File '{path}' is {mime_type} ({file_size} bytes)")

                    return f"The file '{file_name}' is in the attachments directory. To view this file, please use the 'Attach File' button in the chat interface instead of the read_file tool. This ensures the file is properly displayed as an attachment in our conversation."
                else:
                    return f"The file '{path}' is in the attachments directory. To view this file, please use the 'Attach File' button in the chat interface instead of the read_file tool."

            # For regular files, return content as before
            logger.debug(f"Reading file content for '{path}' as regular text file")
            content = self.file_handler.read_file_content(path)
            logger.info(f"Successfully read file '{path}' with {len(content)} characters")
            return f"Content of '{path}':\n\n{content}"

        except Exception as e:
            logger.exception(f"Error reading file '{path}': {e}")
            return f"An error occurred while reading the file: {str(e)}"

    def list_directory(self, path: str = ".", recursive: bool = True) -> str:
        """
        List the contents of a directory within the sandbox directory.

        Args:
            path: The relative path to the directory from the sandbox root. Defaults to the sandbox root.
            recursive: If True, recursively list contents of subdirectories. Defaults to True.

        Returns:
            A hierarchical list of files and directories or an error message.
        """
        logger.info(f"Tool called: list_directory(path='{path}', recursive={recursive})")
        try:
            contents = self.file_handler.list_directory_contents(path, recursive=recursive, include_files=True, include_directories=True)

            if not contents:
                return f"Directory '{path}' is empty."

            # Sort contents: directories first, then files, both alphabetically
            directories = []
            files = []

            for item in contents:
                item_path = item["path"]
                if item["type"] == "directory":
                    directories.append(item_path)
                else:
                    files.append(item_path)

            # Sort both lists
            directories.sort()
            files.sort()

            # Format the output with proper hierarchy
            result_lines = [f"Contents of '{path}':\n"]

            # Add directories first (with trailing slash)
            for directory in directories:
                result_lines.append(f"- {directory}/")

            # Add files
            for file in files:
                result_lines.append(f"- {file}")

            return "\n".join(result_lines)

        except Exception as e:
            logger.exception(f"Error listing directory '{path}': {e}")
            return f"An error occurred while listing the directory: {str(e)}"
