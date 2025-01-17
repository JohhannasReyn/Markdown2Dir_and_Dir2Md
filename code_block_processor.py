"""
The `CodeBlockProcessor` class handles all code block-related operations with these key features:

1. Code Block Extraction:
   - Pattern matching for markdown code blocks
   - Filename resolution from different conventions
   - Block filtering based on configuration

2. Code Injection:
   - Smart injection point detection
   - Language-specific handling (especially Python)
   - Comment preservation
   - Brace counting for complex blocks

3. File Conflict Handling:
   - Multiple conflict resolution strategies
   - Backup creation
   - Comment wrapping
   - Incremental naming

4. Block Analysis:
   - Code block validation
   - Minimum line count checking
   - Content-based filtering
   - Empty block detection

5. Integration:
   - Works with PathProcessor for file operations
   - Uses parent's comment syntax definitions
   - Maintains consistent debug logging

"""
import os
import re
from .utils import debug_print

class CodeBlockProcessor:
    def __init__(self, parent):
        self.parent = parent
        self.view = parent.view

    def extract_code_blocks(self, content, output_dir, config):
        """Extract code blocks with improved error handling."""
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                debug_print("Failed to create directory {}: {}".format(output_dir, str(e)))
                return False

        if not os.access(output_dir, os.W_OK):
            debug_print("No write permission for directory {}".format(output_dir))
            return False

        debug_print("Extracting code blocks to: {}".format(output_dir))
        code_block_pattern = r'```([^\n]*)\n([\s\S]*?)```'
        lines = content.split("\n")
        matches = list(re.finditer(code_block_pattern, content))
        debug_print("Found {} code blocks".format(len(matches)))

        for match in matches:
            try:
                lang_or_filename = match.group(1)
                code = match.group(2)
                debug_print("Processing block with lang/filename: {}".format(lang_or_filename))

                # Get the line before the code block for potential filename
                start_pos = match.start()
                preceding_line = lines[content[:start_pos].count("\n") - 1] if start_pos > 0 else None

                filename = self.get_filename_from_block(lang_or_filename, code, preceding_line, config)
                debug_print("Resolved filename: {}".format(filename))

                if not filename:
                    debug_print("No filename found for block, skipping")
                    continue

                if self.should_ignore_block(lang_or_filename, code, filename, config):
                    debug_print("Skipping {} based on block ignore settings".format(filename))
                    continue

                output_path = self.parent.path_processor.resolve_output_path(output_dir, filename, config)
                if not output_path:
                    continue

                debug_print("Writing to: {}".format(output_path))

                # Ensure parent directories exist
                parent_dir = os.path.dirname(output_path)
                if parent_dir and not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir)
                    except OSError as e:
                        debug_print("Failed to create directory {}: {}".format(parent_dir, str(e)))
                        continue

                # Check write permissions
                if os.path.exists(parent_dir) and not os.access(parent_dir, os.W_OK):
                    debug_print("No write permission for directory {}".format(parent_dir))
                    continue

                if os.path.exists(output_path) and config.get('attempt_injection', False):
                    if self.inject_code_block(output_path, code.strip(), config):
                        debug_print("Successfully injected code into {}".format(output_path))
                        continue

                # Try to write the file with backup
                if not self.safe_write_file(output_path, code.strip()):
                    continue

                debug_print("Extracted: {}".format(output_path))

            except Exception as e:
                debug_print("Error processing code block: {}".format(str(e)))
                continue

        return True

    def _write_code_block(self, output_path, code, config):
        """Write code block to file, handling conflicts according to config."""
        if os.path.exists(output_path):
            self.handle_file_conflict(output_path, code, config)
        else:
            with open(output_path, "w", encoding='utf-8') as file:
                file.write(code)

    def get_filename_from_block(self, lang_or_filename, code, preceding_line, config):
        """Extract filename from code block using configured convention."""
        debug_print("get_filename_from_block input:")
        debug_print("  lang_or_filename: {}".format(lang_or_filename))
        debug_print("  preceding_line: {}".format(preceding_line))
        debug_print("  code first line: {}".format(code.splitlines()[0] if code else None))

        def sanitize_path(path):
            if path:
                return self.parent.path_processor.normalize_path(path)
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

        # Try before_fence if no filename found
        if not filename and preceding_line:
            extracted = extract_path_from_text(preceding_line)
            if extracted:
                filename = extracted
                debug_print("  found filename in preceding line: {}".format(filename))

        # Try after_fence as last resort
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
                debug_print("Ignoring block without extension")
                return True

        # Check if code is empty
        if not code.strip():
            debug_print("Ignoring empty block")
            return True

        return False

    def inject_code_block(self, file_path, code_block, config):
        """Inject code block into existing file with appropriate commenting."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            ext = os.path.splitext(file_path)[1][1:]
            start_comment, end_comment = self.parent.get_comment_syntax(file_path)

            start_idx, end_idx = self.find_code_injection_point(existing_content, code_block, ext)

            if start_idx is not None and end_idx is not None:
                lines = existing_content.split('\n')
                # Comment out existing section
                commented_lines = self._comment_lines(lines[start_idx:end_idx + 1], start_comment, end_comment)

                # Reconstruct file content
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

    def _comment_lines(self, lines, start_comment, end_comment):
        """Add comments to a set of lines using the appropriate syntax."""
        commented_lines = []
        for line in lines:
            if line.strip():
                if end_comment:
                    commented_lines.append("{} {} {}".format(start_comment, line, end_comment))
                else:
                    commented_lines.append("{} {}".format(start_comment, line))
            else:
                commented_lines.append(line)
        return commented_lines

    def find_code_injection_point(self, file_content, code_block, ext):
        """Find injection points in existing file based on code block content."""
        debug_print("Analyzing for code injection points")

        if ext == 'py':
            return self._find_python_injection_points(file_content.split('\n'), code_block.strip().split('\n'))

        return self._find_general_injection_points(file_content.split('\n'), code_block.strip().split('\n'))

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

    def _find_general_injection_points(self, file_lines, code_lines):
        """Find injection points for non-Python files."""
        if not code_lines:
            return None, None

        first_line = code_lines[0].strip()
        last_line = code_lines[-1].strip()

        # Find starting point
        start_idx = None
        for i, line in enumerate(file_lines):
            if line.strip() == first_line:
                start_idx = i
                break

        if start_idx is None:
            return None, None

        # If last line isn't just a closing brace
        if last_line != '}':
            for i in range(start_idx + 1, len(file_lines)):
                if file_lines[i].strip() == last_line:
                    return start_idx, i

        # Try brace counting for complex blocks
        brace_count = 0
        for line in code_lines[1:]:  # Start after first line
            brace_count += line.count('{')
            brace_count -= line.count('}')

        current_count = 0
        for i in range(start_idx + 1, len(file_lines)):
            current_count += file_lines[i].count('{')
            current_count -= file_lines[i].count('}')
            if current_count == brace_count:
                return start_idx, i

        return None, None

    def handle_file_conflict(self, file_path, code, config):
        """Handle file conflicts based on configuration."""
        conflict_handling = config.get('handle_file_conflicts', 'prepend_and_comment')

        if conflict_handling == 'prepend_and_comment':
            start_comment, end_comment = self.parent.get_comment_syntax(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            commented_content = self._comment_lines(existing_content.split('\n'), start_comment, end_comment)
            new_content = code + '\n\n' + '\n'.join(commented_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        elif conflict_handling == 'append_n_to_filename':
            base, ext = os.path.splitext(file_path)
            counter = 1
            while os.path.exists("{}_{}{}".format(base, counter, ext)):
                counter += 1
            with open("{}_{}{}".format(base, counter, ext), 'w', encoding='utf-8') as f:
                f.write(code)

        elif conflict_handling == 'move_to_backup_dir':
            backup_dir = os.path.join(os.path.dirname(file_path), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))

            if os.path.exists(backup_path):
                base, ext = os.path.splitext(backup_path)
                counter = 1
                while os.path.exists("{}_{}{}".format(base, counter, ext)):
                    counter += 1
                backup_path = "{}_{}{}".format(base, counter, ext)

            os.rename(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)


    def safe_write_file(self, file_path, content):
        """Write file with backup mechanism."""
        backup_path = "{}.bak".format(file_path)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    with open(backup_path, 'w', encoding='utf-8') as b:
                        b.write(f.read())
            except Exception as e:
                debug_print("Failed to create backup: {}".format(str(e)))
                return False

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return True
        except Exception as e:
            if os.path.exists(backup_path):
                os.rename(backup_path, file_path)
            debug_print("Failed to write file: {}".format(str(e)))
            return False
