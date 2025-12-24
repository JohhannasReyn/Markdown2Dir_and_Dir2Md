import os
import json
import re
from .utils import debug_print

class ProjectSettings:
    def __init__(self, parent):
        self.parent = parent
        self.current_settings = None

    def get_settings_filename(self, directory):
        """Generate settings filename based on directory name."""
        dir_name = os.path.basename(directory.rstrip(os.sep))
        return "{}.sublime-settings".format(dir_name)

    def extract_settings_from_markdown(self, content, directory):
        """Extract settings from markdown content if present."""
        settings_filename = self.get_settings_filename(directory)
        debug_print("Searching for {} in markdown content".format(settings_filename))

        code_block_pattern = r'```([^\n]*)\n([\s\S]*?)```'
        matches = re.finditer(code_block_pattern, content)

        for match in matches:
            lang_or_filename = match.group(1).strip()
            code = match.group(2).strip()

            if settings_filename in lang_or_filename:
                try:
                    settings = json.loads(code)
                    debug_print("Found settings in markdown")
                    return settings
                except json.JSONDecodeError as e:
                    debug_print("Error parsing settings from markdown: {}".format(e))
                    continue

        return None

    def ensure_project_settings_exist(self, directory, markdown_content=None):
        """Ensure project settings exist and are included in both directory and markdown."""
        settings_filename = self.get_settings_filename(directory)
        settings_path = os.path.join(directory, settings_filename)

        # Try to load existing settings or create new ones
        if self.parent.config.get('use_per_project_settings', True):
            # Check markdown first if provided
            if markdown_content:
                settings = self.extract_settings_from_markdown(markdown_content, directory)
                if settings:
                    debug_print("Using settings from markdown")
                    if not os.path.exists(settings_path):
                        self.save_project_settings(directory, settings)
                    return settings

            # Check for existing file
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    debug_print("Using existing project settings")
                    return settings
                except Exception as e:
                    debug_print("Error loading project settings: {}".format(e))

        # If we should save per-project settings and they don't exist
        if self.parent.config.get('save_settings_per_project', True):
            if not os.path.exists(settings_path):
                # Use current settings as template
                settings = self.parent.config.copy()
                self.save_project_settings(directory, settings)
                debug_print("Created new project settings")
                return settings

        return self.parent.config

    def save_project_settings(self, directory, settings):
        """Save settings to project directory with directory-based filename."""
        try:
            settings_filename = self.get_settings_filename(directory)
            settings_path = os.path.join(directory, settings_filename)
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)

            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            debug_print("Saved settings to {}".format(settings_path))
            return True
        except Exception as e:
            debug_print("Error saving project settings: {}".format(e))
            return False

    def get_or_create_settings_block(self, directory):
        """Get or create settings content block for markdown."""
        settings_filename = self.get_settings_filename(directory)
        settings_path = os.path.join(directory, settings_filename)

        # Get current settings
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = self.parent.config.copy()
                # Save settings file
                self.save_project_settings(directory, settings)
        except Exception as e:
            debug_print("Error loading settings, using defaults: {}".format(e))
            settings = self.parent.config.copy()
            self.save_project_settings(directory, settings)

        # Format as markdown block
        return self.format_settings_for_markdown(directory, settings)

    def format_settings_for_markdown(self, directory, settings):
        """Format settings as a markdown code block using directory-based filename."""
        settings_filename = self.get_settings_filename(directory)
        formatted_settings = json.dumps(settings, indent=4)
        return "```{}\n{}\n```".format(settings_filename, formatted_settings)

    def should_include_settings_in_markdown(self, directory, settings):
        """Determine if settings should be included in markdown generation."""
        settings_filename = self.get_settings_filename(directory)

        # Check if file exists in directory or settings say we should save
        settings_path = os.path.join(directory, settings_filename)
        if os.path.exists(settings_path) or settings.get('save_settings_per_project', True):
            return True

        return False

    def indent_code_block(self, content, spaces=4):
        """Indent a code block to preserve it during processing."""
        lines = content.split('\n')
        return '\n'.join(' ' * spaces + line for line in lines)

    def unindent_code_block(self, content):
        """Remove indentation from a code block."""
        lines = content.split('\n')
        # Find minimum indentation (excluding empty lines)
        min_indent = float('inf')
        for line in lines:
            if line.strip():  # Only check non-empty lines
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)

        if min_indent == float('inf'):
            return content

        # Remove the minimum indentation from all lines
        return '\n'.join(line[min_indent:] if line.strip() else line for line in lines)
