#!/usr/bin/env python3
import csv
from collections import Counter

def load_words_from_file(filepath):
    """Load German words from a CSV file, returning a list of words."""
    words = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row:  # Make sure row is not empty
                german_word = row[0]  # First column is German word
                words.append(german_word)
    return words

def find_duplicates_within_file(filepath, filename):
    """Find duplicate words within a single file."""
    words = load_words_from_file(filepath)
    word_counts = Counter(words)
    duplicates = {word: count for word, count in word_counts.items() if count > 1}
    
    print(f"\nDuplicates within {filename}:")
    if duplicates:
        for word, count in duplicates.items():
            print(f"  {word}: appears {count} times")
    else:
        print("  No duplicates found")
    
    return duplicates

def compare_levels(level1_file, level2_file, level1_name, level2_name):
    """Find words that appear in both levels (cross-level redundancy)."""
    level1_words = set(load_words_from_file(level1_file))
    level2_words = set(load_words_from_file(level2_file))
    
    redundancies = level1_words.intersection(level2_words)
    
    print(f"\nCross-level redundancy between {level1_name} and {level2_name}: {len(redundancies)} words")
    if redundancies:
        sorted_redundancies = sorted(redundancies)
        if len(sorted_redundancies) > 20:  # Limit output for readability
            for word in sorted_redundancies[:20]:
                print(f"  {word}")
            print(f"  ... and {len(sorted_redundancies) - 20} more")
        else:
            for word in sorted_redundancies:
                print(f"  {word}")
    else:
        print("  No redundancy found")
    
    return redundancies

def main():
    base_path = "/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/"
    
    files = {
        "A1": base_path + "A1_vokabeln.csv",
        "A2": base_path + "A2_vokabeln.csv", 
        "B1": base_path + "B1_vokabeln.csv",  # Using the original B1 file
        "B2": base_path + "B2_vokabeln.csv"
    }
    
    print("=== ANALYSIS OF DUPLICATIONS AND REDUNDANCIES ===")
    
    # Find duplicates within each file
    print("\n" + "="*50)
    print("WITHIN-FILE DUPLICATES:")
    print("="*50)
    for name, path in files.items():
        find_duplicates_within_file(path, name)
    
    # Find redundancies between levels
    print("\n" + "="*50)
    print("CROSS-LEVEL REDUNDANCIES:")
    print("="*50)
    
    # A1 vs others
    compare_levels(files["A1"], files["A2"], "A1", "A2")
    compare_levels(files["A1"], files["B1"], "A1", "B1")
    compare_levels(files["A1"], files["B2"], "A1", "B2")
    
    # A2 vs others
    compare_levels(files["A2"], files["B1"], "A2", "B1")
    compare_levels(files["A2"], files["B2"], "A2", "B2")
    
    # B1 vs B2
    compare_levels(files["B1"], files["B2"], "B1", "B2")

if __name__ == '__main__':
    main()