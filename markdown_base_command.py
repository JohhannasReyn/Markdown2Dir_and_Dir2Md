"""
The `MarkdownBaseCommand` class has been streamlined to:
1. Handle basic initialization and configuration
2. Maintain core utilities needed by multiple processors
3. Initialize all processor classes
4. Keep language/comment syntax mappings
5. Remove all processor-specific code that will be moved to other classes

Organization the remaining implementations:
1. PathProcessor: Handle all path-related operations
2. CodeBlockProcessor: Handle code block extraction and injection
3. MarkdownProcessor: Handle markdown generation and formatting

"""
import os
import sublime
import sublime_plugin
from .file_processor import FileProcessor
from .path_processor import PathProcessor
from .code_block_processor import CodeBlockProcessor
from .markdown_processor import MarkdownProcessor
from .project_settings_handler import ProjectSettings
from .utils import debug_print, SUBLIME_AVAILABLE

class MarkdownBaseCommand(sublime_plugin.TextCommand):
    _config_cache = None

    COMMENT_SYNTAX = {
        "py": "#",        # Python
        "cpp": "//",      # C++
        "c": "//",        # C
        "js": "//",       # JavaScript
        "java": "//",     # Java
        "html": "<!--",   # HTML
        "xml": "<!--",    # XML
        "css": "/*",      # CSS
    }

    BLOCK_COMMENT_END = {
        "html": "-->",
        "xml": "-->",
        "css": "*/"
    }

    def __init__(self, view):
        super().__init__(view)
        self.file_processor = FileProcessor(self)
        self.path_processor = PathProcessor(self)
        self.code_processor = CodeBlockProcessor(self)
        self.markdown_processor = MarkdownProcessor(self)
        self.project_settings = ProjectSettings(self)
        self.config = self.load_config() or {}

    def run(self, edit):
        pass  # Implement in child classes

    def load_config(self):
        """Load and parse settings from Sublime Text settings file with fallback defaults"""
        if MarkdownBaseCommand._config_cache is not None:
            return MarkdownBaseCommand._config_cache

        debug_print("Loading config...")
        default_config = {
            'file_naming_convention': 'on_fence',
            'blocks_ignored': ['lessthan_3', 'nameless', 'readme', 'properties', 'without_ext'],
            'extensions_2_include': [],
            'extensions_2_ignore': [],
            'directories_2_include': [],
            'directories_2_ignore': [],
            'include_nested_directories': True,
            'files_2_include': [],
            'files_2_ignore': [],
            'partial_names_2_include': [],
            'partial_names_2_ignore': [],
            'attempt_injection': False,
            'handle_file_conflicts': 'prepend_and_comment',
            'include_system_folders': False,
            'output_directory_tree': True,
            'enable_context_menu': False,
            'enable_key_bindings': False,
            'enable_debug_output': False
        }

        if SUBLIME_AVAILABLE:
            try:
                debug_print("Attempting to load Sublime settings")
                settings = sublime.load_settings("Markdown2Dir.sublime-settings")
                if settings:
                    debug_print("Settings loaded successfully")
                    MarkdownBaseCommand._config_cache = {key: settings.get(key, default_config[key]) for key in default_config}
                    return MarkdownBaseCommand._config_cache
            except Exception as e:
                debug_print("Error loading settings: {}".format(str(e)))

        debug_print("Using default config")
        MarkdownBaseCommand._config_cache = default_config
        return default_config

    @classmethod
    def clear_config_cache(cls):
        """Clear the cached configuration."""
        debug_print("Clearing config cache")
        cls._config_cache = None

    def is_enabled(self):
        """Check if the command should be enabled."""
        if not self.view:
            return False
        if not self.view.file_name():
            return False
        return True

    def get_comment_syntax(self, file_path):
        """Get comment syntax for a given file type."""
        ext = os.path.splitext(file_path)[1][1:]  # Get extension without the dot
        start_comment = self.COMMENT_SYNTAX.get(ext, "#")  # Default to "#" if unknown
        end_comment = self.BLOCK_COMMENT_END.get(ext, "")  # Default to "" if none
        debug_print("Comments used, open: {}, close: {}".format(start_comment, end_comment))
        return start_comment, end_comment

    def is_markdown_file(self):
        """Check if current file is a markdown file."""
        file_name = self.view.file_name()
        return file_name and file_name.lower().endswith(('.md', '.markdown', '.mdown', '.mkd', '.mkdn', '.txt'))

    def get_file_language(self, filename):
        """Determine language from file extension."""
        ext = os.path.splitext(filename)[1][1:].lower()
        ext_to_lang = {
            'py': 'python',
            'js': 'javascript',
            'cpp': 'c++',
            'hpp': 'c++',
            'h': 'c++',
            'c': 'c',
            'cs': 'csharp',
            'java': 'java',
            'html': 'html',
            'css': 'css',
            'sql': 'sql',
            'md': 'markdown',
            'txt': 'text'
        }
        return ext_to_lang.get(ext, ext)
