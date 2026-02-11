# DesktopOrganizer

AI-powered desktop file organizer using local Ollama LLM for intelligent categorization.

## Commands

| Command | Description |
|---------|-------------|
| `python organizer.py ~/Downloads` | Organize a folder |
| `python organizer.py ~/Downloads --dry-run` | Preview changes only |
| `python organizer.py ~/Downloads --fast` | Skip AI, use rules only |
| `python organizer.py --undo` | Restore previous state |
| `python organizer.py --categories` | List 19 categories |
| `python organizer.py ~/Downloads --model mistral` | Use different Ollama model |
| `python organizer.py ~/Downloads --output ~/Sorted` | Custom output directory |
| `ollama serve` | Start Ollama (required for AI mode) |
| `ollama pull llama3.2` | Pull default model |

## Architecture

```
DesktopOrganizer/
  organizer.py    # CLI orchestrator (entry point)
  scanner.py      # File discovery + metadata + PDF extraction (pypdf)
  analyzer.py     # Ollama LLM categorization
  mover.py        # File operations + undo logging
  config.py       # Settings, categories, model config
```

**Flow:** Scanner → Analyzer (Ollama) → Mover → undo_log.json

**Fallback chain:** AI analysis (85%) → Extension matching (90%) → Keyword matching (70%) → Miscellaneous

## Gotchas

- Ollama must be running locally (`ollama serve`) for AI mode
- Default model: `llama3.2` - must be pulled first
- Files >50MB are skipped (configurable in `config.py`)
- Undo relies on `undo_log.json` being intact
- PDF extraction uses `pypdf` (was PyPDF2, now updated)
- No cloud dependency; fully local processing
- `--fast` mode ignores AI entirely; uses extension/keyword rules only
