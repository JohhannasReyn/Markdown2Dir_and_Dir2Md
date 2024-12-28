The Features

## **Features Breakdown**

### **1. Core Functionality**
- **Extracting Code Blocks to Files**:
  - Parse a markdown file to find code blocks.
  - Use a configurable naming convention to determine file names.
  - Create or update files based on the extracted code.
  - Ask for user confirmation if files already exist before overwriting.

- **Reversing the Process**:
  - Read files in the same directory as the markdown file.
  - Match files to code blocks using the same naming convention.
  - Insert the file contents back into the appropriate code blocks.

---

### **2. Configurable File Naming Conventions**
Here are a few potential approaches for determining file names from code blocks:
1. **Standard Markdown Header**: Use the text directly following the opening code block delimiter, e.g., ```` ```filename.cpp ````.
   - Pros: Explicit and unambiguous.
   - Example:
     ```markdown
     ```example.py
     print("Hello, World!")
     ```
     ```

2. **Preceding Comment Line**: Use a commented line at the start of the code block, e.g., `# filename.py` or `// filename.cpp`.
   - Pros: Keeps the filename close to the code.
   - Example:
     ```markdown
     ```
     // filename.cpp
     int main() { return 0; }
     ```
     ```

3. **Preceding Markdown Text**: Use the first non-empty line before the code block.
   - Pros: Integrates well with markdown documentation styles.
   - Example:
     ```markdown
     Example Code (example.py):
     ```
     print("Hello, World!")
     ```
     ```

4. **Fallback**: If none of the above conventions work, generate default names like `codeblock_1.py`.

### **Settings Example**
You could let users configure this via settings like:
```json
{
    "naming_convention": "header", // Options: "header", "comment", "preceding", "default"
    "ask_before_overwriting": true,
    "markdown_extension": ".md"
}
```

---

### **3. Reverse Mode**
Reverse mode could:
- Insert file contents into existing or new code blocks, matching files based on the selected naming convention.
- Add comments or tags in the markdown to denote which file each block corresponds to.

---

## **Technical Feasibility**

- **Parsing Markdown**:
  - Use Python's `markdown` library or a similar parser to identify code blocks.
  - Regular expressions could also handle simpler scenarios.

- **File System Integration**:
  - Python’s built-in `os` and `pathlib` modules are sufficient for managing files and directories.

- **User Prompts**:
  - Integrate confirmation dialogs (e.g., Sublime Text's `show_quick_panel` or similar).

---
---
### Key features to implement. ###
 - Exlude by extension. (i.e. Ignore code blocks with the type `bash`, or `lua`)
 - Ignore code blocks that are less than 4 lines.
 - Check for comments for snippet placement inside of existing files to insert the code in the correct location.
 - If a file already exists before replacing the text within the file, move the file to the recycle bin, then replace it with the new version, this will act as a safety-net/version control in case either the user or the plugin makes a mistake, the originals are preserved. 
     - Additional options could be:
      to rename existing files appending a version id on the end of the name, or moving conflicting files to another folder either nested in the current project folder, or in a user's specified path.