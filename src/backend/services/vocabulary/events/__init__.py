"""Vocabulary events module - Moved from domains/vocabulary/events.py"""

from .events import (
    DomainEvent,
    EventBus,
    EventType,
    LevelCompletedEvent,
    ProgressUpdatedEvent,
    StreakAchievedEvent,
    VocabularyAddedEvent,
    WordForgottenEvent,
    WordLearnedEvent,
    WordMasteredEvent,
    get_event_bus,
    publish_event,
)

__all__ = [
    "DomainEvent",
    "EventBus",
    "EventType",
    "LevelCompletedEvent",
    "ProgressUpdatedEvent",
    "StreakAchievedEvent",
    "VocabularyAddedEvent",
    "WordForgottenEvent",
    "WordLearnedEvent",
    "WordMasteredEvent",
    "get_event_bus",
    "publish_event",
]
