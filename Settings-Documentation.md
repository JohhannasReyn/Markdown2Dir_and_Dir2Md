### Markdown2Dir Plugin Settings Documentation

This document explains the settings for configuring the `Markdown2Dir` plugin. Use these settings to control how markdown files are generated from directories and vice versa.

---

### General Notes
1. **Save the markdown file** in the same directory as your project files.
2. Use the following commands in Sublime Text:
   - **"Build Directory from Markdown"**: Generate files from a markdown file.
   - **"Build Markdown from Directory"**: Generate markdown from existing files.

---

### Settings

#### **`file_naming_convention`**
**Options**: `"on_fence"`, `"before_fence"`, `"after_fence"`

Defines how filenames are represented in markdown code fences.

- **`before_fence`**: Filename is placed above the code block.
```markdown
    path/to/file.cpp
    ```cpp
    // Code content
    ```


- **`on_fence`**: Filename is included directly within the code fence.
```markdown
    ```path/to/file.cpp
    // Code content
    ```

- **`after_fence`**: Filename is the first comment inside the code block.
```markdown
    ```cpp
    // path/to/file.cpp
    // Code content
    ```

#### **`blocks_ignored`**
**Options**: `["conflicts", "non-conflicts", "readme", "properties", "lessthan_<N>", "nameless", "without_ext", "none"]`

Controls which blocks of code to ignore during processing.

- **`conflicts`**: Ignores blocks w/ existing files and files w/ matching blocks.
- **`non-conflicts`**: Ignores blocks w/o matching files and files w/o matching blocks.
- **`readme`**: Ignore blocks containing "readme" or "README".
- **`properties`**: Ignore blocks containing "properties" or "PROPERTIES".
- **`lessthan_<N>`**: Ignore blocks smaller than `N` lines. Default is `3`.
- **`nameless`**: Ignore blocks w/o a specified filename.
- **`without_ext`**: Ignore files w/o extensions.
- **`none`**: Include all blocks, regardless of other settings.

---

#### **`extensions_2_include`**
**Example**: `["cpp", "py", "txt"]`

Include only files with specific extensions. Values should exclude the `.` (e.g., use `"cpp"`, not `".cpp"`).

---

#### **`extensions_2_ignore`**
**Example**: `["log", "tmp"]`

Ignore files with specific extensions.

---

#### **`directories_2_include`**
**Example**: `["src", "include"]`

Include specific directories for markdown generation or building files.

---

#### **`directories_2_ignore`**
**Example**: `["build", "temp"]`

Ignore specific directories.

---

#### **`include_nested_directories`**
**Options**: `true`, `false`

If `true`, includes/excludes nested directories based on the parent directory rules.

---

#### **`files_2_include`**
**Example**: `["main.cpp", "config.json"]`

Include specific files (case-sensitive) for markdown generation or directory creation.

---

#### **`files_2_ignore`**
**Example**: `["debug.log", "README.md"]`

Ignore specific files (case-sensitive) during processing.

---

#### **`partial_names_2_include`**
**Example**: `["config", "settings"]`

Include files whose names contain specified keywords (case-insensitive).

---

#### **`partial_names_2_ignore`**
**Example**: `["debug", "temp"]`

Ignore files whose names contain specified keywords (case-insensitive).

---

#### **`attempt_injection`**
**Options**: `true`, `false`

**Experimental**: Determines how to handle conflicting files during processing.

- **`true`**: Attempts to inject code blocks into existing files. Existing content is commented out as a fallback.
- **`false`**: Handles conflicts based on `handle_file_conflicts`.

---

#### **`handle_file_conflicts`**
**Options**: `"prepend_and_comment"`, `"append_n_to_filename"`, `"append_oN_to_ext"`, `"move_to_backup_dir"`

Defines how to handle conflicting files:

1. **`prepend_and_comment`**: Adds the code block at the start of the file and comments out existing content.
    ```cpp
    // Original content
    ```
    ```cpp
    // Code block from markdown
    ```

2. **`append_n_to_filename`**: Appends a number to the filename.
    - Example: `file_1.cpp`, `file_2.cpp`

3. **`append_oN_to_ext`**: Appends `.oN` to the file extension.
    - Example: `file.o1.cpp`, `file.o2.cpp`

4. **`move_to_backup_dir`**: Moves the conflicting file to a `backup` directory and appends a number if needed.

---

### Additional Notes

- **Inclusion/Exclusion Conflicts**: All filters are applied constructively, meaning you can apply rules for each filter and they will all be applied together for generating a markdown file, or for generating a directory from markdown. Any files or directories that have conflicting filters will be included.

- **Use Experimental Features with Caution**: Settings like `attempt_injection` may have unexpected results. Always back up your data.

- **Customize for Your Workflow**: Adjust the settings to suit the structure and needs of your project.