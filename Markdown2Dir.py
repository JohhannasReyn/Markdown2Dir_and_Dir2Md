"""
The plugin structure:
```
markdown2dir/
    __init__.py
    Markdown2Dir.py           # Main plugin file
    markdown_base_command.py  # Base command class
    file_processor.py         # File processing logic
    path_processor.py         # Path handling logic
    code_block_processor.py   # Code block handling
    markdown_processor.py     # Markdown generation
    utils.py                  # Shared utilities
```

Key integration points:
1. All processors are initialized in MarkdownBaseCommand
2. Each command inherits from MarkdownBaseCommand
3. Utils provides shared functionality
4. Each processor can access other processors through the parent reference

The main improvements from this modular structure are:
1. Better separation of concerns
2. Easier testing and debugging
3. More maintainable code
4. Clearer responsibility boundaries
5. Reduced code duplication
6. Better error handling

"""
import os
import sublime
import sublime_plugin
from .utils import debug_print, show_error_message, SUBLIME_AVAILABLE
from .markdown_base_command import MarkdownBaseCommand
from .project_settings_handler import ProjectSettings

class Dir2MarkdownCommand(MarkdownBaseCommand):

    def _load_settings_for_directory(self, directory):
        """Load settings from the current directory or fallback to user settings."""
        debug_print("Loading settings for directory: {}".format(directory))

        # Get fresh settings using the base command's method
        self.config = self.load_config()
        debug_print("Loaded base settings")

        # Create ProjectSettings instance
        self.project_settings = ProjectSettings(self)

        # Get markdown content if we're in a view
        markdown_content = None
        if self.view:
            markdown_content = self.view.substr(sublime.Region(0, self.view.size()))

        # Load or create project settings
        local_settings = self.project_settings.ensure_project_settings_exist(directory, markdown_content)

        if local_settings:
            debug_print("Found project settings, updating configuration")
            self.config = local_settings
        else:
            debug_print("No project settings found, using base settings")

    def _write_markdown_content(self, edit, markdown_content):
        try:
            # Always clear the entire view first if we're overwriting
            if self.config.get('overwrite_on_build_2_md', True):
                region = sublime.Region(0, self.view.size())
                self.view.erase(edit, region)
                debug_print("Cleared existing markdown content")

            self.view.insert(edit, 0, markdown_content)
            debug_print("Updated current view with generated markdown")
        except Exception as e:
            debug_print("Error writing markdown content: {}".format(str(e)))
            show_error_message("Error writing markdown content: {}".format(str(e)))

    def run(self, edit, **kwargs):
        """Run the command in either Sublime Text or standalone mode."""
        debug_print("Starting Dir2Markdown command")
        try:
            # Determine base directory and output file
            if self.view and self.view.file_name():
                base_dir = os.path.dirname(self.view.file_name())
                output_file = self.view.file_name()
                debug_print("Using Sublime Text mode")
            else:
                base_dir = os.getcwd()
                output_file = os.path.join(base_dir, "generated_example.md")
                debug_print("Using standalone mode")

            debug_print("Base directory: {}".format(base_dir))
            debug_print("Output file: {}".format(output_file))

            # Load settings for the current directory first
            self._load_settings_for_directory(base_dir)

            # Set current markdown file in file processor
            self.file_processor.set_current_markdown(output_file)

            # Start building markdown content
            markdown_content = "# Generated Markdown File\n\n"

            # Add directory tree before settings if enabled
            if self.config.get('output_directory_tree', True):
                debug_print("Adding directory tree to markdown")
                tree_content = self.markdown_processor.generate_directory_tree(base_dir, self.config)
                markdown_content += "# Directory Structure\n\n```\n{}\n```\n\n".format(tree_content)

            # Get and add settings content
            markdown_content += "# Directory Settings\n\n"
            settings_content = self.project_settings.get_or_create_settings_block(base_dir)
            debug_print("Got settings content")
            markdown_content += settings_content + "\n\n"

            # Get filtered files (EXCLUDING settings files)
            all_files = []
            for root, _, files in os.walk(base_dir):
                if not self.file_processor.should_process_path(root, is_dir=True):
                    continue

                for filename in sorted(files):
                    # CRITICAL: Skip settings files - they're handled in Directory Settings
                    if filename.endswith('.sublime-settings'):
                        debug_print("Excluding settings file from file contents: {}".format(filename))
                        continue
                    
                    full_path = os.path.join(root, filename)
                    if not self.file_processor.should_process_path(full_path):
                        continue

                    rel_path = os.path.relpath(full_path, base_dir)
                    all_files.append(rel_path)
                    debug_print("Found file: {}".format(rel_path))

            markdown_content += "# File Contents\n\n"

            # Add remaining file content
            for file_path in all_files:
                try:
                    full_path = os.path.join(base_dir, file_path)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    block = self.markdown_processor.format_markdown_block(file_path, file_content, self.config)
                    markdown_content += block + "\n"
                    debug_print("Added content for: {}".format(file_path))

                except Exception as e:
                    debug_print("Error processing {}: {}".format(file_path, str(e)))

            # Write the content
            if SUBLIME_AVAILABLE and edit is not None and self.view:
                self._write_markdown_content(edit, markdown_content)
            else:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    debug_print("Wrote markdown to: {}".format(output_file))
                except Exception as e:
                    error_msg = "Error writing to file: {}".format(str(e))
                    debug_print(error_msg)
                    show_error_message(error_msg)

        except Exception as e:
            error_msg = "Error generating markdown: {}".format(str(e))
            debug_print(error_msg)
            show_error_message(error_msg)

class Markdown2DirCommand(MarkdownBaseCommand):
    """Command to convert markdown to directory structure."""

    def run(self, edit, **kwargs):
        debug_print("Running Markdown2Dir command")
        if not self.is_markdown_file():
            show_error_message(
                "A directory cannot be determined from an unsaved file. "
                "First, save the file with the desired path and try again."
            )
            return

        config = self.load_config()
        markdown_file = self.view.file_name()
        directory = os.path.dirname(markdown_file)
        debug_print("Processing markdown file: {}".format(markdown_file))
        debug_print("Target directory: {}".format(directory))

        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
                debug_print("Read {} characters from file".format(len(content)))
        except Exception as e:
            debug_print("Error reading markdown file: {}".format(str(e)))
            show_error_message("Error reading markdown file: {}".format(str(e)))
            return

        if content:
            self.code_processor.extract_code_blocks(content, directory, config)
        else:
            debug_print("Markdown file empty.")
            show_error_message("No content found in the markdown file.")

def plugin_loaded():
    """Called when plugin is loaded by Sublime Text."""
    from .utils import plugin_loaded as utils_plugin_loaded
    utils_plugin_loaded()

# For testing without Sublime Text
if __name__ == "__main__":
    if not SUBLIME_AVAILABLE:
        debug_print("Running in standalone mode (Sublime Text not available)")
        try:
            cmd = Dir2MarkdownCommand()
            cmd.run(None)  # Run without edit parameter in standalone mode
        except Exception as e:
            debug_print("Error during markdown generation: {}".format(str(e)))
            import traceback
            debug_print(traceback.format_exc())
    else:
        debug_print("Running in Sublime Text plugin mode")