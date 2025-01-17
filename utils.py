"""
utils.py contains the plugin's helper functions that are used by each of the individual processors.
"""
import os
import sys

# Try to import Sublime Text modules
SUBLIME_AVAILABLE = False
DEBUG_COUNT = 0

try:
    import sublime
    import sublime_plugin
    SUBLIME_AVAILABLE = True
except ImportError:
    # Create mock classes for non-Sublime Text environment
    class MockRegion:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class MockSublime:
        def Region(self, a, b):
            return MockRegion(a, b)

        def error_message(self, message):
            print("Error: {}".format(message))

    sublime = MockSublime()

def debug_print(*args, **kwargs):
    """Print debug messages with line numbers, handling multiline strings."""
    global DEBUG_COUNT
    global SUBLIME_AVAILABLE
    try:
        if SUBLIME_AVAILABLE:
            settings = sublime.load_settings("Markdown2Dir.sublime-settings")
            if settings and not sublime.get("enable_debug_output", False):
                return
    except Exception:
        pass # Fall back to always printing in case of errors
    # Convert all arguments to strings and join them
    message = " ".join(str(arg) for arg in args)

    # Handle multiline messages
    if "\n" in message:
        lines = message.split("\n")
        for line in lines:
            if line.strip():  # Only process non-empty lines
                debug_print(line, **kwargs)
        return

    # Process single line
    DEBUG_COUNT += 1
    print("{}\t| {}".format(str(DEBUG_COUNT), message), **kwargs)

def show_error_message(message):
    """Displays a user-friendly error message in Sublime Text."""
    if SUBLIME_AVAILABLE:
        sublime.error_message("Error: {}".format(message))
    else:
        print("Error: {}".format(message))

def plugin_loaded():
    """Called when the plugin is loaded."""
    debug_print("Markdown2Dir plugin loaded")
    debug_print("SUBLIME_AVAILABLE =", SUBLIME_AVAILABLE)
    if SUBLIME_AVAILABLE:
        debug_print("Plugin directory:", os.path.dirname(os.path.abspath(__file__)))

        # Monitor settings changes
        settings = sublime.load_settings("Markdown2Dir.sublime-settings")
        settings.add_on_change("Markdown2Dir", handle_settings_change)

def handle_settings_change():
    """Handle settings changes by clearing the cache."""
    from .markdown_base_command import MarkdownBaseCommand
    MarkdownBaseCommand.clear_config_cache()

def validate_config(config):
    required_fields = {
        'file_naming_convention': str,
        'blocks_ignored': list,
        'extensions_2_include': list,
        'extensions_2_ignore': list
    }
    for field, expected_type in required_fields.items():
        if field not in config:
            config[field] = [] if expected_type == list else ''
        elif not isinstance(config[field], expected_type):
            config[field] = expected_type()

    return config


def log_message(level, message, *args):
    levels = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40
    }

    if not hasattr(log_message, 'min_level'):
        log_message.min_level = levels['DEBUG']

    if levels[level] >= log_message.min_level:
        formatted_message = message % args if args else message
        debug_print("[{}] {}".format(level,formatted_message))
