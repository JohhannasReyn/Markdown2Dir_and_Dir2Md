import os
import re
import errno

PRINT_DEBUG = True  # Global debug flag
DEBUG_COUNT = 0
def debug_print(*args, **kwargs):
    """Print debug messages with line numbers, handling multiline strings."""
    global DEBUG_COUNT
    if not PRINT_DEBUG:
        return
    # Convert all arguments to strings and join them
    message = " ".join(str(arg) for arg in args)
    # If the message contains newlines, split and process each line
    if "\n" in message:
        lines = message.split("\n")
        # Process each line individually, preserving any kwargs
        for line in lines:
            if line.strip():  # Only process non-empty lines
                debug_print(line, **kwargs)
        return
    # Process single line
    DEBUG_COUNT += 1
    print("{}\t| {}".format(str(DEBUG_COUNT), message), **kwargs)

# Try to import Sublime Text modules
SUBLIME_AVAILABLE = False
try:
    import sublime
    import sublime_plugin
    SUBLIME_AVAILABLE = True
except ImportError:
    # Create mock classes/functions for testing without Sublime Text
    class MockView:
        def file_name(self):
            return "test.md"

    class MockSublime:
        def error_message(self, message):
            print("Error: {}".format(message))

    class MockTextCommand:
        def __init__(self):
            self.view = MockView()

    sublime = MockSublime()
    sublime_plugin = type('MockSublimePlugin', (), {'TextCommand': MockTextCommand})

def plugin_loaded():
    debug_print("Markdown2Dir plugin loaded")
    debug_print("SUBLIME_AVAILABLE =", SUBLIME_AVAILABLE)
    if SUBLIME_AVAILABLE:
        debug_print("Plugin directory:", os.path.dirname(os.path.abspath(__file__)))

class MarkdownBaseCommand(sublime_plugin.TextCommand):
    COMMENT_SYNTAX = {
        "py": "#",        # Python
        "cpp": "//",      # C++
        "c": "//",       # C
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

    def load_config(self):
        """Load and parse settings from Sublime Text settings file with fallback defaults"""
        debug_print("Loading config...")
        default_config = {
            'file_naming_convention': 'on_fence',
            'blocks_ignored': ['lessthan_3', 'nameless', 'readme', 'properties', 'without_ext'],
            'attempt_injection': True,
            'handle_file_conflicts': 'prepend_and_comment',
            'extensions_2_include': [],
            'extensions_2_ignore': []
        }

        if SUBLIME_AVAILABLE:
            try:
                debug_print("Attempting to load Sublime settings")
                settings = sublime.load_settings("Markdown2Dir.sublime-settings")
                if settings:
                    debug_print("Settings loaded successfully")
                    file_naming = settings.get('file_naming_convention', default_config['file_naming_convention'])
                    debug_print("Loaded file naming convention: {}".format(file_naming))
                    return {
                        'file_naming_convention': file_naming,
                        'blocks_ignored': settings.get('blocks_ignored', default_config['blocks_ignored']),
                        'attempt_injection': settings.get('attempt_injection', default_config['attempt_injection']),
                        'handle_file_conflicts': settings.get('handle_file_conflicts', default_config['handle_file_conflicts']),
                        'extensions_2_include': settings.get('extensions_2_include', default_config['extensions_2_include']),
                        'extensions_2_ignore': settings.get('extensions_2_ignore', default_config['extensions_2_ignore'])
                    }
            except Exception as e:
                debug_print("Error loading settings: {}".format(str(e)))
        debug_print("Using default config")
        return default_config

    def get_comment_syntax(self, file_path):
        ext = os.path.splitext(file_path)[1][1:]  # Get extension without the dot
        start_comment = self.COMMENT_SYNTAX.get(ext, "#")  # Default to "#" if unknown
        end_comment = self.BLOCK_COMMENT_END.get(ext, "")  # Default to "" if none
        debug_print("Comments used, open: {}, close: {}".format(start_comment,end_comment))
        return start_comment, end_comment

    def is_markdown_file(self):
        file_name = self.view.file_name()
        return file_name and file_name.lower().endswith((".md", ".markdown", ".mdown", ".mkd", ".mkdn", ".txt"))

    def should_ignore_block(self, lang, code, filename, config):
        """Determine if a code block should be ignored based on configuration settings."""
        blocks_ignored = config.get('blocks_ignored', [])

        # Check if block is nameless
        if 'nameless' in blocks_ignored and not filename:
            debug_print("Ignoring nameless block")
            return True

        # Check minimum line count
        if 'lessthan_3' in blocks_ignored:
            if len(code.strip().splitlines()) < 3:
                debug_print("Ignoring block with less than 3 lines")
                return True

        # Check for readme or properties content
        if 'readme' in blocks_ignored and any(x in code.lower() for x in ['readme', 'README']):
            debug_print("Ignoring readme block")
            return True

        if 'properties' in blocks_ignored and any(x in code.lower() for x in ['properties', 'PROPERTIES']):
            debug_print("Ignoring properties block")
            return True

        # Check if file has extension
        if 'without_ext' in blocks_ignored and filename:
            if not os.path.splitext(filename)[1]:
                debug_print("Ignoring file without extension")
                return True

        # Check if code is empty
        if not code.strip():
            debug_print("Ignoring empty block")
            return True

        return False

    def get_filename_from_block(self, lang_or_filename, code, preceding_line, config):
        debug_print("get_filename_from_block input:")
        debug_print("  lang_or_filename: {}".format(lang_or_filename))
        debug_print("  preceding_line: {}".format(preceding_line))
        debug_print("  code first line: {}".format(code.splitlines()[0] if code else None))

        def sanitize_path(path):
            if path:
                path = path.replace('\\', os.sep).replace('/', os.sep)
                if os.path.isabs(path):
                    path = os.path.relpath(path)
                path = os.path.normpath(path)
                debug_print("  sanitized path: {}".format(path))
                return path
            debug_print("  sanitize_path received None")
            return None

        def extract_path_from_text(text):
            if not text:
                debug_print("  extract_path got empty text")
                return None
            path_pattern = r'(?:[a-zA-Z]:)?(?:[\\\/])?(?:[\w\s.-]+[\\\/])*[\w\s.-]+\.\w+'
            match = re.search(path_pattern, text)
            result = match.group(0) if match else None
            debug_print("  extracted path from text: {}".format(result))
            return result

        naming_convention = config.get("file_naming_convention", "on_fence")
        debug_print("  using naming convention: {}".format(naming_convention))
        filename = None

        # Try on_fence first
        if '.' in str(lang_or_filename):
            filename = lang_or_filename
            debug_print("  found filename in fence: {}".format(filename))

        # Try before_fence next
        if not filename and preceding_line:
            extracted = extract_path_from_text(preceding_line)
            if extracted:
                filename = extracted
                debug_print("  found filename in preceding line: {}".format(filename))

        # Try after_fence last
        if not filename and code:
            first_line = code.splitlines()[0].strip()
            comment_chars = ['#', '//', '<!--', '/*', ';']
            for char in comment_chars:
                if first_line.startswith(char):
                    clean_line = first_line[len(char):].strip()
                    extracted = extract_path_from_text(clean_line)
                    if extracted:
                        filename = extracted
                        debug_print("  found filename in first code line: {}".format(filename))
                        break

        result = sanitize_path(filename)
        debug_print("  final filename: {}".format(result))
        return result

    def ensure_directory_exists(self, filepath):
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
                sublime.error_message("Permission denied creating directory: {}".format(directory))
                return False
            raise

    def resolve_output_path(self, base_dir, filename, config):
        base_dir = os.path.normpath(base_dir)
        filename = os.path.normpath(filename)
        output_path = os.path.join(base_dir, filename)

        # Replace commonpath check with a more compatible version
        def is_within_directory(directory, target):
            directory = os.path.abspath(directory)
            target = os.path.abspath(target)
            relative = os.path.relpath(target, directory)
            return not relative.startswith(os.pardir)

        if not is_within_directory(base_dir, output_path):
            debug_print("Invalid path: {} attempts to escape base directory.".format(filename))
            sublime.error_message("Invalid path: {} attempts to escape base directory".format(filename))
            return None

        if os.path.exists(output_path):
            conflict_handling = config.get('handle_file_conflicts', 'prepend_and_comment')
            debug_print("File exists, using conflict handling: {}".format(conflict_handling))
            if conflict_handling == 'append_n_to_filename':
                base, ext = os.path.splitext(output_path)
                counter = 1
                while os.path.exists("{}_{}{}".format(base,counter,ext)):
                    counter += 1
                output_path = "{}_{}{}".format(base,counter,ext)
            elif conflict_handling == 'move_to_backup_dir':
                backup_dir = os.path.join(os.path.dirname(output_path), 'backup')
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                backup_path = os.path.join(backup_dir, os.path.basename(output_path))
                if os.path.exists(backup_path):
                    base, ext = os.path.splitext(backup_path)
                    counter = 1
                    while os.path.exists("{}_{}{}".format(base,counter,ext)):
                        counter += 1
                    backup_path = "{}_{}{}".format(base,counter,ext)
                os.rename(output_path, backup_path)

        return output_path


    def find_code_injection_point(self, file_content, code_block, ext):
        """Find injection points in existing file based on code block content."""
        debug_print("Analyzing for code injection points")

        file_lines = file_content.split('\n')
        code_lines = code_block.strip().split('\n')

        if not code_lines:
            return None, None

        first_line = code_lines[0].strip()
        last_line = code_lines[-1].strip()

        # Handle Python files differently
        if ext == 'py':
            return self._find_python_injection_points(file_lines, code_lines)

        # For other languages, try brace matching
        start_idx = None
        for i, line in enumerate(file_lines):
            if line.strip() == first_line:
                start_idx = i
                break

        if start_idx is None:
            return None, None

        # If last line matches exactly and isn't just a closing brace
        if last_line != '}':
            for i in range(start_idx + 1, len(file_lines)):
                if file_lines[i].strip() == last_line:
                    return start_idx, i

        # If last line is '}' or no exact match was found, try brace counting
            brace_count = 0
            for line in code_lines[1:]:  # Start after first line
                brace_count += line.count('{')
                brace_count -= line.count('}')

            # Now count braces in file until we match
            current_count = 0
            for i in range(start_idx + 1, len(file_lines)):
                current_count += file_lines[i].count('{')
                current_count -= file_lines[i].count('}')
                if current_count == brace_count:
                    return start_idx, i

        return None, None

    def _find_python_injection_points(self, file_lines, code_lines):
        """Find injection points specifically for Python files."""
        debug_print("Finding Python-specific injection points")

        def get_definition_name(line):
            """Extract function or class name from definition line."""
            line = line.strip()
            if line.startswith('def ') or line.startswith('class '):
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1].split('(')[0]
            return None

        # Get the name of the function/class being defined in code block
        code_def_name = None
        for line in code_lines:
            name = get_definition_name(line)
            if name:
                code_def_name = name
                break

        if not code_def_name:
            return None, None

        # Find matching definition in file
        start_idx = None
        end_idx = None
        current_indent = None

        for i, line in enumerate(file_lines):
            name = get_definition_name(line)
            if name == code_def_name:
                start_idx = i
                current_indent = len(line) - len(line.lstrip())
                continue

            if start_idx is not None:
                # Check if we've returned to the same or lower indentation level
                if line.strip() and len(line) - len(line.lstrip()) <= current_indent:
                    end_idx = i - 1
                    break

        if start_idx is not None and end_idx is None:
            end_idx = len(file_lines) - 1

        return start_idx, end_idx


    def should_process_extension(self, filename, config):
        """Check if file extension should be processed based on configuration."""
        if not filename:
            return False
        ext = os.path.splitext(filename)[1][1:].lower()
        include_list = config.get('extensions_2_include', [])
        ignore_list = config.get('extensions_2_ignore', [])
        # If include list is specified, only process those extensions
        if include_list:
            return ext in include_list
        # Otherwise, process everything except ignored extensions
        return ext not in ignore_list


    def inject_code_block(self, file_path, code_block, config):
        """Inject code block into existing file with appropriate commenting."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            ext = os.path.splitext(file_path)[1][1:]
            start_comment, end_comment = self.get_comment_syntax(file_path)

            start_idx, end_idx = self.find_code_injection_point(existing_content, code_block, ext)

            if start_idx is not None and end_idx is not None:
                lines = existing_content.split('\n')

                # Comment out the existing section
                commented_lines = []
                for line in lines[start_idx:end_idx + 1]:
                    if line.strip():
                        if end_comment:
                            commented_lines.append("{} {} {}".format(start_comment,line,end_comment))
                        else:
                            commented_lines.append("{} {}".format(start_comment,line))
                    else:
                        commented_lines.append(line)

                # Reconstruct the file content
                new_content = (
                    '\n'.join(lines[:start_idx]) + '\n' +
                    code_block + '\n' +
                    '\n'.join(commented_lines) + '\n' +
                    '\n'.join(lines[end_idx + 1:])
                )

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                return True

            return False

        except Exception as e:
            debug_print("Error during code injection: {}".format(str(e)))
            return False

    def extract_code_blocks(self, content, output_dir, config):
        """Extract code blocks with updated extension handling."""
        debug_print("Extracting code blocks to: {}".format(output_dir))
        code_block_pattern = r'```([^\n]*)\n([\s\S]*?)```'
        lines = content.split("\n")
        matches = list(re.finditer(code_block_pattern, content))
        debug_print("Found {} code blocks".format(len(matches)))

        for match in matches:
            lang_or_filename = match.group(1)
            code = match.group(2)
            debug_print("Processing block with lang/filename: {}".format(lang_or_filename))

            start_pos = match.start()
            preceding_line = lines[content[:start_pos].count("\n") - 1] if start_pos > 0 else None
            filename = self.get_filename_from_block(lang_or_filename, code, preceding_line, config)
            debug_print("Resolved filename: {}".format(filename))

            if filename:
                # Check if we should process this extension
                if not self.should_process_extension(filename, config):
                    debug_print("Skipping {} based on extension settings".format(filename))
                    continue

                # Check other ignore conditions
                if self.should_ignore_block(lang_or_filename, code, filename, config):
                    debug_print("Skipping {} based on block ignore settings".format(filename))
                    continue

                try:
                    output_path = self.resolve_output_path(output_dir, filename, config)
                    debug_print("Writing to: {}".format(output_path))

                    if output_path and self.ensure_directory_exists(output_path):
                        if os.path.exists(output_path) and config.get('attempt_injection', False):
                            if self.inject_code_block(output_path, code.strip(), config):
                                debug_print("Successfully injected code into {}".format(output_path))
                                continue

                        # Handle according to conflict settings if injection failed or wasn't attempted
                        if os.path.exists(output_path):
                            self.handle_file_conflict(output_path, code.strip(), config)
                        else:
                            with open(output_path, "w", encoding='utf-8') as file:
                                file.write(code.strip())
                            debug_print("Extracted: {}".format(output_path))

                except Exception as e:
                    debug_print("Error processing {}: {}".format(filename, str(e)))
                    sublime.error_message("Error processing {}: {}".format(filename, str(e)))


    def handle_file_conflict(self, file_path, code, config):
        """Handle file conflicts based on configuration."""
        conflict_handling = config.get('handle_file_conflicts', 'prepend_and_comment')

        if conflict_handling == 'prepend_and_comment':
            start_comment, end_comment = self.get_comment_syntax(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            commented_content = []
            for line in existing_content.split('\n'):
                if line.strip():
                    if end_comment:
                        commented_content.append("{} {} {}".format(start_comment, line, end_comment))
                    else:
                        commented_content.append("{} {}".format(start_comment, line))
                else:
                    commented_content.append(line)

            new_content = code + '\n\n' + '\n'.join(commented_content)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        elif conflict_handling == 'append_n_to_filename':
            base, ext = os.path.splitext(file_path)
            counter = 1
            while os.path.exists("{}_{}.{}".format(base, counter, ext)):
                counter += 1
            with open("{}_{}.{}".format(base, counter, ext), 'w', encoding='utf-8') as f:
                f.write(code)

        elif conflict_handling == 'move_to_backup_dir':
            backup_dir = os.path.join(os.path.dirname(file_path), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            if os.path.exists(backup_path):
                base, ext = os.path.splitext(backup_path)
                counter = 1
                while os.path.exists("{}_{}.{}".format(base, counter, ext)):
                    counter += 1
                backup_path = "{}_{}.{}".format(base, counter, ext)
            os.rename(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)


    def insert_code_blocks(self, content, directory, config):
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

            filename = self.get_filename_from_block(lang_or_filename, code, None, config)
            debug_print("Resolved filename: {}".format(filename))

            if filename and not self.should_ignore_block(lang_or_filename, code, filename, config):
                try:
                    file_path = os.path.join(directory, filename)
                    debug_print("Attempting to write to: {}".format(file_path))
                    if os.path.exists(file_path):
                        debug_print("File exists: {}".format(file_path))
                        with open(file_path, 'r', encoding='utf-8') as f:
                            updated_code = f.read().strip()
                            content = content.replace(match.group(0), "```{}\n{}\n```".format(
                                lang_or_filename or '', updated_code))
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
                    sublime.error_message("Error processing {}: {}".format(filename, str(e)))

        try:
            debug_print("Saving changes to markdown file: {}".format(self.view.file_name()))
            with open(self.view.file_name(), 'w', encoding='utf-8') as f:
                f.write(content)
            debug_print("Markdown file updated successfully")
        except Exception as e:
            debug_print("Error writing to markdown file: {}".format(str(e)))
            sublime.error_message("Error writing to markdown file: {}".format(str(e)))

    def get_files_recursive(self, directory):
        """Gets all files in directory and subdirectories."""
        debug_print("Scanning directory: {}".format(directory))
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                debug_print("Found directory: {}".format(root))
                for filename in filenames:
                    if not filename.startswith('.'):  # Skip hidden files
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, directory)
                        files.append(rel_path)
                        debug_print("Added file: {}".format(rel_path))
        except Exception as e:
            debug_print("Error scanning directory: {}".format(str(e)))
        return sorted(files)  # Sort for consistent output

    def generate_markdown_content(self, directory, files, config):
        """Generates markdown content from files."""
        debug_print("Generating markdown for {} files".format(len(files)))
        content = ["# Generated Markdown File\n"]
        naming_convention = config.get("file_naming_convention", "on_fence")

        for file_path in files:
            try:
                full_path = os.path.join(directory, file_path)
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                ext = os.path.splitext(file_path)[1][1:]
                if naming_convention == "before_fence":
                    content.append(file_path)
                    content.append("```{}".format(ext))
                elif naming_convention == "after_fence":
                    content.append("```{}".format(ext))
                    content.append("// {}".format(file_path))
                else:  # on_fence or following_first_code_fence
                    content.append("```{}".format(file_path))

                content.append(file_content)
                content.append("```\n")
                debug_print("Added content for: {}".format(file_path))
            except Exception as e:
                debug_print("Error processing file {}: {}".format(file_path, str(e)))

        return "\n".join(content)

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

    def format_markdown_block(self, file_path, content, config):
        """Format a single file as a markdown code block."""
        naming_convention = config.get("file_naming_convention", "on_fence")
        lines = []

        if naming_convention == "before_fence":
            lines.append(file_path)
            lines.append("```{}".format(self.get_file_language(file_path)))
        elif naming_convention == "after_fence":
            lines.append("```{}".format(self.get_file_language(file_path)))
            lines.append("// {}".format(file_path))
        else:  # on_fence
            lines.append("```{}".format(file_path))

        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")  # Empty line after block
        return "\n".join(lines)

class Dir2MarkdownCommand(MarkdownBaseCommand):
    def __init__(self, view=None):
        if SUBLIME_AVAILABLE and view:
            self.view = view
        else:
            self.view = None

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

    def generate_directory_tree(self, base_dir):
        """Generate a visual directory tree structure using os.walk()."""
        debug_print("Generating directory tree for: {}".format(base_dir))

        def should_exclude(name):
            """Check if a file or directory should be excluded from the tree."""
            # Add any folders or files you want to exclude
            excludes = ['.git', '__pycache__', '.DS_Store', '.pio']
            return name in excludes or name.startswith('.git')

        def add_files_to_tree(tree_dict, path_parts, is_file):
            """Recursively build tree dictionary."""
            if not path_parts:
                return

            current = path_parts[0]
            remaining = path_parts[1:]

            if current not in tree_dict:
                tree_dict[current] = {"files": [], "dirs": {}}

            if is_file and not remaining:
                tree_dict[current]["files"].append(current)
            elif not is_file and not remaining:
                pass  # Directory already created
            else:
                add_files_to_tree(tree_dict[current]["dirs"], remaining, is_file)

        def format_tree(tree_dict, prefix="", is_last=True, is_root=False):
            """Convert tree dictionary to formatted string."""
            lines = []

            if is_root:
                lines.append(os.path.basename(base_dir))

            # Sort files and directories
            items = []

            # Add directories
            for dirname in sorted(tree_dict["dirs"].keys()):
                items.append((dirname, True))

            # Add files
            for filename in sorted(tree_dict["files"]):
                items.append((filename, False))

            # Process all items
            for idx, (name, is_dir) in enumerate(items):
                is_last_item = (idx == len(items) - 1)

                if is_root:
                    new_prefix = "|   " if not is_last_item else "    "
                else:
                    new_prefix = prefix + ("|   " if not is_last_item else "    ")

                lines.append(prefix + "|__ " + name)

                if is_dir:
                    lines.extend(format_tree(
                        tree_dict["dirs"][name],
                        new_prefix,
                        is_last_item
                    ))

            return lines

        try:
            # Build tree structure
            tree = {"files": [], "dirs": {}}

            for root, dirs, files in os.walk(base_dir):
                # Remove excluded directories
                dirs[:] = [d for d in dirs if not should_exclude(d)]

                # Calculate relative path
                rel_path = os.path.relpath(root, base_dir)
                if rel_path != ".":
                    path_parts = rel_path.split(os.sep)
                    add_files_to_tree(tree["dirs"], path_parts, False)

                # Add files
                for file in sorted(files):
                    if rel_path == ".":
                        add_files_to_tree(tree, [file], True)
                    else:
                        path_parts = rel_path.split(os.sep) + [file]
                        add_files_to_tree(tree["dirs"], path_parts, True)

            # Format tree
            tree_lines = format_tree(tree, is_root=True)
            return "\n".join(tree_lines)

        except Exception as e:
            debug_print("Error generating directory tree: {}".format(str(e)))
            return "Error generating directory tree"


    def format_markdown_block(self, file_path, content, config):
        """Format a single file as a markdown code block."""
        naming_convention = config.get("file_naming_convention", "on_fence")
        lines = []

        if naming_convention == "before_fence":
            lines.append(file_path)
            lines.append("```{}".format(self.get_file_language(file_path)))
        elif naming_convention == "after_fence":
            lines.append("```{}".format(self.get_file_language(file_path)))
            lines.append("// {}".format(file_path))
        else:  # on_fence or following_first_code_fence
            lines.append("```{}".format(file_path))

        lines.append(content.strip())
        lines.append("```\n")
        return "\n".join(lines)

    def run(self, edit=None):
        """Run the command in either Sublime Text or standalone mode."""
        debug_print("Starting Dir2Markdown command")
        config = self.load_config()

        # Determine base directory and output file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(script_dir, ".example")
        output_file = os.path.join(base_dir, "generated_example.md")

        if SUBLIME_AVAILABLE and self.view and self.view.file_name():
            base_dir = os.path.dirname(self.view.file_name())
            output_file = self.view.file_name()
            debug_print("Using Sublime Text mode")
        else:
            debug_print("Using standalone mode")

        debug_print("Base directory: {}".format(base_dir))
        debug_print("Output file: {}".format(output_file))

        try:
            # Generate directory tree first
            directory_tree = self.generate_directory_tree(base_dir)

            # Start content with directory tree
            content = [
                "# Directory Structure\n",
                "```",
                directory_tree,
                "```\n",
                "# File Contents\n"
            ]
            # Skip test output directories and focus on original files
            all_files = []
            for root, _, files in os.walk(base_dir):
                if "output_" in root:
                    continue
                for filename in sorted(files):
                    if filename.startswith('.') or filename.endswith('.md'):
                        continue
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, base_dir)
                    # Check if the file extension should be processed based on config
                    if self.should_process_extension(rel_path, config):
                        all_files.append(rel_path)
                        debug_print("Found file: {}".format(rel_path))
                    else:
                        debug_print("Skipping file due to extension settings: {}".format(rel_path))

            if not all_files:
                msg = "No files found in directory matching extension criteria"
                debug_print(msg)
                if SUBLIME_AVAILABLE:
                    sublime.message_dialog(msg)
                return

            for file_path in sorted(all_files):
                try:
                    full_path = os.path.join(base_dir, file_path)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    block = self.format_markdown_block(file_path, file_content, config)
                    content.append(block)
                    debug_print("Added content for: {}".format(file_path))
                except Exception as e:
                    debug_print("Error processing {}: {}".format(file_path, str(e)))

            markdown_content = "\n".join(content)

            # Write the content
            if SUBLIME_AVAILABLE and edit is not None and self.view:
                self.view.replace(edit, sublime.Region(0, self.view.size()), markdown_content)
                debug_print("Updated current view with generated markdown")
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                debug_print("Wrote markdown to: {}".format(output_file))

        except Exception as e:
            error_msg = "Error generating markdown: {}".format(str(e))
            debug_print(error_msg)
            if SUBLIME_AVAILABLE:
                sublime.error_message(error_msg)
            raise


class Markdown2DirCommand(MarkdownBaseCommand):
    def run(self, edit):
        debug_print("Running Markdown2Dir command")
        if not self.is_markdown_file():
            debug_print("Not a markdown file")
            sublime.message_dialog(
                "A directory cannot be determined from an unsaved file. First, save the file with the desired path and try again."
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
                debug_print("First 100 characters of content:")
                debug_print(content[:100])
        except Exception as e:
            debug_print("Error reading markdown file: {}".format(str(e)))
            sublime.error_message("Error reading markdown file: {}".format(str(e)))
            return

        if content:
            self.extract_code_blocks(content, directory, config)
        else:
            debug_print("Markdown file empty.")
            sublime.error_message("No content found in the markdown file.")


def test_markdown_extraction():
    """
    Test function for direct Python execution.
    Creates test files in script_directory/.example directory structure.
    Tests all three naming conventions: before_fence, on_fence, and after_fence.
    """
    class MockConfig:
        def __init__(self):
            self.config = {
                "file_naming_convention": "on_fence",
                "blocks_ignored": [],
                "attempt_injection": False,
                "handle_file_conflicts": "prepend_and_comment"
            }

        def get(self, key, default=None):
            return self.config.get(key, default)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, ".example")
    os.makedirs(base_dir, exist_ok=True)

    debug_print("Creating test files in: {}".format(base_dir))

    test_content = """# Test Markdown File

project/sub_dir/prefence_file.cpp
```c++
// This is a test C++ file using before_fence convention
int main() {
    return 0;
}
```

```project/sub_dir/onfence_file.hpp
// This is a test C++ header using on_fence convention
class TestClass {
public:
    TestClass() {}
};
```

```c++
// project/sub_dir/postfence_file.cpp
// This is a test C++ file using after_fence convention
void test_function() {
    // Implementation
}
```"""

    md_path = os.path.join(base_dir, "Example.md")
    with open(md_path, "w", encoding='utf-8') as f:
        f.write(test_content)

    try:
        config = MockConfig()

        for convention in ["before_fence", "on_fence", "after_fence"]:
            config.config["file_naming_convention"] = convention
            output_dir = os.path.join(base_dir, "output_{}".format(convention))
            os.makedirs(output_dir, exist_ok=True)

            debug_print("Testing {} convention...".format(convention))
            debug_print("Output directory: {}".format(output_dir))

            cmd = MarkdownBaseCommand()
            cmd.extract_code_blocks(test_content, output_dir, config)

            debug_print("Directory structure for {}:".format(convention))
            for root, dirs, files in os.walk(output_dir):
                rel_path = os.path.relpath(root, output_dir)
                if rel_path == ".":
                    rel_path = "root"
                debug_print("Directory: {}".format(rel_path))
                if dirs:
                    debug_print("Subdirectories:", dirs)
                if files:
                    debug_print("Files:", files)
                    for file in files:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            debug_print("Content of {}:".format(file))
                            debug_print("```")
                            debug_print(content)
                            debug_print("```")
    except Exception as e:
        debug_print("Error during testing: {}".format(str(e)))
        raise


if __name__ == "__main__":
    if not SUBLIME_AVAILABLE:
        debug_print("Running in standalone mode (Sublime Text not available)")
        debug_print("\nPhase 1: Running test extraction...")
        test_markdown_extraction()
        debug_print("\nPhase 2: Running directory to markdown conversion...")
        cmd = Dir2MarkdownCommand()
        try:
            cmd.run()  # Run without edit parameter in standalone mode
        except Exception as e:
            debug_print("Error during markdown generation: {}".format(str(e)))
            import traceback
            debug_print(traceback.format_exc())
    else:
        debug_print("Running in Sublime Text plugin mode")
