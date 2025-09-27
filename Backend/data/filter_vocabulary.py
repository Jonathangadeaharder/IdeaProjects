#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter script to remove words from 10K_csv.csv that already exist in A1, A2, or B1 vocabulary files.
"""

import csv
import os
from pathlib import Path

def load_vocabulary_from_csv(file_path):
    """Load German words from a CSV file with format 'Deutsch_grundform,spanisch_grundform'"""
    vocabulary = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            # Skip header
            next(csv_reader, None)
            
            for row in csv_reader:
                if row and len(row) >= 1:
                    german_word = row[0].strip().lower()
                    if german_word:
                        vocabulary.add(german_word)
        
        print(f"Loaded {len(vocabulary)} words from {file_path}")
        return vocabulary
    
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
        return set()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return set()

def load_10k_words(file_path):
    """Load words from 10K_csv.csv (one word per line)"""
    words = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                word = line.strip().lower()
                if word:
                    words.append(word)
        
        print(f"Loaded {len(words)} words from {file_path}")
        return words
    
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def filter_words(words_10k, existing_vocabulary):
    """Filter out words that exist in the existing vocabulary and remove numbers"""
    filtered_words = []
    removed_count = 0
    
    for word in words_10k:
        # Skip if word exists in existing vocabulary
        if word in existing_vocabulary:
            removed_count += 1
            continue
            
        # Skip if word is purely numeric
        if word.isdigit():
            removed_count += 1
            continue
            
        # Skip if word contains only numbers and special characters (no letters)
        if not any(c.isalpha() for c in word):
            removed_count += 1
            continue
            
        filtered_words.append(word)
    
    return filtered_words, removed_count

def main():
    # Define file paths
    data_dir = Path(__file__).parent
    a1_file = data_dir / "A1_vokabeln.csv"
    a2_file = data_dir / "A2_vokabeln.csv"
    b1_file = data_dir / "B1_vokabeln.csv"
    input_10k_file = data_dir / "10K_csv.csv"
    output_file = data_dir / "10K_csv_filtered.csv"
    
    print("Starting vocabulary filtering process...")
    print("=" * 50)
    
    # Load existing vocabulary from A1, A2, B1 files
    print("Loading existing vocabulary...")
    a1_vocab = load_vocabulary_from_csv(a1_file)
    a2_vocab = load_vocabulary_from_csv(a2_file)
    b1_vocab = load_vocabulary_from_csv(b1_file)
    
    # Combine all existing vocabulary
    existing_vocabulary = a1_vocab.union(a2_vocab).union(b1_vocab)
    print(f"Total unique words in A1+A2+B1: {len(existing_vocabulary)}")
    
    # Load 10K words
    print("\nLoading 10K word list...")
    words_10k = load_10k_words(input_10k_file)
    
    # Filter out existing words
    print("\nFiltering words...")
    filtered_words, removed_count = filter_words(words_10k, existing_vocabulary)
    
    # Save filtered results
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            for word in filtered_words:
                file.write(word + '\n')
        
        print(f"\nFiltering complete!")
        print(f"Original words: {len(words_10k)}")
        print(f"Words removed: {removed_count}")
        print(f"Words remaining: {len(filtered_words)}")
        print(f"Filtered words saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving filtered words: {e}")

if __name__ == "__main__":
    main()
