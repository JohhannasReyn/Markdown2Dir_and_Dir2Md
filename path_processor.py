"""
The `PathProcessor` class handles all path-related operations with these key features:

1. Path Management:
   - Directory creation and verification
   - Path resolution and normalization
   - Relative path handling
   - Directory traversal security checks

2. File Conflict Handling:
   - Multiple strategies (append_n, backup_dir)
   - Configurable through settings
   - Safe file renaming and moving

3. Directory Operations:
   - Recursive file scanning
   - Parent directory tracking
   - Directory filtering based on config

4. Security Features:
   - Path escape prevention
   - Permission checking
   - Safe path normalization

5. Integration:
   - Works with the parent command class
   - Uses shared configuration
   - Maintains consistent debug logging

"""

import os
import errno
import sublime
from .utils import debug_print, SUBLIME_AVAILABLE

class PathProcessor:
    def __init__(self, parent):
        self.parent = parent
        self.view = parent.view

    def ensure_directory_exists(self, filepath):
        """Create directory structure for a given filepath if it doesn't exist."""
        if not filepath:
            return False
        filepath = os.path.normpath(filepath)
        directory = os.path.dirname(filepath)
        if not directory:
            return True
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(directory):
                return True
            if e.errno == errno.EACCES:
                if SUBLIME_AVAILABLE:
                    sublime.error_message("Permission denied creating directory: {}".format(directory))
                return False
            raise

    def resolve_output_path(self, base_dir, filename, config):
        """Resolve the output path for a file, handling conflicts according to config."""
        base_dir = os.path.normpath(base_dir)
        filename = os.path.normpath(filename)
        output_path = os.path.join(base_dir, filename)

        # Check if path attempts to escape base directory
        if not self.is_within_directory(base_dir, output_path):
            debug_print("Invalid path: {} attempts to escape base directory.".format(filename))
            if SUBLIME_AVAILABLE:
                sublime.error_message("Invalid path: {} attempts to escape base directory".format(filename))
            return None

        if os.path.exists(output_path):
            conflict_handling = config.get('handle_file_conflicts', 'prepend_and_comment')
            debug_print("File exists, using conflict handling: {}".format(conflict_handling))

            if conflict_handling == 'append_n_to_filename':
                output_path = self._handle_append_n(output_path)
            elif conflict_handling == 'move_to_backup_dir':
                output_path = self._handle_backup_dir(output_path)

        return output_path

    def is_within_directory(self, directory, target):
        """Check if target path is within the specified directory."""
        directory = os.path.abspath(directory)
        target = os.path.abspath(target)
        relative = os.path.relpath(target, directory)
        return not relative.startswith(os.pardir)

    def _handle_append_n(self, path):
        """Handle file conflict by appending incrementing number."""
        base, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists("{}_{}{}".format(base, counter, ext)):
            counter += 1
        return "{}_{}{}".format(base, counter, ext)

    def _handle_backup_dir(self, path):
        """Handle file conflict by moving to backup directory."""
        backup_dir = os.path.join(os.path.dirname(path), 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_path = os.path.join(backup_dir, os.path.basename(path))

        if os.path.exists(backup_path):
            base, ext = os.path.splitext(backup_path)
            counter = 1
            while os.path.exists("{}_{}{}".format(base, counter, ext)):
                counter += 1
            backup_path = "{}_{}{}".format(base, counter, ext)

        if os.path.exists(path):
            os.rename(path, backup_path)
        return path

    def get_all_parent_directories(self, filepath, base_dir):
        """Get all parent directories of a file path relative to base_dir."""
        try:
            rel_path = os.path.relpath(filepath, base_dir)
            path_parts = rel_path.split(os.sep)
            debug_print("Parent directories for {}: {}".format(filepath, path_parts[:-1]))
            return path_parts[:-1]  # Exclude the filename itself
        except Exception as e:
            debug_print("Error getting parent directories: {}".format(str(e)))
            return []

    def get_relative_path(self, path, base_dir):
        """Get relative path from base directory."""
        try:
            return os.path.relpath(path, base_dir)
        except Exception as e:
            debug_print("Error getting relative path: {}".format(str(e)))
            return os.path.basename(path)

    def normalize_path(self, path):
        """Normalize path separators and format."""
        if not path:
            return path
        return os.path.normpath(path.replace('\\', os.sep).replace('/', os.sep))

    def get_files_recursive(self, directory, config):
        """Gets all files in directory and subdirectories, applying filtering rules."""
        debug_print("Scanning directory: {}".format(directory))
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                # Filter directories based on config
                if config.get('directories_2_include'):
                    dirs[:] = [d for d in dirs if d in config['directories_2_include']]
                elif config.get('directories_2_ignore'):
                    dirs[:] = [d for d in dirs if d not in config['directories_2_ignore']]

                debug_print("Found directory: {}".format(root))
                for filename in filenames:
                    if filename.startswith('.') and not config.get('include_system_folders', False):
                        continue
                    full_path = os.path.join(root, filename)
                    rel_path = self.get_relative_path(full_path, directory)

                    # Use FileProcessor's should_process_path method through parent
                    if self.parent.file_processor.should_process_path(full_path):
                        files.append(rel_path)
                        debug_print("Added file: {}".format(rel_path))
                    else:
                        debug_print("Skipped file: {}".format(rel_path))

            return sorted(files)  # Sort for consistent output
        except Exception as e:
            debug_print("Error scanning directory: {}".format(str(e)))
            return []
