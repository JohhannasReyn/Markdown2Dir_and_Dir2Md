import os
import re
import sublime
import sublime_plugin
import json

class CodeBlockManagerBase:
    """Base class containing shared functionality for code block operations"""
    
    @staticmethod
    def plugin_loaded():
        """Load and parse settings from Sublime Text settings file"""
        settings = sublime.load_settings("ABicycleMakingClown.sublime-settings")
        config = {
            'file_naming_convention': settings.get('file_naming_convention', 'following_first_code_fence'),
            'blocks_ignored': settings.get('blocks_ignored', ['ext_bash', 'ext_lua', 'lessthan_3', 'nameless']),
            'attempt_injection': settings.get('attempt_injection', True),
            'handle_file_conflicts': settings.get('handle_file_conflicts', 'prepend_and_comment')
        }
        return config

    @staticmethod
    def get_filename_from_block(lang, code, preceding_line, config):
        """Extract filename based on configured naming convention"""
        convention = config['file_naming_convention']
        
        if convention == 'following_first_code_fence':
            return lang if '.' in lang else None
            
        elif convention == 'line_preceding_code_fence':
            if preceding_line and preceding_line.strip():
                filename_match = re.search(r'[\w.-]+\.\w+', preceding_line)
                return filename_match.group(0) if filename_match else None
            return None
            
        elif convention == 'first_line_of_code':
            first_line = code.splitlines()[0].strip() if code else ""
            match = re.match(r"[#/]{1,2}\s*(.+\.\w+)", first_line)
            return match.group(1) if match else None
        
        return None

    @staticmethod
    def should_ignore_block(lang, code, filename, config):
        """Check if block should be ignored based on settings"""
        blocks_ignored = config['blocks_ignored']
        
        if 'nameless' in blocks_ignored and not filename:
            return True
            
        if 'lessthan_3' in blocks_ignored:
            if len(code.splitlines()) < 3:
                return True
                
        if any(rule.startswith('ext_') for rule in blocks_ignored):
            ext = filename.split('.')[-1] if filename else ''
            if f'ext_{ext}' in blocks_ignored:
                return True
                
        return False

    @staticmethod
    def handle_file_conflict(output_path, code, config):
        """Handle file conflicts based on settings"""
        conflict_handling = config['handle_file_conflicts']
        
        if conflict_handling == 'prepend_and_comment':
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    existing_code = f.read()
                
                ext = output_path.split('.')[-1].lower()
                comment_char = '//' if ext in ['js', 'cpp', 'c', 'h'] else '#' if ext in ['py', 'rb'] else ';'
                
                commented_code = '\n'.join(f'{comment_char} {line}' for line in existing_code.splitlines())
                final_code = f"{code.strip()}\n\n# Original code (commented out):\n{commented_code}"
                
                with open(output_path, 'w') as f:
                    f.write(final_code)
                return True
                
        elif conflict_handling == 'append_n_to_filename':
            n = 1
            base, ext = os.path.splitext(output_path)
            while os.path.exists(f"{base}({n}){ext}"):
                n += 1
            output_path = f"{base}({n}){ext}"
            
        elif conflict_handling == 'append_oN_to_ext':
            n = 1
            while os.path.exists(f"{output_path}.o{n}"):
                n += 1
            output_path = f"{output_path}.o{n}"
            
        elif conflict_handling == 'move_to_backup_dir':
            backup_dir = os.path.join(os.path.dirname(output_path), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(output_path))
            if os.path.exists(backup_path):
                n = 1
                base, ext = os.path.splitext(backup_path)
                while os.path.exists(f"{base}({n}){ext}"):
                    n += 1
                backup_path = f"{base}({n}){ext}"
            os.rename(output_path, backup_path)
            
        return False

class Dir2MarkdownCommand(sublime_plugin.TextCommand, CodeBlockManagerBase):
    """Sublime Text command to extract code from markdown to directory"""
    
    def run(self, edit):
        config = self.plugin_loaded()
        markdown_file = self.view.file_name()
        if markdown_file:
            directory = os.path.dirname(markdown_file)
            self.extract_code_blocks(markdown_file, directory, config)
        else:
            sublime.message_dialog("A directory cannot be parsed from an unsaved file. First, save the file with the targeted directory, then try again.")

    def extract_code_blocks(self, markdown_path, output_dir, config):
        """Extract code blocks from markdown file based on configuration"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(markdown_path, 'r') as md_file:
            content = md_file.read()

        lines = content.split('\n')
        code_block_pattern = r'```(\S+)?\n([\s\S]*?)```'
        matches = list(re.finditer(code_block_pattern, content))
        
        for match in matches:
            lang = match.group(1)
            code = match.group(2)
            
            start_pos = match.start()
            preceding_line = None
            
            text_before = content[:start_pos]
            line_number = text_before.count('\n')
            if line_number > 0:
                preceding_line = lines[line_number - 1]
            
            filename = self.get_filename_from_block(lang, code, preceding_line, config)
            
            if self.should_ignore_block(lang, code, filename, config):
                continue
                
            if not filename and 'nameless' not in config['blocks_ignored']:
                n = 1
                ext = lang if lang else 'txt'
                while os.path.exists(os.path.join(output_dir, f"{n}.{ext}")):
                    n += 1
                filename = f"{n}.{ext}"
                
            if filename:
                output_path = os.path.join(output_dir, filename)
                
                if os.path.exists(output_path):
                    if 'conflicts' in config['blocks_ignored']:
                        continue
                        
                    if not self.handle_file_conflict(output_path, code, config):
                        with open(output_path, 'w') as file:
                            file.write(code.strip())
                else:
                    with open(output_path, 'w') as file:
                        file.write(code.strip())
                        
                print(f"Extracted: {filename}")

class Markdown2DirCommand(sublime_plugin.TextCommand, CodeBlockManagerBase):
    """Sublime Text command to insert code from directory into markdown"""
    
    def run(self, edit):
        config = self.plugin_loaded()
        markdown_file = self.view.file_name()
        if markdown_file:
            directory = os.path.dirname(markdown_file)
            self.insert_code_blocks(markdown_file, directory, config)
        else:
            sublime.message_dialog("A directory cannot be determined from an unsaved file. First, save the file with the desired path and try again.")

    def insert_code_blocks(self, markdown_path, input_dir, config):
        """Insert code blocks into markdown file based on configuration"""
        with open(markdown_path, 'r') as md_file:
            content = md_file.read()
            
        lines = content.split('\n')
        
        def replace_code_block(match):
            lang = match.group(1)
            code = match.group(2)
            
            start_pos = match.start()
            preceding_line = None
            
            text_before = content[:start_pos]
            line_number = text_before.count('\n')
            if line_number > 0:
                preceding_line = lines[line_number - 1]
                
            filename = self.get_filename_from_block(lang, code, preceding_line, config)
            
            if filename and not self.should_ignore_block(lang, code, filename, config):
                file_path = os.path.join(input_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        updated_code = file.read().strip()
                    if config['file_naming_convention'] == 'first_line_of_code':
                        return f"```{lang}\n{code.splitlines()[0]}\n{updated_code}\n```"
                    return f"```{lang}\n{updated_code}\n```"
                else:
                    print(f"Warning: {filename} not found in {input_dir}.")
                    
            return match.group(0)
            
        updated_content = re.sub(r'```(\S+)?\n([\s\S]*?)```', replace_code_block, content)
        
        with open(markdown_path, 'w') as md_file:
            md_file.write(updated_content)
            
        print("Markdown file updated.")

def plugin_loaded():
    """Called by Sublime Text when the plugin is loaded"""
    return CodeBlockManagerBase.plugin_loaded()