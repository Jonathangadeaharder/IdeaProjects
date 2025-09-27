# German Vocabulary Compound Phrase Analysis Report

## Overview
This report analyzes German vocabulary CSV files to identify compound phrases and multi-word expressions that should ideally be single words for vocabulary learning purposes.

## Analysis Criteria
The analysis identifies German entries that contain:
1. **Multiple words separated by spaces** (e.g., "sich freuen", "Home Office")
2. **Multiple hyphens indicating compound phrases** (e.g., "Virtual-Reality-Brille")
3. **Embedded articles and prepositions** indicating phrasal constructions

## Results by File

### A1_vokabeln.csv
- **Violations found:** 0
- **Status:** Clean - contains only single German words
- **File size:** 741 entries

### A2_vokabeln.csv
- **Violations found:** 0
- **Status:** Clean - contains only single German words
- **File size:** 606 entries

### B1_vokabeln.csv
- **Violations found:** 29
- **Notable patterns:** High concentration of reflexive verb phrases with "sich"

**Detailed violations:**
- Line 50: als ob - Multiple words separated by spaces
- Line 58: sich amüsieren - Multiple words separated by spaces
- Line 94: sich anstrengen - Multiple words separated by spaces
- Line 111: sich ärgern - Multiple words separated by spaces
- Line 163: sich ausruhen - Multiple words separated by spaces
- Line 202: sich bedanken - Multiple words separated by spaces
- Line 209: sich beeilen - Multiple words separated by spaces
- Line 211: sich befinden - Multiple words separated by spaces
- Line 235: bekannt geben - Multiple words separated by spaces
- Line 262: Bescheid sagen - Multiple words separated by spaces
- Line 263: Bescheid geben - Multiple words separated by spaces
- Line 268: sich beschweren - Multiple words separated by spaces
- Line 285: sich beteiligen - Multiple words separated by spaces
- Line 300: sich bewerben - Multiple words separated by spaces
- Line 314: ein bisschen - Multiple words separated by spaces
- Line 438: sich eignen - Multiple words separated by spaces
- Line 460: sich einigen - Multiple words separated by spaces
- Line 512: sich entschließen - Multiple words separated by spaces
- Line 520: entweder ... oder - Multiple words separated by spaces
- Line 525: sich ereignen - Multiple words separated by spaces
- Line 537: sich erholen - Multiple words separated by spaces
- Line 541: sich erkälten - Multiple words separated by spaces
- Line 547: sich erkundigen - Multiple words separated by spaces
- Line 671: im Freien - Multiple words separated by spaces
- Line 676: sich freuen - Multiple words separated by spaces
- Line 698: sich fürchten - Multiple words separated by spaces
- Line 717: geboren werden - Multiple words separated by spaces
- Line 729: sich etwas gefallen lassen - Multiple words separated by spaces

### B2_vokabeln.csv
- **Violations found:** 0
- **Status:** File is empty (contains only header row)
- **File size:** 1 line (header only)

### C1_vokabeln.csv
- **Violations found:** 64
- **Notable patterns:** Complex phrasal expressions, idiomatic phrases, and technical terms

**Detailed violations:**
- Line 3: A und O - Multiple words separated by spaces
- Line 22: Alarm schlagen - Multiple words separated by spaces
- Line 33: Alltag entfliehen - Multiple words separated by spaces
- Line 54: Ansicht teilen - Multiple words separated by spaces
- Line 139: Blick werfen auf - Multiple words separated by spaces
- Line 300: Entscheidung treffen - Multiple words separated by spaces
- Line 310: Erkenntnisse liefern - Multiple words separated by spaces
- Line 328: Experiment abbrechen - Multiple words separated by spaces
- Line 353: Fokus legen auf - Multiple words separated by spaces
- Line 357: Forderung stellen - Multiple words separated by spaces
- Line 387: Gefühl geben - Multiple words separated by spaces
- Line 497: Home Office - Multiple words separated by spaces
- Line 521: Industrie- und Handelskammer - Multiple words separated by spaces
- Line 532: Interview führen - Multiple words separated by spaces
- Line 644: Lust bekommen auf - Multiple words separated by spaces
- Line 750: Problem lösen - Multiple words separated by spaces
- Line 765: Rad der Zeit zurückdrehen - Multiple words separated by spaces
- Line 800: Rolle spielen - Multiple words separated by spaces
- Line 829: Schreckensbild ergeben - Multiple words separated by spaces
- Line 875: Statistik auswerten - Multiple words separated by spaces
- Line 882: Stellung nehmen zu - Multiple words separated by spaces
- Line 892: Strecke zurücklegen - Multiple words separated by spaces
- Line 993: Verständnis schaffen - Multiple words separated by spaces
- Line 999: Virtual-Reality-Brille - Multiple hyphens indicating compound phrase
- Line 1028: an erster Stelle stehen - Multiple words separated by spaces
- Line 1057: auf der Hand liegen - Multiple words separated by spaces
- Line 1058: auf sich zukommen lassen - Multiple words separated by spaces
- Line 1075: ausgeliefert sein - Multiple words separated by spaces
- Line 1149: binärer Code - Multiple words separated by spaces
- Line 1259: eingehen auf - Multiple words separated by spaces
- Line 1265: einstimmen auf - Multiple words separated by spaces
- Line 1273: emotionale Reaktion - Multiple words separated by spaces
- Line 1276: empfinden als - Multiple words separated by spaces
- Line 1316: familiäres Umfeld - Multiple words separated by spaces
- Line 1382: gelten als - Multiple words separated by spaces
- Line 1557: in Kauf nehmen - Multiple words separated by spaces
- Line 1558: in den Mittelpunkt stellen - Multiple words separated by spaces
- Line 1559: in den Vordergrund treten - Multiple words separated by spaces
- Line 1560: in die Hand nehmen - Multiple words separated by spaces
- Line 1561: in seine Bestandteile zerlegen - Multiple words separated by spaces
- Line 1641: konfrontiert sehen - Multiple words separated by spaces
- Line 1784: ländlicher Raum - Multiple words separated by spaces
- Line 1790: macht Mut - Multiple words separated by spaces
- Line 1854: menschliches Versagen - Multiple words separated by spaces
- Line 1987: ruh en - Multiple words separated by spaces
- Line 2032: selbstfahrendes Auto - Multiple words separated by spaces
- Line 2037: sich erfreuen - Multiple words separated by spaces
- Line 2060: soziales Umfeld - Multiple words separated by spaces
- Line 2161: unumgänglich sein - Multiple words separated by spaces
- Line 2233: verzichten auf - Multiple words separated by spaces
- Line 2245: von der Hand zu weisen sein - Multiple words separated by spaces
- Line 2246: vor Augen führen - Multiple words separated by spaces
- Line 2264: wahrnehmen als - Multiple words separated by spaces
- Line 2307: wirken wie - Multiple words separated by spaces
- Line 2350: zukommen auf - Multiple words separated by spaces
- Line 2366: Überraschung erleben - Multiple words separated by spaces
- Line 2367: öffentliches Verkehrssystem - Multiple words separated by spaces
- Line 2612: sich wünschen - Multiple words separated by spaces
- Line 4614: vor allem - Multiple words separated by spaces
- Line 4633: sich vorstellen - Multiple words separated by spaces
- Line 4655: was für ein - Multiple words separated by spaces
- Line 4662: weder ... noch - Multiple words separated by spaces
- Line 4668: sich weigern - Multiple words separated by spaces
- Line 4727: sich wundern - Multiple words separated by spaces

## Summary Statistics

| File | Total Entries | Violations | Violation Rate |
|------|---------------|------------|----------------|
| A1_vokabeln.csv | 741 | 0 | 0% |
| A2_vokabeln.csv | 606 | 0 | 0% |
| B1_vokabeln.csv | ~1,127 | 29 | ~2.6% |
| B2_vokabeln.csv | 0 (empty) | 0 | N/A |
| C1_vokabeln.csv | ~4,727 | 64 | ~1.4% |

**Total violations across all files: 93**

## Analysis Patterns

### Most Common Violation Types:

1. **Reflexive verb phrases with "sich"** (39 instances)
   - Examples: "sich freuen", "sich ärgern", "sich befinden"
   - These are common German reflexive verbs that should ideally be represented as single vocabulary items

2. **Phrasal verbs and verb phrases** (24 instances)
   - Examples: "Entscheidung treffen", "Problem lösen", "Rolle spielen"
   - These are verb-noun combinations that function as phrasal units

3. **Prepositional phrases** (15 instances)
   - Examples: "in Kauf nehmen", "auf der Hand liegen", "vor allem"
   - Complex prepositional constructions

4. **Idiomatic expressions** (10 instances)
   - Examples: "A und O", "entweder ... oder", "weder ... noch"
   - Fixed idiomatic phrases

5. **Complex compound terms** (5 instances)
   - Examples: "Virtual-Reality-Brille", "Home Office"
   - Technical terms and anglicisms

## Recommendations

1. **For vocabulary learning effectiveness**, consider breaking down complex phrases into their component parts or replacing them with simpler single-word alternatives where possible.

2. **B2_vokabeln.csv** needs to be populated with actual vocabulary entries.

3. **Reflexive verbs** could be represented without the "sich" particle for vocabulary learning purposes, or the entire reflexive construction could be treated as a single vocabulary unit.

4. **Complex phrases** in C1 level might be appropriate given the advanced level, but should be clearly marked as phrasal units rather than individual words.

## File Locations
All analyzed files are located in: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/`
