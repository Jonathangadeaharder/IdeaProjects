#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to apply German capitalization corrections to vocabulary CSV files
Based on the analysis results from the capitalization analysis
"""

import csv
import re
from typing import Dict, List, Set

# Critical corrections based on German capitalization rules
# These are high-confidence corrections for common German words

VERB_CORRECTIONS = {
    # Verbs that should be lowercase (infinitive forms)
    'Abfahren': 'abfahren',
    'Abgeben': 'abgeben',
    'Abholen': 'abholen',
    'Anbieten': 'anbieten',
    'Anfangen': 'anfangen',
    'Anklicken': 'anklicken',
    'Ankommen': 'ankommen',
    'Ankreuzen': 'ankreuzen',
    'Anmachen': 'anmachen',
    'Anmelden': 'anmelden',
    'Anrufen': 'anrufen',
    'Antworten': 'antworten',
    'Anziehen': 'anziehen',
    'Arbeiten': 'arbeiten',
    'Aufhören': 'aufhören',
    'Aufstehen': 'aufstehen',
    'Ausfüllen': 'ausfüllen',
    'Ausmachen': 'ausmachen',
    'Aussehen': 'aussehen',
    'Aussteigen': 'aussteigen',
    'Ausziehen': 'ausziehen',
    'Baden': 'baden',
    'Bedeuten': 'bedeuten',
    'Beginnen': 'beginnen',
    'Bekommen': 'bekommen',
    'Benutzen': 'benutzen',
    'Bestellen': 'bestellen',
    'Besuchen': 'besuchen',
    'Bezahlen': 'bezahlen',
    'Bitten': 'bitten',
    'Bleiben': 'bleiben',
    'Brauchen': 'brauchen',
    'Bringen': 'bringen',
    'Danken': 'danken',
    'Dauern': 'dauern',
    'Drucken': 'drucken',
    'Drücken': 'drücken',
    'Dürfen': 'dürfen',
    'Duschen': 'duschen',
    'Einkaufen': 'einkaufen',
    'Einladen': 'einladen',
    'Einsteigen': 'einsteigen',
    'Empfehlen': 'empfehlen',
    'Enden': 'enden',
    'Entschuldigen': 'entschuldigen',
    'Erklären': 'erklären',
    'Erlauben': 'erlauben',
    'Erzählen': 'erzählen',
    'Essen': 'essen',
    'Fahren': 'fahren',
    'Fehlen': 'fehlen',
    'Feiern': 'feiern',
    'Finden': 'finden',
    'Fliegen': 'fliegen',
    'Abfliegen': 'abfliegen',
    'Fragen': 'fragen',
    'Freuen': 'freuen',
    'Frühstücken': 'frühstücken',
    'Geben': 'geben',
    'Gefallen': 'gefallen',
    'Gehen': 'gehen',
    'Gehören': 'gehören',
    'Gewinnen': 'gewinnen',
    'Glauben': 'glauben',
    'Gratulieren': 'gratulieren',
    'Grillen': 'grillen',
    'Haben': 'haben',
    'Halten': 'halten',
    'Heiraten': 'heiraten',
    'Heißen': 'heißen',
    'Helfen': 'helfen',
    'Holen': 'holen',
    'Hören': 'hören',
    'Kaufen': 'kaufen',
    'Kennen': 'kennen',
    'Kennenlernen': 'kennenlernen',
    'Kochen': 'kochen',
    'Kommen': 'kommen',
    'Können': 'können',
    'Kosten': 'kosten',
    'Kümmern': 'kümmern',
    'Lachen': 'lachen',
    'Laufen': 'laufen',
    'Leben': 'leben',
    'Legen': 'legen',
    'Lernen': 'lernen',
    'Lesen': 'lesen',
    'Lieben': 'lieben',
    'Liegen': 'liegen',
    'Machen': 'machen',
    'Mieten': 'mieten',
    'Mitbringen': 'mitbringen',
    'Mitkommen': 'mitkommen',
    'Mitmachen': 'mitmachen',
    'Mitnehmen': 'mitnehmen',
    'Möchten': 'möchten',
    'Mögen': 'mögen',
    'Müssen': 'müssen',
    'Nehmen': 'nehmen',
    'Öffnen': 'öffnen',
    'Passieren': 'passieren',
    'Rauchen': 'rauchen',
    'Regnen': 'regnen',
    'Reisen': 'reisen',
    'Reparieren': 'reparieren',
    'Riechen': 'riechen',
    'Sagen': 'sagen',
    'Scheinen': 'scheinen',
    'Schicken': 'schicken',
    'Schlafen': 'schlafen',
    'Schließen': 'schließen',
    'Schmecken': 'schmecken',
    'Schreiben': 'schreiben',
    'Schwimmen': 'schwimmen',
    'Sehen': 'sehen',
    'Sein': 'sein',
    'Sitzen': 'sitzen',
    'Sollen': 'sollen',
    'Sprechen': 'sprechen',
    'Stehen': 'stehen',
    'Stellen': 'stellen',
    'Studieren': 'studieren',
    'Suchen': 'suchen',
    'Tanzen': 'tanzen',
    'Telefonieren': 'telefonieren',
    'Treffen': 'treffen',
    'Trinken': 'trinken',
    'Tun': 'tun',
    'Übernachten': 'übernachten',
    'Überweisen': 'überweisen',
    'Umziehen': 'umziehen',
    'Unterschreiben': 'unterschreiben',
    'Verdienen': 'verdienen',
    'Verkaufen': 'verkaufen',
    'Vermieten': 'vermieten',
    'Verstehen': 'verstehen',
    'Vorstellen': 'vorstellen',
    'Wandern': 'wandern',
    'Warten': 'warten',
    'Waschen': 'waschen',
    'Werden': 'werden',
    'Wiederholen': 'wiederholen',
    'Wissen': 'wissen',
    'Wohnen': 'wohnen',
    'Wollen': 'wollen',
    'Zahlen': 'zahlen'
}

ADJECTIVE_CORRECTIONS = {
    # Adjectives that should be lowercase
    'Alt': 'alt',
    'Bekannt': 'bekannt',
    'Besetzt': 'besetzt',
    'Billig': 'billig',
    'Breit': 'breit',
    'Deutlich': 'deutlich',
    'Dick': 'dick',
    'Dumm': 'dumm',
    'Dunkel': 'dunkel',
    'Dünn': 'dünn',
    'Echt': 'echt',
    'Eilig': 'eilig',
    'Einfach': 'einfach',
    'Einmal': 'einmal',
    'Eng': 'eng',
    'Falsch': 'falsch',
    'Fertig': 'fertig',
    'Frei': 'frei',
    'Freiwillig': 'freiwillig',
    'Freundlich': 'freundlich',
    'Frisch': 'frisch',
    'Froh': 'froh',
    'Früh': 'früh',
    'Gefährlich': 'gefährlich',
    'Genau': 'genau',
    'Gesund': 'gesund',
    'Glücklich': 'glücklich',
    'Groß': 'groß',
    'Gültig': 'gültig',
    'Günstig': 'günstig',
    'Gut': 'gut',
    'Hart': 'hart',
    'Hässlich': 'hässlich',
    'Heiß': 'heiß',
    'Hell': 'hell',
    'Herzlich': 'herzlich',
    'Hoch': 'hoch',
    'Intelligent': 'intelligent',
    'Interessant': 'interessant',
    'International': 'international',
    'Jung': 'jung',
    'Kalt': 'kalt',
    'Klar': 'klar',
    'Klein': 'klein',
    'Komisch': 'komisch',
    'Kostenlos': 'kostenlos',
    'Krank': 'krank',
    'Kulturell': 'kulturell',
    'Kurz': 'kurz',
    'Lang': 'lang',
    'Langweilig': 'langweilig',
    'Langsam': 'langsam',
    'Laut': 'laut',
    'Ledig': 'ledig',
    'Leicht': 'leicht',
    'Leise': 'leise',
    'Lustig': 'lustig',
    'Männlich': 'männlich',
    'Modern': 'modern',
    'Möglich': 'möglich',
    'Müde': 'müde',
    'Nass': 'nass',
    'Natürlich': 'natürlich',
    'Nervös': 'nervös',
    'Nett': 'nett',
    'Neu': 'neu',
    'Normal': 'normal',
    'Notwendig': 'notwendig',
    'Nützlich': 'nützlich',
    'Offen': 'offen',
    'Praktisch': 'praktisch',
    'Preiswert': 'preiswert',
    'Privat': 'privat',
    'Pünktlich': 'pünktlich',
    'Reich': 'reich',
    'Richtig': 'richtig',
    'Romantisch': 'romantisch',
    'Ruhig': 'ruhig',
    'Rund': 'rund',
    'Sauber': 'sauber',
    'Sauer': 'sauer',
    'Scharf': 'scharf',
    'Schlecht': 'schlecht',
    'Schlimm': 'schlimm',
    'Schnell': 'schnell',
    'Schön': 'schön',
    'Schrecklich': 'schrecklich',
    'Schriftlich': 'schriftlich',
    'Schwach': 'schwach',
    'Schwanger': 'schwanger',
    'Schwer': 'schwer',
    'Schwierig': 'schwierig',
    'Selbstständig': 'selbstständig',
    'Sicher': 'sicher',
    'Sonnig': 'sonnig',
    'Spannend': 'spannend',
    'Spät': 'spät',
    'Sportlich': 'sportlich',
    'Stark': 'stark',
    'Streng': 'streng',
    'Stressig': 'stressig',
    'Süß': 'süß',
    'Sympathisch': 'sympathisch',
    'Teuer': 'teuer',
    'Tief': 'tief',
    'Total': 'total',
    'Traurig': 'traurig',
    'Trocken': 'trocken',
    'Typisch': 'typisch',
    'Verheiratet': 'verheiratet',
    'Verschieden': 'verschieden',
    'Voll': 'voll',
    'Vorsichtig': 'vorsichtig',
    'Wach': 'wach',
    'Wahrscheinlich': 'wahrscheinlich',
    'Warm': 'warm',
    'Weiblich': 'weiblich',
    'Weich': 'weich',
    'Wenig': 'wenig',
    'Wichtig': 'wichtig',
    'Windig': 'windig',
    'Wirklich': 'wirklich',
    'Witzig': 'witzig',
    'Zufrieden': 'zufrieden'
}

NOUN_CORRECTIONS = {
    # Common nouns that should be capitalized but might not be
    'auto': 'Auto',
    'haus': 'Haus',
    'hund': 'Hund',
    'katze': 'Katze',
    'baum': 'Baum',
    'buch': 'Buch',
    'tisch': 'Tisch',
    'stuhl': 'Stuhl',
    'bett': 'Bett',
    'fenster': 'Fenster',
    'tür': 'Tür',
    'wasser': 'Wasser',
    'brot': 'Brot',
    'fleisch': 'Fleisch',
    'gemüse': 'Gemüse',
    'obst': 'Obst',
    'milch': 'Milch',
    'kaffee': 'Kaffee',
    'tee': 'Tee',
    'bier': 'Bier',
    'wein': 'Wein',
    'geld': 'Geld',
    'arbeit': 'Arbeit',
    'beruf': 'Beruf',
    'schule': 'Schule',
    'universität': 'Universität',
    'student': 'Student',
    'lehrer': 'Lehrer',
    'arzt': 'Arzt'
}

# Combine all corrections
ALL_CORRECTIONS = {}
ALL_CORRECTIONS.update(VERB_CORRECTIONS)
ALL_CORRECTIONS.update(ADJECTIVE_CORRECTIONS)
ALL_CORRECTIONS.update(NOUN_CORRECTIONS)

def apply_corrections_to_file(input_file: str, output_file: str) -> Dict[str, int]:
    """Apply corrections to a CSV file and return statistics"""
    corrections_applied = {}
    total_corrections = 0

    try:
        # Read the original file
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)

        # Apply corrections
        for i, row in enumerate(rows):
            if i == 0 or not row:  # Skip header or empty rows
                continue

            if len(row) >= 2:
                german_word = row[0].strip()

                if german_word in ALL_CORRECTIONS:
                    corrected_word = ALL_CORRECTIONS[german_word]
                    row[0] = corrected_word
                    corrections_applied[german_word] = corrected_word
                    total_corrections += 1

        # Write the corrected file
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)

        return corrections_applied, total_corrections

    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return {}, 0

def main():
    """Apply corrections to all vocabulary files"""
    files_to_correct = [
        ('A1_vokabeln.csv', 'A1_vokabeln_corrected.csv'),
        ('A2_vokabeln.csv', 'A2_vokabeln_corrected.csv'),
        ('B1_vokabeln.csv', 'B1_vokabeln_corrected.csv'),
        ('B2_vokabeln.csv', 'B2_vokabeln_corrected.csv'),
        ('C1_vokabeln.csv', 'C1_vokabeln_corrected.csv')
    ]

    print("=" * 80)
    print("APPLYING GERMAN CAPITALIZATION CORRECTIONS")
    print("=" * 80)
    print()

    total_files_processed = 0
    total_corrections_made = 0
    all_corrections = {}

    for input_file, output_file in files_to_correct:
        print(f"Processing {input_file}...")

        corrections, count = apply_corrections_to_file(input_file, output_file)

        if count > 0:
            print(f"  Applied {count} corrections")
            print(f"  Output saved to {output_file}")
            all_corrections.update(corrections)
            total_corrections_made += count
        else:
            print(f"  No corrections needed or file not found")

        total_files_processed += 1
        print()

    # Summary
    print("=" * 80)
    print("CORRECTION SUMMARY")
    print("=" * 80)
    print(f"Files processed: {total_files_processed}")
    print(f"Total corrections applied: {total_corrections_made}")
    print()

    if all_corrections:
        print("Corrections applied:")
        for original, corrected in sorted(all_corrections.items()):
            word_type = "verb" if original in VERB_CORRECTIONS else "adjective" if original in ADJECTIVE_CORRECTIONS else "noun"
            print(f"  {original} -> {corrected} ({word_type})")

if __name__ == '__main__':
    main()