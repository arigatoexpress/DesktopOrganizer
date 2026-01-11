"""Category definitions and rule-based classification for the AI File Organizer."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Category:
    """Represents a file category."""
    name: str
    path: str  # Relative path in organized structure
    description: str
    extensions: set[str] = None  # File extensions that match this category
    keywords: set[str] = None  # Keywords in filename that match

    def __post_init__(self):
        self.extensions = self.extensions or set()
        self.keywords = self.keywords or set()


# Default category hierarchy
CATEGORIES = {
    # Documents
    "work": Category(
        name="Work Documents",
        path="Documents/Work",
        description="Work-related documents, reports, presentations",
        extensions={'.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.ods', '.odp'},
        keywords={'report', 'meeting', 'project', 'proposal', 'invoice', 'contract', 'agenda', 'memo'}
    ),
    "personal": Category(
        name="Personal Documents",
        path="Documents/Personal",
        description="Personal documents, letters, notes",
        extensions=set(),
        keywords={'personal', 'diary', 'journal', 'letter', 'note', 'todo', 'list'}
    ),
    "financial": Category(
        name="Financial Documents",
        path="Documents/Financial",
        description="Financial records, receipts, tax documents",
        extensions=set(),
        keywords={'tax', 'receipt', 'invoice', 'bank', 'statement', 'budget', 'expense', 'payment', 'salary'}
    ),
    "legal": Category(
        name="Legal Documents",
        path="Documents/Legal",
        description="Legal documents, contracts, agreements",
        extensions=set(),
        keywords={'legal', 'contract', 'agreement', 'license', 'terms', 'policy', 'nda', 'court', 'law'}
    ),
    "ebooks": Category(
        name="eBooks",
        path="Documents/eBooks",
        description="Electronic books and publications",
        extensions={'.epub', '.mobi', '.azw', '.azw3'},
        keywords={'ebook', 'book', 'novel', 'guide', 'manual'}
    ),
    "pdf": Category(
        name="PDFs",
        path="Documents/PDFs",
        description="PDF documents",
        extensions={'.pdf'},
        keywords=set()
    ),

    # Code
    "python": Category(
        name="Python Code",
        path="Code/Python",
        description="Python source files",
        extensions={'.py', '.pyw', '.pyx', '.pxd', '.pyi'},
        keywords=set()
    ),
    "javascript": Category(
        name="JavaScript Code",
        path="Code/JavaScript",
        description="JavaScript and TypeScript files",
        extensions={'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'},
        keywords=set()
    ),
    "web": Category(
        name="Web Files",
        path="Code/Web",
        description="HTML, CSS, and web assets",
        extensions={'.html', '.htm', '.css', '.scss', '.sass', '.less', '.svg'},
        keywords=set()
    ),
    "code_other": Category(
        name="Other Code",
        path="Code/Other",
        description="Other programming languages",
        extensions={
            '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs', '.rb',
            '.php', '.swift', '.kt', '.scala', '.r', '.m', '.mm', '.sql',
            '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd'
        },
        keywords=set()
    ),
    "config": Category(
        name="Config Files",
        path="Code/Config",
        description="Configuration and settings files",
        extensions={
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.env', '.properties', '.xml'
        },
        keywords={'config', 'settings', 'preferences'}
    ),

    # Media
    "photos": Category(
        name="Photos",
        path="Media/Photos",
        description="Image files and photographs",
        extensions={'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw'},
        keywords={'photo', 'image', 'picture', 'screenshot', 'img', 'pic'}
    ),
    "videos": Category(
        name="Videos",
        path="Media/Videos",
        description="Video files",
        extensions={'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg', '.3gp'},
        keywords={'video', 'movie', 'clip', 'recording'}
    ),
    "music": Category(
        name="Music",
        path="Media/Music",
        description="Audio and music files",
        extensions={'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.alac'},
        keywords={'music', 'song', 'audio', 'track', 'podcast'}
    ),
    "graphics": Category(
        name="Graphics",
        path="Media/Graphics",
        description="Design and graphics files",
        extensions={'.psd', '.ai', '.eps', '.indd', '.sketch', '.fig', '.xd', '.afdesign', '.afphoto'},
        keywords={'design', 'graphic', 'logo', 'icon', 'banner'}
    ),

    # Archives
    "archives": Category(
        name="Archives",
        path="Archives",
        description="Compressed files and archives",
        extensions={'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.tbz2'},
        keywords={'backup', 'archive'}
    ),

    # Data
    "data": Category(
        name="Data Files",
        path="Data",
        description="Data files, spreadsheets, databases",
        extensions={'.csv', '.tsv', '.parquet', '.sqlite', '.db', '.mdb', '.accdb'},
        keywords={'data', 'dataset', 'export', 'import'}
    ),

    # Applications
    "installers": Category(
        name="Installers",
        path="Applications/Installers",
        description="Application installers and packages",
        extensions={'.dmg', '.pkg', '.msi', '.exe', '.deb', '.rpm', '.appimage', '.snap'},
        keywords={'install', 'setup', 'installer'}
    ),

    # Misc
    "misc": Category(
        name="Miscellaneous",
        path="Misc",
        description="Uncategorized files",
        extensions=set(),
        keywords=set()
    )
}


def get_category_by_extension(extension: str) -> Optional[Category]:
    """Get category based on file extension."""
    ext = extension.lower()
    for category in CATEGORIES.values():
        if ext in category.extensions:
            return category
    return None


def get_category_by_keywords(filename: str) -> Optional[Category]:
    """Get category based on filename keywords."""
    name_lower = filename.lower()
    for category in CATEGORIES.values():
        for keyword in category.keywords:
            if keyword in name_lower:
                return category
    return None


def get_fallback_category() -> Category:
    """Get the fallback category for unclassified files."""
    return CATEGORIES["misc"]


def get_all_categories() -> list[Category]:
    """Get all available categories."""
    return list(CATEGORIES.values())


def get_category_by_name(name: str) -> Optional[Category]:
    """Get category by its key name."""
    return CATEGORIES.get(name.lower())


# Category names for AI prompt
CATEGORY_NAMES = list(CATEGORIES.keys())
CATEGORY_DESCRIPTIONS = "\n".join(
    f"- {key}: {cat.description} (path: {cat.path})"
    for key, cat in CATEGORIES.items()
)
