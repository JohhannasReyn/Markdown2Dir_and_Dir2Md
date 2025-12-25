"""
The `CodeBlockProcessor` class handles all code block-related operations with these key features:

1. Code Block Extraction:
   - Pattern matching for markdown code blocks (ONLY at column 0)
   - Filename resolution from different conventions
   - Block filtering based on configuration
   - Nested code fence indentation handling

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
   - Nested code fence detection and indentation level tracking

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

    def is_markdown_fence(self, lang_or_filename, code):
        """
        Check if this code block should be skipped as a markdown fence.
        
        IMPORTANT: We only skip if:
        1. The language is explicitly 'md' or 'markdown' AND
        2. There's NO file extension in the identifier
        
        This allows .md FILES to be processed even if they contain code fences.
        """
        # If it has a file extension (contains a dot), it's a file, not just a language
        if '.' in lang_or_filename:
            # It's a filename, not just a language identifier
            # Don't skip it even if it's a .md file
            return False
        
        # No file extension - check if it's a markdown language identifier
        if lang_or_filename.lower() in ['md', 'markdown']:
            return True

        return False

    def measure_indentation(self, line):
        """
        Measure the indentation of a line in spaces.
        Converts tabs to 4 spaces for consistency.
        """
        expanded = line.expandtabs(4)
        stripped = expanded.lstrip(' ')
        return len(expanded) - len(stripped)

    def reduce_indentation(self, code, reduction_level):
        """
        Reduce the indentation of code content by the specified number of spaces.
        """
        if reduction_level <= 0:
            return code
        
        lines = code.split('\n')
        result_lines = []
        
        for line in lines:
            # Convert tabs to spaces for consistent handling
            expanded_line = line.expandtabs(4)
            
            # Calculate how many leading spaces this line has
            leading_spaces = len(expanded_line) - len(expanded_line.lstrip(' '))
            
            # Remove up to reduction_level spaces
            spaces_to_remove = min(leading_spaces, reduction_level)
            result_lines.append(expanded_line[spaces_to_remove:])
        
        return '\n'.join(result_lines)

    def process_nested_fences(self, code):
        """
        Process nested code fences within a code block.
        Recursively reduces indentation of nested fences by one level (4 spaces).
        """
        lines = code.split('\n')
        result_lines = []
        inside_fence = False
        
        for line in lines:
            line_indent = self.measure_indentation(line)
            stripped = line.lstrip()
            
            if stripped.startswith('```'):
                if not inside_fence:
                    # Opening fence
                    if line_indent > 0:
                        inside_fence = True
                        reduced_indent = max(0, line_indent - 4)
                        result_lines.append(' ' * reduced_indent + stripped)
                        debug_print("Reducing nested fence from {} to {} spaces".format(
                            line_indent, reduced_indent))
                    else:
                        result_lines.append(line)
                else:
                    # Closing fence
                    if line_indent > 0:
                        reduced_indent = max(0, line_indent - 4)
                        result_lines.append(' ' * reduced_indent + stripped)
                    else:
                        result_lines.append(line)
                    inside_fence = False
            elif inside_fence and line_indent > 0:
                # Content inside a nested fence
                reduced_indent = max(0, line_indent - 4)
                content = line.expandtabs(4)[line_indent:]
                result_lines.append(' ' * reduced_indent + content)
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)

    def extract_code_blocks(self, content, output_dir, config):
        """Extract code blocks with proper nested fence handling."""
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                debug_print("Failed to create directory {}: {}".format(output_dir, str(e)))
                return False

        debug_print("Extracting code blocks to: {}".format(output_dir))
        
        # Pattern ONLY matches fences at column 0 (no leading whitespace)
        code_block_pattern = r'^```([^\n]*)\n([\s\S]*?)^```'
        matches = list(re.finditer(code_block_pattern, content, re.MULTILINE))
        debug_print("Found {} potential code blocks at column 0".format(len(matches)))

        processed_files = set()

        for match in matches:
            try:
                # Double-check that fence is truly at column 0
                pos = match.start()
                line_start = content.rfind('\n', 0, pos)
                if line_start == -1:
                    line_start = 0
                else:
                    line_start += 1
                
                # Check for any whitespace before the fence
                prefix = content[line_start:pos]
                
                if prefix.strip() == '' and len(prefix) > 0:
                    # There's whitespace - skip this indented fence
                    debug_print("Skipping fence with {} chars whitespace before it".format(len(prefix)))
                    continue
                
                # Measure indentation as additional safety check
                line_end = content.find('\n', pos)
                full_line = content[line_start:line_end if line_end != -1 else len(content)]
                line_indent = self.measure_indentation(full_line)
                
                if line_indent > 0:
                    debug_print("Skipping fence with {} spaces indentation".format(line_indent))
                    continue

                debug_print("Processing top-level code block (column 0)")

                lang_or_filename = match.group(1).strip()
                code = match.group(2)
                debug_print("Block identifier: '{}'".format(lang_or_filename))

                # Check if this should be skipped as a markdown fence
                # (language="md" with no filename)
                if self.is_markdown_fence(lang_or_filename, code):
                    debug_print("Skipping markdown language fence (no filename)")
                    continue

                # Get the line before the code block for potential filename
                lines = content[:match.start()].split('\n')
                preceding_line = lines[-1] if lines else None

                filename = self.get_filename_from_block(lang_or_filename, code, preceding_line, config)
                debug_print("Resolved filename: '{}'".format(filename))

                if not filename:
                    debug_print("No filename found for block, skipping")
                    continue

                # Skip files we've already processed
                if filename in processed_files:
                    debug_print("Already processed {}, skipping".format(filename))
                    continue
                processed_files.add(filename)

                if self.should_ignore_block(lang_or_filename, code, filename, config):
                    debug_print("Skipping {} based on block ignore settings".format(filename))
                    continue

                # Skip files in .git directory
                if '.git' in filename.split(os.sep):
                    debug_print("Skipping file in .git directory: {}".format(filename))
                    continue

                output_path = self.parent.path_processor.resolve_output_path(output_dir, filename, config)
                if not output_path:
                    continue

                debug_print("Writing to: {}".format(output_path))

                # Process nested code fences in the content
                # Reduce indentation of any nested fences by 4 spaces
                processed_code = self.process_nested_fences(code)

                # Write the file
                code_content = processed_code.strip()
                try:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(code_content)
                    debug_print("Successfully created file: {}".format(output_path))
                except Exception as e:
                    debug_print("Error writing file {}: {}".format(output_path, str(e)))
                    continue

            except Exception as e:
                debug_print("Error processing code block: {}".format(str(e)))
                import traceback
                debug_print(traceback.format_exc())
                continue

        return True

    def merge_code_blocks(self, existing_content, new_content):
        """Merge two code blocks line by line, preserving order and adding new content."""
        existing_lines = existing_content.strip().split('\n')
        new_lines = new_content.strip().split('\n')
        merged_lines = []
        remaining_new_lines = new_lines.copy()

        for existing_line in existing_lines:
            merged_lines.append(existing_line)

            for i, new_line in enumerate(remaining_new_lines):
                if new_line == existing_line:
                    merged_lines.extend(remaining_new_lines[:i])
                    remaining_new_lines = remaining_new_lines[i+1:]
                    break

        if remaining_new_lines:
            merged_lines.extend(remaining_new_lines)

        return '\n'.join(merged_lines)

    def _write_code_block(self, output_path, code, config):
        """Write code block to file, handling conflicts according to config."""
        if os.path.exists(output_path):
            if config.get('overwrite_on_build_2_md', True):
                with open(output_path, "w", encoding='utf-8') as file:
                    file.write(code)
            else:
                try:
                    with open(output_path, "r", encoding='utf-8') as file:
                        existing_content = file.read()
                    merged_content = self.merge_code_blocks(existing_content, code)
                    with open(output_path, "w", encoding='utf-8') as file:
                        file.write(merged_content)
                except Exception as e:
                    debug_print("Error during merge, falling back to overwrite: {}".format(str(e)))
                    with open(output_path, "w", encoding='utf-8') as file:
                        file.write(code)
        else:
            with open(output_path, "w", encoding='utf-8') as file:
                file.write(code)

    def get_filename_from_block(self, lang_or_filename, code, preceding_line, config):
        """Extract filename from code block using configured convention."""
        debug_print("get_filename_from_block input:")
        debug_print("  lang_or_filename: '{}'".format(lang_or_filename))
        debug_print("  preceding_line: '{}'".format(preceding_line))
        debug_print("  code first line: '{}'".format(code.splitlines()[0] if code else None))

        def sanitize_path(path):
            if path:
                return self.parent.path_processor.normalize_path(path)
            debug_print("  sanitize_path received None")
            return None

        def extract_path_from_text(text):
            """Extract file path from text, stripping whitespace."""
            if not text:
                debug_print("  extract_path got empty text")
                return None
            
            # CRITICAL: Strip whitespace BEFORE pattern matching
            text = text.strip()
            
            # Pattern matches paths with optional drive letter and slashes
            path_pattern = r'(?:[a-zA-Z]:)?(?:[\\\/])?(?:[\w\s.-]+[\\\/])*[\w\s.-]+\.\w+'
            match = re.search(path_pattern, text)
            
            if match:
                # CRITICAL: Strip whitespace from the matched result
                result = match.group(0).strip()
                debug_print("  extracted path from text: '{}'".format(result))
                return result
            
            debug_print("  no path found in text")
            return None

        naming_convention = config.get("file_naming_convention", "on_fence")
        debug_print("  using naming convention: {}".format(naming_convention))
        filename = None

        # Try on_fence first
        if '.' in str(lang_or_filename):
            filename = lang_or_filename
            debug_print("  found filename in fence: '{}'".format(filename))

        # Try before_fence if no filename found
        if not filename and preceding_line:
            extracted = extract_path_from_text(preceding_line)
            if extracted:
                filename = extracted
                debug_print("  found filename in preceding line: '{}'".format(filename))

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
                        debug_print("  found filename in first code line: '{}'".format(filename))
                        break

        result = sanitize_path(filename)
        debug_print("  final filename: '{}'".format(result))
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
        # NOTE: Only check content, not filename, to avoid false positives
        if 'readme' in blocks_ignored:
            # Only ignore if the content is predominantly readme-like
            # (not just a file that happens to be named README.md)
            if filename and 'readme' in filename.lower():
                # It's a README file - don't auto-ignore based on content
                pass
            elif any(x in code.lower() for x in ['# readme', '## readme']):
                debug_print("Ignoring readme content block")
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

    def is_indented_code_block(self, match, content):
        """Check if a code block is intentionally indented (should be treated as content)."""
        pos = match.start()

        line_start = content.rfind('\n', 0, pos)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1

        line_prefix = content[line_start:pos]
        stripped_prefix = line_prefix.strip()

        debug_print("Code block line prefix: '{}', stripped: '{}'".format(
            line_prefix.replace(' ', '·'),
            stripped_prefix
        ))

        if stripped_prefix or line_prefix.startswith('    ') or line_prefix.startswith('\t'):
            debug_print("Determined code block is indented")
            return True

        debug_print("Determined code block is not indented")
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

        code_def_name = None
        for line in code_lines:
            name = get_definition_name(line)
            if name:
                code_def_name = name
                break

        if not code_def_name:
            return None, None

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

        start_idx = None
        for i, line in enumerate(file_lines):
            if line.strip() == first_line:
                start_idx = i
                break

        if start_idx is None:
            return None, None

        if last_line != '}':
            for i in range(start_idx + 1, len(file_lines)):
                if file_lines[i].strip() == last_line:
                    return start_idx, i

        brace_count = 0
        for line in code_lines[1:]:
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

    def process_code_block(self, code):
        """Process code content, handling nested code blocks through indentation."""
        code_block_pattern = r'```([^\n]*)\n([\s\S]*?)```'

        def replace_code_blocks(match):
            block = match.group(0)
            return self.parent.project_settings.indent_code_block(block)

        processed_code = re.sub(code_block_pattern, replace_code_blocks, code)
        return processed_code

    def format_code_block(self, content, filename):
        """Format code block, properly handling nested code blocks."""
        processed_content = self.process_nested_fences(content)
        return processed_content