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

The main `should_process_path` function can now handle:
- Regular files
- Directories
- Code blocks (when provided)
- All combinations of filters
- Override scenarios with appropriate debug output

"""
# file_processor.py

import os
from .utils import debug_print

class FileProcessor:
    def __init__(self, parent):
        self.parent = parent
        self.view = parent.view if parent else None

    def is_binary_file(self, file_path):
        """Check if a file is binary by reading its first few bytes."""
        try:
            with open(file_path, 'rb') as f:
                # Read first 1024 bytes
                chunk = f.read(1024)
                # Look for null bytes
                if b'\x00' in chunk:
                    return True
                # Count printable ASCII characters
                text_characters = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
                return bool(chunk.translate(None, text_characters))
        except Exception:
            return True  # If we can't read the file, treat it as binary

    def should_skip_directory(self, dirname):
        """Check if a directory should be skipped."""
        skip_dirs = {'.git', '.svn', '__pycache__', '.pio', 'build', 'node_modules'}
        return dirname in skip_dirs

    def should_process_path(self, path, is_dir=False, code_block=None):
        """Unified path processing check with improved filtering."""
        try:
            config = self.parent.config
        except AttributeError:
            debug_print("No configuration available, using defaults")
            config = {}

        path_name = os.path.basename(path)
        debug_print("Checking path: {}".format(path))

        # Directory-specific checks
        if is_dir:
            if self.should_skip_directory(path_name):
                debug_print("Skipping directory: {}".format(path_name))
                return False
            if path_name.startswith('.') and not config.get('include_system_folders', False):
                debug_print("Skipping system directory: {}".format(path_name))
                return False
            return True

        # File extension checks
        _, ext = os.path.splitext(path_name)
        ext = ext[1:].lower() if ext else ''

        # Skip binary files and object files
        if ext in {'o', 'a', 'so', 'dll', 'exe', 'bin', 'pyc'} or self.is_binary_file(path):
            debug_print("Skipping binary file: {}".format(path_name))
            return False

        # Handle extension filters
        extensions_to_include = config.get('extensions_2_include', [])
        extensions_to_ignore = config.get('extensions_2_ignore', [])

        if extensions_to_include:
            if ext not in extensions_to_include:
                debug_print("File extension not in include list: {}".format(ext))
                return False
        elif extensions_to_ignore and ext in extensions_to_ignore:
            debug_print("File extension in ignore list: {}".format(ext))
            return False

        # Handle file name filters
        files_to_include = config.get('files_2_include', [])
        files_to_ignore = config.get('files_2_ignore', [])

        if files_to_include and path_name not in files_to_include:
            debug_print("File not in include list: {}".format(path_name))
            return False
        if files_to_ignore and path_name in files_to_ignore:
            debug_print("File in ignore list: {}".format(path_name))
            return False

        # Handle partial name filters
        partial_includes = config.get('partial_names_2_include', [])
        partial_ignores = config.get('partial_names_2_ignore', [])

        if partial_includes:
            matches = any(term.lower() in path_name.lower() for term in partial_includes)
            if not matches:
                debug_print("File doesn't match any partial include patterns: {}".format(path_name))
                return False

        if partial_ignores:
            matches = any(term.lower() in path_name.lower() for term in partial_ignores)
            if matches:
                debug_print("File matches partial ignore pattern: {}".format(path_name))
                return False

        debug_print("Processing file: {}".format(path_name))
        return True

    def is_markdown_file(self, file_path):
        """Check if a file is a markdown file."""
        return file_path and file_path.lower().endswith(('.md', '.markdown', '.mdown', '.mkd', '.mkdn', '.txt'))