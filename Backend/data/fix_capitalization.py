#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
German Vocabulary Capitalization Fixer
Applies comprehensive German grammar rules for capitalization across vocabulary files.

German Capitalization Rules:
1. Nouns are always capitalized (der Hund, das Haus, die Frau)
2. Verbs are lowercase (gehen, laufen, arbeiten)
3. Adjectives are lowercase (schön, groß, alt)
4. Compound words follow their primary component's rule

Common patterns to fix:
- Verbs incorrectly capitalized: "Arbeiten" → "arbeiten"
- Adjectives incorrectly capitalized: "Alt" → "alt", "Schön" → "schön"
- Nouns incorrectly lowercased: "wasser" → "Wasser"
"""

import csv
import re
from typing import Dict, List, Tuple, Set

class GermanCapitalizationFixer:

    def __init__(self):
        # German verb infinitive patterns
        self.verb_endings = {
            'en', 'ern', 'eln', 'chen', 'sen'  # Common German verb endings
        }

        # Common German verb stems that should be lowercase
        self.common_verbs = {
            'abfahren', 'abgeben', 'abholen', 'anbieten', 'anfangen', 'anklicken',
            'ankommen', 'ankreuzen', 'anmachen', 'anmelden', 'anrufen', 'antworten',
            'anziehen', 'arbeiten', 'aufhören', 'aufstehen', 'aussteigen', 'ausziehen',
            'baden', 'bedeuten', 'beginnen', 'bekommen', 'benutzen', 'besuchen',
            'bezahlen', 'bitten', 'bleiben', 'brauchen', 'bringen', 'danken',
            'dauern', 'duschen', 'einkaufen', 'einladen', 'einsteigen', 'empfehlen',
            'enden', 'entschuldigen', 'erzählen', 'essen', 'fahren', 'feiern',
            'fehlen', 'fernsehen', 'finden', 'fliegen', 'fragen', 'freuen',
            'frühstücken', 'geben', 'gebären', 'gehen', 'gehören', 'gewinnen',
            'glauben', 'gratulieren', 'grillen', 'haben', 'halten', 'heißen',
            'helfen', 'holen', 'hören', 'kaufen', 'kennen', 'kennenlernen',
            'kochen', 'kommen', 'können', 'kosten', 'lachen', 'laufen', 'leben',
            'legen', 'lernen', 'lesen', 'lieben', 'liegen', 'machen', 'mieten',
            'mitbringen', 'mitkommen', 'mitmachen', 'mitnehmen', 'möchten', 'mögen',
            'müssen', 'nehmen', 'öffnen', 'rauchen', 'regnen', 'reisen',
            'reparieren', 'sagen', 'scheinen', 'schicken', 'schlafen', 'schließen',
            'schmecken', 'schreiben', 'schwimmen', 'sehen', 'sein', 'sitzen',
            'spielen', 'sprechen', 'stehen', 'stellen', 'studieren', 'suchen',
            'tanzen', 'telefonieren', 'treffen', 'trinken', 'tun', 'übernachten',
            'überweisen', 'umziehen', 'unterschreiben', 'verkaufen', 'vermieten',
            'verstehen', 'vorstellen', 'wandern', 'warten', 'waschen', 'werden',
            'wiederholen', 'wissen', 'wohnen', 'wollen', 'zahlen', 'zeigen',
            'zurückkommen', 'sterben', 'vergessen', 'verlieren', 'passieren',
            'stimmen', 'weinen', 'überraschen', 'putzen', 'probieren', 'reden',
            'renovieren', 'reservieren', 'sammeln', 'schaffen', 'schenken',
            'schimpfen', 'schneiden', 'schneien', 'setzen', 'singen', 'sparen',
            'spazieren', 'speichern', 'stattfinden', 'sterben', 'stören',
            'streiten', 'surfen', 'teilen', 'teilnehmen', 'tragen', 'trainieren',
            'träumen', 'üben', 'umsteigen', 'unternehmen', 'untersuchen',
            'verabredet', 'verbieten', 'vereinbaren', 'vergleichen', 'verletzen',
            'verlieben', 'verpassen', 'verreisen', 'verschieben', 'versuchen',
            'vorbereiten', 'wählen', 'wechseln', 'wecken', 'wehtun', 'zeichnen',
            'ziehen', 'zuhören', 'zumachen'
        }

        # Common German adjectives that should be lowercase
        self.common_adjectives = {
            'alt', 'ander', 'bekannt', 'besetzt', 'billig', 'bisschen', 'bitter',
            'böse', 'breit', 'deutlich', 'dick', 'dumm', 'dunkel', 'dünn', 'echt',
            'eigen', 'eilig', 'einfach', 'einig', 'einzeln', 'eng', 'erst', 'faul',
            'fantastisch', 'fett', 'fit', 'fleißig', 'freiwillig', 'freundlich',
            'frisch', 'froh', 'früh', 'furchtbar', 'ganz', 'gefährlich', 'genau',
            'genug', 'gering', 'gesund', 'glücklich', 'groß', 'günstig', 'gut',
            'hart', 'hässlich', 'heiß', 'hell', 'hoch', 'intelligent', 'interessant',
            'kalt', 'kaputt', 'klar', 'klein', 'klug', 'komisch', 'kostenlos',
            'kühl', 'kurz', 'lang', 'langsam', 'langweilig', 'laut', 'leer', 'leicht',
            'leise', 'lieb', 'lustig', 'meist', 'müde', 'nass', 'neblig', 'nervös',
            'nett', 'neu', 'normal', 'offen', 'praktisch', 'preiswert', 'privat',
            'reich', 'richtig', 'romantisch', 'ruhig', 'rund', 'sauer', 'scharf',
            'schlimm', 'schmutzig', 'schnell', 'schön', 'schrecklich', 'schwach',
            'schwanger', 'schwer', 'schwierig', 'sicher', 'sonnig', 'spannend',
            'sportlich', 'stark', 'streng', 'stressig', 'süß', 'sympathisch',
            'tief', 'total', 'trocken', 'traurig', 'typisch', 'voll', 'wach',
            'wahr', 'warm', 'weich', 'wichtig', 'windig', 'wirklich', 'witzig',
            'alt', 'jung', 'schön', 'groß', 'schlecht'
        }

        # Words that are definitely nouns (should be capitalized)
        self.definite_nouns = {
            'haus', 'auto', 'kind', 'mann', 'frau', 'tag', 'nacht', 'zeit', 'geld',
            'arbeit', 'schule', 'lehrer', 'student', 'buch', 'tisch', 'stuhl',
            'wasser', 'brot', 'käse', 'fleisch', 'gemüse', 'obst', 'apfel',
            'bier', 'wein', 'kaffee', 'tee', 'milch', 'zucker', 'salz', 'butter',
            'ei', 'fisch', 'fleisch', 'reis', 'kartoffel', 'tomate', 'salat',
            'restaurant', 'hotel', 'flughafen', 'bahnhof', 'bus', 'zug', 'auto',
            'fahrrad', 'straße', 'platz', 'stadt', 'land', 'beruf', 'büro',
            'krankenhaus', 'arzt', 'apotheke', 'bank', 'post', 'polizei',
            'feuerwehr', 'kirche', 'museum', 'theater', 'kino', 'park', 'meer',
            'berg', 'fluss', 'see', 'baum', 'blume', 'tier', 'hund', 'katze',
            'vogel', 'pferd', 'kuh', 'schwein', 'huhn', 'fisch'
        }

    def is_verb(self, word: str) -> bool:
        """Check if word is likely a German verb."""
        word_lower = word.lower()
        return (word_lower in self.common_verbs or
                any(word_lower.endswith(ending) for ending in self.verb_endings))

    def is_adjective(self, word: str) -> bool:
        """Check if word is likely a German adjective."""
        return word.lower() in self.common_adjectives

    def is_noun(self, word: str) -> bool:
        """Check if word is likely a German noun."""
        word_lower = word.lower()
        return (word_lower in self.definite_nouns or
                # Words ending in typical noun suffixes
                any(word_lower.endswith(suffix) for suffix in
                    ['ung', 'heit', 'keit', 'schaft', 'tum', 'nis', 'chen', 'lein', 'er', 'in']))

    def apply_capitalization_rules(self, word: str) -> str:
        """Apply German capitalization rules to a word."""
        if not word or len(word) < 2:
            return word

        # Skip if word contains non-alphabetic characters at the start
        if not word[0].isalpha():
            return word

        word_lower = word.lower()

        # Check if it's a verb (should be lowercase)
        if self.is_verb(word):
            return word_lower

        # Check if it's an adjective (should be lowercase)
        if self.is_adjective(word):
            return word_lower

        # Check if it's definitely a noun (should be capitalized)
        if self.is_noun(word):
            return word_lower.capitalize()

        # Default: if unsure and currently capitalized, likely a noun
        if word[0].isupper() and len(word) > 2:
            # Check if it could be a verb disguised as capitalized
            if word_lower.endswith(('en', 'ern', 'eln')) and word_lower in self.common_verbs:
                return word_lower
            # Otherwise keep as noun (capitalized)
            return word.capitalize()

        # If it's currently lowercase, keep it unless it's a definite noun
        return word

    def fix_file_capitalization(self, file_path: str) -> Tuple[List[str], int]:
        """Fix capitalization in a CSV file and return corrections made."""
        corrections = []
        corrections_count = 0

        # Read the file
        rows = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)

        # Process each row (skip header)
        for i, row in enumerate(rows):
            if i == 0:  # Skip header
                continue

            if len(row) >= 2:
                original_german = row[0]
                corrected_german = self.apply_capitalization_rules(original_german)

                if original_german != corrected_german:
                    corrections.append(f"{original_german} → {corrected_german}")
                    rows[i][0] = corrected_german
                    corrections_count += 1

        # Write back the corrected file
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        return corrections, corrections_count

def main():
    """Main function to fix capitalization across all vocabulary files."""
    fixer = GermanCapitalizationFixer()

    files = [
        '/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/A1_vokabeln.csv',
        '/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/A2_vokabeln.csv',
        '/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/B1_vokabeln.csv',
        '/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/B2_vokabeln.csv',
        '/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/C1_vokabeln.csv'
    ]

    total_corrections = 0
    all_corrections = {}

    for file_path in files:
        file_name = file_path.split('/')[-1]
        print(f"\nProcessing {file_name}...")

        try:
            corrections, count = fixer.fix_file_capitalization(file_path)
            all_corrections[file_name] = corrections
            total_corrections += count
            print(f"Applied {count} corrections to {file_name}")

            # Show first 10 corrections as examples
            if corrections:
                print(f"Examples: {corrections[:10]}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    print(f"\n=== SUMMARY ===")
    print(f"Total corrections applied: {total_corrections}")

    for file_name, corrections in all_corrections.items():
        if corrections:
            print(f"\n{file_name}: {len(corrections)} corrections")
            for correction in corrections[:5]:  # Show first 5 for each file
                print(f"  {correction}")
            if len(corrections) > 5:
                print(f"  ... and {len(corrections) - 5} more")

    print("\n✓ German capitalization corrections completed!")

if __name__ == "__main__":
    main()