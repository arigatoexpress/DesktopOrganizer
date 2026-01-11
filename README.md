# AI File Organizer

```
    _    ___   _____ _ _        ___                        _
   / \  |_ _| |  ___(_) | ___  / _ \ _ __ __ _  __ _ _ __ (_)_______ _ __
  / _ \  | |  | |_  | | |/ _ \| | | | '__/ _` |/ _` | '_ \| |_  / _ \ '__|
 / ___ \ | |  |  _| | | |  __/| |_| | | | (_| | (_| | | | | |/ /  __/ |
/_/   \_\___| |_|   |_|_|\___| \___/|_|  \__, |\__,_|_| |_|_/___\___|_|
                                         |___/
```

**An intelligent file organization tool powered by local LLM (Ollama) that automatically categorizes and organizes your files based on content analysis.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- **AI-Powered Analysis** - Uses local Ollama LLM to intelligently categorize files by content
- **Privacy-First** - All processing happens locally, no data leaves your machine
- **Smart Fallbacks** - Works without AI using extension and keyword matching
- **Dry Run Mode** - Preview all changes before executing
- **Full Undo Support** - Reverse any organization with a single command
- **Fast Mode** - Skip AI for rapid bulk organization
- **19 Categories** - Documents, Code, Media, Archives, and more

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI FILE ORGANIZER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│   │              │     │              │     │              │                │
│   │   SCANNER    │────▶│   ANALYZER   │────▶│    MOVER     │                │
│   │              │     │              │     │              │                │
│   └──────────────┘     └──────────────┘     └──────────────┘                │
│          │                    │                    │                        │
│          ▼                    ▼                    ▼                        │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│   │ • Find files │     │ • Read content│     │ • Create dirs │               │
│   │ • Get metadata│    │ • Query Ollama│     │ • Move files  │               │
│   │ • Extract text│    │ • Categorize  │     │ • Log undo    │               │
│   └──────────────┘     └──────────────┘     └──────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                              BEFORE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ~/Downloads/                                                               │
│   ├── IMG_1234.jpg                                                          │
│   ├── report_final_v2.pdf                                                   │
│   ├── script.py                                                             │
│   ├── meeting_notes.docx                                                    │
│   ├── song.mp3                                                              │
│   ├── data.csv                                                              │
│   ├── archive.zip                                                           │
│   └── ... (hundreds more files)                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                          python organizer.py
                                    │
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                               AFTER                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ~/Downloads/Organized/                                                     │
│   │                                                                          │
│   ├── Documents/                                                             │
│   │   ├── PDFs/           ← report_final_v2.pdf                             │
│   │   ├── Work/           ← meeting_notes.docx                              │
│   │   └── Financial/                                                        │
│   │                                                                          │
│   ├── Code/                                                                  │
│   │   ├── Python/         ← script.py                                       │
│   │   ├── JavaScript/                                                       │
│   │   └── Config/                                                           │
│   │                                                                          │
│   ├── Media/                                                                 │
│   │   ├── Photos/         ← IMG_1234.jpg                                    │
│   │   ├── Videos/                                                           │
│   │   └── Music/          ← song.mp3                                        │
│   │                                                                          │
│   ├── Data/               ← data.csv                                        │
│   ├── Archives/           ← archive.zip                                     │
│   └── Misc/                                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai) (optional, for AI-powered analysis)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-file-organizer.git
cd ai-file-organizer

# Install dependencies
pip install -r requirements.txt

# (Optional) Install and start Ollama for AI features
# Visit https://ollama.ai to install, then:
ollama pull llama3.2
ollama serve
```

---

## Usage

### Basic Commands

```bash
# Organize a folder (with AI analysis)
python organizer.py ~/Downloads

# Preview changes without moving files
python organizer.py ~/Downloads --dry-run

# Fast mode (no AI, uses extension/keyword matching)
python organizer.py ~/Downloads --fast

# Organize only top-level files (no subdirectories)
python organizer.py ~/Downloads --no-recursive

# Specify output directory
python organizer.py ~/Downloads --output ~/Sorted

# Use a different Ollama model
python organizer.py ~/Downloads --model mistral

# Undo the last organization
python organizer.py --undo

# List available categories
python organizer.py --categories
```

### Command Reference

```
┌────────────────────┬───────────────────────────────────────────────────────┐
│ Option             │ Description                                           │
├────────────────────┼───────────────────────────────────────────────────────┤
│ <source>           │ Directory to organize                                 │
│ --output, -o       │ Output directory (default: source/Organized)          │
│ --dry-run, -n      │ Preview changes without moving files                  │
│ --fast, -f         │ Skip AI analysis, use extension/keyword matching      │
│ --recursive, -r    │ Scan subdirectories (default: true)                   │
│ --no-recursive     │ Only scan top-level files                             │
│ --model, -m        │ Ollama model to use (default: llama3.2)               │
│ --undo, -u         │ Undo the last organization session                    │
│ --categories, -c   │ List all available categories                         │
└────────────────────┴───────────────────────────────────────────────────────┘
```

---

## Categories

The organizer sorts files into these categories:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FILE CATEGORIES                                   │
├──────────────────┬──────────────────────────┬───────────────────────────────┤
│ Category         │ Path                     │ File Types                    │
├──────────────────┼──────────────────────────┼───────────────────────────────┤
│ Work Documents   │ Documents/Work           │ .docx, .xlsx, .pptx           │
│ Personal Docs    │ Documents/Personal       │ notes, letters, journals      │
│ Financial        │ Documents/Financial      │ invoices, receipts, tax docs  │
│ Legal            │ Documents/Legal          │ contracts, agreements         │
│ PDFs             │ Documents/PDFs           │ .pdf                          │
│ eBooks           │ Documents/eBooks         │ .epub, .mobi                  │
├──────────────────┼──────────────────────────┼───────────────────────────────┤
│ Python           │ Code/Python              │ .py                           │
│ JavaScript       │ Code/JavaScript          │ .js, .ts, .jsx, .tsx          │
│ Web Files        │ Code/Web                 │ .html, .css, .scss            │
│ Config           │ Code/Config              │ .json, .yaml, .toml           │
│ Other Code       │ Code/Other               │ .go, .rs, .java, .c           │
├──────────────────┼──────────────────────────┼───────────────────────────────┤
│ Photos           │ Media/Photos             │ .jpg, .png, .heic             │
│ Videos           │ Media/Videos             │ .mp4, .mov, .mkv              │
│ Music            │ Media/Music              │ .mp3, .wav, .flac             │
│ Graphics         │ Media/Graphics           │ .psd, .ai, .sketch            │
├──────────────────┼──────────────────────────┼───────────────────────────────┤
│ Archives         │ Archives                 │ .zip, .rar, .tar.gz           │
│ Data Files       │ Data                     │ .csv, .sqlite, .parquet       │
│ Installers       │ Applications/Installers  │ .dmg, .exe, .pkg              │
│ Miscellaneous    │ Misc                     │ uncategorized files           │
└──────────────────┴──────────────────────────┴───────────────────────────────┘
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROJECT STRUCTURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ai-file-organizer/                                                         │
│   │                                                                          │
│   ├── organizer.py      ─────────────────────────  Main CLI entry point     │
│   │         │                                                                │
│   │         ├── scanner.py    ────────────────────  File discovery          │
│   │         │         │                                                      │
│   │         │         └── Recursively scans directories                     │
│   │         │             Extracts metadata (size, dates, type)             │
│   │         │             Reads text content from files                     │
│   │         │             Extracts text from PDFs                           │
│   │         │                                                                │
│   │         ├── analyzer.py   ────────────────────  AI categorization       │
│   │         │         │                                                      │
│   │         │         └── Connects to local Ollama                          │
│   │         │             Sends file content for analysis                   │
│   │         │             Falls back to rules if AI unavailable             │
│   │         │                                                                │
│   │         ├── mover.py      ────────────────────  File operations         │
│   │         │         │                                                      │
│   │         │         └── Creates category directories                      │
│   │         │             Moves files with collision handling               │
│   │         │             Logs all operations for undo                      │
│   │         │                                                                │
│   │         └── categories.py ────────────────────  Category definitions    │
│   │                   │                                                      │
│   │                   └── 19 predefined categories                          │
│   │                       Extension mappings                                │
│   │                       Keyword rules                                     │
│   │                                                                          │
│   ├── config.py         ─────────────────────────  Configuration            │
│   ├── requirements.txt  ─────────────────────────  Dependencies             │
│   └── undo_log.json     ─────────────────────────  Generated at runtime     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CATEGORIZATION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌───────────┐                                   │
│                              │   FILE    │                                   │
│                              └─────┬─────┘                                   │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                              │
│                         │  Has text content?  │                              │
│                         └──────────┬──────────┘                              │
│                                    │                                         │
│                    ┌───────────────┴───────────────┐                         │
│                    │ YES                       NO  │                         │
│                    ▼                               ▼                         │
│         ┌─────────────────────┐      ┌─────────────────────┐                │
│         │   Ollama Available? │      │  Check Extension    │                │
│         └──────────┬──────────┘      └──────────┬──────────┘                │
│                    │                            │                            │
│         ┌──────────┴──────────┐                 │                            │
│         │ YES             NO  │                 │                            │
│         ▼                 ▼   │                 │                            │
│   ┌───────────┐    ┌───────────┐                │                            │
│   │ AI        │    │ Extension │◄───────────────┘                            │
│   │ Analysis  │    │ Matching  │                                             │
│   │ (99%)     │    │ (90%)     │                                             │
│   └─────┬─────┘    └─────┬─────┘                                             │
│         │                │                                                   │
│         │                ▼                                                   │
│         │         ┌─────────────────────┐                                    │
│         │         │  Extension matched? │                                    │
│         │         └──────────┬──────────┘                                    │
│         │                    │                                               │
│         │         ┌──────────┴──────────┐                                    │
│         │         │ YES             NO  │                                    │
│         │         ▼                 ▼   │                                    │
│         │   ┌───────────┐    ┌───────────┐                                   │
│         │   │ Category  │    │ Keyword   │                                   │
│         │   │ Found     │    │ Matching  │                                   │
│         │   └─────┬─────┘    └─────┬─────┘                                   │
│         │         │                │                                         │
│         │         │                ▼                                         │
│         │         │         ┌─────────────────────┐                          │
│         │         │         │  Keyword matched?   │                          │
│         │         │         └──────────┬──────────┘                          │
│         │         │                    │                                     │
│         │         │         ┌──────────┴──────────┐                          │
│         │         │         │ YES             NO  │                          │
│         │         │         ▼                 ▼   │                          │
│         │         │   ┌───────────┐    ┌───────────┐                         │
│         │         │   │ Category  │    │ Fallback  │                         │
│         │         │   │ (70%)     │    │ Misc (30%)│                         │
│         │         │   └─────┬─────┘    └─────┬─────┘                         │
│         │         │         │                │                               │
│         ▼         ▼         ▼                ▼                               │
│   ┌─────────────────────────────────────────────────┐                        │
│   │                 FINAL CATEGORY                  │                        │
│   └─────────────────────────────────────────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Examples

### Organize Downloads with Preview

```bash
$ python organizer.py ~/Downloads --dry-run

╭──────────────────────────────────────────────────────────────────────────────╮
│ AI File Organizer - Intelligent file organization powered by local LLM       │
╰──────────────────────────────────────────────────────────────────────────────╯
DRY RUN MODE - No files will be moved

Scanning: /Users/you/Downloads
Found 156 files to organize

Ollama connected - using model: llama3.2
Analyzing files... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Analysis Summary:
  AI: 23 files
  Ext: 127 files
  Fallback: 6 files

                               Organization Plan
╭─────────────────┬─────────────────┬─────────────────┬───────────┬────────────╮
│ File            │ Category        │ Destination     │ Method    │ Confidence │
├─────────────────┼─────────────────┼─────────────────┼───────────┼────────────┤
│ report.pdf      │ PDFs            │ Documents/PDFs  │ extension │        90% │
│ script.py       │ Python Code     │ Code/Python     │ extension │        90% │
│ notes.txt       │ Work Documents  │ Documents/Work  │ ai        │        95% │
│ photo.jpg       │ Photos          │ Media/Photos    │ extension │        90% │
╰─────────────────┴─────────────────┴─────────────────┴───────────┴────────────╯

Dry run complete. Use without --dry-run to organize files.
```

### Fast Bulk Organization

```bash
$ python organizer.py ~/Desktop --fast

╭──────────────────────────────────────────────────────────────────────────────╮
│ AI File Organizer - Intelligent file organization powered by local LLM       │
╰──────────────────────────────────────────────────────────────────────────────╯
FAST MODE - Skipping AI analysis

Scanning: /Users/you/Desktop
Found 42 files to organize

Fast mode - using extension/keyword matching only
Analyzing files... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
Moving files...    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Organization complete!
  Organized 42 files into /Users/you/Desktop/Organized
  Use --undo to reverse this operation
```

### Undo Organization

```bash
$ python organizer.py --undo

╭──────────────────────────────────────────────────────────────────────────────╮
│ AI File Organizer - Intelligent file organization powered by local LLM       │
╰──────────────────────────────────────────────────────────────────────────────╯

Undoing last organization...
Successfully undid 42 file moves

                              Restored Files
╭────────────────────────────────┬────────────────────────────────────────╮
│ From                           │ To                                     │
├────────────────────────────────┼────────────────────────────────────────┤
│ report.pdf                     │ /Users/you/Desktop/report.pdf          │
│ script.py                      │ /Users/you/Desktop/script.py           │
│ ...                            │ ...                                    │
╰────────────────────────────────┴────────────────────────────────────────╯
```

---

## Configuration

The default configuration can be customized in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `ollama_model` | `llama3.2` | Ollama model for AI analysis |
| `ollama_host` | `http://localhost:11434` | Ollama server address |
| `max_file_size_mb` | `50` | Skip files larger than this |
| `max_content_chars` | `4000` | Max characters to send to LLM |
| `output_dir_name` | `Organized` | Name of output directory |

---

## Requirements

- **Python 3.8+**
- **Dependencies:**
  - `ollama` - Ollama Python client
  - `rich` - Beautiful terminal output
  - `python-magic` - File type detection
  - `PyPDF2` - PDF text extraction

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Acknowledgments

- [Ollama](https://ollama.ai) for local LLM inference
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output

---

<p align="center">
  Made with AI assistance
</p>
