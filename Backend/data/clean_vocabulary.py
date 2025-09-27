#!/usr/bin/env python3
"""
Clean German vocabulary CSV files by removing inappropriate entries.
This script removes personal names, interjections, English loanwords,
and other inappropriate entries based on the vocabulary analysis.
"""

import csv
import shutil
import os
from typing import Dict, List, Set

# Define all the problematic entries by German word (not line number for reliability)
WORDS_TO_REMOVE = {
    'A1_vokabeln.csv': {
        # Personal names and inappropriate entries
        'Mama', 'Papa', 'Mr', 'Mrs', 'Sorry',
        # Interjections
        'Hallo', 'Tschüss', 'Ach', 'Hey', 'Na', 'Ok', 'Okay', 'Tja',
        # Place name confusion
        'Essen'  # This creates confusion with the verb "essen" (to eat)
    },
    'A2_vokabeln.csv': {
        # Personal names
        'Dad', 'Mom', 'Alex',
        # English loanwords
        'Fan', 'Festival', 'Hamburger', 'Laptop', 'Pizza', 'Team', 'Tennis',
        'Volleyball', 'Captain', 'Deal', 'Lord', "Ma'am", 'Major', 'Sir',
        # Interjections
        'Tschüs', 'Äh', 'Ähm', 'Wow',
        # Acronyms
        'Lkw', 'Cd'
    },
    'B1_vokabeln.csv': {
        # Place name confusion
        'essen',  # lowercase confusion with verb
        # English loanwords
        'Show', 'Basketball', 'Blog', 'Club', 'Comic', 'Container'
    }
}

# Define replacements for colloquial terms
REPLACEMENTS = {
    'A1_vokabeln.csv': {
        'Cool': 'großartig',
        'Toll': 'wunderbar',
    },
    'A2_vokabeln.csv': {
        'Super': 'großartig',
        'Boss': 'Chef',
        'Quatsch': 'Unsinn',
    },
    'B1_vokabeln.csv': {
        'Mist': 'Ärger',
        'Blöd': 'dumm',
    }
}

def backup_file(file_path: str) -> str:
    """Create a backup of the original file."""
    backup_path = file_path + '.violations_backup'
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def clean_vocabulary_file(file_path: str) -> Dict[str, int]:
    """Clean a vocabulary file by removing inappropriate entries and making replacements."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {'removed': 0, 'replaced': 0}

    filename = os.path.basename(file_path)
    words_to_remove = WORDS_TO_REMOVE.get(filename, set())
    replacements = REPLACEMENTS.get(filename, {})

    if not words_to_remove and not replacements:
        print(f"No cleaning needed for {filename}")
        return {'removed': 0, 'replaced': 0}

    # Create backup
    backup_file(file_path)

    # Process the file
    new_rows = []
    removed_count = 0
    replaced_count = 0
    removed_words = []
    replaced_words = []

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            # Always keep header row
            if reader.line_num == 1:
                new_rows.append(row)
                continue

            # Skip empty rows
            if not row or len(row) < 2:
                continue

            german_word = row[0].strip()

            # Check if this word should be removed
            if german_word in words_to_remove:
                print(f"  Removing: '{german_word}' -> '{row[1]}'")
                removed_words.append(f"{german_word} -> {row[1]}")
                removed_count += 1
                continue

            # Check if this word should be replaced
            if german_word in replacements:
                old_word = german_word
                row[0] = replacements[german_word]
                print(f"  Replacing: '{old_word}' -> '{row[0]}' (meaning: {row[1]})")
                replaced_words.append(f"{old_word} -> {row[0]}")
                replaced_count += 1

            new_rows.append(row)

    # Write the cleaned file
    with open(file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(new_rows)

    return {
        'removed': removed_count,
        'replaced': replaced_count,
        'removed_words': removed_words,
        'replaced_words': replaced_words
    }

def main():
    """Main function to clean all vocabulary files."""
    data_dir = "/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data"
    files_to_clean = [
        "A1_vokabeln.csv",
        "A2_vokabeln.csv",
        "B1_vokabeln.csv"
    ]

    print("CLEANING GERMAN VOCABULARY FILES")
    print("=" * 50)
    print("Removing inappropriate entries based on vocabulary analysis")
    print("=" * 50)
    print()

    total_removed = 0
    total_replaced = 0
    all_removed_words = []
    all_replaced_words = []

    for filename in files_to_clean:
        file_path = os.path.join(data_dir, filename)
        print(f"Cleaning {filename}...")

        try:
            results = clean_vocabulary_file(file_path)
            removed = results.get('removed', 0)
            replaced = results.get('replaced', 0)

            print(f"  Removed {removed} inappropriate entries")
            print(f"  Replaced {replaced} colloquial terms")

            total_removed += removed
            total_replaced += replaced
            all_removed_words.extend(results.get('removed_words', []))
            all_replaced_words.extend(results.get('replaced_words', []))

        except Exception as e:
            print(f"Error processing {filename}: {e}")

        print()

    # Summary report
    print("=" * 50)
    print("CLEANING SUMMARY")
    print("=" * 50)
    print(f"Total entries removed: {total_removed}")
    print(f"Total terms replaced: {total_replaced}")
    print()

    if all_removed_words:
        print("REMOVED ENTRIES:")
        print("(These were inappropriate for vocabulary learning)")
        for word in all_removed_words:
            print(f"  - {word}")
        print()

    if all_replaced_words:
        print("REPLACED ENTRIES:")
        print("(Colloquial terms replaced with standard German)")
        for word in all_replaced_words:
            print(f"  - {word}")
        print()

    print("NOTES:")
    print("- Backup files (.violations_backup) have been created")
    print("- B2_vokabeln.csv was empty, no cleaning needed")
    print("- C1_vokabeln.csv requires manual review due to complexity")
    print("- Technical terms in B1 should be moved to advanced vocabulary")
    print("- See vocabulary_violations_report.md for complete analysis")
    print()
    print("NEXT STEPS:")
    print("1. Review the cleaned files")
    print("2. Consider creating specialized vocabulary lists for:")
    print("   - Technical/professional terms")
    print("   - Academic field terms")
    print("   - Numbers and counting")
    print("   - Geography and place names")

if __name__ == "__main__":
    main()