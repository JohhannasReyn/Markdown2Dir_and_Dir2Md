
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