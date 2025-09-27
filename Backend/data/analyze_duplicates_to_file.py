#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vocabulary Duplicate Analyzer - File Output Version
Analyzes vocabulary CSV files and saves detailed report to file.
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

    # Output file
    output_file = os.path.join(data_dir, 'duplicate_analysis_report.txt')

    # Read all vocabulary files
    vocab_data = {}
    total_words = 0

    with open(output_file, 'w', encoding='utf-8') as report:
        report.write("VOCABULARY DUPLICATE ANALYSIS REPORT\n")
        report.write("=" * 50 + "\n\n")

        report.write("FILE STATISTICS:\n")
        for level, filepath in files.items():
            if os.path.exists(filepath):
                vocabulary = read_vocab_file(filepath)
                vocab_data[level] = vocabulary
                total_words += len(vocabulary)
                report.write(f"{level}: {len(vocabulary)} words\n")
            else:
                report.write(f"Warning: {filepath} not found\n")
                vocab_data[level] = []

        report.write(f"\nTotal words across all levels: {total_words}\n\n")

        # 1. Analyze internal duplicates within each level
        report.write("1. INTERNAL DUPLICATES (within each level)\n")
        report.write("-" * 40 + "\n\n")

        total_internal_duplicates = 0
        for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
            if level in vocab_data:
                duplicates = analyze_internal_duplicates(level, vocab_data[level])

                report.write(f"{level} Level:\n")
                if duplicates:
                    report.write(f"  Found {len(duplicates)} duplicate German words:\n")
                    for german, translations in duplicates.items():
                        total_internal_duplicates += len(translations) - 1  # Count extra occurrences
                        report.write(f"    '{german}' appears {len(translations)} times with translations: {translations}\n")
                else:
                    report.write("  No internal duplicates found ✓\n")
                report.write("\n")

        report.write(f"Total internal duplicate entries: {total_internal_duplicates}\n\n")

        # 2. Analyze cross-level duplicates
        report.write("2. CROSS-LEVEL DUPLICATES (same word in multiple levels)\n")
        report.write("-" * 55 + "\n\n")

        cross_duplicates = analyze_cross_level_duplicates(vocab_data)

        if cross_duplicates:
            report.write(f"Found {len(cross_duplicates)} German words appearing in multiple levels:\n\n")

            # Group by number of levels for better organization
            by_level_count = defaultdict(list)
            for german, levels in cross_duplicates.items():
                by_level_count[len(levels)].append((german, levels))

            for level_count in sorted(by_level_count.keys(), reverse=True):
                words = by_level_count[level_count]
                report.write(f"Words appearing in {level_count} levels ({len(words)} words):\n")

                for german, levels in sorted(words):
                    recommended_level = recommend_level_placement(german, levels)
                    report.write(f"  '{german}' in levels: {', '.join(sorted(levels, key=get_level_priority))}\n")
                    report.write(f"    → Recommendation: Keep in {recommended_level}, remove from {', '.join([l for l in levels if l != recommended_level])}\n\n")
        else:
            report.write("No cross-level duplicates found ✓\n")

        # 3. Summary and recommendations
        report.write("\n3. SUMMARY AND RECOMMENDATIONS\n")
        report.write("-" * 35 + "\n\n")

        if total_internal_duplicates > 0:
            report.write(f"• Internal duplicates: {total_internal_duplicates} entries need to be removed\n")
            report.write("  - Review each duplicate and keep only one entry per German word per level\n")
            report.write("  - Check if different Spanish translations are valid variations or errors\n\n")

        if cross_duplicates:
            # Calculate how many entries would be removed
            entries_to_remove = sum(len(levels) - 1 for levels in cross_duplicates.values())
            report.write(f"• Cross-level duplicates: {entries_to_remove} entries should be moved/removed\n")
            report.write("  - Follow the hierarchy: A1 < A2 < B1 < B2 < C1\n")
            report.write("  - Keep words in the lowest appropriate level only\n")
            report.write("  - Consider if the word truly belongs at different difficulty levels\n\n")

            # Level-specific recommendations
            report.write("Specific actions needed:\n")
            level_removals = defaultdict(list)
            for german, levels in cross_duplicates.items():
                recommended_level = recommend_level_placement(german, levels)
                for level in levels:
                    if level != recommended_level:
                        level_removals[level].append(german)

            for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
                if level in level_removals and level_removals[level]:
                    report.write(f"  - Remove {len(level_removals[level])} words from {level}:\n")
                    # Write first 20 words per line, then continue on new lines
                    words = sorted(level_removals[level])
                    for i in range(0, len(words), 20):
                        chunk = words[i:i+20]
                        report.write(f"    {', '.join(chunk)}\n")

        total_issues = total_internal_duplicates + (sum(len(levels) - 1 for levels in cross_duplicates.values()) if cross_duplicates else 0)
        if total_issues == 0:
            report.write("✓ No duplicate issues found! The vocabulary files are clean.\n")
        else:
            report.write(f"\nTotal cleanup needed: {total_issues} entries\n")
            report.write("After cleanup, the vocabulary will be more efficient and avoid confusion.\n")

    print(f"Analysis complete! Report saved to: {output_file}")
    print(f"Total issues found: {total_internal_duplicates} internal duplicates + {sum(len(levels) - 1 for levels in cross_duplicates.values()) if cross_duplicates else 0} cross-level duplicates")


if __name__ == "__main__":
    main()