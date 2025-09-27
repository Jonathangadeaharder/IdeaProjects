#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
German Capitalization Analysis Tool
Analyzes German vocabulary CSV files for proper capitalization compliance
"""

import csv
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set
import unicodedata

# Common German words categorized by type
COMMON_NOUNS = {
    # Basic nouns that should always be capitalized
    'haus', 'auto', 'hund', 'katze', 'baum', 'buch', 'tisch', 'stuhl', 'bett', 'fenster',
    'tür', 'wasser', 'brot', 'fleisch', 'gemüse', 'obst', 'milch', 'kaffee', 'tee', 'bier',
    'wein', 'geld', 'arbeit', 'beruf', 'schule', 'universität', 'student', 'lehrer', 'arzt',
    'familie', 'vater', 'mutter', 'kind', 'bruder', 'schwester', 'freund', 'mensch', 'frau',
    'mann', 'zeit', 'jahr', 'monat', 'woche', 'tag', 'stadt', 'land', 'welt', 'leben',
    'liebe', 'glück', 'problem', 'lösung', 'beispiel', 'gruppe', 'teil', 'anfang', 'ende',
    'nummer', 'name', 'adresse', 'telefon', 'computer', 'handy', 'internet', 'email',
    'brief', 'paket', 'geschenk', 'preis', 'euro', 'dollar', 'kunde', 'verkäufer',
    'geschäft', 'markt', 'laden', 'restaurant', 'hotel', 'zimmer', 'küche', 'bad',
    'garten', 'park', 'straße', 'weg', 'platz', 'bahnhof', 'flughafen', 'zug',
    'bus', 'fahrrad', 'reise', 'urlaub', 'ferien', 'wetter', 'sonne', 'regen', 'schnee',
    'wind', 'himmel', 'erde', 'berg', 'tal', 'fluss', 'see', 'meer', 'strand', 'wald',
    'tier', 'vogel', 'fisch', 'pferd', 'schwein', 'kuh', 'schaf', 'ziege', 'huhn',
    'essen', 'trinken', 'frühstück', 'mittagessen', 'abendessen', 'hunger', 'durst',
    'gesundheit', 'krankheit', 'medikament', 'krankenhaus', 'zahnarzt', 'apotheke',
    'körper', 'kopf', 'gesicht', 'auge', 'nase', 'mund', 'ohr', 'haar', 'hand', 'fuß',
    'arm', 'bein', 'herz', 'blut', 'haut', 'knochen', 'musik', 'lied', 'instrument',
    'bild', 'foto', 'film', 'fernsehen', 'radio', 'zeitung', 'geschichte',
    'sprache', 'deutsch', 'englisch', 'französisch', 'spanisch', 'italienisch',
    'kleidung', 'hemd', 'hose', 'kleid', 'jacke', 'mantel', 'schuhe', 'socken',
    'sport', 'fußball', 'tennis', 'schwimmen', 'laufen', 'spielen', 'spiel',
    'farbe', 'rot', 'blau', 'grün', 'gelb', 'schwarz', 'weiß', 'braun', 'grau',
    'orange', 'rosa', 'lila', 'silber', 'gold', 'stuhl', 'sessel', 'sofa',
    'schrank', 'regal', 'lampe', 'spiegel', 'uhr', 'kalender', 'blume', 'pflanze'
}

COMMON_VERBS = {
    # Basic verbs that should be lowercase (infinitive form)
    'sein', 'haben', 'werden', 'können', 'müssen', 'sollen', 'wollen', 'dürfen', 'mögen',
    'gehen', 'kommen', 'fahren', 'laufen', 'fliegen', 'schwimmen', 'stehen', 'sitzen',
    'liegen', 'schlafen', 'aufstehen', 'aufwachen', 'essen', 'trinken', 'kochen',
    'kaufen', 'verkaufen', 'bezahlen', 'arbeiten', 'lernen', 'studieren', 'lehren',
    'sprechen', 'sagen', 'fragen', 'antworten', 'hören', 'sehen', 'schauen', 'lesen',
    'schreiben', 'denken', 'verstehen', 'wissen', 'kennen', 'glauben', 'meinen',
    'fühlen', 'lieben', 'hassen', 'mögen', 'helfen', 'geben', 'nehmen', 'bringen',
    'holen', 'suchen', 'finden', 'verlieren', 'gewinnen', 'beginnen', 'aufhören',
    'machen', 'tun', 'öffnen', 'schließen', 'waschen', 'putzen', 'reparieren',
    'bauen', 'kaufen', 'mieten', 'wohnen', 'leben', 'sterben', 'heiraten',
    'scheiden', 'treffen', 'besuchen', 'einladen', 'gratulieren', 'danken',
    'entschuldigen', 'vergessen', 'erinnern', 'hoffen', 'warten', 'passieren',
    'geschehen', 'bedeuten', 'kosten', 'dauern', 'bleiben', 'ändern', 'verbessern',
    'reparieren', 'organisieren', 'planen', 'vorbereiten', 'kontrollieren',
    'telefonieren', 'mailen', 'schicken', 'bekommen', 'erhalten', 'verlassen',
    'ankommen', 'abfahren', 'umsteigen', 'reservieren', 'buchen', 'bestellen',
    'abholen', 'liefern', 'packen', 'auspacken', 'anziehen', 'ausziehen',
    'waschen', 'duschen', 'baden', 'kämmen', 'rasieren', 'schminken'
}

COMMON_ADJECTIVES = {
    # Basic adjectives that should be lowercase
    'gut', 'schlecht', 'schön', 'hässlich', 'groß', 'klein', 'alt', 'jung', 'neu',
    'hoch', 'niedrig', 'lang', 'kurz', 'breit', 'schmal', 'dick', 'dünn',
    'schwer', 'leicht', 'stark', 'schwach', 'schnell', 'langsam', 'früh', 'spät',
    'warm', 'kalt', 'heiß', 'kühl', 'hell', 'dunkel', 'laut', 'leise', 'voll',
    'leer', 'offen', 'geschlossen', 'richtig', 'falsch', 'einfach', 'schwierig',
    'wichtig', 'unwichtig', 'interessant', 'langweilig', 'lustig', 'traurig',
    'glücklich', 'unglücklich', 'gesund', 'krank', 'müde', 'wach', 'hungrig',
    'satt', 'durstig', 'reich', 'arm', 'teuer', 'billig', 'kostenlos', 'frei',
    'besetzt', 'verheiratet', 'ledig', 'geschieden', 'berufstätig', 'arbeitslos',
    'fleißig', 'faul', 'pünktlich', 'unpünktlich', 'höflich', 'unhöflich',
    'freundlich', 'unfreundlich', 'nett', 'gemein', 'ehrlich', 'unehrlich',
    'intelligent', 'dumm', 'klug', 'blöd', 'kreativ', 'langweilig', 'modern',
    'altmodisch', 'praktisch', 'unpraktisch', 'bequem', 'unbequem', 'sauber',
    'schmutzig', 'ordentlich', 'unordentlich', 'ruhig', 'unruhig', 'entspannt',
    'nervös', 'selbstständig', 'unselbstständig', 'bekannt', 'unbekannt',
    'berühmt', 'unberühmt', 'erfolgreich', 'erfolglos', 'zufrieden', 'unzufrieden'
}

def normalize_text(text: str) -> str:
    """Normalize text by removing accents and converting to lowercase for comparison"""
    # Remove accents/diacritics
    normalized = unicodedata.normalize('NFD', text)
    without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return without_accents.lower()

def is_compound_noun(word: str) -> bool:
    """Check if a word is likely a compound noun based on common patterns"""
    word_lower = word.lower()
    # Common compound noun patterns
    compound_patterns = [
        'arbeitsplatz', 'krankenhaus', 'bahnhof', 'flughafen', 'kindergarten',
        'einkaufszentrum', 'parkplatz', 'busstation', 'polizeistation',
        'feuerwehr', 'rathaus', 'stadtpark', 'hauptstraße', 'nebenstraße',
        'wohnzimmer', 'schlafzimmer', 'badezimmer', 'arbeitszimmer',
        'doppelzimmer', 'einzelzimmer', 'hotelzimmer', 'klassenzimmer',
        'briefkasten', 'briefmarke', 'briefträger', 'postleitzahl'
    ]

    # Check for exact matches first
    if word_lower in compound_patterns:
        return True

    # Check for compound endings
    compound_endings = [
        'haus', 'platz', 'straße', 'weg', 'hof', 'markt', 'zentrum', 'stadt',
        'werk', 'fabrik', 'betrieb', 'laden', 'geschäft', 'büro', 'amt',
        'zimmer', 'raum', 'saal', 'halle', 'station', 'bahnhof', 'flughafen'
    ]

    for ending in compound_endings:
        if word_lower.endswith(ending) and len(word_lower) > len(ending):
            return True

    return False

def classify_word_type(word: str) -> str:
    """
    Classify a German word as noun, verb, adjective, or unknown
    Returns the most likely word type based on common patterns
    """
    word_clean = re.sub(r'[^\w\säöüß]', '', word).strip()
    word_lower = word_clean.lower()
    word_normalized = normalize_text(word_clean)

    # Skip empty words or single letters
    if len(word_clean) < 2:
        return 'unknown'

    # Check explicit word lists first
    if word_normalized in {normalize_text(n) for n in COMMON_NOUNS}:
        return 'noun'

    if word_normalized in {normalize_text(v) for v in COMMON_VERBS}:
        return 'verb'

    if word_normalized in {normalize_text(a) for a in COMMON_ADJECTIVES}:
        return 'adjective'

    # Check for compound nouns
    if is_compound_noun(word):
        return 'noun'

    # Pattern-based classification
    # Verb patterns (infinitive forms)
    if word_lower.endswith(('en', 'ern', 'eln')) and len(word_lower) > 3:
        # Exclude nouns that end in -en
        noun_exclusions = ['laden', 'boden', 'ofen', 'regen', 'wagen', 'garten']
        if word_lower not in noun_exclusions:
            return 'verb'

    # Noun patterns (common suffixes)
    noun_suffixes = [
        'ung', 'heit', 'keit', 'schaft', 'tum', 'nis', 'sal', 'sel',
        'er', 'ler', 'ner', 'ter', 'der', 'ger', 'ker', 'mer',
        'in', 'erin', 'lerin', 'nerin', 'terin', 'derin', 'gerin',
        'chen', 'lein', 'el', 'le', 'ie', 'ei', 'erei',
        'tion', 'sion', 'ität', 'ur', 'tur', 'eur', 'anz', 'enz',
        'ment', 'ismus', 'ist', 'ant', 'ent', 'age'
    ]

    if any(word_lower.endswith(suffix) for suffix in noun_suffixes):
        return 'noun'

    # Adjective patterns
    adj_suffixes = [
        'lich', 'ig', 'isch', 'ös', 'al', 'ell', 'iv', 'ar', 'är',
        'bar', 'sam', 'haft', 'los', 'voll', 'reich', 'arm', 'frei',
        'wert', 'würdig', 'fähig', 'mäßig', 'artig'
    ]

    if any(word_lower.endswith(suffix) for suffix in adj_suffixes):
        return 'adjective'

    # If capitalized and not in verb/adjective lists, likely a noun
    if word[0].isupper():
        return 'noun'

    return 'unknown'

def should_be_capitalized(word: str, word_type: str) -> bool:
    """Determine if a word should be capitalized based on German rules"""
    if word_type in ['noun']:
        return True
    elif word_type in ['verb', 'adjective']:
        return False
    else:
        # For unknown words, be conservative - assume nouns should be capitalized
        return word[0].isupper() if word else False

def analyze_capitalization_violations(csv_file: str) -> List[Dict]:
    """Analyze a single CSV file for German capitalization violations"""
    violations = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Skip header
            next(reader, None)

            for line_num, row in enumerate(reader, start=2):
                if not row or len(row) < 2:
                    continue

                german_word = row[0].strip()

                # Skip empty words
                if not german_word:
                    continue

                # Clean the word (remove extra spaces, punctuation for analysis)
                word_for_analysis = re.sub(r'[^\w\säöüß-]', '', german_word).strip()

                # Skip if nothing left after cleaning
                if not word_for_analysis:
                    continue

                # Classify the word type
                word_type = classify_word_type(word_for_analysis)

                # Check if capitalization is correct
                should_capitalize = should_be_capitalized(word_for_analysis, word_type)
                is_capitalized = word_for_analysis[0].isupper() if word_for_analysis else False

                # Determine the violation
                if should_capitalize and not is_capitalized:
                    correct_form = word_for_analysis[0].upper() + word_for_analysis[1:]
                    violations.append({
                        'file': csv_file,
                        'line': line_num,
                        'word': german_word,
                        'word_type': word_type,
                        'violation': 'Should be capitalized',
                        'correct_form': correct_form,
                        'rule': f"{word_type.title()}s must be capitalized"
                    })
                elif not should_capitalize and is_capitalized:
                    correct_form = word_for_analysis[0].lower() + word_for_analysis[1:]
                    violations.append({
                        'file': csv_file,
                        'line': line_num,
                        'word': german_word,
                        'word_type': word_type,
                        'violation': 'Should be lowercase',
                        'correct_form': correct_form,
                        'rule': f"{word_type.title()}s should be lowercase"
                    })

    except FileNotFoundError:
        print(f"File not found: {csv_file}")
    except Exception as e:
        print(f"Error analyzing {csv_file}: {e}")

    return violations

def main():
    """Main function to analyze all German vocabulary files"""
    files_to_analyze = [
        'A1_vokabeln.csv',
        'A2_vokabeln.csv',
        'B1_vokabeln.csv',
        'B2_vokabeln.csv',
        'C1_vokabeln.csv'
    ]

    all_violations = []
    file_stats = {}

    print("=" * 80)
    print("GERMAN CAPITALIZATION ANALYSIS REPORT")
    print("=" * 80)
    print()

    for filename in files_to_analyze:
        filepath = filename
        print(f"Analyzing {filename}...")

        violations = analyze_capitalization_violations(filepath)
        all_violations.extend(violations)
        file_stats[filename] = len(violations)

        if violations:
            print(f"\nFound {len(violations)} capitalization violations in {filename}:")
            print("-" * 60)

            for violation in violations:
                print(f"Line {violation['line']}: '{violation['word']}' -> '{violation['correct_form']}'")
                print(f"  Type: {violation['word_type']}")
                print(f"  Issue: {violation['violation']}")
                print(f"  Rule: {violation['rule']}")
                print()
        else:
            print(f"No capitalization violations found in {filename}")

        print()

    # Summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total_violations = len(all_violations)
    print(f"Total violations found: {total_violations}")
    print()

    print("Violations by file:")
    for filename, count in file_stats.items():
        print(f"  {filename}: {count} violations")
    print()

    if total_violations > 0:
        # Violation type breakdown
        violation_types = {}
        word_types = {}

        for violation in all_violations:
            v_type = violation['violation']
            w_type = violation['word_type']

            violation_types[v_type] = violation_types.get(v_type, 0) + 1
            word_types[w_type] = word_types.get(w_type, 0) + 1

        print("Violations by type:")
        for v_type, count in sorted(violation_types.items()):
            print(f"  {v_type}: {count}")
        print()

        print("Violations by word type:")
        for w_type, count in sorted(word_types.items()):
            print(f"  {w_type}: {count}")
        print()

    return all_violations

if __name__ == '__main__':
    violations = main()