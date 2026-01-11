"""AI-powered content analyzer using Ollama for intelligent file categorization."""

from dataclasses import dataclass
from typing import Optional
import json

from scanner import FileInfo
from categories import (
    Category, CATEGORIES, CATEGORY_NAMES, CATEGORY_DESCRIPTIONS,
    get_category_by_extension, get_category_by_keywords, get_fallback_category
)
from config import Config, DEFAULT_CONFIG


@dataclass
class AnalysisResult:
    """Result of analyzing a file."""
    file_info: FileInfo
    category: Category
    confidence: float  # 0.0 to 1.0
    reasoning: str
    method: str  # 'ai', 'extension', 'keyword', 'fallback'


class FileAnalyzer:
    """Analyzes files using Ollama LLM for intelligent categorization."""

    def __init__(self, config: Config = None):
        self.config = config or DEFAULT_CONFIG
        self._client = None
        self._ollama_available = None

    def _get_client(self):
        """Lazy load Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.config.ollama_host)
                # Test connection
                self._client.list()
                self._ollama_available = True
            except Exception as e:
                self._ollama_available = False
                self._client = False
        return self._client if self._client else None

    @property
    def ollama_available(self) -> bool:
        """Check if Ollama is available."""
        if self._ollama_available is None:
            self._get_client()
        return self._ollama_available

    def analyze_file(self, file_info: FileInfo) -> AnalysisResult:
        """
        Analyze a single file and determine its category.

        Uses a cascading approach:
        1. Try AI analysis if content is available and Ollama is running
        2. Fall back to extension-based classification
        3. Fall back to keyword-based classification
        4. Finally use the misc category
        """
        # Try AI analysis if we have content
        if file_info.content and self.ollama_available:
            result = self._analyze_with_ai(file_info)
            if result:
                return result

        # Fall back to extension-based classification
        category = get_category_by_extension(file_info.extension)
        if category:
            return AnalysisResult(
                file_info=file_info,
                category=category,
                confidence=0.9,
                reasoning=f"Matched by file extension: {file_info.extension}",
                method="extension"
            )

        # Fall back to keyword-based classification
        category = get_category_by_keywords(file_info.name)
        if category:
            return AnalysisResult(
                file_info=file_info,
                category=category,
                confidence=0.7,
                reasoning=f"Matched by filename keywords",
                method="keyword"
            )

        # Final fallback
        return AnalysisResult(
            file_info=file_info,
            category=get_fallback_category(),
            confidence=0.3,
            reasoning="No matching category found, using fallback",
            method="fallback"
        )

    def _analyze_with_ai(self, file_info: FileInfo) -> Optional[AnalysisResult]:
        """Use Ollama to analyze file content and categorize."""
        client = self._get_client()
        if not client:
            return None

        prompt = self._build_prompt(file_info)

        try:
            response = client.chat(
                model=self.config.ollama_model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a file categorization assistant. Your job is to analyze file information and categorize files into the appropriate category.

You must respond with ONLY a valid JSON object in this exact format:
{"category": "category_name", "confidence": 0.95, "reasoning": "brief explanation"}

The category must be one of the valid categories provided. The confidence should be between 0.0 and 1.0."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.1,  # Low temperature for consistent results
                    "num_predict": 200   # Short response
                }
            )

            # Parse the response
            response_text = response['message']['content'].strip()
            return self._parse_ai_response(file_info, response_text)

        except Exception as e:
            return None

    def _build_prompt(self, file_info: FileInfo) -> str:
        """Build the prompt for AI analysis."""
        content_preview = file_info.content[:2000] if file_info.content else "No content available"

        return f"""Categorize this file based on its information:

**File Name:** {file_info.name}
**Extension:** {file_info.extension}
**Size:** {file_info.size_mb:.2f} MB
**MIME Type:** {file_info.mime_type or 'Unknown'}

**Content Preview:**
```
{content_preview}
```

**Available Categories:**
{CATEGORY_DESCRIPTIONS}

Analyze the file name, extension, and content to determine the best category. Respond with JSON only."""

    def _parse_ai_response(self, file_info: FileInfo, response: str) -> Optional[AnalysisResult]:
        """Parse the AI response and create an AnalysisResult."""
        try:
            # Try to extract JSON from the response
            # Handle cases where the model wraps JSON in markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            data = json.loads(response.strip())

            category_name = data.get('category', '').lower()
            confidence = float(data.get('confidence', 0.8))
            reasoning = data.get('reasoning', 'AI classification')

            # Validate category
            if category_name not in CATEGORIES:
                # Try to find a close match
                for key in CATEGORIES:
                    if key in category_name or category_name in key:
                        category_name = key
                        break
                else:
                    return None

            return AnalysisResult(
                file_info=file_info,
                category=CATEGORIES[category_name],
                confidence=min(confidence, 1.0),
                reasoning=reasoning,
                method="ai"
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def analyze_files(self, files: list[FileInfo], progress_callback=None) -> list[AnalysisResult]:
        """Analyze multiple files."""
        results = []
        total = len(files)

        for i, file_info in enumerate(files):
            result = self.analyze_file(file_info)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total, file_info.name)

        return results


def analyze_files(files: list[FileInfo], config: Config = None) -> list[AnalysisResult]:
    """Convenience function to analyze a list of files."""
    analyzer = FileAnalyzer(config)
    return analyzer.analyze_files(files)
