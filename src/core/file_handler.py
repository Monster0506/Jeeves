"""
Secure file handler for Jeeves AI Assistant.
Provides safe file operations within the sandbox directory.
"""

import os
import shutil
import logging
import hashlib
import re
import zipfile
import tarfile
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
from src.config.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


class SandboxViolationError(ValueError):
    """Raised when an operation attempts to access paths outside the sandbox."""

    pass


class JeevesFileHandler:
    """Secure file handler for Jeeves AI Assistant operations."""

    def __init__(self, sandbox_root_dir: str = None):
        """
        Initialize the file handler with sandbox directory.

        Args:
            sandbox_root_dir: Root directory for all Jeeves file operations.
                             If None, uses the setting from config.
        """
        # Get sandbox directory from settings if not provided
        if sandbox_root_dir is None:
            sandbox_root_dir = APP_SETTINGS["sandbox_directory"]

        # Resolve sandbox root path immediately to its absolute, canonical form.
        # This handles user expansion (~) and '..' components, and follows symlinks.
        # All subsequent path checks will be against this resolved path.
        pathObject = Path(sandbox_root_dir).expanduser().resolve()

        # Ensure the sandbox root directory exists
        if not pathObject.exists():
            try:
                pathObject.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created sandbox directory: {pathObject}")
            except OSError as e:
                logger.error(f"Failed to create sandbox directory {pathObject}: {e}")
                raise

        # Verify it's a directory
        if not pathObject.is_dir():
            raise FileExistsError(
                f"WARNING: Specified root dir '{sandbox_root_dir}' is already a non-directory path: {pathObject}"
            )
        self.sandbox = pathObject
        logger.info(f"JeevesFileHandler initialized with sandbox: {self.sandbox}")

        # --- Internal Configuration ---
        self._trash_dir = self.sandbox / ".trash"
        self._backups_dir = self.sandbox / ".backups"
        self._default_encoding = "utf-8"
        self._backup_retention_days = 30
        self._max_file_size_bytes = 100 * 1024 * 1024  # Default to 100 MB
        self._allowed_extensions: Optional[List[str]] = None  # None means all allowed
        self._operation_history: List[Dict] = []
        self._last_error_message: Optional[str] = None
        self._caching_enabled = False  # Placeholder for a more complex feature

        # Ensure internal directories exist
        self._trash_dir.mkdir(parents=True, exist_ok=True)
        self._backups_dir.mkdir(parents=True, exist_ok=True)

    # Path & Security Methods
    def _sanitize_path(self, filepath: str) -> str:
        """
        Clean and normalize file paths by resolving to an absolute,
        canonical path. This handles '..' and '.' and symlinks.

        Note: This method canonicalizes ANY path. Sandbox boundary checks
        are performed by methods like `get_absolute_path` and `is_within_sandbox`.
        """
        return str(Path(filepath).resolve())

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Convert a path relative to the sandbox into an absolute, canonical path.

        This method ensures the resulting path is within the sandbox boundaries.

        Args:
            relative_path: The path string relative to the sandbox root.

        Returns:
            The absolute, canonical path as a string.

        Raises:
            SandboxViolationError: If the `relative_path` attempts to resolve outside
                                   the sandbox.
        """
        # Expand any user (~) in the provided relative path
        expanded_relative_path = Path(relative_path).expanduser()

        # Join the sandbox path with the (possibly expanded) relative path.
        # The '/' operator for Path objects handles this elegantly.
        potential_full_path = self.sandbox / expanded_relative_path

        # Resolve the potential full path to get its absolute, canonical form.
        # This is critical for handling '..' within `relative_path` that
        # might try to escape the sandbox.
        resolved_full_path = potential_full_path.resolve()

        # SECURITY CHECK: Verify that the resolved path is actually within the sandbox.
        if not self.is_within_sandbox(str(resolved_full_path)):
            logger.warning(
                f"Attempted sandbox escape: '{relative_path}' resolves to "
                f"'{resolved_full_path}' which is outside the sandbox boundary '{self.sandbox}'."
            )
            raise SandboxViolationError(
                f"Path '{relative_path}' resolves to '{resolved_full_path}' "
                "which is outside the sandbox boundary."
            )
        return str(resolved_full_path)

    def get_relative_path(self, absolute_path: str) -> str:
        """
        Convert an absolute path to a path relative to the sandbox.

        Args:
            absolute_path: The absolute path string.

        Returns:
            The path string relative to the sandbox root.

        Raises:
            SandboxViolationError: If the `absolute_path` is not within the sandbox.
        """
        # Get the resolved, canonical form of the input absolute_path.
        resolved_absolute_path = Path(absolute_path).expanduser().resolve()

        # Check if the resolved absolute path is actually within the sandbox.
        if not self.is_within_sandbox(str(resolved_absolute_path)):
            logger.warning(
                f"Path '{absolute_path}' is outside sandbox when getting relative path."
            )
            raise SandboxViolationError(
                f"Path '{absolute_path}' is not within the sandbox "
                f"'{self.sandbox}'."
            )

        # Use Path.relative_to() to get the path relative to the sandbox.
        # This method will raise ValueError if it's not relative, but our
        # `is_within_sandbox` check already covers that case.
        relative_path_object = resolved_absolute_path.relative_to(self.sandbox)
        return str(relative_path_object)

    def is_within_sandbox(self, absolute_path: str) -> bool:
        """
        Check if an absolute path is strictly within the sandbox boundaries.

        The check is performed against the resolved, canonical paths to ensure
        accuracy and security (e.g., handling '..' or symlinks).

        Args:
            absolute_path: The absolute path string to check.

        Returns:
            True if the path is within the sandbox, False otherwise.
        """
        try:
            # Get the canonical, absolute path of the input path.
            # This handles '..', '.', and symlinks, giving us the true location.
            resolved_input_path = Path(absolute_path).expanduser().resolve()

            # Compare the resolved input path to the resolved sandbox path.
            # Path.is_relative_to() (Python 3.9+) is the most robust way to
            # check if one path is a subpath of another.
            # It returns True if `resolved_input_path` is the same as `self.sandbox`
            # or a subdirectory/file within `self.sandbox`.
            return resolved_input_path.is_relative_to(self.sandbox)
        except (
            OSError
        ) as e:  # Catch errors like broken symlinks which .resolve() might raise
            logger.debug(
                f"Could not resolve path '{absolute_path}': {e}. Considering it outside sandbox."
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error checking sandbox boundary for '{absolute_path}': {e}"
            )
            return False

    # File Operations
    def read_file_content(
        self,
        relative_file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        """
        Read file content with optional line range.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.
            start_line: Optional 1-based index of the starting line to read.
            end_line: Optional 1-based index of the ending line to read (inclusive).

        Returns:
            The content of the file (or specified lines) as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If there are insufficient permissions to read the file.
            SandboxViolationError: If the path is outside the sandbox.
            ValueError: If start_line > end_line or invalid line numbers.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            if not abs_file_path.is_file():
                logger.error(
                    f"Attempted to read non-existent or non-file path: {abs_file_path}"
                )
                raise FileNotFoundError(
                    f"File not found or is not a file: {relative_file_path}"
                )

            content_lines: List[str] = []
            with open(abs_file_path, "r", encoding=self._default_encoding) as f:
                if start_line is None and end_line is None:
                    content_lines = f.readlines()
                else:
                    if start_line is not None and start_line < 1:
                        raise ValueError("start_line must be 1 or greater.")
                    if end_line is not None and end_line < 1:
                        raise ValueError("end_line must be 1 or greater.")
                    if (
                        start_line is not None
                        and end_line is not None
                        and start_line > end_line
                    ):
                        raise ValueError("start_line cannot be greater than end_line.")

                    for i, line in enumerate(f, 1):
                        if start_line is not None and i < start_line:
                            continue
                        if end_line is not None and i > end_line:
                            break
                        content_lines.append(line)

            logger.info(f"Successfully read content from {relative_file_path}")
            return "".join(content_lines)

        except SandboxViolationError as e:
            logger.error(f"Read file failed due to sandbox violation: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found: {relative_file_path} - {e}")
            raise
        except PermissionError as e:
            logger.error(f"Permission denied to read {relative_file_path}: {e}")
            raise
        except UnicodeDecodeError as e:
            logger.error(
                f"Failed to decode file {relative_file_path} with encoding {self._default_encoding}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while reading {relative_file_path}: {e}"
            )
            raise

    def write_file(
        self,
        relative_file_path: str,
        content: str,
        line_number: Optional[int] = None,
        overwrite: bool = False,
    ) -> bool:
        """
        Write content to file with optional line insertion or full overwrite.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.
            content: The string content to write.
            line_number: Optional 1-based index to insert content. If None,
                         content replaces the whole file (if overwrite=True)
                         or appends (if overwrite=False, acts like append_to_file).
            overwrite: If True, completely overwrites the file. If False,
                       behaves like append_to_file if line_number is None,
                       or inserts if line_number is specified.

        Returns:
            True if write successful, False otherwise.

        Raises:
            SandboxViolationError: If the path is outside the sandbox.
            FileExistsError: If file exists and overwrite is False and line_number is None.
            ValueError: If line_number is invalid.
            PermissionError: If insufficient permissions.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            # Ensure parent directory exists
            self.ensure_directory_exists(
                str(abs_file_path.parent.relative_to(self.sandbox))
            )

            # Check file size limit
            if len(content.encode(self._default_encoding)) > self._max_file_size_bytes:
                logger.error(
                    f"Content size ({len(content.encode(self._default_encoding))} bytes) "
                    f"exceeds maximum allowed file size ({self._max_file_size_bytes} bytes)."
                )
                return False

            # Validate file extension
            if not self._validate_file_type(str(abs_file_path)):
                logger.warning(
                    f"File extension for {relative_file_path} is not allowed."
                )
                return False

            # If line_number is not None, we need to read and rewrite
            if line_number is not None:
                if line_number < 1:
                    logger.error("line_number must be 1 or greater for insertion.")
                    return False

                current_lines: List[str] = []
                if abs_file_path.exists() and abs_file_path.is_file():
                    try:
                        with open(
                            abs_file_path, "r", encoding=self._default_encoding
                        ) as f:
                            current_lines = f.readlines()
                    except Exception as e:
                        logger.warning(
                            f"Could not read existing file for line insertion {abs_file_path}: {e}"
                        )
                        # If we can't read, we'll treat it as empty and overwrite
                        current_lines = []

                # Adjust line_number to 0-based index for list insertion
                insert_idx = min(line_number - 1, len(current_lines))

                # Split content into lines to correctly insert if it contains newlines
                content_lines = content.splitlines(keepends=True)
                if (
                    not content_lines and content
                ):  # If content is not empty but splitlines makes it empty (e.g., just " "), handle it
                    content_lines = [content]

                # Ensure the last line has a newline if it's meant to be a full line insertion
                # and it's not the very end of the file.
                if (
                    content_lines
                    and not content_lines[-1].endswith("\n")
                    and insert_idx < len(current_lines)
                ):
                    content_lines[-1] += "\n"

                new_lines = (
                    current_lines[:insert_idx]
                    + content_lines
                    + current_lines[insert_idx:]
                )

                # Write the modified content back
                mode = "w"
                with open(abs_file_path, mode, encoding=self._default_encoding) as f:
                    f.writelines(new_lines)
                logger.info(
                    f"Content written/inserted at line {line_number} in {relative_file_path}"
                )
                return True

            else:  # No line_number specified
                if abs_file_path.exists() and abs_file_path.is_file():
                    if not overwrite:
                        # If not overwriting and file exists, delegate to append
                        return self.append_to_file(relative_file_path, content)
                    # Else, proceed with 'w' mode (overwrite)

                mode = "w"  # Overwrite or create new file
                with open(abs_file_path, mode, encoding=self._default_encoding) as f:
                    f.write(content)
                logger.info(
                    f"Content {'overwritten' if overwrite else 'written'} to {relative_file_path}"
                )
                return True

        except SandboxViolationError as e:
            logger.error(f"Write file failed due to sandbox violation: {e}")
            # Do not re-raise SandboxViolationError if the API suggests returning False for failure
            return False
        except OSError as e:
            logger.error(f"OS error writing to {relative_file_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while writing to {relative_file_path}: {e}"
            )
            return False

    def append_to_file(self, relative_file_path: str, content: str) -> bool:
        """
        Append content to end of file.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.
            content: The string content to append.

        Returns:
            True if append successful, False otherwise.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            # Ensure parent directory exists
            self.ensure_directory_exists(
                str(abs_file_path.parent.relative_to(self.sandbox))
            )

            # Check file size limit (after appending)
            current_size = (
                abs_file_path.stat().st_size if abs_file_path.is_file() else 0
            )
            if (
                current_size + len(content.encode(self._default_encoding))
                > self._max_file_size_bytes
            ):
                logger.error(
                    f"Appending content to {relative_file_path} would exceed "
                    f"maximum allowed file size ({self._max_file_size_bytes} bytes)."
                )
                return False

            # Validate file extension
            if not self._validate_file_type(str(abs_file_path)):
                logger.warning(
                    f"File extension for {relative_file_path} is not allowed."
                )
                return False

            with open(abs_file_path, "a", encoding=self._default_encoding) as f:
                f.write(content)
            logger.info(f"Content appended to {relative_file_path}")
            return True

        except SandboxViolationError as e:
            logger.error(f"Append to file failed due to sandbox violation: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error appending to {relative_file_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while appending to {relative_file_path}: {e}"
            )
            return False

    def delete_file(self, relative_path: str, soft: bool = True) -> bool:
        """
        Delete file (move to .trash if soft=True, else permanently delete).

        Args:
            relative_path: The path of the file relative to the sandbox root.
            soft: If True, moves the file to a .trash directory within the sandbox.
                  If False, permanently deletes the file.

        Returns:
            True if deletion successful, False otherwise.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_path))

            if not abs_file_path.is_file():
                logger.warning(
                    f"Attempted to delete non-existent or non-file: {abs_file_path}"
                )
                return False

            if soft:
                self._trash_dir.mkdir(
                    parents=True, exist_ok=True
                )  # Ensure trash dir exists
                # Create a unique name for the trashed file to avoid collisions
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                # Store original relative path in the filename or a metadata file
                trashed_name = f"{abs_file_path.name}_{timestamp}__{abs_file_path.parent.name.replace(os.sep, '_')}"
                # For more robust restoration, a small metadata file could be stored next to the trashed file.
                # For simplicity, we embed parent directory name.

                destination_path = self._trash_dir / trashed_name
                shutil.move(abs_file_path, destination_path)
                logger.info(
                    f"Soft deleted file: {relative_path} moved to {destination_path}"
                )
            else:
                os.remove(abs_file_path)
                logger.info(f"Permanently deleted file: {relative_path}")
            return True

        except SandboxViolationError as e:
            logger.error(f"Delete file failed due to sandbox violation: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error deleting file {relative_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while deleting {relative_path}: {e}"
            )
            return False

    def copy_file(self, source_relative_path: str, dest_relative_path: str) -> bool:
        """
        Copy file from source to destination within the sandbox.

        Args:
            source_relative_path: The path of the source file relative to the sandbox root.
            dest_relative_path: The path of the destination file relative to the sandbox root.

        Returns:
            True if copy successful, False otherwise.
        """
        try:
            abs_source_path = Path(self.get_absolute_path(source_relative_path))
            abs_dest_path = Path(self.get_absolute_path(dest_relative_path))

            if not abs_source_path.is_file():
                logger.error(
                    f"Source file not found or is not a file: {source_relative_path}"
                )
                return False

            # Ensure destination directory exists
            self.ensure_directory_exists(
                str(abs_dest_path.parent.relative_to(self.sandbox))
            )

            # Validate file extension of destination
            if not self._validate_file_type(str(abs_dest_path)):
                logger.warning(
                    f"Destination file extension for {dest_relative_path} is not allowed."
                )
                return False

            shutil.copy2(abs_source_path, abs_dest_path)  # copy2 preserves metadata
            logger.info(
                f"Copied file from {source_relative_path} to {dest_relative_path}"
            )
            return True

        except SandboxViolationError as e:
            logger.error(f"Copy file failed due to sandbox violation: {e}")
            return False
        except FileNotFoundError as e:
            logger.error(
                f"Source file not found for copy: {source_relative_path} - {e}"
            )
            return False
        except OSError as e:
            logger.error(
                f"OS error copying file from {source_relative_path} to {dest_relative_path}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while copying {source_relative_path} to {dest_relative_path}: {e}"
            )
            return False

    def move_file(self, source_relative_path: str, dest_relative_path: str) -> bool:
        """
        Move file from source to destination within the sandbox.

        Args:
            source_relative_path: The path of the source file relative to the sandbox root.
            dest_relative_path: The path of the destination file relative to the sandbox root.

        Returns:
            True if move successful, False otherwise.
        """
        try:
            abs_source_path = Path(self.get_absolute_path(source_relative_path))
            abs_dest_path = Path(self.get_absolute_path(dest_relative_path))

            if not abs_source_path.exists():  # Can be file or dir for move
                logger.error(f"Source path not found: {source_relative_path}")
                return False

            # Ensure destination directory exists
            self.ensure_directory_exists(
                str(abs_dest_path.parent.relative_to(self.sandbox))
            )

            # Validate file extension of destination if it's a file move
            if abs_source_path.is_file() and not self._validate_file_type(
                str(abs_dest_path)
            ):
                logger.warning(
                    f"Destination file extension for {dest_relative_path} is not allowed."
                )
                return False

            shutil.move(abs_source_path, abs_dest_path)
            logger.info(
                f"Moved file/directory from {source_relative_path} to {dest_relative_path}"
            )
            return True

        except SandboxViolationError as e:
            logger.error(f"Move file/directory failed due to sandbox violation: {e}")
            return False
        except FileNotFoundError as e:
            logger.error(
                f"Source path not found for move: {source_relative_path} - {e}"
            )
            return False
        except OSError as e:
            logger.error(
                f"OS error moving file/directory from {source_relative_path} to {dest_relative_path}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while moving {source_relative_path} to {dest_relative_path}: {e}"
            )
            return False

    # Directory Operations
    def list_directory_contents(
        self,
        relative_directory_path: str,
        recursive: bool = False,
        include_files: bool = True,
        include_directories: bool = True,
    ) -> List[Dict]:
        """
        List directory contents with filtering options.

        Args:
            relative_directory_path: The path of the directory relative to the sandbox root.
            recursive: If True, list contents of subdirectories as well.
            include_files: If True, include files in the list.
            include_directories: If True, include directories in the list.

        Returns:
            A list of dictionaries, each containing 'path' (relative to sandbox) and 'type' ('file' or 'directory').
            Returns an empty list if directory not found or cannot be accessed.
        """
        try:
            abs_dir_path = Path(self.get_absolute_path(relative_directory_path))

            if not abs_dir_path.is_dir():
                logger.warning(
                    f"Cannot list contents of non-directory path: {relative_directory_path}"
                )
                return []

            contents: List[Dict] = []

            # Use appropriate glob method based on recursion
            if recursive:
                # `rglob('*')` recursively finds all files and directories
                # We then filter them by type and whether they are within the sandbox.
                # `glob` and `rglob` return iterators of Path objects.
                # We explicitly convert `abs_path` to relative path to ensure output consistency
                for item_path in abs_dir_path.rglob("*"):
                    # Ensure each item found is still within the sandbox, just in case
                    # (though rglob starting from a sandboxed path should stay within it).
                    if self.is_within_sandbox(str(item_path)):
                        item_type = ""
                        if item_path.is_file():
                            if include_files:
                                item_type = "file"
                        elif item_path.is_dir():
                            if include_directories:
                                item_type = "directory"

                        if item_type:
                            contents.append(
                                {
                                    "path": self.get_relative_path(str(item_path)),
                                    "type": item_type,
                                }
                            )
            else:
                # `iterdir()` lists immediate children
                for item_path in abs_dir_path.iterdir():
                    item_type = ""
                    if item_path.is_file():
                        if include_files:
                            item_type = "file"
                    elif item_path.is_dir():
                        if include_directories:
                            item_type = "directory"

                    if item_type:
                        contents.append(
                            {
                                "path": self.get_relative_path(str(item_path)),
                                "type": item_type,
                            }
                        )

            logger.info(f"Listed contents of directory: {relative_directory_path}")
            return contents

        except SandboxViolationError as e:
            logger.error(
                f"List directory contents failed due to sandbox violation: {e}"
            )
            return []
        except FileNotFoundError:
            logger.warning(
                f"Directory not found for listing: {relative_directory_path}"
            )
            return []
        except PermissionError as e:
            logger.error(
                f"Permission denied to list directory {relative_directory_path}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while listing directory {relative_directory_path}: {e}"
            )
            return []

    def ensure_directory_exists(self, relative_directory_path: str) -> bool:
        """
        Create directory if it doesn't exist, ensuring it's within the sandbox.
        This version is slightly modified to align with the provided one previously
        but ensuring it uses `SandboxViolationError`.

        Args:
            relative_directory_path: The path of the directory relative to the
                                     sandbox root.

        Returns:
            True if the directory was successfully ensured (either created or
            already existed and is a directory). False if the path is invalid
            (e.g., attempts to escape sandbox), points to an existing non-directory
            file, or an OS error occurs (e.g., permissions).
        """
        try:
            # get_absolute_path will raise SandboxViolationError if path is outside
            abs_dir_path = Path(self.get_absolute_path(relative_directory_path))

            if abs_dir_path.exists():
                if not abs_dir_path.is_dir():
                    logger.error(
                        f"Error: Path '{relative_directory_path}' resolves to '{abs_dir_path}' "
                        "which is an existing file, not a directory. Cannot create directory."
                    )
                    return False
                else:
                    logger.debug(f"Directory already exists: {relative_directory_path}")
                    return True  # Already exists and is a directory

            # Create the directory, including parents
            abs_dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created: {relative_directory_path}")
            return True

        except SandboxViolationError as e:
            logger.error(
                f"Security Error: Cannot ensure directory '{relative_directory_path}'. "
                f"Path attempts to escape sandbox: {e}"
            )
            return False
        except OSError as e:
            logger.error(
                f"OS Error: Could not ensure directory '{relative_directory_path}': {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while ensuring directory {relative_directory_path}: {e}"
            )
            return False

    def create_directory(self, relative_directory_path: str) -> bool:
        """
        Create a new directory. This function fails if the directory already exists.

        Args:
            relative_directory_path: The path of the new directory relative to the sandbox root.

        Returns:
            True if the directory was created, False otherwise (e.g., if it already exists,
            sandbox violation, or OS error).
        """
        try:
            # get_absolute_path will handle sandbox validation
            abs_dir_path = Path(self.get_absolute_path(relative_directory_path))

            if abs_dir_path.exists():
                logger.warning(
                    f"Cannot create directory, path already exists: {relative_directory_path}"
                )
                return False

            abs_dir_path.mkdir(
                parents=True, exist_ok=False
            )  # exist_ok=False ensures it fails if it exists
            logger.info(f"New directory created: {relative_directory_path}")
            return True

        except SandboxViolationError as e:
            logger.error(f"Create directory failed due to sandbox violation: {e}")
            return False
        except (
            FileExistsError
        ):  # Specifically caught when exist_ok=False and directory exists
            logger.warning(
                f"Cannot create directory; '{relative_directory_path}' already exists."
            )
            return False
        except OSError as e:
            logger.error(
                f"OS Error creating directory '{relative_directory_path}': {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while creating directory {relative_directory_path}: {e}"
            )
            return False

    def delete_directory(
        self, relative_path: str, recursive: bool = False, soft: bool = True
    ) -> bool:
        """
        Delete directory (move to .trash if soft=True, else permanently delete).

        Args:
            relative_path: The path of the directory relative to the sandbox root.
            recursive: If True, recursively deletes directory and its contents.
                       If False and directory is not empty, deletion will fail.
            soft: If True, moves the directory to a .trash directory within the sandbox.
                  If False, permanently deletes the directory.

        Returns:
            True if deletion successful, False otherwise.
        """
        try:
            abs_dir_path = Path(self.get_absolute_path(relative_path))

            if not abs_dir_path.is_dir():
                logger.warning(
                    f"Attempted to delete non-existent or non-directory: {relative_path}"
                )
                return False

            # Check if directory is empty if not recursive
            if not recursive and list(
                abs_dir_path.iterdir()
            ):  # if generator is not empty
                logger.warning(
                    f"Cannot delete non-empty directory non-recursively: {relative_path}"
                )
                return False

            if soft:
                self._trash_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                trashed_name = f"{abs_dir_path.name}_{timestamp}_DIR__{abs_dir_path.parent.name.replace(os.sep, '_')}"
                destination_path = self._trash_dir / trashed_name
                shutil.move(abs_dir_path, destination_path)
                logger.info(
                    f"Soft deleted directory: {relative_path} moved to {destination_path}"
                )
            else:
                shutil.rmtree(
                    abs_dir_path
                )  # Recursively delete directory and its contents
                logger.info(f"Permanently deleted directory: {relative_path}")
            return True

        except SandboxViolationError as e:
            logger.error(f"Delete directory failed due to sandbox violation: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error deleting directory {relative_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while deleting directory {relative_path}: {e}"
            )
            return False

    # Search & Discovery
    def find_files_by_pattern(
        self, root_relative_path: str, pattern: str, recursive: bool = True
    ) -> List[str]:
        """
        Find files matching pattern (glob-style) within the sandbox.

        Args:
            root_relative_path: The path relative to the sandbox root where the search begins.
            pattern: Glob-style pattern (e.g., "*.txt", "data_*.csv").
            recursive: If True, search recursively into subdirectories.

        Returns:
            A list of matching file paths, relative to the sandbox root.
        """
        found_files: List[str] = []
        try:
            abs_root_path = Path(self.get_absolute_path(root_relative_path))

            if not abs_root_path.is_dir():
                logger.warning(f"Search root is not a directory: {root_relative_path}")
                return []

            # Use glob or rglob based on recursive flag
            search_method = abs_root_path.rglob if recursive else abs_root_path.glob

            for fpath in search_method(pattern):
                if fpath.is_file() and self.is_within_sandbox(str(fpath)):
                    found_files.append(self.get_relative_path(str(fpath)))

            logger.info(
                f"Found {len(found_files)} files matching pattern '{pattern}' in {root_relative_path}."
            )
            return found_files

        except SandboxViolationError as e:
            logger.error(f"Find files by pattern failed due to sandbox violation: {e}")
            return []
        except OSError as e:
            logger.error(
                f"OS error finding files by pattern in {root_relative_path}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while finding files by pattern in {root_relative_path}: {e}"
            )
            return []

    def find_files_by_extension(
        self, root_relative_path: str, extension: str, recursive: bool = True
    ) -> List[str]:
        """
        Find files with specific extension within the sandbox.

        Args:
            root_relative_path: The path relative to the sandbox root where the search begins.
            extension: The file extension (e.g., "txt", "csv", "py"). Do not include leading dot.
            recursive: If True, search recursively into subdirectories.

        Returns:
            A list of matching file paths, relative to the sandbox root.
        """
        # Ensure extension starts with a dot for the glob pattern
        if not extension.startswith("."):
            extension = "." + extension

        # Delegate to find_files_by_pattern
        return self.find_files_by_pattern(
            root_relative_path, f"*{extension}", recursive
        )

    def search_file_contents(
        self,
        relative_root_path: str,  # Added a root path argument for consistency
        pattern: str,
        file_paths: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Search file contents using regex pattern.

        Args:
            relative_root_path: The path relative to the sandbox root where to start search if `file_paths` is None.
            pattern: Regular expression pattern to search for.
            file_paths: Optional list of specific file paths (relative to sandbox) to search.
                        If None, all files in `relative_root_path` (recursively) are searched.

        Returns:
            A list of dictionaries, each containing:
            - 'file_path': The path of the file (relative to sandbox).
            - 'line_number': The 1-based line number where a match was found.
            - 'line_content': The content of the line where the match was found.
            - 'match_start': Start index of the match in the line.
            - 'match_end': End index of the match in the line.
        """
        results: List[Dict] = []
        try:
            re_pattern = re.compile(pattern)

            files_to_search: List[str]
            if file_paths is None:
                # If no specific files, find all files in the root_relative_path recursively
                files_to_search = self.find_files_by_pattern(
                    relative_root_path, "*", recursive=True
                )
            else:
                files_to_search = file_paths

            for rel_file_path in files_to_search:
                abs_file_path = Path(self.get_absolute_path(rel_file_path))

                if not abs_file_path.is_file():
                    logger.warning(
                        f"Skipping non-file or non-existent path during search: {rel_file_path}"
                    )
                    continue

                try:
                    with open(abs_file_path, "r", encoding=self._default_encoding) as f:
                        for i, line in enumerate(f, 1):
                            for match in re_pattern.finditer(line):
                                results.append(
                                    {
                                        "file_path": rel_file_path,
                                        "line_number": i,
                                        "line_content": line.rstrip(
                                            "\n"
                                        ),  # Remove trailing newline for cleaner output
                                        "match_start": match.start(),
                                        "match_end": match.end(),
                                    }
                                )
                except UnicodeDecodeError:
                    logger.warning(
                        f"Skipping binary or undecodable file: {rel_file_path}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Error reading file {rel_file_path} for content search: {e}"
                    )

            logger.info(
                f"Completed content search for pattern '{pattern}'. Found {len(results)} matches."
            )
            return results

        except SandboxViolationError as e:
            logger.error(f"Search file contents failed due to sandbox violation: {e}")
            return []
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return []
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during search file contents: {e}"
            )
            return []

    def get_file_info(self, relative_file_path: str) -> Dict:
        """
        Get file metadata (size, modified date, etc.).

        Args:
            relative_file_path: Path to the file relative to the sandbox root.

        Returns:
            A dictionary containing file metadata:
            - 'size_bytes': Size of the file in bytes.
            - 'created_time': Datetime object of creation time (platform dependent).
            - 'modified_time': Datetime object of last modification time.
            - 'accessed_time': Datetime object of last access time.
            - 'is_file': Boolean, True if it's a file.
            - 'is_directory': Boolean, True if it's a directory.
            - 'permissions': Octal representation of file permissions.
            Returns an empty dictionary if file not found or inaccessible.
        """
        try:
            abs_path = Path(self.get_absolute_path(relative_file_path))

            if not abs_path.exists():
                logger.warning(
                    f"File or directory not found for info: {relative_file_path}"
                )
                return {}

            stats = abs_path.stat()

            info = {
                "size_bytes": stats.st_size,
                "created_time": datetime.fromtimestamp(
                    stats.st_ctime
                ),  # ctime is creation time on some systems, change time on others
                "modified_time": datetime.fromtimestamp(stats.st_mtime),
                "accessed_time": datetime.fromtimestamp(stats.st_atime),
                "is_file": abs_path.is_file(),
                "is_directory": abs_path.is_dir(),
                "permissions": oct(stats.st_mode & 0o777),  # permissions in octal
            }
            logger.debug(f"Retrieved info for {relative_file_path}")
            return info

        except SandboxViolationError as e:
            logger.error(f"Get file info failed due to sandbox violation: {e}")
            return {}
        except FileNotFoundError:
            logger.warning(f"File not found for info: {relative_file_path}")
            return {}
        except PermissionError as e:
            logger.error(f"Permission denied to get info for {relative_file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while getting info for {relative_file_path}: {e}"
            )
            return {}

    # File Management
    def file_exists(self, relative_file_path: str) -> bool:
        """
        Check if file exists and is a file.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.

        Returns:
            True if the file exists and is a regular file, False otherwise.
        """
        try:
            abs_path = Path(self.get_absolute_path(relative_file_path))
            return abs_path.is_file()
        except SandboxViolationError:
            return False  # Path outside sandbox means it doesn't "exist" for us
        except Exception as e:
            logger.error(f"Error checking if file exists for {relative_file_path}: {e}")
            return False

    def directory_exists(self, relative_directory_path: str) -> bool:
        """
        Check if directory exists and is a directory.

        Args:
            relative_directory_path: Path to the directory relative to the sandbox root.

        Returns:
            True if the directory exists and is a directory, False otherwise.
        """
        try:
            abs_path = Path(self.get_absolute_path(relative_directory_path))
            return abs_path.is_dir()
        except SandboxViolationError:
            return False  # Path outside sandbox means it doesn't "exist" for us
        except Exception as e:
            logger.error(
                f"Error checking if directory exists for {relative_directory_path}: {e}"
            )
            return False

    def get_file_size(self, relative_file_path: str) -> int:
        """
        Get file size in bytes.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.

        Returns:
            File size in bytes. Returns -1 if file not found or inaccessible.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))
            if not abs_file_path.is_file():
                logger.warning(
                    f"Cannot get size of non-existent or non-file path: {relative_file_path}"
                )
                return -1
            return abs_file_path.stat().st_size
        except SandboxViolationError:
            logger.error(
                f"Get file size failed due to sandbox violation: {relative_file_path}"
            )
            return -1
        except FileNotFoundError:
            logger.warning(f"File not found for size check: {relative_file_path}")
            return -1
        except PermissionError as e:
            logger.error(f"Permission denied to get size for {relative_file_path}: {e}")
            return -1
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while getting file size for {relative_file_path}: {e}"
            )
            return -1

    def get_file_modified_time(self, relative_file_path: str) -> Optional[datetime]:
        """
        Get file last modified timestamp.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.

        Returns:
            Datetime object of last modification time, or None if file not found or inaccessible.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))
            if not abs_file_path.is_file():
                logger.warning(
                    f"Cannot get modified time of non-existent or non-file path: {relative_file_path}"
                )
                return None
            return datetime.fromtimestamp(abs_file_path.stat().st_mtime)
        except SandboxViolationError:
            logger.error(
                f"Get file modified time failed due to sandbox violation: {relative_file_path}"
            )
            return None
        except FileNotFoundError:
            logger.warning(
                f"File not found for modified time check: {relative_file_path}"
            )
            return None
        except PermissionError as e:
            logger.error(
                f"Permission denied to get modified time for {relative_file_path}: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while getting modified time for {relative_file_path}: {e}"
            )
            return None

    def touch_file(self, relative_file_path: str) -> bool:
        """
        Update file modified time. Creates the file if it doesn't exist.

        Args:
            relative_file_path: Path to the file relative to the sandbox root.

        Returns:
            True if successful, False otherwise.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            # Ensure parent directory exists
            self.ensure_directory_exists(
                str(abs_file_path.parent.relative_to(self.sandbox))
            )

            abs_file_path.touch()
            logger.info(f"Touched file: {relative_file_path}")
            return True
        except SandboxViolationError as e:
            logger.error(f"Touch file failed due to sandbox violation: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error touching file {relative_file_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while touching {relative_file_path}: {e}"
            )
            return False

    # Trash Management
    def empty_trash(self) -> int:
        """
        Permanently delete all files and directories in .trash directory.

        Returns:
            The number of items (files/directories) permanently deleted.
            Returns -1 on error.
        """
        deleted_count = 0
        try:
            if not self._trash_dir.is_dir():
                logger.info(
                    "Trash directory does not exist or is not a directory. Nothing to empty."
                )
                return 0

            for item in self._trash_dir.iterdir():
                try:
                    if item.is_file():
                        os.remove(item)
                    elif item.is_dir():
                        shutil.rmtree(item)
                    deleted_count += 1
                except OSError as e:
                    logger.warning(f"Failed to delete item in trash '{item}': {e}")

            logger.info(f"Emptied trash. Permanently deleted {deleted_count} items.")
            return deleted_count

        except Exception as e:
            logger.error(f"An unexpected error occurred while emptying trash: {e}")
            return -1

    def list_trash_contents(self) -> List[str]:
        """
        List all files and directories in trash directory (relative paths within trash).

        Returns:
            A list of strings, each representing a path relative to the .trash directory.
            Returns empty list if trash is empty or error.
        """
        contents: List[str] = []
        try:
            if not self._trash_dir.is_dir():
                return []

            for item in self._trash_dir.iterdir():
                contents.append(item.name)  # Get just the name within trash
            logger.info(f"Listed {len(contents)} items in trash.")
            return contents

        except OSError as e:
            logger.error(f"OS error listing trash contents: {e}")
            return []
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while listing trash contents: {e}"
            )
            return []

    def restore_from_trash(
        self, trashed_item_name: str, original_relative_path: Optional[str] = None
    ) -> bool:
        """
        Restore file/directory from trash.

        Args:
            trashed_item_name: The name of the item as it appears in the trash directory (e.g., from `list_trash_contents`).
            original_relative_path: Optional. The desired original path relative to the sandbox to restore to.
                                    If None, the system attempts to infer the original path from the trashed_item_name.
                                    Inferred paths are less reliable.

        Returns:
            True if restoration successful, False otherwise.
        """
        try:
            source_trash_path = self._trash_dir / trashed_item_name

            if not source_trash_path.exists():
                logger.warning(f"Item '{trashed_item_name}' not found in trash.")
                return False

            dest_path_str: str
            if original_relative_path:
                dest_path_str = original_relative_path
            else:
                # Attempt to infer original path. This is a simple heuristic.
                # If the name was generated with __<parent_name>, try to use that.
                parts = trashed_item_name.split("__")
                if len(parts) > 1:
                    original_parent_name = parts[-1].replace("_", os.sep)
                    # Check if original_parent_name is actually a path
                    if os.sep in original_parent_name:
                        # Reconstruct: take everything before the last __ and reconstruct path
                        original_file_name_part = "__".join(parts[:-1])
                        # Remove timestamp and directory marker from file name part
                        name_parts_no_ts = original_file_name_part.split("_")
                        if len(name_parts_no_ts) >= 2:  # "filename_timestamp"
                            original_file_name = "_".join(name_parts_no_ts[:-1])
                        elif "DIR" in original_file_name_part:  # for directories
                            original_file_name = (
                                "_".join(name_parts_no_ts[:-2])
                                if len(name_parts_no_ts) >= 3
                                else ""
                            )  # _DIR_ removed
                            if (
                                not original_file_name
                            ):  # if it was just name_timestamp_DIR
                                original_file_name = name_parts_no_ts[0]
                        else:
                            original_file_name = original_file_name_part

                        dest_path_str = os.path.join(
                            original_parent_name, original_file_name
                        )
                    else:  # If no os.sep, it was likely just the file name in sandbox root
                        dest_path_str = parts[0].rsplit("_", 1)[0]  # remove timestamp
                else:  # Fallback: assume it was originally in the sandbox root and try to remove timestamp
                    # Attempt to remove _YYYYMMDDHHMMSS and _DIR_ suffix
                    if "_DIR__" in trashed_item_name:
                        dest_path_str = trashed_item_name.rsplit("_DIR__", 1)[0]
                        dest_path_str = (
                            dest_path_str.rsplit("_", 1)[0]
                            if "_" in dest_path_str
                            else dest_path_str
                        )
                    else:
                        dest_path_str = trashed_item_name.rsplit("_", 1)[
                            0
                        ]  # remove _timestamp
                logger.warning(
                    f"No original path provided for '{trashed_item_name}'. "
                    f"Attempting to infer destination to: {dest_path_str}"
                )
                if not dest_path_str:
                    logger.error(
                        f"Failed to infer original path for '{trashed_item_name}'. Restore failed."
                    )
                    return False

            abs_dest_path = Path(
                self.get_absolute_path(dest_path_str)
            )  # Validate inferred/provided path

            # Ensure parent directory exists for restoration
            self.ensure_directory_exists(
                str(abs_dest_path.parent.relative_to(self.sandbox))
            )

            # If target exists, prevent overwriting
            if abs_dest_path.exists():
                logger.warning(
                    f"Cannot restore '{trashed_item_name}' to '{abs_dest_path}', destination already exists."
                )
                return False

            shutil.move(source_trash_path, abs_dest_path)
            logger.info(f"Restored '{trashed_item_name}' from trash to {dest_path_str}")
            return True

        except SandboxViolationError as e:
            logger.error(f"Restore from trash failed due to sandbox violation: {e}")
            return False
        except FileNotFoundError as e:
            logger.error(f"Source item not found in trash: {trashed_item_name} - {e}")
            return False
        except OSError as e:
            logger.error(
                f"OS error restoring '{trashed_item_name}' to {original_relative_path}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while restoring '{trashed_item_name}': {e}"
            )
            return False

    def get_trash_size(self) -> int:
        """
        Get total size of trash directory in bytes.

        Returns:
            Total size in bytes, or -1 on error.
        """
        total_size = 0
        try:
            if not self._trash_dir.is_dir():
                return 0

            for item in self._trash_dir.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
            logger.info(f"Calculated trash size: {total_size} bytes.")
            return total_size

        except OSError as e:
            logger.error(f"OS error getting trash size: {e}")
            return -1
        except Exception as e:
            logger.error(f"An unexpected error occurred while getting trash size: {e}")
            return -1

    # Backup & Versioning
    def create_backup(
        self, relative_file_path: str, backup_suffix: str = ".bak"
    ) -> Optional[str]:
        """
        Create backup of file with timestamp in the .backups directory.

        Args:
            relative_file_path: The path of the file relative to the sandbox root.
            backup_suffix: Suffix to add to the backup file name before the timestamp.

        Returns:
            The relative path of the created backup file, or None if unsuccessful.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            if not abs_file_path.is_file():
                logger.warning(
                    f"Cannot create backup: file not found or is not a file: {relative_file_path}"
                )
                return None

            self._backups_dir.mkdir(parents=True, exist_ok=True)

            # Create a backup path structure: backups/<relative_path_to_file>/filename.suffix.timestamp
            backup_sub_dir_path = self._backups_dir / self.get_relative_path(
                str(abs_file_path.parent)
            )
            backup_sub_dir_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_filename = f"{abs_file_path.name}{backup_suffix}_{timestamp}"
            backup_abs_path = backup_sub_dir_path / backup_filename

            shutil.copy2(abs_file_path, backup_abs_path)

            backup_relative_path = self.get_relative_path(str(backup_abs_path))
            logger.info(
                f"Created backup for {relative_file_path} at {backup_relative_path}"
            )
            return backup_relative_path

        except SandboxViolationError as e:
            logger.error(f"Create backup failed due to sandbox violation: {e}")
            return None
        except FileNotFoundError:
            logger.error(f"File not found for backup: {relative_file_path}")
            return None
        except OSError as e:
            logger.error(f"OS error creating backup for {relative_file_path}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while creating backup for {relative_file_path}: {e}"
            )
            return None

    def list_backups(self, relative_file_path: str) -> List[str]:
        """
        List all backup files for a given original file within the sandbox.

        Args:
            relative_file_path: The path of the original file relative to the sandbox root.

        Returns:
            A list of relative paths (within sandbox) to the backup files.
        """
        backups: List[str] = []
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            backup_sub_dir_path = self._backups_dir / self.get_relative_path(
                str(abs_file_path.parent)
            )

            if not backup_sub_dir_path.is_dir():
                return []  # No backups directory for this file's parent

            # Construct pattern for glob: original_filename.*_YYYYMMDDHHMMSS
            # This relies on the naming convention used in create_backup
            original_filename_stem = abs_file_path.name

            # rglob is safer here to account for any depth in backup paths
            for backup_path in backup_sub_dir_path.glob(f"{original_filename_stem}*_*"):
                if backup_path.is_file() and self.is_within_sandbox(str(backup_path)):
                    backups.append(self.get_relative_path(str(backup_path)))

            logger.info(f"Listed {len(backups)} backups for {relative_file_path}.")
            return backups

        except SandboxViolationError as e:
            logger.error(f"List backups failed due to sandbox violation: {e}")
            return []
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while listing backups for {relative_file_path}: {e}"
            )
            return []

    def restore_from_backup(
        self, backup_relative_path: str, target_relative_path: Optional[str] = None
    ) -> bool:
        """
        Restore file from backup.

        Args:
            backup_relative_path: The relative path (within sandbox) to the backup file to restore.
            target_relative_path: Optional. The relative path (within sandbox) where the file should be restored.
                                  If None, the function attempts to infer the original location based on the
                                  backup file naming convention.

        Returns:
            True if restoration successful, False otherwise.
        """
        try:
            abs_backup_path = Path(self.get_absolute_path(backup_relative_path))

            if not abs_backup_path.is_file():
                logger.warning(
                    f"Backup file not found or is not a file: {backup_relative_path}"
                )
                return False

            abs_target_path: Path
            if target_relative_path:
                abs_target_path = Path(self.get_absolute_path(target_relative_path))
            else:
                # Infer original path from backup_relative_path
                # Expected format: .backups/<original_parent_path>/filename.suffix_timestamp
                # Need to strip .backups/ and the suffix_timestamp

                # Get path relative to .backups dir itself
                relative_to_backups = abs_backup_path.relative_to(self._backups_dir)

                # Split the filename from suffix_timestamp
                filename_parts = relative_to_backups.name.rsplit("_", 1)
                inferred_filename = filename_parts[0]  # This still includes .suffix

                # If backup_suffix was used, remove it from inferred_filename
                # This is heuristic, and better done by parsing original_filename from the backup name.
                # A more robust solution might embed the original_relative_path into the backup filename or a sidecar file.
                # For now, assume common suffix removed for simplicity.
                # Example: `file.txt.bak_2024...` -> `file.txt`
                for suffix in [".bak", ".backup"]:  # Common suffixes
                    if inferred_filename.endswith(suffix):
                        inferred_filename = inferred_filename[: -len(suffix)]
                        break

                # Reconstruct the original parent path by stripping the filename
                inferred_parent_path = relative_to_backups.parent

                abs_target_path = (
                    self.sandbox / inferred_parent_path / inferred_filename
                )
                logger.info(
                    f"No target path provided for restoration. Inferred target: "
                    f"'{self.get_relative_path(str(abs_target_path))}'"
                )

            # Ensure target parent directory exists
            self.ensure_directory_exists(
                str(abs_target_path.parent.relative_to(self.sandbox))
            )

            # If target exists, overwrite it. A backup restoration usually means replacing the current.
            if abs_target_path.exists():
                if abs_target_path.is_file():
                    os.remove(abs_target_path)
                elif abs_target_path.is_dir():
                    # If target is a directory but we're restoring a file, this is an issue.
                    logger.error(
                        f"Cannot restore file '{backup_relative_path}' to '{abs_target_path}', "
                        f"which is an existing directory."
                    )
                    return False

            shutil.copy2(abs_backup_path, abs_target_path)
            logger.info(
                f"Restored file from backup {backup_relative_path} to {self.get_relative_path(str(abs_target_path))}"
            )
            return True

        except SandboxViolationError as e:
            logger.error(f"Restore from backup failed due to sandbox violation: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"Backup file not found: {backup_relative_path}")
            return False
        except OSError as e:
            logger.error(f"OS error restoring from backup {backup_relative_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while restoring from backup {backup_relative_path}: {e}"
            )
            return False

    # Utility Methods
    def get_sandbox_root(self) -> str:
        """
        Get absolute path to sandbox root directory.

        Returns:
            The absolute path of the sandbox root as a string.
        """
        return str(self.sandbox)

    def get_available_space(self) -> int:
        """
        Get available disk space in sandbox directory in bytes.

        Returns:
            Available space in bytes, or -1 on error.
        """
        try:
            # shutil.disk_usage provides total, used, and free space (bytes)
            # This is more cross-platform than os.statvfs
            total, used, free = shutil.disk_usage(self.sandbox)
            logger.debug(f"Available space in sandbox: {free} bytes.")
            return free
        except OSError as e:
            logger.error(
                f"OS error getting available space for sandbox {self.sandbox}: {e}"
            )
            return -1
        except Exception as e:
            logger.error(f"An unexpected error occurred getting available space: {e}")
            return -1

    def get_sandbox_stats(self) -> Dict:
        """
        Get sandbox statistics (total files, directories, size, etc.).

        Returns:
            A dictionary containing sandbox statistics.
            - 'total_files': Number of files.
            - 'total_directories': Number of directories.
            - 'total_size_bytes': Total size of files within the sandbox.
            - 'last_modified': Datetime of the most recently modified item.
            - 'available_space_bytes': Disk space available in the sandbox partition.
        """
        total_files = 0
        total_directories = 0
        total_size_bytes = 0
        last_modified: Optional[datetime] = None

        try:
            # Walk through all items in the sandbox recursively
            for item_path in self.sandbox.rglob("*"):
                if item_path.is_file():
                    total_files += 1
                    try:
                        file_size = item_path.stat().st_size
                        total_size_bytes += file_size
                        mod_time = datetime.fromtimestamp(item_path.stat().st_mtime)
                        if last_modified is None or mod_time > last_modified:
                            last_modified = mod_time
                    except OSError as e:
                        logger.warning(f"Could not get stats for file {item_path}: {e}")
                elif item_path.is_dir():
                    total_directories += 1
                    try:
                        mod_time = datetime.fromtimestamp(item_path.stat().st_mtime)
                        if last_modified is None or mod_time > last_modified:
                            last_modified = mod_time
                    except OSError as e:
                        logger.warning(
                            f"Could not get stats for directory {item_path}: {e}"
                        )

            available_space = self.get_available_space()

            stats = {
                "total_files": total_files,
                "total_directories": total_directories,
                "total_size_bytes": total_size_bytes,
                "last_modified": last_modified,
                "available_space_bytes": available_space,
                "sandbox_root": str(self.sandbox),
            }
            logger.info("Generated sandbox statistics.")
            return stats

        except Exception as e:
            logger.error(
                f"An unexpected error occurred while getting sandbox statistics: {e}"
            )
            return {
                "total_files": -1,
                "total_directories": -1,
                "total_size_bytes": -1,
                "last_modified": None,
                "available_space_bytes": -1,
                "sandbox_root": str(self.sandbox),
                "error": str(e),
            }

    # Advanced Features
    def watch_directory(self, relative_directory_path: str, callback: Callable) -> bool:
        """
        Set up file system monitoring for directory.
        NOTE: This is a placeholder as robust file system monitoring typically requires
              external libraries (e.g., `watchdog`) and running in a separate thread/process.
              A simple polling mechanism is inefficient and generally not recommended for production.

        Args:
            relative_directory_path: The path of the directory relative to the sandbox root.
            callback: A callable function that will be executed when a change is detected.
                      Signature: `callback(event_type: str, file_path: str)`

        Returns:
            False, indicating that this feature is not fully implemented or requires external setup.
        """
        logger.warning(
            "The `watch_directory` function is a placeholder and not fully implemented "
            "for robust real-time file system monitoring. Consider using libraries "
            "like 'watchdog' for production use cases."
        )
        try:
            abs_dir_path = Path(self.get_absolute_path(relative_directory_path))
            if not abs_dir_path.is_dir():
                logger.error(
                    f"Cannot watch non-existent or non-directory path: {relative_directory_path}"
                )
                return False

            # Simple, inefficient polling example (DO NOT USE FOR PRODUCTION):
            # This would need to run in a separate thread and continuously check.
            # last_known_state = {}
            # for item in abs_dir_path.rglob('*'):
            #     last_known_state[str(item)] = item.stat().st_mtime
            # def _poll():
            #     nonlocal last_known_state
            #     while True: # This would be a loop in a separate thread
            #         current_state = {}
            #         for item in abs_dir_path.rglob('*'):
            #             current_state[str(item)] = item.stat().st_mtime
            #
            #         # Detect changes
            #         for path_str, mtime in current_state.items():
            #             if path_str not in last_known_state:
            #                 callback("created", self.get_relative_path(path_str))
            #             elif last_known_state[path_str] != mtime:
            #                 callback("modified", self.get_relative_path(path_str))
            #         for path_str in last_known_state:
            #             if path_str not in current_state:
            #                 callback("deleted", self.get_relative_path(path_str))
            #
            #         last_known_state = current_state
            #         time.sleep(5) # Poll every 5 seconds (configurable)
            # # You would start `_poll` in a new thread.

            return False  # Indicate not fully operational for real-time monitoring

        except SandboxViolationError as e:
            logger.error(f"Watch directory failed due to sandbox violation: {e}")
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred trying to set up watch for {relative_directory_path}: {e}"
            )
            return False

    def create_symlink(
        self, target_relative_path: str, link_relative_path: str
    ) -> bool:
        """
        Create symbolic link within the sandbox.

        Args:
            target_relative_path: The relative path to the existing file or directory the symlink will point to.
            link_relative_path: The relative path where the new symlink will be created.

        Returns:
            True if symlink created successfully, False otherwise.
        """
        try:
            abs_target_path = Path(self.get_absolute_path(target_relative_path))
            abs_link_path = Path(self.get_absolute_path(link_relative_path))

            if not abs_target_path.exists():
                logger.error(f"Symlink target does not exist: {target_relative_path}")
                return False

            if abs_link_path.exists():
                logger.warning(
                    f"Symlink creation failed: link path already exists: {link_relative_path}"
                )
                return False

            # Ensure parent directory for the symlink exists
            self.ensure_directory_exists(
                str(abs_link_path.parent.relative_to(self.sandbox))
            )

            # Note: os.symlink target can be absolute or relative.
            # Using absolute target path here as sandbox means all targets should be inside.
            os.symlink(abs_target_path, abs_link_path)
            logger.info(
                f"Created symlink from {link_relative_path} to {target_relative_path}"
            )
            return True

        except SandboxViolationError as e:
            logger.error(f"Create symlink failed due to sandbox violation: {e}")
            return False
        except OSError as e:
            logger.error(
                f"OS error creating symlink from {link_relative_path} to {target_relative_path}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while creating symlink {link_relative_path}: {e}"
            )
            return False

    def get_file_hash(
        self, relative_file_path: str, algorithm: str = "sha256"
    ) -> Optional[str]:
        """
        Calculate file hash for integrity checking.

        Args:
            relative_file_path: The path of the file relative to the sandbox root.
            algorithm: Hashing algorithm to use (e.g., "md5", "sha1", "sha256", "sha512").

        Returns:
            The hexadecimal digest of the file hash, or None if file not found/inaccessible or invalid algorithm.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            if not abs_file_path.is_file():
                logger.warning(
                    f"Cannot calculate hash for non-existent or non-file path: {relative_file_path}"
                )
                return None

            # Get hash function from hashlib
            hash_func = getattr(hashlib, algorithm, None)
            if hash_func is None:
                logger.error(
                    f"Unsupported hashing algorithm: {algorithm}. Supported: {hashlib.algorithms_available}"
                )
                return None

            hasher = hash_func()
            chunk_size = 4096  # Read in chunks to handle large files
            with open(abs_file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)

            return hasher.hexdigest()

        except SandboxViolationError as e:
            logger.error(f"Get file hash failed due to sandbox violation: {e}")
            return None
        except FileNotFoundError:
            logger.warning(f"File not found for hash calculation: {relative_file_path}")
            return None
        except PermissionError as e:
            logger.error(
                f"Permission denied to read file for hash: {relative_file_path} - {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while calculating hash for {relative_file_path}: {e}"
            )
            return None

    def compress_directory(
        self,
        relative_directory_path: str,
        output_relative_path: Optional[str] = None,
        archive_format: str = "zip",
    ) -> Optional[str]:
        """
        Create compressed archive of directory within the sandbox.

        Args:
            relative_directory_path: The path of the directory relative to the sandbox root to compress.
            output_relative_path: Optional. The desired path for the output archive relative to the sandbox root.
                                  If None, defaults to `<directory_name>.zip` (or .tar/.gztar) in sandbox root.
            archive_format: 'zip', 'tar', 'gztar', 'bztar', 'xztar'.

        Returns:
            The relative path to the created archive file, or None if compression fails.
        """
        try:
            abs_dir_path = Path(self.get_absolute_path(relative_directory_path))

            if not abs_dir_path.is_dir():
                logger.error(
                    f"Cannot compress non-existent or non-directory path: {relative_directory_path}"
                )
                return None

            # Determine base name for archive (without format extension)
            archive_base_name: str
            if output_relative_path:
                abs_output_path = Path(self.get_absolute_path(output_relative_path))
                # Ensure output directory exists if provided
                self.ensure_directory_exists(
                    str(abs_output_path.parent.relative_to(self.sandbox))
                )
                archive_base_name = str(
                    abs_output_path.with_suffix("")
                )  # Remove any existing suffix
            else:
                archive_base_name = str(
                    self.sandbox / abs_dir_path.name
                )  # Default to sandbox root / dir_name

            # shutil.make_archive returns the full path to the archive, including extension
            # It also creates the directory if needed.
            archive_full_path = shutil.make_archive(
                base_name=archive_base_name,
                format=archive_format,
                root_dir=str(
                    self.sandbox
                ),  # This is the base directory to start the archive from
                base_dir=str(
                    abs_dir_path.relative_to(self.sandbox)
                ),  # This is the directory relative to root_dir to archive
            )

            # Ensure the created archive is within the sandbox
            if not self.is_within_sandbox(archive_full_path):
                logger.error(
                    f"Generated archive '{archive_full_path}' is outside sandbox. Deleting unsafe archive."
                )
                os.remove(archive_full_path)  # Clean up unsafe file
                raise SandboxViolationError(
                    "Archive creation resulted in a file outside sandbox."
                )

            relative_archive_path = self.get_relative_path(archive_full_path)
            logger.info(
                f"Compressed directory {relative_directory_path} to {relative_archive_path} (format: {archive_format})"
            )
            return relative_archive_path

        except SandboxViolationError as e:
            logger.error(f"Compress directory failed due to sandbox violation: {e}")
            return None
        except FileNotFoundError:
            logger.error(
                f"Directory not found for compression: {relative_directory_path}"
            )
            return None
        except shutil.ReadError as e:
            logger.error(
                f"Error reading directory for compression {relative_directory_path}: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while compressing {relative_directory_path}: {e}"
            )
            return None

    def extract_archive(
        self, archive_relative_path: str, extract_to_relative_path: Optional[str] = None
    ) -> bool:
        """
        Extract compressed archive within the sandbox.

        Args:
            archive_relative_path: The path of the archive file relative to the sandbox root.
            extract_to_relative_path: Optional. The path relative to the sandbox root where contents will be extracted.
                                      If None, extracts to the sandbox root directory.

        Returns:
            True if extraction successful, False otherwise.
        """
        try:
            abs_archive_path = Path(self.get_absolute_path(archive_relative_path))

            if not abs_archive_path.is_file():
                logger.error(
                    f"Archive file not found or is not a file: {archive_relative_path}"
                )
                return False

            abs_extract_to_path: Path
            if extract_to_relative_path:
                abs_extract_to_path = Path(
                    self.get_absolute_path(extract_to_relative_path)
                )
            else:
                abs_extract_to_path = self.sandbox

            # Ensure the destination directory exists
            self.ensure_directory_exists(
                str(abs_extract_to_path.relative_to(self.sandbox))
            )

            # Prevent zip-slip or similar vulnerabilities by checking paths inside archive
            # This is a critical security measure.
            def _check_extraction_path(member_path: str) -> Path:
                full_member_path = Path(abs_extract_to_path) / member_path
                # Resolve to canonical path. This handles `..` and symlinks within the archive paths.
                resolved_member_path = full_member_path.resolve()
                if not resolved_member_path.is_relative_to(
                    abs_extract_to_path.resolve()
                ):
                    raise SandboxViolationError(
                        f"Archive contains path attempting to escape extraction directory: {member_path}"
                    )
                if not resolved_member_path.is_relative_to(
                    self.sandbox
                ):  # Double check against sandbox itself
                    raise SandboxViolationError(
                        f"Archive contains path attempting to escape sandbox: {member_path}"
                    )
                return full_member_path

            # Use zipfile or tarfile directly for fine-grained control
            if zipfile.is_zipfile(abs_archive_path):
                with zipfile.ZipFile(abs_archive_path, "r") as zip_ref:
                    for member_name in zip_ref.namelist():
                        # Validate the member path
                        safe_path = _check_extraction_path(member_name)
                        # Extract individual member to safe path
                        zip_ref.extract(member_name, abs_extract_to_path)
                        # Move to correct location if needed
                        extracted_path = abs_extract_to_path / member_name
                        if extracted_path != safe_path:
                            extracted_path.rename(safe_path)
            elif tarfile.is_tarfile(abs_archive_path):
                with tarfile.open(abs_archive_path, "r") as tar_ref:
                    for member in tar_ref.getmembers():
                        # Validate the member path
                        safe_path = _check_extraction_path(member.name)
                        # Extract individual member to safe path
                        tar_ref.extract(member, abs_extract_to_path)
                        # Move to correct location if needed
                        extracted_path = abs_extract_to_path / member.name
                        if extracted_path != safe_path:
                            extracted_path.rename(safe_path)
            else:
                logger.error(
                    f"Unsupported archive format for {archive_relative_path}. Must be zip or tar-based."
                )
                return False

            logger.info(
                f"Extracted archive {archive_relative_path} to {self.get_relative_path(str(abs_extract_to_path))}"
            )
            return True

        except SandboxViolationError as e:
            logger.error(f"Extract archive failed due to sandbox violation: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"Archive file not found: {archive_relative_path}")
            return False
        except (zipfile.BadZipFile, tarfile.ReadError, tarfile.FilterError) as e:
            logger.error(
                f"Error reading or extracting archive {archive_relative_path}: {e}"
            )
            return False
        except OSError as e:
            logger.error(
                f"OS error during archive extraction {archive_relative_path}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while extracting archive {archive_relative_path}: {e}"
            )
            return False

    # Error Handling & Logging (Placeholders/basic implementations)
    # For a real system, these would interact with a more persistent logging/auditing system.

    def _log_operation(
        self, operation_type: str, status: str, path: str, details: Dict = None
    ) -> None:
        """Internal method to log operation history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "status": status,
            "path": path,
            "details": details if details is not None else {},
        }
        self._operation_history.append(entry)
        if len(self._operation_history) > 100:  # Keep history trimmed
            self._operation_history.pop(0)

        if status == "error":
            self._last_error_message = entry["details"].get(
                "message", "An unspecified error occurred."
            )

    def get_last_error(self) -> str:
        """
        Get last operation error message.

        Returns:
            The last error message as a string, or an empty string if no errors.
        """
        return self._last_error_message if self._last_error_message else ""

    def clear_error_log(self) -> None:
        """
        Clear the internal error log message.
        (For persistent log files, this would involve log rotation/truncation).
        """
        self._last_error_message = None
        logger.info("Internal last error message cleared.")

    def get_operation_history(self, limit: int = 100) -> List[Dict]:
        """
        Get audit trail of file operations.

        Args:
            limit: Maximum number of history entries to return.

        Returns:
            A list of dictionaries, each representing a logged file operation.
        """
        return self._operation_history[-limit:]

    # Configuration
    def set_default_encoding(self, encoding: str) -> None:
        """
        Set default file encoding for read/write operations.

        Args:
            encoding: The encoding string (e.g., "utf-8", "latin-1").
        """
        try:
            # Test if encoding is valid
            "".encode(encoding).decode(encoding)
            self._default_encoding = encoding
            logger.info(f"Default encoding set to: {encoding}")
        except LookupError:
            logger.error(
                f"Invalid encoding name provided: {encoding}. Encoding not changed."
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred setting encoding: {e}")

    def set_backup_retention_days(self, days: int) -> None:
        """
        Set number of days to retain backup files.

        Args:
            days: Number of days to retain backups. Set to 0 for infinite retention.
        """
        if days < 0:
            logger.warning(
                "Backup retention days cannot be negative. Setting to 0 (infinite)."
            )
            self._backup_retention_days = 0
        else:
            self._backup_retention_days = days
            logger.info(f"Backup retention set to {days} days.")

    def set_max_file_size(self, size_mb: int) -> None:
        """
        Set maximum allowed file size in MB for writes.

        Args:
            size_mb: Maximum allowed file size in megabytes. Set to 0 for no limit.
        """
        if size_mb < 0:
            logger.warning("Max file size cannot be negative. Setting to 0 (no limit).")
            self._max_file_size_bytes = 0
        else:
            self._max_file_size_bytes = size_mb * 1024 * 1024  # Convert MB to bytes
            logger.info(
                f"Max file size set to {size_mb} MB ({self._max_file_size_bytes} bytes)."
            )

    # Security Enhancements
    def _validate_file_type(self, file_path: str) -> bool:
        """
        Check if file extension is allowed based on the `_allowed_extensions` whitelist.

        Args:
            file_path: The absolute path of the file to check.

        Returns:
            True if the file extension is allowed or if no whitelist is set, False otherwise.
        """
        if self._allowed_extensions is None:  # No whitelist set, all extensions allowed
            return True

        file_extension = Path(file_path).suffix.lower()
        if not file_extension:  # File has no extension
            return "" in self._allowed_extensions  # Check if empty extension is allowed
        return file_extension in self._allowed_extensions

    def _scan_for_malicious_content(self, content: str) -> bool:
        """
        Basic content validation for security.
        NOTE: This is a placeholder. Real-world malicious content scanning
              requires integration with antivirus/malware detection libraries
              or services. This implementation is purely illustrative.

        Args:
            content: The string content to scan.

        Returns:
            True if content appears safe, False if potentially malicious.
        """
        # Very basic check: look for common malicious patterns (e.g., shell commands, specific script headers)
        suspicious_patterns = [
            r"rm -rf",
            r"sudo",
            r"curl",
            r"wget",
            r"powershell",
            r"Invoke-Expression",
            r"<?php system",
            r"<script>alert",
            r"EXECUTE\s+xp_cmdshell",
        ]
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(
                    f"Potential malicious content detected: {pattern} in file content."
                )
                return False
        return True

    def set_allowed_extensions(self, extensions: Optional[List[str]]) -> None:
        """
        Set whitelist of allowed file extensions.
        Extensions should be provided *without* leading dots (e.g., "txt", "pdf", "py").
        An empty string ("") can be included to allow files with no extension.
        Setting to None means all extensions are allowed.

        Args:
            extensions: A list of allowed extensions (lowercase), or None to allow all.
        """
        if extensions is None:
            self._allowed_extensions = None
            logger.info("All file extensions are now allowed.")
        else:
            # Convert to lowercase and add leading dots for internal consistency
            self._allowed_extensions = [
                f".{ext.lower()}" if ext else "" for ext in extensions
            ]
            logger.info(f"Allowed file extensions set to: {self._allowed_extensions}")

    # Performance (Placeholders)
    def enable_caching(self, enable: bool = True) -> None:
        """
        Enable/disable file content caching.
        NOTE: This is a placeholder. Actual caching implementation would involve
              a dictionary or LRU cache to store file contents and invalidate them.
        """
        self._caching_enabled = enable
        logger.info(f"File content caching {'enabled' if enable else 'disabled'}.")

    def preload_directory(self, relative_directory_path: str) -> None:
        """
        Preload directory contents into cache.
        NOTE: This is a placeholder. Requires caching to be implemented.
        """
        if not self._caching_enabled:
            logger.warning("Caching is not enabled. Cannot preload directory.")
            return

        try:
            abs_dir_path = Path(self.get_absolute_path(relative_directory_path))
            if not abs_dir_path.is_dir():
                logger.warning(
                    f"Cannot preload non-directory path: {relative_directory_path}"
                )
                return

            logger.info(
                f"Preloading contents of directory: {relative_directory_path} (placeholder for caching)."
            )
            # In a real implementation, you would iterate files and read them into cache.
            # for file_path in abs_dir_path.rglob('*'):
            #     if file_path.is_file():
            #         try:
            #             content = self.read_file_content(self.get_relative_path(str(file_path)))
            #             # Store content in a cache (e.g., self._cache[str(file_path)] = content)
            #         except Exception as e:
            #             logger.warning(f"Failed to preload {file_path}: {e}")

        except SandboxViolationError as e:
            logger.error(f"Preload directory failed due to sandbox violation: {e}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while preloading directory {relative_directory_path}: {e}"
            )

    # Integration (Placeholders)
    def export_to_json(self, relative_file_path: str) -> Dict:
        """
        Export file metadata as JSON. Reads file content and basic info.
        NOTE: This is a basic export; full JSON representation of arbitrary files
              can be complex. For binaries, content would be base64 encoded.
        """
        try:
            abs_file_path = Path(self.get_absolute_path(relative_file_path))
            if not abs_file_path.is_file():
                logger.error(
                    f"Cannot export non-existent or non-file to JSON: {relative_file_path}"
                )
                return {"error": "File not found or is not a file."}

            file_info = self.get_file_info(relative_file_path)
            content = None
            try:
                content = self.read_file_content(relative_file_path)
            except Exception:
                # If content can't be read as text, try binary (base64 encode)
                try:
                    with open(abs_file_path, "rb") as f:
                        import base64

                        content = base64.b64encode(f.read()).decode(
                            self._default_encoding
                        )
                        file_info["content_encoding"] = "base64"
                except Exception as e:
                    logger.warning(
                        f"Could not read content for JSON export from {relative_file_path}: {e}"
                    )
                    content = "[Content not readable or encoded]"

            json_data = {
                "file_path": relative_file_path,
                "metadata": file_info,
                "content": content,
            }
            logger.info(
                f"Exported {relative_file_path} metadata and content to JSON structure."
            )
            return json_data

        except SandboxViolationError as e:
            logger.error(f"Export to JSON failed due to sandbox violation: {e}")
            return {"error": f"Sandbox violation: {e}"}
        except Exception as e:
            logger.error(
                f"An unexpected error occurred exporting {relative_file_path} to JSON: {e}"
            )
            return {"error": f"An unexpected error occurred: {e}"}

    def import_from_json(self, json_data: Dict) -> bool:
        """
        Restore file from JSON metadata and content.
        This assumes the `json_data` structure matches the output of `export_to_json`.

        Args:
            json_data: A dictionary containing file path, metadata, and content.

        Returns:
            True if file restored successfully, False otherwise.
        """
        try:
            relative_file_path = json_data.get("file_path")
            content = json_data.get("content")
            content_encoding = json_data.get("metadata", {}).get("content_encoding")

            if not relative_file_path or content is None:
                logger.error(
                    "Invalid JSON data for import: missing 'file_path' or 'content'."
                )
                return False

            abs_file_path = Path(self.get_absolute_path(relative_file_path))

            # Ensure parent directory exists
            self.ensure_directory_exists(
                str(abs_file_path.parent.relative_to(self.sandbox))
            )

            # Decode content if necessary
            write_content = content
            write_mode = "w"
            if content_encoding == "base64":
                import base64

                write_content = base64.b64decode(content.encode(self._default_encoding))
                write_mode = "wb"

            with open(abs_file_path, write_mode) as f:
                f.write(write_content)

            # Optionally restore metadata (like modification time)
            metadata = json_data.get("metadata", {})
            if "modified_time" in metadata:
                try:
                    # Convert ISO format string back to datetime, then to timestamp
                    mod_dt = datetime.fromisoformat(metadata["modified_time"])
                    os.utime(
                        abs_file_path,
                        (abs_file_path.stat().st_atime, mod_dt.timestamp()),
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not restore modified time for {relative_file_path}: {e}"
                    )

            logger.info(f"Imported file from JSON: {relative_file_path}.")
            return True

        except SandboxViolationError as e:
            logger.error(f"Import from JSON failed due to sandbox violation: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred importing from JSON: {e}")
            return False
