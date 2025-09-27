#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vocabulary Duplicate Analyzer
Analyzes vocabulary CSV files to identify duplicates within and across levels.
"""

import csv
import os
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple


def read_vocab_file(filepath: str) -> List[Tuple[str, str]]:
    """Read a vocabulary CSV file and return list of (German, Spanish) tuples."""
    vocabulary = []

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Skip header
            next(reader, None)

            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    german_word = row[0].strip()
                    spanish_word = row[1].strip()
                    vocabulary.append((german_word, spanish_word))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return vocabulary


def analyze_internal_duplicates(level: str, vocabulary: List[Tuple[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
    """Find duplicates within a single level file."""
    word_count = Counter()
    word_translations = defaultdict(list)

    for german, spanish in vocabulary:
        word_count[german] += 1
        word_translations[german].append(spanish)

    # Find words that appear more than once
    duplicates = {}
    for german, count in word_count.items():
        if count > 1:
            duplicates[german] = word_translations[german]

    return duplicates


def analyze_cross_level_duplicates(vocab_data: Dict[str, List[Tuple[str, str]]]) -> Dict[str, List[str]]:
    """Find words that appear in multiple levels."""
    word_to_levels = defaultdict(list)

    for level, vocabulary in vocab_data.items():
        for german, _ in vocabulary:
            word_to_levels[german].append(level)

    # Find words that appear in multiple levels
    cross_duplicates = {}
    for german, levels in word_to_levels.items():
        if len(levels) > 1:
            cross_duplicates[german] = levels

    return cross_duplicates


def get_level_priority(level: str) -> int:
    """Return priority for level (lower number = higher priority)."""
    priority_map = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5}
    return priority_map.get(level, 999)


def recommend_level_placement(word: str, levels: List[str]) -> str:
    """Recommend which level a word should be kept in (lowest appropriate level)."""
    # Sort levels by priority (A1 first, then A2, etc.)
    sorted_levels = sorted(levels, key=get_level_priority)
    return sorted_levels[0]  # Return the lowest level


def main():
    # Define file paths
    data_dir = '/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data'
    files = {
        'A1': os.path.join(data_dir, 'A1_vokabeln.csv'),
        'A2': os.path.join(data_dir, 'A2_vokabeln.csv'),
        'B1': os.path.join(data_dir, 'B1_vokabeln.csv'),
        'B2': os.path.join(data_dir, 'B2_vokabeln.csv'),
        'C1': os.path.join(data_dir, 'C1_vokabeln.csv')
    }

    # Read all vocabulary files
    vocab_data = {}
    total_words = 0

    print("VOCABULARY DUPLICATE ANALYSIS REPORT")
    print("=" * 50)
    print()

    for level, filepath in files.items():
        if os.path.exists(filepath):
            vocabulary = read_vocab_file(filepath)
            vocab_data[level] = vocabulary
            total_words += len(vocabulary)
            print(f"{level}: {len(vocabulary)} words")
        else:
            print(f"Warning: {filepath} not found")
            vocab_data[level] = []

    print(f"\nTotal words across all levels: {total_words}")
    print()

    # 1. Analyze internal duplicates within each level
    print("1. INTERNAL DUPLICATES (within each level)")
    print("-" * 40)

    total_internal_duplicates = 0
    for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
        if level in vocab_data:
            duplicates = analyze_internal_duplicates(level, vocab_data[level])

            print(f"\n{level} Level:")
            if duplicates:
                print(f"  Found {len(duplicates)} duplicate German words:")
                for german, translations in duplicates.items():
                    total_internal_duplicates += len(translations) - 1  # Count extra occurrences
                    print(f"    '{german}' appears {len(translations)} times with translations: {translations}")
            else:
                print("  No internal duplicates found ✓")

    print(f"\nTotal internal duplicate entries: {total_internal_duplicates}")
    print()

    # 2. Analyze cross-level duplicates
    print("2. CROSS-LEVEL DUPLICATES (same word in multiple levels)")
    print("-" * 55)

    cross_duplicates = analyze_cross_level_duplicates(vocab_data)

    if cross_duplicates:
        print(f"\nFound {len(cross_duplicates)} German words appearing in multiple levels:")
        print()

        # Group by number of levels for better organization
        by_level_count = defaultdict(list)
        for german, levels in cross_duplicates.items():
            by_level_count[len(levels)].append((german, levels))

        for level_count in sorted(by_level_count.keys(), reverse=True):
            words = by_level_count[level_count]
            print(f"Words appearing in {level_count} levels ({len(words)} words):")

            for german, levels in sorted(words):
                recommended_level = recommend_level_placement(german, levels)
                print(f"  '{german}' in levels: {', '.join(sorted(levels, key=get_level_priority))}")
                print(f"    → Recommendation: Keep in {recommended_level}, remove from {', '.join([l for l in levels if l != recommended_level])}")
                print()
    else:
        print("No cross-level duplicates found ✓")

    # 3. Summary and recommendations
    print("3. SUMMARY AND RECOMMENDATIONS")
    print("-" * 35)
    print()

    if total_internal_duplicates > 0:
        print(f"• Internal duplicates: {total_internal_duplicates} entries need to be removed")
        print("  - Review each duplicate and keep only one entry per German word per level")
        print("  - Check if different Spanish translations are valid variations or errors")
        print()

    if cross_duplicates:
        # Calculate how many entries would be removed
        entries_to_remove = sum(len(levels) - 1 for levels in cross_duplicates.values())
        print(f"• Cross-level duplicates: {entries_to_remove} entries should be moved/removed")
        print("  - Follow the hierarchy: A1 < A2 < B1 < B2 < C1")
        print("  - Keep words in the lowest appropriate level only")
        print("  - Consider if the word truly belongs at different difficulty levels")
        print()

        # Level-specific recommendations
        print("Specific actions needed:")
        level_removals = defaultdict(list)
        for german, levels in cross_duplicates.items():
            recommended_level = recommend_level_placement(german, levels)
            for level in levels:
                if level != recommended_level:
                    level_removals[level].append(german)

        for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
            if level in level_removals and level_removals[level]:
                print(f"  - Remove {len(level_removals[level])} words from {level}: {', '.join(sorted(level_removals[level])[:10])}{'...' if len(level_removals[level]) > 10 else ''}")

    total_issues = total_internal_duplicates + (entries_to_remove if cross_duplicates else 0)
    if total_issues == 0:
        print("✓ No duplicate issues found! The vocabulary files are clean.")
    else:
        print(f"\nTotal cleanup needed: {total_issues} entries")
        print("After cleanup, the vocabulary will be more efficient and avoid confusion.")


if __name__ == "__main__":
    main()