"""
Markdown2Dir - A Sublime Text plugin for converting between markdown files and directory structures;
additionally a directory tree of the targeted files is also constructed in the generated markdown.

Two licenses are available:
1. Standard User License (Free) - For personal and non-commercial use
2. Commercial License - For commercial use with collaboration features
"""

from .Markdown2Dir import Dir2MarkdownCommand, Markdown2DirCommand
from .utils import plugin_loaded

__all__ = [
    'Dir2MarkdownCommand',
    'Markdown2DirCommand',
    'plugin_loaded'
]

__version__ = '2.0.0'

__title__ = 'Markdown2Dir'
__author__ = 'John Reyn'
__author_email__ = 'JohnReyn.developer@gmail.com'

__license__ = 'Dual License'
__license_types__ = {
    'standard': 'Standard User License (Free) - For personal and non-commercial use',
    'commercial': 'Commercial License - For commercial use with collaboration features'
}
__copyright__ = 'Copyright 2024 John Reyn'

__url__ = 'https://github.com/JohhannasReyn/Markdown2Dir_and_Dir2Md'
__description__ = 'A Sublime Text plugin for converting between markdown files and directory structures'
__keywords__ = ['sublime-text', 'plugin', 'markdown', 'directory', 'conversion']

__license_files__ = {
    'standard': 'LICENSE',
    'commercial': 'COMMERCIAL_LICENSE'
}
