# Markdown2Dir

This package adds a feature to Sublime Text that makes it easier to manage Markdown files containing code blocks by allowing seamless extraction and reinsertion of those blocks to and from the file's parent directory.

It's home is here on [GitHub](https://github.com/JohhannasReyn/Markdown2Dir/).

## Features

- **Directory to Markdown**: Extract code blocks from a Markdown file and save them as separate files in the same directory.
- **Markdown to Directory**: Update the Markdown file with code from corresponding files in the directory.
- Configurable file naming conventions.
- Options to ignore specific blocks or handle file conflicts gracefully.

## Installation Options

- From within Sublime Text's Package Control: Install Package, search for Markdown2Dir, select and hit enter.
- Alternatively, download this repository, save it with the extension ".sublime-package" (i.e., "Markdown2Dir.sublime-package") in your "Sublime Text/Installed Packages" directory. On Windows, this is usually "C://Users/<UserName>/AppData/Roaming/Sublime Text/Installed Packages/".
  If Sublime Text is already open and you don't see it listed under:
  *Preferences -> Package Settings*, then you'll need to restart Sublime Text.

## Usage Options

- Adjust the plugin settings first! (Refer to the settings file, or doc, for details)
- Open a Markdown file (.md, .markdown).
- Via the Context Menu: Right-click on the document or selected text and select *Directory to Markdown* or *Markdown to Directory*.
- Via the Menu Bar (if enabled): *Tools -> Build Directory from Markdown* or *Build Markdown from Directory*.
- Via Key Bindings (if enabled): Use the defined key-mapping specified in the sublime-keymap file. Suggested mappings:
  - `Ctrl+Alt+M` for *Directory to Markdown*.
  - `Alt+Shift+M` for *Markdown to Directory*.

## Configuration

- Options can be configured in Markdown2Dir.sublime-settings. Access via: *Preferences -> Package Settings -> Markdown2Dir*.
- For more information about the plugin's options, see the settings file or the documentation in the GitHub repository.

## License

Markdown2Dir is available under two licenses:

- **Standard User License (Free)**: For personal and non-commercial use. [View License](LICENSE)
- **Commercial License**: For commercial use, including collaboration features and priority support. [View Commercial License](COMMERCIAL_LICENSE)

For commercial inquiries, please contact [JohnReyn.developer@gmail.com](mailto:JohnReyn.developer@gmail.com)

## Contributing

Contributions are welcome! Here's how you can help:

1. **Bug Reports & Feature Requests**
   - Use the GitHub [issue tracker](https://github.com/JohhannasReyn/Markdown2Dir/issues)
   - Clearly describe the issue/feature including steps to reproduce when it is a bug
   - Make sure you fill in the earliest version that you know has the issue

2. **Pull Requests**
   - Fork the repository on GitHub
   - Create a topic branch from where you want to base your work
   - Make commits of logical and atomic units
   - Check for unnecessary whitespace with `git diff --check` before committing
   - Write meaningful commit messages
   - Push your changes to a topic branch in your fork of the repository
   - Submit a pull request

3. **Code Style**
   - Follow PEP 8 coding standards
   - Add appropriate test coverage for new features
   - Document new code based on the project's documentation standards

4. **License**
   - By contributing code, you agree to license your contribution under the same terms as the project.
   - All contributions are governed by the Standard User License (Free) terms.

## Support

- For general questions and discussions, open an [issue](https://github.com/JohhannasReyn/Markdown2Dir/issues)
- For commercial support, contact [JohnReyn.developer@gmail.com](mailto:JohnReyn.developer@gmail.com)
- Check the [documentation](https://github.com/JohhannasReyn/Markdown2Dir/wiki) for detailed information

---
Made with ❤️ by John Reyn