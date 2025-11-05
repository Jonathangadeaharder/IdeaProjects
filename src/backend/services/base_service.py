"""
Base service interface for all AI/ML services.

Provides common contract for service lifecycle management,
eliminating duplication across transcription and translation services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IAIService(ABC):
    """
    Base interface for all AI/ML services (transcription, translation, etc.).

    Defines common lifecycle methods that all services must implement.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the service and load models.

        Should be idempotent - calling multiple times should be safe.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources and unload models.

        Should release GPU memory, close connections, etc.
        """
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """
        Get the name of this service.

        Returns:
            Human-readable service name (e.g., "Whisper", "NLLB")
        """
        pass

    @property
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Check if the service is initialized and ready to use.

        Returns:
            True if service is ready, False otherwise
        """
        pass
