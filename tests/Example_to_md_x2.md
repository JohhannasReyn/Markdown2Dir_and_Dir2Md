# Generated Markdown File

# Directory Structure

```
tests
├── project
│   └── sub_dir
│       ├── README.md
│       ├── onfence_file.hpp
│       └── postfence_file.cpp
├── Example.md
└── Example_to_md.md
```

# Directory Settings

```tests.sublime-settings
{
    "blocks_ignored": [], 
    "files_2_include": [], 
    "include_system_folders": false, 
    "handle_file_conflicts": "prepend_and_comment", 
    "directories_2_ignore": [], 
    "partial_names_2_ignore": [], 
    "extensions_2_ignore": [], 
    "attempt_injection": false, 
    "directories_2_include": [], 
    "enable_debug_output": true, 
    "partial_names_2_include": [], 
    "files_2_ignore": [], 
    "include_nested_directories": true, 
    "file_naming_convention": "on_fence", 
    "output_directory_tree": true, 
    "extensions_2_include": []
}
```

# File Contents

```Example.md
# Test Markdown File

project/sub_dir/prefence_file.cpp
    ```cpp
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

    ```cpp
    // project/sub_dir/postfence_file.cpp
    // This is a test C++ file using after_fence convention
    void test_function() {
        // Implementation
    }
    ```

project/sub_dir/README.md
    ```project/sub_dir/README.md
    // project/sub_dir/README.md
    
    All three file/path conventions are used in this test which is designed to test the parsers
    handling of nested code blocks. 
    
        ```nested_code_fence/example.md

    # This is an example of a nested code fence, and what it should look like when encountered inside of a file.

    **When building a markdown file from directory**

    - the parser will indent the code fence in the generated markdown.

    **When building out a directory and files from a markdown file** 
    
    - Codefences that are discovered inside the file will be indented by one tab, maintaining any indentation
      they may or may not have already.
    
            ```indented_nested_codefence/example.md
            this indented codefence would be indented only one tab when this markdown is built out into a directory.
            if this markdown file is inside of a file that is built into another markdown file, the indentation
            would be prepended to, making it three tabs at the beginning of each line herein. 
            ```
    
    - that is to say, an extra indentation will always preceed nested codefences, so that when being built out, 
      any encounted code fence will be reduced by one indentation inside the generated file.
    
    - by maintaining this adding/removing of indentation, markdown files containing directory/file content 
      structures can be nested inside other markdown files, repeatedly, much like russian dolls. This recursive
      structuring can be very useful when working with large codebases, or nested projects within parent projects.
    
        ```
    
    ```
```

```Example_to_md.md
# Generated Markdown File

# Directory Structure

    ```
    tests
    ├── project
    │   └── sub_dir
    │       ├── README.md
    │       ├── onfence_file.hpp
    │       └── postfence_file.cpp
    └── Example.md
    ```

# Directory Settings

    ```tests.sublime-settings
    {
        "blocks_ignored": [], 
        "files_2_include": [], 
        "include_system_folders": false, 
        "handle_file_conflicts": "prepend_and_comment", 
        "directories_2_ignore": [], 
        "partial_names_2_ignore": [], 
        "extensions_2_ignore": [], 
        "attempt_injection": false, 
        "directories_2_include": [], 
        "enable_debug_output": true, 
        "partial_names_2_include": [], 
        "files_2_ignore": [], 
        "include_nested_directories": true, 
        "file_naming_convention": "on_fence", 
        "output_directory_tree": true, 
        "extensions_2_include": []
    }
    ```

# File Contents

    ```Example.md
    # Test Markdown File
    
    project/sub_dir/prefence_file.cpp
        ```cpp
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
    
        ```cpp
    // project/sub_dir/postfence_file.cpp
    // This is a test C++ file using after_fence convention
    void test_function() {
        // Implementation
    }
        ```
    
    project/sub_dir/README.md
        ```project/sub_dir/README.md
    // project/sub_dir/README.md
    
    All three file/path conventions are used in this test which is designed to test the parsers
    handling of nested code blocks. 
    
            ```nested_code_fence/example.md
    
        # This is an example of a nested code fence, and what it should look like when encountered inside of a file.
    
        **When building a markdown file from directory**
    
        - the parser will indent the code fence in the generated markdown.
    
        **When building out a directory and files from a markdown file** 
        
        - Codefences that are discovered inside the file will be indented by one tab, maintaining any indentation
          they may or may not have already.
        
                ```indented_nested_codefence/example.md
            this indented codefence would be indented only one tab when this markdown is built out into a directory.
            if this markdown file is inside of a file that is built into another markdown file, the indentation
            would be prepended to, making it three tabs at the beginning of each line herein. 
                ```
        
        - that is to say, an extra indentation will always preceed nested codefences, so that when being built out, 
          any encounted code fence will be reduced by one indentation inside the generated file.
        
        - by maintaining this adding/removing of indentation, markdown files containing directory/file content 
          structures can be nested inside other markdown files, repeatedly, much like russian dolls. This recursive
          structuring can be very useful when working with large codebases, or nested projects within parent projects.
        
            ```
    
        ```
    ```

    ```project\sub_dir\README.md
    // project/sub_dir/README.md
    
    All three file/path conventions are used in this test which is designed to test the parsers
    handling of nested code blocks. 
    
        ```nested_code_fence/example.md
    
    # This is an example of a nested code fence, and what it should look like when encountered inside of a file.
    
    **When building a markdown file from directory**
    
    - the parser will indent the code fence in the generated markdown.
    
    **When building out a directory and files from a markdown file** 
    
    - Codefences that are discovered inside the file will be indented by one tab, maintaining any indentation
      they may or may not have already.
    
            ```indented_nested_codefence/example.md
            this indented codefence would be indented only one tab when this markdown is built out into a directory.
            if this markdown file is inside of a file that is built into another markdown file, the indentation
            would be prepended to, making it three tabs at the beginning of each line herein. 
            ```
    
    - that is to say, an extra indentation will always preceed nested codefences, so that when being built out, 
      any encounted code fence will be reduced by one indentation inside the generated file.
    
    - by maintaining this adding/removing of indentation, markdown files containing directory/file content 
      structures can be nested inside other markdown files, repeatedly, much like russian dolls. This recursive
      structuring can be very useful when working with large codebases, or nested projects within parent projects.
    
        ```
    ```

    ```project\sub_dir\onfence_file.hpp
    // This is a test C++ header using on_fence convention
    class TestClass {
    public:
        TestClass() {}
    };
    ```

    ```project\sub_dir\postfence_file.cpp
    // project/sub_dir/postfence_file.cpp
    // This is a test C++ file using after_fence convention
    void test_function() {
        // Implementation
    }
    ```
```

```project\sub_dir\README.md
// project/sub_dir/README.md

All three file/path conventions are used in this test which is designed to test the parsers
handling of nested code blocks. 

    ```nested_code_fence/example.md
    
    # This is an example of a nested code fence, and what it should look like when encountered inside of a file.
    
    **When building a markdown file from directory**
    
    - the parser will indent the code fence in the generated markdown.
    
    **When building out a directory and files from a markdown file** 
    
    - Codefences that are discovered inside the file will be indented by one tab, maintaining any indentation
      they may or may not have already.
    
        ```indented_nested_codefence/example.md
        this indented codefence would be indented only one tab when this markdown is built out into a directory.
        if this markdown file is inside of a file that is built into another markdown file, the indentation
        would be prepended to, making it three tabs at the beginning of each line herein. 
        ```
    
    - that is to say, an extra indentation will always preceed nested codefences, so that when being built out, 
      any encounted code fence will be reduced by one indentation inside the generated file.
    
    - by maintaining this adding/removing of indentation, markdown files containing directory/file content 
      structures can be nested inside other markdown files, repeatedly, much like russian dolls. This recursive
      structuring can be very useful when working with large codebases, or nested projects within parent projects.
    
    ```
```

```project\sub_dir\onfence_file.hpp
// This is a test C++ header using on_fence convention
class TestClass {
public:
    TestClass() {}
};
```

```project\sub_dir\postfence_file.cpp
// project/sub_dir/postfence_file.cpp
// This is a test C++ file using after_fence convention
void test_function() {
    // Implementation
}
```

