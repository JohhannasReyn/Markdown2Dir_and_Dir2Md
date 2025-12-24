# Visual Guide: Nested Code Fence Indentation

## The Core Concept

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKDOWN DOCUMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ```myfile.txt                    ← TOP-LEVEL FENCE         │
│  Regular content                    (0 spaces indent)       │
│                                     EXTRACTED AS FILE       │
│      ```nested_example            ← NESTED FENCE            │
│      This is an example             (4+ spaces indent)      │
│      ```                            KEPT IN FILE            │
│                                                             │
│  More content                                               │
│  ```                                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## How It Works: Two Directions

### Direction 1: Markdown → Directory

```
INPUT: Markdown File
┌──────────────────────┐
│ ```file.md           │
│ Content:             │
│     ```example       │
│     code here        │
│     ```              │
│ ```                  │
└──────────────────────┘
         │
         │ (EXTRACT)
         │ • Detects top-level fence (0 indent)
         │ • Finds nested fence (4 spaces)
         │ • Reduces indent by 4 spaces
         ↓
OUTPUT: File Created
┌──────────────────────┐
│ file.md              │
│ ─────────────────    │
│ Content:             │
│ ```example           │← Indent reduced!
│ code here            │
│ ```                  │
└──────────────────────┘
```

### Direction 2: Directory → Markdown

```
INPUT: File on Disk
┌──────────────────────┐
│ file.md              │
│ ─────────────────    │
│ Content:             │
│ ```example           │
│ code here            │
│ ```                  │
└──────────────────────┘
         │
         │ (READ & FORMAT)
         │ • Detects code fence in content
         │ • Adds 4-space indentation
         │ • Wraps in top-level fence
         ↓
OUTPUT: Markdown
┌──────────────────────┐
│ ```file.md           │
│ Content:             │
│     ```example       │← Indent added!
│     code here        │
│     ```              │
│ ```                  │
└──────────────────────┘
```

## Indentation Levels

```
LEVEL 0 (No indent) = Extracted as File
└─ ```myfile.txt
   Content here
   ```

LEVEL 1 (4 spaces) = Kept in file, reduced by 4
└─ ```myfile.txt
       ```nested
       content
       ```
   ```
   
   Creates: myfile.txt with:
   ```nested
   content
   ```

LEVEL 2 (8 spaces) = Kept in file, reduced by 4
└─ ```myfile.txt
           ```double_nested
           content
           ```
   ```
   
   Creates: myfile.txt with:
       ```double_nested
       content
       ```
```

## The Indentation Rules

```
╔══════════════════════════════════════════════════════════╗
║              INDENTATION DECISION TREE                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Is code fence at column 0?                              ║
║  (No leading spaces/tabs)                                ║
║         │                                                ║
║         ├─ YES → Extract as file                         ║
║         │        Process nested fences inside            ║
║         │                                                ║
║         └─ NO  → Keep as content                         ║
║                  (Part of parent file)                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

## Example: Multiple Nesting Levels

### Original Markdown

```
```documentation.md
# Documentation

    ```example_1.cpp
    int main() {
        return 0;
    }
    ```

    ```example_2.py
        ```output.txt
        Expected output here
        ```
    ```
```
```

### After Markdown → Directory

Creates ONE file: `documentation.md`

```
# Documentation

```example_1.cpp        ← Reduced by 4 spaces
int main() {
    return 0;
}
```

```example_2.py         ← Reduced by 4 spaces
    ```output.txt       ← Reduced by 4 spaces (was 8, now 4)
    Expected output here
    ```
```
```

### After Directory → Markdown (Round Trip)

```
```documentation.md
# Documentation

    ```example_1.cpp    ← Added 4 spaces
    int main() {
        return 0;
    }
    ```

    ```example_2.py     ← Added 4 spaces
        ```output.txt   ← Maintains 4-space difference
        Expected output here
        ```
    ```
```
```

## Comparison: Before vs After Update

### BEFORE (Old Behavior)

```
Markdown:                    Result:
┌────────────────┐          ┌────────────────┐
│ ```file1.txt   │          │ file1.txt      │
│     ```nested  │    →     │ (content A)    │
│     content A  │          ├────────────────┤
│     ```        │          │ nested         │
│ ```            │          │ (content A)    │← PROBLEM!
└────────────────┘          └────────────────┘
                            Two files created!
```

### AFTER (New Behavior)

```
Markdown:                    Result:
┌────────────────┐          ┌────────────────┐
│ ```file1.txt   │          │ file1.txt      │
│     ```nested  │    →     │ ```nested      │
│     content A  │          │ content A      │
│     ```        │          │ ```            │
│ ```            │          └────────────────┘
└────────────────┘          One file, nested 
                            fence preserved!
```

## Edge Cases Handled

### Case 1: Mixed Content

```
INPUT:
```file.md
Regular text

    ```code_example
    print("hello")
    ```

More text

    ```another_example
    code here
    ```
```

OUTPUT: Single file with both examples indented correctly
```

### Case 2: Deep Nesting

```
INPUT:
```file.md
            ```level_3
            content
            ```
```

OUTPUT: File with nested fence at correct level
```file.md contains:
        ```level_3
        content
        ```
```

### Case 3: No Nesting

```
INPUT:
```file.txt
Just plain content
No code fences here
```

OUTPUT: Works exactly as before (backward compatible)
```

## Benefits Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    BEFORE UPDATE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [X] Code examples become separate files                    │
│  [X] Manual indentation management needed                   │
│  [X] Documentation files break into pieces                  │
│  [X] Round-trip loses structure                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

                            ↓
                    (AFTER UPDATE)
                            ↓

┌─────────────────────────────────────────────────────────────┐
│                     AFTER UPDATE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [D] Code examples stay in parent files                     │
│  [D] Automatic indentation handling                         │
│  [D] Documentation files stay intact                        │
│  [D] Perfect round-trip preservation                        │
│  [D] Backward compatible (old files still work)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Reference

### Indentation Cheat Sheet

| Indent Level| Spaces | Action (MD→Dir) | Action (Dir→MD) |
|-------------|--------|-----------------|-----------------|
| 0           | 0      | Extract as file | Wrap in fence   |
| 1           | 4      | Keep, reduce 4  | Add 4 spaces    |
| 2           | 8      | Keep, reduce 4  | Add 4 spaces    |
| 3           | 12     | Keep, reduce 4  | Add 4 spaces    |
| N           | N×4    | Keep, reduce 4  | Add 4 spaces    |

### Key Functions

```
code_block_processor.py:
├─ get_indentation_level()    → Measures indent in spaces
├─ reduce_indentation()        → Removes N spaces from lines
└─ process_nested_fences()     → Recursively handles nesting

markdown_processor.py:
└─ indent_nested_fences()      → Adds 4 spaces to nested fences
```

## Testing Workflow

```
1. Create Test Markdown
   └─ Include nested code fences

2. Run: Markdown → Directory
   └─ Verify only top-level extracted
   └─ Check nested fences in files

3. Modify Files (optional)
   └─ Add/edit content

4. Run: Directory → Markdown  
   └─ Verify structure preserved
   └─ Check indentation correct

5. Compare Original vs Final
   └─ Should be identical (except whitespace normalization)
```

## Summary

```
╔═══════════════════════════════════════════════════════════╗
║         NESTED CODE FENCE INDENTATION SYSTEM              ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  [C] Goal: Differentiate files from code examples         ║
║  [C] Method: Indentation-based detection                  ║
║  [C] Direction: Bidirectional (MD ↔ Dir)                  ║
║  [C] Unit: 4 spaces per nesting level                     ║
║  [C]  Compatibility: Fully backward compatible            ║
║                                                           ║
║  Result: Seamless handling of nested code fences!         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```
