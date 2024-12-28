Markdown2Dir
============

This package adds a feature to Sublime Text that makes it easier to manage Markdown files containing code blocks by allowing seamless extraction and reinsertion of those blocks to and from the file's parent directory.

It's home is here on [GitHub](https://github.com/JohhannasReyn/Markdown2Dir/).

Features
--------
  - **Directory to Markdown**: Extract code blocks from a Markdown file and save them as separate files in the same directory.
  - **Markdown to Directory**: Update the Markdown file with code from corresponding files in the directory.
  - Configurable file naming conventions.
  - Options to ignore specific blocks or handle file conflicts gracefully.

Installation Options
--------------------
  - From within Sublime Text's Package Control: Install Package, search for Markdown2Dir, select and hit enter.
  - Alternatively, download this repository, save it with the extension ".sublime-package" (i.e., "Markdown2Dir.sublime-package") in your "Sublime Text/Installed Packages" directory. On Windows, this is usually "C://Users/<UserName>/AppData/Roaming/Sublime Text/Installed Packages/".

    If Sublime Text is already open and you don't see it listed under:
    *Preferences -> Package Settings*, then you'll need to restart Sublime Text.

Usage Options
-------------
  - Open a Markdown file (.md, .markdown).
  - Via the Context Menu: Right-click on the document or selected text and select *Directory to Markdown* or *Markdown to Directory*.
  - Via the Menu Bar: *Tools -> Markdown2Dir -> Directory to Markdown* or *Markdown to Directory*.
  - Via Key Bindings (if enabled): Use the defined key-mapping specified in the sublime-keymap file. Suggested mappings:
    - `Ctrl+Alt+M` for *Directory to Markdown*.
    - `Alt+Shift+M` for *Markdown to Directory*.

Configuration
-------------
  - Options can be configured in Markdown2Dir.sublime-settings. Access via: *Preferences -> Package Settings -> Markdown2Dir*.
  - For more information about the plugin's options, see the settings file or the documentation in the GitHub repository.

License & Contributing
----------------------
 - [MIT license](LICENSE)

