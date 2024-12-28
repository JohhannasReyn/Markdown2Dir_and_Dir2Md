The Code

## **Phase One Implementation**

Let’s begin by focusing on the **basic prototype** for extracting and updating files. Here’s a simple plan for this phase:

### **Core Features**
1. **Markdown Parsing**:
   - Use Python to read markdown files and extract code blocks based on a naming convention.
   - Example: Parse blocks following ```` ```filename.ext ````.

2. **File Creation and Updates**:
   - Create or overwrite files based on extracted code blocks.
   - Ask for user confirmation if files already exist.

3. **Reverse Operation**:
   - Read files from a directory.
   - Insert file contents back into corresponding code blocks.

---

### **Example Script**
Here’s a skeleton for the script in Python:

```python
import os
import re

def extract_code_blocks(markdown_path, output_dir):
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()

    # Match code blocks with a header indicating the filename
    code_blocks = re.findall(r'```(\S+)\n(.*?)```', content, re.DOTALL)

    for filename, code in code_blocks:
        output_path = os.path.join(output_dir, filename)
        if os.path.exists(output_path):
            confirm = input(f"File {filename} exists. Overwrite? (y/n): ")
            if confirm.lower() != 'y':
                continue
        with open(output_path, 'w') as file:
            file.write(code.strip())
        print(f"Saved {filename}")

def insert_code_blocks(markdown_path, input_dir):
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()

    def replace_code_block(match):
        filename = match.group(1)
        file_path = os.path.join(input_dir, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {filename} not found.")
            return match.group(0)

        with open(file_path, 'r') as file:
            code = file.read().strip()
        return f"```{filename}\n{code}\n```"

    updated_content = re.sub(r'```(\S+)\n(.*?)```', replace_code_block, content, flags=re.DOTALL)
    with open(markdown_path, 'w') as md_file:
        md_file.write(updated_content)
    print("Markdown file updated.")

# Example usage
markdown_file = "example.md"
output_directory = "output"
extract_code_blocks(markdown_file, output_directory)
insert_code_blocks(markdown_file, output_directory)
```

---

## **Next Steps**
1. **Prototype Development**:
   - Implement the script above and test it with sample markdown files.
   - Fine-tune the parsing logic and user prompts.

2. **Plan for Phase Two**:
   - Add settings for naming conventions.
   - Begin Sublime Text plugin development.

3. **Monetization Research**:
   - Survey potential users (developers, teams).
   - Define tiers and features for the paid version.

---

### **Phase One: Prototype Development**

We’ll develop a **Python script** that:
1. Extracts code blocks from a markdown file and saves them as individual files in a directory.
2. Inserts code from those files back into the markdown file in the corresponding code blocks.

Here’s the plan:
1. **Directory Setup**: Ensure you have a markdown file (`example.md`) with multiple code blocks to test with.
2. **Script Setup**: Create and test the Python script to handle the extraction and insertion tasks.
3. **Test Cases**: Verify that the script correctly creates, updates, and inserts files.

---

### **Step 1: Setting Up the Markdown File**

Prepare a sample markdown file (`example.md`) with multiple code blocks, using the following example:

```markdown
# Example Markdown File

Some introductory text.

```python
# my_script.py
print("Hello, World!")
```

Here’s another code block:

```javascript
// app.js
console.log("Hello, JavaScript!");
```

This is a plain code block (no filename):

```
Just some random code.
```

One more with a filename:

```cpp
// main.cpp
#include <iostream>
int main() {
    std::cout << "Hello, C++!" << std::endl;
    return 0;
}
```
---

### **Step 2: Write the Python Script**

Here’s the script:

```python
import os
import re

def extract_code_blocks(markdown_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(markdown_path, 'r') as md_file:
        content = md_file.read()

    # Regex to find code blocks with filenames (after `//` or `#`)
    code_blocks = re.findall(r'```(\S+)?\n([\s\S]*?)```', content)
    for lang, code in code_blocks:
        first_line = code.splitlines()[0].strip() if code else ""
        match = re.match(r"[#/]{1,2}\s*(.+\.\w+)", first_line)
        filename = match.group(1) if match else None

        if filename:
            output_path = os.path.join(output_dir, filename)
            if os.path.exists(output_path):
                confirm = input(f"File {filename} exists. Overwrite? (y/n): ")
                if confirm.lower() != 'y':
                    continue
            with open(output_path, 'w') as file:
                file.write("\n".join(code.splitlines()[1:]).strip())  # Skip first line
            print(f"Extracted: {filename}")

def insert_code_blocks(markdown_path, input_dir):
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()

    def replace_code_block(match):
        lang = match.group(1)
        code = match.group(2)
        first_line = code.splitlines()[0].strip() if code else ""
        match_filename = re.match(r"[#/]{1,2}\s*(.+\.\w+)", first_line)
        filename = match_filename.group(1) if match_filename else None

        if filename:
            file_path = os.path.join(input_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    updated_code = file.read().strip()
                return f"```{lang}\n{first_line}\n{updated_code}\n```"
            else:
                print(f"Warning: {filename} not found in {input_dir}.")
        return match.group(0)

    updated_content = re.sub(r'```(\S+)?\n([\s\S]*?)```', replace_code_block, content)
    with open(markdown_path, 'w') as md_file:
        md_file.write(updated_content)
    print("Markdown file updated.")

# Example Usage
markdown_file = "example.md"
output_directory = "extracted_files"

# Extract code blocks to files
print("Extracting code blocks...")
extract_code_blocks(markdown_file, output_directory)

# Insert file contents back into code blocks
print("\nInserting code blocks...")
insert_code_blocks(markdown_file, output_directory)
```

---

### **Step 3: Testing the Script**

#### **Steps to Test Extraction**
1. Create `example.md` with the content above.
2. Run the script: `python script.py`.
3. Check the `extracted_files` directory:
   - Verify that files like `my_script.py`, `app.js`, and `main.cpp` are created with the correct contents.

#### **Steps to Test Insertion**
1. Modify one of the extracted files, e.g., `my_script.py`:
   ```python
   print("Hello from the modified script!")
   ```
2. Run the script again, selecting the **Insert Code Blocks** step.
3. Check that the content of `example.md` reflects the updated content from `my_script.py`.

---

### **Step 4: Next Steps**
1. **Fine-Tuning**:
   - Test edge cases like missing filenames or existing files.
   - Add more descriptive messages for user prompts.
2. **Feedback**:
   - Test this prototype with different markdown files and report any issues.
3. **Phase Two**:
   - Convert this into a Sublime Text plugin.


## ---------------------------------------------------------------------------
## ===========================================================================
## ---------------------------------------------------------------------------


## COMPARISON OF SCRIPTS A & B

### Script A
```python
import os
import re
def extract_code_blocks(markdown_path, output_dir):
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()
    # Match code blocks with a header indicating the filename
    code_blocks = re.findall(r'(\S+)\n(.*?)', content, re.DOTALL)
    for filename, code in code_blocks:
        output_path = os.path.join(output_dir, filename)
        if os.path.exists(output_path):
            confirm = input(f"File {filename} exists. Overwrite? (y/n): ")
            if confirm.lower() != 'y':
                continue
        with open(output_path, 'w') as file:
            file.write(code.strip())
        print(f"Saved {filename}")
def insert_code_blocks(markdown_path, input_dir):
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()
    def replace_code_block(match):
        filename = match.group(1)
        file_path = os.path.join(input_dir, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {filename} not found.")
            return match.group(0)
        with open(file_path, 'r') as file:
            code = file.read().strip()
        return f"{filename}\n{code}\n"
    updated_content = re.sub(r'(\S+)\n(.*?)', replace_code_block, content, flags=re.DOTALL)
    with open(markdown_path, 'w') as md_file:
        md_file.write(updated_content)
    print("Markdown file updated.")
# Example usage
markdown_file = "example.md"
output_directory = "output"
extract_code_blocks(markdown_file, output_directory)
insert_code_blocks(markdown_file, output_directory)
```

### Script B

```python
import os
import re
def extract_code_blocks(markdown_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()
    # Regex to find code blocks with filenames (after `//` or `#`)
    code_blocks = re.findall(r'```(\S+)?\n([\s\S]*?)```', content)
    for lang, code in code_blocks:
        first_line = code.splitlines()[0].strip() if code else ""
        match = re.match(r"[#/]{1,2}\s*(.+\.\w+)", first_line)
        filename = match.group(1) if match else None
        if filename:
            output_path = os.path.join(output_dir, filename)
            if os.path.exists(output_path):
                confirm = input(f"File {filename} exists. Overwrite? (y/n): ")
                if confirm.lower() != 'y':
                    continue
            with open(output_path, 'w') as file:
                file.write("\n".join(code.splitlines()[1:]).strip())  # Skip first line
            print(f"Extracted: {filename}")
def insert_code_blocks(markdown_path, input_dir):
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()
    def replace_code_block(match):
        lang = match.group(1)
        code = match.group(2)
        first_line = code.splitlines()[0].strip() if code else ""
        match_filename = re.match(r"[#/]{1,2}\s*(.+\.\w+)", first_line)
        filename = match_filename.group(1) if match_filename else None
        if filename:
            file_path = os.path.join(input_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    updated_code = file.read().strip()
                return f"```{lang}\n{first_line}\n{updated_code}\n```"
            else:
                print(f"Warning: {filename} not found in {input_dir}.")
        return match.group(0)
    updated_content = re.sub(r'```(\S+)?\n([\s\S]*?)```', replace_code_block, content)
    with open(markdown_path, 'w') as md_file:
        md_file.write(updated_content)
    print("Markdown file updated.")
# Example Usage
markdown_file = "example.md"
output_directory = "extracted_files"
# Extract code blocks to files
print("Extracting code blocks...")
extract_code_blocks(markdown_file, output_directory)
# Insert file contents back into code blocks
print("\nInserting code blocks...")
insert_code_blocks(markdown_file, output_directory)

```

# Script Comparison: Code Block Extraction and Insertion Tools

## Core Functionality
Both scripts handle the extraction and insertion of code blocks from/to markdown files, but with different approaches and capabilities.

## Key Differences

### 1. Code Block Detection
- Script A:
  - Uses `r'```(\S+)\n(.*?)```'` pattern
  - Expects filename directly after backticks
  - More rigid format requirements
  - Cannot handle empty language specifications

- Script B:
  - Uses `r'```(\S+)?\n([\s\S]*?)```'` pattern
  - Makes language specification optional with `?`
  - Handles filename from comments (`#` or `//`)
  - More flexible format support

### 2. Directory Handling
- Script A:
  - Assumes output directory exists
  - No directory creation functionality
  - Could fail if directory missing

- Script B:
  - Checks if output directory exists
  - Creates directory if missing
  - More robust for general use

### 3. Filename Extraction
- Script A:
  - Filename must be specified in code fence
  - Example: ````python.txt`
  - Less flexible naming convention
  - Requires changing markdown structure

- Script B:
  - Extracts filename from first line comments
  - Supports both `#` and `//` comment styles
  - Example: `# filename.py` or `// script.js`
  - Works with existing documentation conventions

### 4. Code Content Handling
- Script A:
  - Writes entire code block
  - Includes potential filename line
  - No special first-line handling

- Script B:
  - Skips first line (filename comment)
  - Cleaner output files
  - Preserves original code structure

### 5. Error Handling
- Script A:
  - Basic error handling
  - Could fail on malformed inputs

- Script B:
  - More robust error checking
  - Better handling of edge cases
  - Maintains original content if file not found

## Example Usage Formats

Script A expects:
```python
```python.txt
print("Hello")
```

Script B expects:
```python
# example.py
print("Hello")
```

## Recommendation
Script B is generally preferred because:
1. More flexible file naming through comments
2. Better directory handling
3. More robust error handling
4. Follows common documentation practices
5. Cleaner separation of metadata and code
6. Better compatibility with existing markdown files

The main tradeoff is that Script B is slightly more complex, but this complexity serves to make it more robust and user-friendly.

## Use Case Considerations
Choose Script A if:
- You need a simpler implementation
- You control the markdown format completely
- File naming in code fences is preferred

Choose Script B if:
- Working with various documentation styles
- Need more robust error handling
- Want to follow common commenting conventions
- Working with existing documentation


## ---------------------------------------------------------------------------
## ===========================================================================
## ---------------------------------------------------------------------------


### Using both scripts to generate a more complete implementation.
```python
import os
import re
import sublime
import json

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

def get_filename_from_block(lang, code, preceding_line, config):
    """Extract filename based on configured naming convention"""
    convention = config['file_naming_convention']
    
    if convention == 'following_first_code_fence':
        return lang if '.' in lang else None
        
    elif convention == 'line_preceding_code_fence':
        if preceding_line and preceding_line.strip():
            # Look for a filename pattern in the preceding line
            filename_match = re.search(r'[\w.-]+\.\w+', preceding_line)
            return filename_match.group(0) if filename_match else None
        return None
        
    elif convention == 'first_line_of_code':
        first_line = code.splitlines()[0].strip() if code else ""
        match = re.match(r"[#/]{1,2}\s*(.+\.\w+)", first_line)
        return match.group(1) if match else None
    
    return None

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

def handle_file_conflict(output_path, code, config):
    """Handle file conflicts based on settings"""
    conflict_handling = config['handle_file_conflicts']
    
    if conflict_handling == 'prepend_and_comment':
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                existing_code = f.read()
            
            # Determine comment style based on file extension
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

def extract_code_blocks(markdown_path, output_dir, config):
    """Extract code blocks from markdown file based on configuration"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()

    # Split content into lines for context
    lines = content.split('\n')
    
    # Modified regex to capture line numbers
    code_block_pattern = r'```(\S+)?\n([\s\S]*?)```'
    matches = list(re.finditer(code_block_pattern, content))
    
    for match in matches:
        lang = match.group(1)
        code = match.group(2)
        
        # Find the line number where this code block starts
        start_pos = match.start()
        preceding_line = None
        
        # Get text before the code block and count newlines to find preceding line
        text_before = content[:start_pos]
        line_number = text_before.count('\n')
        if line_number > 0:
            preceding_line = lines[line_number - 1]
        
        filename = get_filename_from_block(lang, code, preceding_line, config)
        
        if should_ignore_block(lang, code, filename, config):
            continue
            
        if not filename and 'nameless' not in config['blocks_ignored']:
            # Generate name for nameless block if not ignored
            n = 1
            ext = lang if lang else 'o'
            while os.path.exists(os.path.join(output_dir, f"{n}.{ext}")):
                n += 1
            filename = f"{n}.{ext}"
            
        if filename:
            output_path = os.path.join(output_dir, filename)
            
            if os.path.exists(output_path):
                if 'conflicts' in config['blocks_ignored']:
                    continue
                    
                if config['attempt_injection']:
                    # Implement injection logic here
                    pass
                    
                if not handle_file_conflict(output_path, code, config):
                    with open(output_path, 'w') as file:
                        file.write(code.strip())
            else:
                with open(output_path, 'w') as file:
                    file.write(code.strip())
                    
            print(f"Extracted: {filename}")

def insert_code_blocks(markdown_path, input_dir, config):
    """Insert code blocks into markdown file based on configuration"""
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()
        
    lines = content.split('\n')
    
    def replace_code_block(match):
        lang = match.group(1)
        code = match.group(2)
        
        # Find the line number where this code block starts
        start_pos = match.start()
        preceding_line = None
        
        # Get text before the code block and count newlines to find preceding line
        text_before = content[:start_pos]
        line_number = text_before.count('\n')
        if line_number > 0:
            preceding_line = lines[line_number - 1]
            
        filename = get_filename_from_block(lang, code, preceding_line, config)
        
        if filename and not should_ignore_block(lang, code, filename, config):
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

# Example Usage
if __name__ == '__main__':
    config = plugin_loaded()  # Load settings
    markdown_file = "example.md"
    output_directory = "extracted_files"
    
    print("Extracting code blocks...")
    extract_code_blocks(markdown_file, output_directory, config)
    
    print("\nInserting code blocks...")
    insert_code_blocks(markdown_file, output_directory, config)
``` 
    the code above makes use of the settings file titled 'ABicycleMakingClown.sublime-settings' which is specified below:

```json
{
    // PLEASE NOTE: It is best to set these values before beginning on a project, as generating the
    // markdown will follow the same rules as building the directory from the markdown, if you are
    // not familiar with the way in which the markdown is formatted from the files found, I advised
    // you to begin first by constructing a markdown file from an existing directoy to familirize 
    // yourself with the format used, then if you are building a directory from a markdown file you
    // would be able to follow the same format used in the markdown file generated.

    // ALSO: The markdown file will need to be saved to the same directory as the project files that 
    // are to be either generated or read, if you are building the markdown from existing files you
    // will first need to save an empty markdown file (i.e. <your_project_name>.md) in the target
    // directory, then open the empty .md file in Sublime Text and select:
    // "Make Me A Markdown, Clown!"
    // if you are building a directory from markdown, the option to select will be: 
    // "Build My Directory, Clown!"

    "file_naming_convention": "following_first_code_fence", // Options are:
    // "following_first_code_fence" - i.e. ```filename.h
    // "line_preceding_code_fence" - looks to the line directly above the code fence for a filename
    //      (i.e. filename.h\n```cpp, where '\n' is a newline) 
    // "first_line_of_code" - looks inside code block at first line for a comment containing only
    //      the filename i.e. "// filename.h"

    "blocks_ignored": ["ext_bash","ext_lua","lessthan_3","nameless"], // Add or remove any values
    //      needed, following the format:
    // "ext_<ext>" - followed by the extension type to be ignored (e.g. "ext_bash" or "ext_lua")
    // "lessthan_<N>" - followed by the size of a code block to ignore less than the specified
    //      number of lines (default is 3 - meaning blocks of 1 or 2 lines are ignored)
    //      Note: setting this value to zero is the same as removing it.
    // Other options are:
    //      "nameless" - ignores blocks without a name,
    //      "none" - uses all blocks regardless of other factors, 
    //              (Please note: nameless files will be named <N>.<ext>, where N is the first non-
    //              conflicting integer found with the specified extension from the code fence, or
    //              '.o' if unspecified)
    //      "conflicts" - ignores files that already exist,
    //      "new", ignores blocks of code found that do not correspond to an existing file

    "attempt_injection": true, // Note: ignored if "blocks_ignored" uses "conflicts". Options are:
    // true - conflicts will be treated first as being injectable, if a location is undetermined
    //      then the setting "handle_file_conflicts" goes into effect.  injection is attempted using
    //      the first line of uncommented code found that matches a line in the existing file, and
    //      the last line of the code block to determine where to insert or replace the existing
    //      code. If the section found is to be replaced, it is commented out, not destroyed, and
    //      the snippet to be inserted is prepended to the commented section.
    // false - then all conflicts will be handled according to "handle_file_conflicts"

    "handle_file_conflicts": "prepend_and_comment"  // Note: ignored if "blocks_ignored" uses
    // "conflicts". Options are:
    // "prepend_and_comment" - places the code block at the beginning of the file and comments out
    //      everything else using '//', '#', or ';' according to filetype. 
    // "append_n_to_filename" - adds (n) to the end of the conflicting filename before creating the
    //      file,
    // "append_oN_to_ext" - adds ".oN" after the extension type where N is the next number to not
    //      exist in the working directory,
    // "move_to_backup_dir" - moves the file to a nested directory inside the working directory also
    //      adds (N) to the end of the filename if it exists in the backup dir,
}
```