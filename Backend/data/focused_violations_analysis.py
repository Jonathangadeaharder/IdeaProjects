#!/usr/bin/env python3
"""
Focused analysis of German vocabulary CSV files for inappropriate entries.
This version excludes the false positive "likely_proper_noun" violations
since all German nouns are capitalized.
"""

import csv
import re
import os
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass

@dataclass
class Violation:
    file_name: str
    line_number: int
    german_word: str
    spanish_translation: str
    violation_type: str
    reason: str
    suggested_action: str

class FocusedVocabularyAnalyzer:
    def __init__(self):
        # Known proper names (personal names) - these should be detected more carefully
        self.personal_names = {
            'abby', 'adams', 'aeryn', 'alex', 'alexander', 'andrea', 'anna',
            'barbara', 'christian', 'frank', 'hans', 'klaus', 'maria',
            'michael', 'peter', 'thomas', 'wolfgang', 'dad', 'mom', 'mama', 'papa'
        }

        # Known place names
        self.place_names = {
            'afrika', 'amerika', 'australien', 'europa', 'asien',
            'berlin', 'münchen', 'hamburg', 'köln', 'frankfurt', 'stuttgart',
            'düsseldorf', 'dortmund', 'essen', 'leipzig', 'bremen', 'dresden',
            'deutschland', 'österreich', 'schweiz', 'bayern'
        }

        # Known brand names
        self.brand_names = {
            'mercedes', 'bmw', 'audi', 'volkswagen', 'porsche', 'adidas', 'nike',
            'coca-cola', 'pepsi', 'mcdonald', 'burger king', 'apple', 'samsung',
            'google', 'facebook', 'amazon', 'microsoft', 'sony', 'toyota'
        }

        # Acronyms/abbreviations that shouldn't be in vocabulary lists
        self.acronyms = {
            'usa', 'eu', 'nato', 'uno', 'who', 'unesco', 'fbi', 'cia', 'nasa',
            'dvd', 'cd', 'tv', 'pc', 'it', 'lkw', 'pkw'
        }

        # Interjections and sounds
        self.interjections = {
            'äh', 'ähm', 'hmm', 'hm', 'oh', 'ah', 'ahh', 'wow', 'hey', 'hallo',
            'tschüss', 'tschüs', 'okay', 'ok', 'na', 'naja', 'tja', 'ach'
        }

        # Technical terms that are too specialized for basic language learning
        self.technical_terms = {
            'cyberangriff', 'automatisierung', 'digitalisierung', 'atomkraftwerk',
            'atommeiler', 'atombombe', 'atomenergie', 'bakterium', 'blutzuckerspiegel',
            'computerspielsucht', 'datenverarbeitung', 'datensicherheit',
            'diskriminierung', 'forschungseinrichtung', 'fingerspitzengefühl',
            'arbeitgeber', 'arbeitnehmer', 'arbeitsmarkt', 'arbeitsrechtler'
        }

        # Colloquial/slang terms
        self.colloquial_terms = {
            'cool', 'super', 'toll', 'boss', 'quatsch', 'mist', 'blöd', 'doof'
        }

        # English loanwords that are clearly just English
        self.english_loanwords = {
            'sorry', 'deal', 'captain', 'major', 'sir', 'madam', "ma'am", 'lord',
            'mr', 'mrs', 'blog', 'comic', 'show', 'team', 'fan',
            'festival', 'hamburger', 'pizza', 'laptop', 'container',
            'basketball', 'tennis', 'volleyball', 'club'
        }

        # Number words (unless specifically for teaching numbers)
        self.number_words = {
            'null', 'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben',
            'acht', 'neun', 'zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn',
            'fünfzehn', 'sechzehn', 'siebzehn', 'achtzehn', 'neunzehn', 'zwanzig'
        }

        # Academic field terms
        self.academic_terms = {
            'erziehungswissenschaft', 'ingenieurwissenschaft', 'naturwissenschaft',
            'politikwissenschaft', 'sozialwissenschaft', 'rechtswissenschaft'
        }

    def analyze_word(self, german_word: str, spanish_translation: str) -> List[str]:
        """Analyze a word and return list of violation types."""
        violations = []
        word_lower = german_word.lower().strip()

        # Skip empty or very short entries
        if len(word_lower) < 2:
            return violations

        # Check for personal names
        if word_lower in self.personal_names:
            violations.append("personal_name")

        # Check for place names
        if word_lower in self.place_names:
            violations.append("place_name")

        # Check for brand names
        if word_lower in self.brand_names:
            violations.append("brand_name")

        # Check for acronyms/abbreviations
        if word_lower in self.acronyms:
            violations.append("acronym")

        # Check for all-caps abbreviations (but not common prepositions)
        if (len(german_word) >= 2 and german_word.isupper() and
            word_lower not in ['an', 'auf', 'in', 'zu', 'um', 'von', 'mit', 'bei']):
            violations.append("acronym_caps")

        # Check for interjections
        if word_lower in self.interjections:
            violations.append("interjection")

        # Check for technical terms
        if word_lower in self.technical_terms:
            violations.append("technical_term")

        # Check for colloquial terms
        if word_lower in self.colloquial_terms:
            violations.append("colloquial")

        # Check for English loanwords
        if word_lower in self.english_loanwords:
            violations.append("english_loanword")

        # Check for number words
        if word_lower in self.number_words:
            violations.append("number_word")

        # Check for academic terms
        if word_lower in self.academic_terms:
            violations.append("academic_term")

        # Check for overly technical suffixes
        if word_lower.endswith('ierung') and len(word_lower) > 10:
            violations.append("technical_suffix")

        # Check for very complex compound words (more than 2 hyphens)
        if german_word.count('-') > 2:
            violations.append("complex_compound")

        return violations

    def get_violation_details(self, violation_type: str) -> Tuple[str, str]:
        """Get reason and suggested action for a violation type."""
        details = {
            "personal_name": ("Personal name - not appropriate for vocabulary learning", "Remove - personal names aren't general vocabulary"),
            "place_name": ("Place name - too specific for general vocabulary", "Remove or move to geography-specific lesson"),
            "brand_name": ("Brand/company name - not general vocabulary", "Remove - brand names aren't vocabulary"),
            "acronym": ("Acronym/abbreviation - not suitable for vocabulary learning", "Remove or expand to full form"),
            "acronym_caps": ("All-caps abbreviation - likely acronym", "Review - expand to full form or remove"),
            "interjection": ("Interjection/sound - not proper vocabulary", "Remove - interjections aren't structured vocabulary"),
            "technical_term": ("Overly technical/specialized term", "Remove or move to advanced/technical vocabulary"),
            "colloquial": ("Too colloquial/slang for structured learning", "Replace with standard German equivalent"),
            "english_loanword": ("English loanword - not native German vocabulary", "Remove or replace with German equivalent"),
            "number_word": ("Number word - should be in dedicated numbers lesson", "Move to numbers-specific vocabulary"),
            "academic_term": ("Academic field term", "Move to academic/professional vocabulary"),
            "technical_suffix": ("Technical suffix suggests specialized term", "Review for appropriateness at this level"),
            "complex_compound": ("Overly complex compound word", "Consider simpler alternatives")
        }
        return details.get(violation_type, ("Unknown violation", "Review entry"))

    def analyze_file(self, file_path: str) -> List[Violation]:
        """Analyze a single CSV file for violations."""
        violations = []

        if not os.path.exists(file_path):
            return violations

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                content = csvfile.read()
                if not content.strip():
                    return violations

                csvfile.seek(0)
                reader = csv.reader(csvfile)

                for line_num, row in enumerate(reader, 1):
                    if line_num == 1:  # Skip header
                        continue

                    if not row or len(row) < 2:  # Skip empty rows
                        continue

                    german_word = row[0].strip()
                    spanish_translation = row[1].strip() if len(row) > 1 else ""

                    if not german_word:  # Skip empty entries
                        continue

                    violation_types = self.analyze_word(german_word, spanish_translation)

                    for violation_type in violation_types:
                        reason, suggested_action = self.get_violation_details(violation_type)

                        violation = Violation(
                            file_name=os.path.basename(file_path),
                            line_number=line_num,
                            german_word=german_word,
                            spanish_translation=spanish_translation,
                            violation_type=violation_type,
                            reason=reason,
                            suggested_action=suggested_action
                        )
                        violations.append(violation)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return violations

def main():
    """Main analysis function."""
    data_dir = "/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data"
    files_to_analyze = [
        "A1_vokabeln.csv",
        "A2_vokabeln.csv",
        "B1_vokabeln.csv",
        "B2_vokabeln.csv",
        "C1_vokabeln.csv"
    ]

    analyzer = FocusedVocabularyAnalyzer()
    all_violations = []

    print("FOCUSED German Vocabulary Analysis Report")
    print("=" * 60)
    print("This analysis focuses on genuine vocabulary violations,")
    print("excluding false positives for normal German noun capitalization.")
    print("=" * 60)
    print()

    for filename in files_to_analyze:
        file_path = os.path.join(data_dir, filename)
        print(f"Analyzing {filename}...")

        violations = analyzer.analyze_file(file_path)
        all_violations.extend(violations)

        if violations:
            print(f"Found {len(violations)} genuine violations in {filename}")
        else:
            print(f"No violations found in {filename}")
        print()

    # Group violations by file and type
    violations_by_file = {}
    for violation in all_violations:
        if violation.file_name not in violations_by_file:
            violations_by_file[violation.file_name] = {}

        vtype = violation.violation_type
        if vtype not in violations_by_file[violation.file_name]:
            violations_by_file[violation.file_name][vtype] = []

        violations_by_file[violation.file_name][vtype].append(violation)

    # Report detailed results
    print("\nDETAILED VIOLATIONS REPORT")
    print("=" * 50)

    total_violations = 0
    for filename in files_to_analyze:
        file_violations = violations_by_file.get(filename, {})
        file_total = sum(len(vlist) for vlist in file_violations.values())
        total_violations += file_total

        print(f"\n{filename}: {file_total} violations")
        print("-" * 40)

        if file_violations:
            for vtype, vlist in file_violations.items():
                print(f"\n  {vtype.upper().replace('_', ' ')}: {len(vlist)} violations")

                # Show all violations for this type (since we're focusing on genuine issues)
                for v in vlist:
                    print(f"    Line {v.line_number}: '{v.german_word}' -> '{v.spanish_translation}'")

                print(f"    Reason: {vlist[0].reason}")
                print(f"    Suggested Action: {vlist[0].suggested_action}")
        else:
            print("  No violations found")

    # Summary statistics
    print("\n\nSUMMARY STATISTICS")
    print("=" * 30)
    print(f"Total genuine violations found: {total_violations}")

    # Count by violation type across all files
    violation_type_counts = {}
    for violation in all_violations:
        vtype = violation.violation_type
        violation_type_counts[vtype] = violation_type_counts.get(vtype, 0) + 1

    print("\nViolations by type:")
    for vtype, count in sorted(violation_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {vtype.replace('_', ' ')}: {count}")

    print(f"\nFiles analyzed: {len(files_to_analyze)}")
    print(f"Files with violations: {len([f for f in violations_by_file.keys() if violations_by_file[f]])}")

    # Provide recommendations
    print("\n\nRECOMMENDations FOR CLEANUP")
    print("=" * 30)
    print("1. Remove all personal names - they don't belong in vocabulary lists")
    print("2. Remove interjections and sounds - focus on structured vocabulary")
    print("3. Replace colloquial terms with standard German equivalents")
    print("4. Move technical terms to advanced/specialized vocabulary sections")
    print("5. Replace English loanwords with proper German equivalents where possible")
    print("6. Move number words to a dedicated numbers lesson")
    print("7. Expand or remove acronyms/abbreviations")

if __name__ == "__main__":
    main()