"""
Unified implementation with separation of concerns:

1. Class-based structure with `should_process_path` function as the entry point
2. Broke down the functionality into logical private methods:
   - `_process_code_block`: Handles code block-specific checks
   - `_apply_common_filters`: Applies filters common to both files and directories
   - `_process_directory`: Handles directory-specific filters
   - `_process_file`: Handles file-specific filters including extension checks
   - `_handle_filter_result`: Manages final decision and debug output

Key improvements:

1. Better organization:
   - Each type of filtering has its own method
   - Code is more modular and easier to maintain
   - Clear separation of concerns while maintaining interconnectivity

2. Enhanced flexibility:
   - Can process paths, directories, and code blocks
   - All filters work additively
   - Comprehensive debug output for all decisions

3. Improved error handling:
   - Better path resolution error handling
   - Clearer debug messages
   - More robust filter application

4. Better code reuse:
   - Common functionality is shared between different types of checks
   - Reduced code duplication
   - More consistent behavior across different types of filtering

5. The main `should_process_path` function can now handle:
- Regular files
- Directories
- Code blocks (when provided)
- All combinations of filters
- Override scenarios with appropriate debug output

6. v2.0.1 edits made 1/17/25:
- Changed priority of filters to check files_2_include first
- Removed unnecessary directory filtering checks
- Simplified binary file checking
- Made extension filtering only apply when no specific files are included
- Added current markdown file tracking
- Always excludes the current markdown file from processing
- Added set_current_markdown method to update the current file

7. v2.1.1 edits made 1/27/25
- Corrected filtering to filter directories and files nested under excluded directories.

"""
# file_processor.py
import os
from .utils import debug_print

class FileProcessor:
    def __init__(self, parent):
        self.parent = parent
        self.view = parent.view if parent else None
        self.current_markdown_file = None

    def is_binary_file(self, file_path):
        """Check if a file is binary by reading its first few bytes."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return True
                text_characters = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
                return bool(chunk.translate(None, text_characters))
        except Exception:
            # If we can't read the file, assume it's not binary
            return False

    def set_current_markdown(self, file_path):
        """Set the current markdown file being processed."""
        self.current_markdown_file = os.path.normpath(file_path) if file_path else None
        debug_print("Set current markdown file: {}".format(self.current_markdown_file))

    def is_markdown_file(self, file_path):
        """Check if a file is a markdown file."""
        return file_path and file_path.lower().endswith(('.md', '.markdown', '.mdown', '.mkd', '.mkdn', '.txt'))

    def _is_in_ignored_directory(self, path):
        """Check if path is within any ignored directory."""
        try:
            config = self.parent.config
        except AttributeError:
            debug_print("No configuration available for directory check")
            return False

        directories_to_ignore = config.get('directories_2_ignore', [])
        path_parts = path.split(os.sep)

        # Check if any component of the path matches an ignored directory
        for directory in directories_to_ignore:
            if directory in path_parts:
                debug_print("Path '{}' is within ignored directory '{}'".format(path,directory))
                return True
        return False

    def should_process_path(self, path, is_dir=False, code_block=None):
        """Unified path processing check with improved filtering."""
        try:
            config = self.parent.config
        except AttributeError:
            debug_print("No configuration available, using defaults")
            config = {}

        path = os.path.normpath(path)
        path_name = os.path.basename(path)
        debug_print("Checking path: {}".format(path))

        # Always skip the current markdown file
        if self.current_markdown_file and path == self.current_markdown_file:
            debug_print("Skipping current markdown file")
            return False

        # Always skip .git directories and their contents
        path_parts = path.split(os.sep)
        if '.git' in path_parts:
            debug_print("Skipping .git path: {}".format(path))
            return False

        # Check if path is within any ignored directory
        if self._is_in_ignored_directory(path):
            debug_print("REJECTED: Path '{}' is within an ignored directory".format(path))
            return False

        # Directory processing
        if is_dir:
            # System folder check
            if path_name.startswith('.') and not config.get('include_system_folders', False):
                debug_print("Skipping system directory: {}".format(path_name))
                return False

            # Check directories_2_include
            directories_to_include = config.get('directories_2_include', [])
            if directories_to_include and path_name not in directories_to_include:
                debug_print("REJECTED: Directory '{}' not in include list".format(path_name))
                return False

            return True

        # File processing
        debug_print("Processing as file...")

        # Check specific files lists first
        files_to_include = config.get('files_2_include', [])
        if files_to_include and path_name not in files_to_include:
            debug_print("REJECTED: File '{}' not in include list".format(path_name))
            return False

        files_to_ignore = config.get('files_2_ignore', [])
        if path_name in files_to_ignore:
            debug_print("REJECTED: File '{}' in ignore list".format(path_name))
            return False

        # Check partial names
        partial_names_to_include = config.get('partial_names_2_include', [])
        if partial_names_to_include and not any(partial in path_name for partial in partial_names_to_include):
            debug_print("REJECTED: File '{}' doesn't match any partial include patterns".format(path_name))
            return False

        partial_names_to_ignore = config.get('partial_names_2_ignore', [])
        if any(partial in path_name for partial in partial_names_to_ignore):
            debug_print("REJECTED: File '{}' matches ignored partial pattern".format(path_name))
            return False

        # Extension checks
        _, ext = os.path.splitext(path_name)
        ext = ext[1:].lower() if ext else ''

        extensions_to_include = config.get('extensions_2_include', [])
        if extensions_to_include and ext not in extensions_to_include:
            debug_print("REJECTED: Extension '{}' not in include list".format(ext))
            return False

        extensions_to_ignore = config.get('extensions_2_ignore', [])
        if ext in extensions_to_ignore:
            debug_print("REJECTED: Extension '{}' in ignore list".format(ext))
            return False

        # Binary file check
        if os.path.isfile(path) and self.is_binary_file(path):
            debug_print("REJECTED: File '{}' is binary".format(path_name))
            return False

        debug_print("ACCEPTED: File '{}' passed all checks".format(path_name))
        return True
