#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
German Vocabulary Base Form Analysis
Analyzes CSV files to find German words that are NOT in their base forms (lemma/Grundform)
"""

import csv
import re
from typing import List, Dict, Tuple, Set
from pathlib import Path

class GermanBaseFormAnalyzer:
    def __init__(self):
        # Common German verb conjugations that should be infinitives
        self.verb_conjugation_patterns = {
            # Past tense patterns
            r'(.*)(te|st|ten|tet)$': 'conjugated_verb_past',  # machte -> machen
            r'(.*)(ete|est|eten|etet)$': 'conjugated_verb_past',  # arbeitete -> arbeiten

            # Present tense patterns (excluding infinitives ending in -en, -ern, -eln)
            r'^(.+[^e][^r][^n])t$': 'conjugated_verb_present',  # macht -> machen (but not "Amt")
            r'^(.+)st$': 'conjugated_verb_present',  # machst -> machen
            r'^(.+[^e][^r][^n])en$': 'possible_plural_or_infinitive',  # could be plural or infinitive
        }

        # Common noun plural patterns
        self.noun_plural_patterns = {
            r'^(.+)er$': 'plural_noun',  # Häuser -> Haus, Männer -> Mann
            r'^(.+)en$': 'plural_noun',  # Frauen -> Frau, Katzen -> Katze
            r'^(.+)s$': 'plural_noun',   # Autos -> Auto, Hotels -> Hotel
            r'^(.+)e$': 'plural_noun',   # Hunde -> Hund, Tische -> Tisch
        }

        # Adjective declension patterns
        self.adjective_patterns = {
            r'^(.+)e$': 'declined_adjective',      # große -> groß, schöne -> schön
            r'^(.+)en$': 'declined_adjective',     # großen -> groß, schönen -> schön
            r'^(.+)er$': 'declined_adjective',     # großer -> groß, schöner -> schön
            r'^(.+)es$': 'declined_adjective',     # großes -> groß, schönes -> schön
            r'^(.+)em$': 'declined_adjective',     # großem -> groß, schönem -> schön
        }

        # Comparative/superlative patterns
        self.comparison_patterns = {
            r'^(.+)er$': 'comparative',            # größer -> groß
            r'^(.+)ste?$': 'superlative',         # größte/größte -> groß
        }

        # Past participle patterns (when used as adjectives)
        self.participle_patterns = {
            r'^ge(.+)t$': 'past_participle',       # gemacht -> machen
            r'^ge(.+)en$': 'past_participle',      # gegangen -> gehen
            r'^(.+)t$': 'past_participle',         # verkauft -> verkaufen
        }

        # Known exceptions (words that look like they violate rules but are actually correct)
        self.exceptions = {
            # Words ending in -er that are correct base forms
            'Aber', 'Ander', 'Wasser', 'Vater', 'Mutter', 'Lehrer', 'Fahrer', 'Verkäufer',
            'Arbeiter', 'Computer', 'Hamburger', 'Finger', 'Winter', 'Sommer', 'Bruder',
            'Schwester', 'Besucher', 'Kunde', 'Meter', 'Liter', 'Kilometer', 'Zentimeter',
            'Theater', 'Wetter', 'Peter', 'Dieter', 'Alexander', 'Oliver', 'Philipp',
            'Vermieter', 'Anbieter', 'Empfänger', 'Absender', 'Sprecher', 'Hörer',

            # Words ending in -e that are correct base forms
            'Blume', 'Katze', 'Straße', 'Kirche', 'Schule', 'Lampe', 'Tasse', 'Flasche',
            'Tasche', 'Brücke', 'Küche', 'Ecke', 'Liebe', 'Farbe', 'Seite', 'Reise',
            'Karte', 'Torte', 'Sahne', 'Schere', 'Garage', 'Orange', 'Minute',

            # Words ending in -en that are infinitives (correct base forms)
            'Machen', 'Gehen', 'Kommen', 'Haben', 'Sein', 'Werden', 'Können', 'Müssen',
            'Sollen', 'Wollen', 'Dürfen', 'Mögen', 'Wissen', 'Sehen', 'Hören', 'Sprechen',
            'Verstehen', 'Lernen', 'Arbeiten', 'Spielen', 'Essen', 'Trinken', 'Schlafen',

            # Other exceptions
            'Best', 'Test', 'Rest', 'West', 'Ost', 'Nord', 'Süd', 'Text', 'Fest',
            'Ernst', 'August', 'Herbst', 'Frost', 'Durst', 'Verlust', 'Kunst',
        }

        # Common base form corrections
        self.corrections = {
            # Verb conjugations to infinitives
            'machte': 'machen', 'ging': 'gehen', 'kam': 'kommen', 'war': 'sein',
            'hatte': 'haben', 'wurde': 'werden', 'konnte': 'können', 'musste': 'müssen',
            'sollte': 'sollen', 'wollte': 'wollen', 'durfte': 'dürfen', 'mochte': 'mögen',
            'wusste': 'wissen', 'sah': 'sehen', 'hörte': 'hören', 'sprach': 'sprechen',

            # Common plural nouns to singular
            'Häuser': 'Haus', 'Männer': 'Mann', 'Frauen': 'Frau', 'Kinder': 'Kind',
            'Bücher': 'Buch', 'Tiere': 'Tier', 'Autos': 'Auto', 'Hotels': 'Hotel',
            'Blumen': 'Blume', 'Katzen': 'Katze', 'Hunde': 'Hund', 'Tische': 'Tisch',

            # Declined adjectives to base form
            'große': 'groß', 'schöne': 'schön', 'gute': 'gut', 'neue': 'neu',
            'große': 'groß', 'kleinen': 'klein', 'alten': 'alt', 'jungen': 'jung',

            # Comparatives/superlatives
            'größer': 'groß', 'größte': 'groß', 'schöner': 'schön', 'schönste': 'schön',
            'besser': 'gut', 'beste': 'gut', 'mehr': 'viel', 'meisten': 'viel',
        }

    def analyze_word(self, word: str) -> Tuple[bool, str, str]:
        """
        Analyze if a German word is in its base form.
        Returns: (is_violation, violation_type, suggested_correction)
        """
        if not word or len(word) < 2:
            return False, "", ""

        # Skip if word is in exceptions
        if word in self.exceptions:
            return False, "", ""

        # Check if we have a known correction
        if word in self.corrections:
            return True, "known_violation", self.corrections[word]

        # Check verb conjugation patterns
        for pattern, violation_type in self.verb_conjugation_patterns.items():
            if re.match(pattern, word, re.IGNORECASE):
                if violation_type == 'conjugated_verb_past':
                    # Try to construct infinitive
                    base = re.sub(r'(te|st|ten|tet|ete|est|eten|etet)$', 'en', word)
                    if base != word:
                        return True, violation_type, base
                elif violation_type == 'conjugated_verb_present':
                    # For present tense, add -en to root
                    if word.endswith('t') and len(word) > 3:
                        base = word[:-1] + 'en'
                        return True, violation_type, base
                    elif word.endswith('st'):
                        base = word[:-2] + 'en'
                        return True, violation_type, base

        # Check noun plural patterns (be careful with false positives)
        if len(word) > 4:  # Only check longer words to avoid false positives
            for pattern, violation_type in self.noun_plural_patterns.items():
                if re.match(pattern, word):
                    if word.endswith('er') and word not in self.exceptions:
                        # Common plural endings like Häuser -> Haus
                        if word.endswith('äuser'):
                            base = word[:-5] + 'aus'
                            return True, violation_type, base
                        elif word.endswith('änner'):
                            base = word[:-5] + 'ann'
                            return True, violation_type, base
                    elif word.endswith('en') and not word.lower().endswith(('hen', 'gen', 'ken', 'sen', 'ten', 'nen', 'ren', 'len', 'ien')):
                        # Check if it could be a plural
                        if word.endswith('ien'):
                            base = word[:-2]
                            return True, violation_type, base
                        elif word.endswith('en') and len(word) > 4:
                            base = word[:-2]
                            return True, violation_type, base

        # Check adjective patterns
        for pattern, violation_type in self.adjective_patterns.items():
            if re.match(pattern, word):
                if word.endswith('e') and len(word) > 4:
                    # große -> groß, schöne -> schön
                    if word.endswith('ße'):
                        continue  # Words ending in ß+e are often correct
                    base = word[:-1]
                    # Add umlaut removal logic for common cases
                    if 'ö' in base:
                        base = base.replace('ö', 'o')
                    if 'ä' in base:
                        base = base.replace('ä', 'a')
                    if 'ü' in base:
                        base = base.replace('ü', 'u')
                    return True, violation_type, base

        # Check comparative/superlative
        for pattern, violation_type in self.comparison_patterns.items():
            if re.match(pattern, word):
                if word.endswith('er') and len(word) > 5:
                    base = word[:-2]
                    # Remove umlauts for comparatives
                    base = base.replace('ö', 'o').replace('ä', 'a').replace('ü', 'u')
                    return True, violation_type, base
                elif word.endswith('ste') or word.endswith('st'):
                    base = word[:-3] if word.endswith('ste') else word[:-2]
                    base = base.replace('ö', 'o').replace('ä', 'a').replace('ü', 'u')
                    return True, violation_type, base

        return False, "", ""

    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a CSV file for German base form violations."""
        violations = []

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return violations

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Skip header

                for line_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is line 1)
                    if not row or len(row) < 1:
                        continue

                    german_word = row[0].strip()
                    spanish_translation = row[1].strip() if len(row) > 1 else ""

                    if not german_word:
                        continue

                    # Handle multi-word phrases (analyze each word)
                    words = german_word.split()
                    for word_idx, word in enumerate(words):
                        # Remove punctuation
                        clean_word = re.sub(r'[^\w\-äöüÄÖÜß]', '', word)
                        if not clean_word or len(clean_word) < 2:
                            continue

                        # Skip proper names (capitalized words that don't start sentences)
                        if clean_word[0].isupper() and len(clean_word) > 1 and clean_word not in ['AN', 'AUF', 'IN', 'UM', 'VON', 'ZU']:
                            if not clean_word.isupper():  # Skip unless all caps (likely abbreviation)
                                continue

                        is_violation, violation_type, suggested_correction = self.analyze_word(clean_word)

                        if is_violation:
                            violations.append({
                                'file': file_path.name,
                                'line': line_num,
                                'full_entry': german_word,
                                'word': clean_word,
                                'word_position': word_idx + 1 if len(words) > 1 else None,
                                'violation_type': violation_type,
                                'suggested_correction': suggested_correction,
                                'spanish_translation': spanish_translation
                            })

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return violations

    def generate_report(self, all_violations: Dict[str, List[Dict]]) -> str:
        """Generate a comprehensive report of all violations."""
        report = []
        report.append("=" * 80)
        report.append("GERMAN VOCABULARY BASE FORM ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        total_violations = sum(len(violations) for violations in all_violations.values())
        report.append(f"SUMMARY: Found {total_violations} potential base form violations across {len(all_violations)} files")
        report.append("")

        # Summary by violation type
        violation_types = {}
        for file_violations in all_violations.values():
            for violation in file_violations:
                vtype = violation['violation_type']
                violation_types[vtype] = violation_types.get(vtype, 0) + 1

        if violation_types:
            report.append("VIOLATIONS BY TYPE:")
            for vtype, count in sorted(violation_types.items()):
                report.append(f"  - {vtype}: {count} cases")
            report.append("")

        # Detailed results by file
        for filename, violations in all_violations.items():
            if not violations:
                report.append(f"FILE: {filename}")
                report.append("  ✓ No base form violations found")
                report.append("")
                continue

            report.append(f"FILE: {filename} ({len(violations)} violations)")
            report.append("-" * 50)

            # Group by violation type for better readability
            violations_by_type = {}
            for violation in violations:
                vtype = violation['violation_type']
                if vtype not in violations_by_type:
                    violations_by_type[vtype] = []
                violations_by_type[vtype].append(violation)

            for vtype, type_violations in sorted(violations_by_type.items()):
                report.append(f"\n{vtype.upper().replace('_', ' ')} ({len(type_violations)} cases):")

                for violation in type_violations:
                    line_info = f"Line {violation['line']}"
                    if violation['word_position']:
                        line_info += f", word {violation['word_position']}"

                    report.append(f"  {line_info}: '{violation['word']}' → '{violation['suggested_correction']}'")
                    if violation['full_entry'] != violation['word']:
                        report.append(f"    Full entry: \"{violation['full_entry']}\"")
                    if violation['spanish_translation']:
                        report.append(f"    Spanish: {violation['spanish_translation']}")
                    report.append("")

            report.append("")

        return "\n".join(report)

def main():
    """Main analysis function."""
    analyzer = GermanBaseFormAnalyzer()

    # Files to analyze
    data_dir = Path('.')
    csv_files = [
        'A1_vokabeln.csv',
        'A2_vokabeln.csv',
        'B1_vokabeln.csv',
        'B2_vokabeln.csv',
        'C1_vokabeln.csv'
    ]

    all_violations = {}

    print("Analyzing German vocabulary files for base form violations...")
    print("=" * 60)

    for filename in csv_files:
        file_path = data_dir / filename
        print(f"Analyzing {filename}...")

        violations = analyzer.analyze_file(file_path)
        all_violations[filename] = violations

        print(f"  Found {len(violations)} potential violations")

    print("=" * 60)
    print(f"Analysis complete. Total violations found: {sum(len(v) for v in all_violations.values())}")

    # Generate and save report
    report = analyzer.generate_report(all_violations)

    # Save to file
    with open('base_form_violations_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    print("\nDetailed report saved to: base_form_violations_report.txt")

    # Also print report to console
    print("\n" + report)

if __name__ == '__main__':
    main()