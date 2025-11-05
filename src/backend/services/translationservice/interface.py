"""
Translation Service Interface
Defines the contract that all translation services must implement
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from services.base_service import IAIService


@dataclass
class TranslationResult:
    """Result of a translation operation"""

    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float | None = None
    metadata: dict[str, Any] | None = None


class ITranslationService(IAIService):
    """
    Interface for translation services
    All translation implementations must implement these methods
    """

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """
        Translate a single text

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'de')
            target_lang: Target language code

        Returns:
            TranslationResult with translation details
        """
        pass

    @abstractmethod
    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str) -> list[TranslationResult]:
        """
        Translate multiple texts in batch

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            List of TranslationResult objects
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> dict[str, str]:
        """
        Get dictionary of supported language codes and names

        Returns:
            Dictionary mapping language codes to language names
        """
        pass

    @abstractmethod
    def is_language_supported(self, lang_code: str) -> bool:
        """
        Check if a language is supported

        Args:
            lang_code: Language code to check

        Returns:
            True if language is supported, False otherwise
        """
        pass
