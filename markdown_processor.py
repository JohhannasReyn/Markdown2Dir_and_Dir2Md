"""
The `MarkdownProcessor` class handles all markdown-related operations with these key features:

1. Markdown Generation:
   - Directory tree visualization
   - Code block formatting
   - File content integration
   - Consistent layout generation
   - **NEW**: Nested code fence indentation handling

2. Code Block Management:
   - Code block extraction
   - Block formatting according to conventions
   - Block insertion and updating
   - File synchronization
   - **NEW**: Automatic indentation of nested fences

3. Directory Tree Generation:
   - Visual tree structure creation
   - Filtered directory listing
   - Recursive directory traversal
   - Pretty-printed output

4. File Synchronization:
   - Two-way sync between markdown and files
   - Content updating
   - File creation and modification
   - Error handling

5. Integration:
   - Works with FileProcessor for filtering
   - Uses CodeBlockProcessor for block handling
   - Uses PathProcessor for path operations
   - Maintains consistent debug logging

"""
import os
import re
import sublime
import sublime_plugin
from .utils import debug_print, SUBLIME_AVAILABLE

class MarkdownProcessor:
    def __init__(self, parent):
        self.parent = parent
        self.view = parent.view

    def extract_code_blocks_from_markdown(self):
        """Extract filenames of code blocks from the markdown file."""
        file_content = self.view.file_name()  # Replace with actual file reading logic
        code_block_pattern = r'```(?:[^\n]*)\n([\s\S]*?)```'
        matches = re.findall(code_block_pattern, file_content)
        filenames = set()

        for match in matches:
            # Extract the filename from the code block
            filename_line = match.splitlines()[0].strip()
            filenames.add(filename_line)

        return filenames

    def generate_markdown_content(self, directory, files, config):
        """Generates markdown content from files."""
        debug_print("Generating markdown for {} files".format(len(files)))
        content = ["# Generated Markdown File\n"]

        # Add directory tree if enabled
        if config.get('output_directory_tree', True):
            debug_print("Adding directory tree to markdown")
            tree_content = self.generate_directory_tree(directory, config)
            content.extend([
                "# Directory Structure\n",
                "```",
                tree_content,
                "```\n",
                "# File Contents\n"
            ])

        # Process each file
        for file_path in files:
            try:
                full_path = os.path.join(directory, file_path)
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                block = self.format_markdown_block(file_path, file_content, config)
                content.append(block)
                debug_print("Added content for: {}".format(file_path))

            except Exception as e:
                debug_print("Error processing {}: {}".format(file_path, str(e)))

        return "\n".join(content)

    def indent_nested_fences(self, content):
        """
        Add indentation to nested code fences found within file content.
        This ensures that code fences within files are properly indented
        when generating markdown, so they won't be extracted as separate files.

        For example, if a file contains:
        ```example
            content
        ```

        It will be transformed to:
            ```example
                content
            ```
        """
        # Pattern to match code fences (both opening and closing)
        fence_pattern = r'^(```[^\n]*\n?)'

        lines = content.split('\n')
        result_lines = []
        in_fence = False
        fence_indent = '    '  # 4 spaces for one indentation level

        for line in lines:
            # Check if this line contains a fence marker
            if line.strip().startswith('```'):
                # Toggle fence state
                in_fence = not in_fence
                # Indent the fence marker
                result_lines.append(fence_indent + line)
            elif in_fence:
                # We're inside a fence, indent the content
                result_lines.append(fence_indent + line)
            else:
                # Outside fence, keep as is
                result_lines.append(line)

        return '\n'.join(result_lines)

    def format_markdown_block(self, file_path, content, config):
        """
        Format a single file as a markdown code block.
        Automatically indents any nested code fences found in the content.
        """
        naming_convention = config.get("file_naming_convention", "on_fence")
        lines = []

        # Check if content contains code fences - if so, indent them
        if '```' in content:
            debug_print("File {} contains nested code fences, adding indentation".format(file_path))
            content = self.indent_nested_fences(content)

        if naming_convention == "before_fence":
            lines.append(file_path)
            lines.append("```{}".format(self.parent.get_file_language(file_path)))
        elif naming_convention == "after_fence":
            lines.append("```{}".format(self.parent.get_file_language(file_path)))
            lines.append("// {}".format(file_path))
        else:  # on_fence
            lines.append("```{}".format(file_path))

        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")  # Empty line after block
        return "\n".join(lines)

    def generate_directory_tree(self, base_dir, config):
        """Generate a visual directory tree structure with improved filtering."""
        debug_print("Generating directory tree for: {}".format(base_dir))

        def get_directory_with_included_files(dir_path):
            """Check if directory contains any included files (recursively)."""
            has_included_files = False
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    if self.parent.file_processor.should_process_path(full_path, is_dir=False):
                        has_included_files = True
                        break
                if has_included_files:
                    break
            return has_included_files

        def format_tree_line(name, prefix="", is_last=True):
            """Format a single line of the tree."""
            return "{}{}{}".format(
                prefix,
                "└── " if is_last else "├── ",
                name
            )

        def build_tree(current_path, prefix=""):
            """Recursively build the tree structure."""
            lines = []
            try:
                # Get directory contents
                items = os.listdir(current_path)

                # Separate directories and files
                dirs = []
                files = []

                for item in sorted(items):
                    full_path = os.path.join(current_path, item)

                    if os.path.isdir(full_path):
                        # Only include directory if it contains files we want
                        if get_directory_with_included_files(full_path):
                            dirs.append(item)
                    else:
                        # Apply file filters
                        if self.parent.file_processor.should_process_path(full_path, is_dir=False):
                            files.append(item)

                # Combine filtered items
                filtered_items = dirs + files

                # Generate tree lines
                for idx, item in enumerate(filtered_items):
                    is_last = (idx == len(filtered_items) - 1)
                    full_path = os.path.join(current_path, item)

                    # Add current item
                    lines.append(format_tree_line(item, prefix, is_last))

                    # Recursively process directories
                    if os.path.isdir(full_path) and item in dirs:
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        subtree = build_tree(full_path, new_prefix)
                        if subtree:  # Only add non-empty directories
                            lines.extend(subtree)

                return lines

            except OSError as e:
                debug_print("Error accessing directory {}: {}".format(current_path, str(e)))
                return []

        try:
            # Only show root directory if it contains files we want
            if not get_directory_with_included_files(base_dir):
                return ""

            # Start with base directory name
            base_name = os.path.basename(base_dir)
            tree_lines = [base_name]

            # Build the tree structure
            subtree = build_tree(base_dir)
            if subtree:
                tree_lines.extend(subtree)

            return "\n".join(tree_lines)

        except Exception as e:
            error_msg = "Error generating directory tree: {}".format(str(e))
            debug_print(error_msg)
            return "Error generating directory tree"

    def insert_code_blocks(self, content, directory, config):
        """Insert code blocks from files into markdown content."""
        if not content or not directory:
            debug_print("No content or directory provided")
            return

        debug_print("Content length: {} characters".format(len(content)))
        debug_print("Directory: {}".format(directory))

        code_block_pattern = r'```([^\n]*)\n([\s\S]*?)```'
        matches = list(re.finditer(code_block_pattern, content))
        debug_print("Found {} code blocks".format(len(matches)))

        for i, match in enumerate(matches):
            lang_or_filename = match.group(1)
            code = match.group(2)
            debug_print("Processing block {}:".format(i+1))
            debug_print("Language/filename: {}".format(lang_or_filename))
            debug_print("Code length: {} characters".format(len(code)))

            filename = self.parent.code_processor.get_filename_from_block(
                lang_or_filename, code, None, config)

            if not filename or self.parent.code_processor.should_ignore_block(
                lang_or_filename, code, filename, config):
                continue

            try:
                file_path = os.path.join(directory, filename)
                debug_print("Attempting to write to: {}".format(file_path))

                if os.path.exists(file_path):
                    debug_print("File exists: {}".format(file_path))
                    with open(file_path, 'r', encoding='utf-8') as f:
                        updated_code = f.read().strip()

                        # If the file contains code fences, indent them for markdown
                        if '```' in updated_code:
                            updated_code = self.indent_nested_fences(updated_code)

                        content = content.replace(
                            match.group(0),
                            "```{}\n{}\n```".format(lang_or_filename or '', updated_code)
                        )
                        debug_print("Updated content with file contents")
                else:
                    debug_print("Creating new file: {}".format(file_path))
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code.strip())
                    debug_print("Created file: {}".format(file_path))

            except Exception as e:
                debug_print("Error processing {}: {}".format(filename, str(e)))

        try:
            # Save changes back to markdown file
            if self.view and self.view.file_name():
                debug_print("Saving changes to markdown file: {}".format(
                    self.view.file_name()))
                with open(self.view.file_name(), 'w', encoding='utf-8') as f:
                    f.write(content)
                debug_print("Markdown file updated successfully")
        except Exception as e:
            debug_print("Error writing to markdown file: {}".format(str(e)))
