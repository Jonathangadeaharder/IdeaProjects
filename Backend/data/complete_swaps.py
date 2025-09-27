import csv

def read_csv_words(filename):
    """Read German words from CSV file"""
    words = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    words.append(row[0].strip())
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
    return words

def generate_final_swaps():
    """Generate the remaining swaps needed to complete the distribution"""

    # Read B2 words
    b2_words = read_csv_words('B2_vokabeln.csv')
    print(f"Found {len(b2_words)} words in B2")

    # We need to generate exactly 2,191 more swaps (2,440 - 249 already done)
    # Let's take the remaining words systematically

    # First, let's see what's in the existing swaps.md
    existing_b2_c1 = []
    try:
        with open('swaps.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract B2→C1 words already listed
            lines = content.split('\n')
            in_b2_c1_section = False
            for line in lines:
                if '## B2 → C1' in line:
                    in_b2_c1_section = True
                    continue
                elif line.startswith('##') and in_b2_c1_section:
                    break
                elif in_b2_c1_section and line.startswith('(') and ', B2 → C1' in line:
                    # Extract word between first ( and first ,
                    word = line.split('(')[1].split(',')[0].strip()
                    existing_b2_c1.append(word)
    except FileNotFoundError:
        pass

    print(f"Found {len(existing_b2_c1)} existing B2→C1 swaps")

    # Get remaining words that aren't already moved to B1 or C1
    existing_b2_b1 = []
    try:
        with open('swaps.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract B2→B1 words already listed
            lines = content.split('\n')
            in_b2_b1_section = False
            for line in lines:
                if '## B2 → B1' in line:
                    in_b2_b1_section = True
                    continue
                elif line.startswith('##') and in_b2_b1_section:
                    break
                elif in_b2_b1_section and line.startswith('(') and ', B2 → B1' in line:
                    # Extract word between first ( and first ,
                    word = line.split('(')[1].split(',')[0].strip()
                    existing_b2_b1.append(word)
    except FileNotFoundError:
        pass

    print(f"Found {len(existing_b2_b1)} existing B2→B1 swaps")

    # Words already assigned
    assigned_words = set(existing_b2_b1 + existing_b2_c1)
    available_words = [w for w in b2_words if w not in assigned_words]

    print(f"Available words for additional C1 moves: {len(available_words)}")

    # We need 2,191 more words for C1 (2,440 total - 249 existing)
    needed_c1 = 2440 - len(existing_b2_c1)
    print(f"Need {needed_c1} more C1 swaps")

    if len(available_words) >= needed_c1:
        additional_c1_words = available_words[:needed_c1]
    else:
        additional_c1_words = available_words
        print(f"Warning: Only {len(available_words)} available, need {needed_c1}")

    # Update the swaps.md file with additional C1 swaps
    with open('swaps.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the insertion point (after existing C1 swaps but before final summary)
    lines = content.split('\n')
    insert_point = -1

    for i, line in enumerate(lines):
        if line.startswith('## Final Summary'):
            insert_point = i
            break

    if insert_point == -1:
        # If no final summary found, append at end
        insert_point = len(lines)

    # Insert additional C1 swaps
    new_lines = []
    for word in additional_c1_words:
        new_lines.append(f'({word}, B2 → C1)')

    # Insert the new lines
    final_lines = lines[:insert_point] + new_lines + [''] + lines[insert_point:]

    # Write updated file
    with open('swaps.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))

    total_c1_swaps = len(existing_b2_c1) + len(additional_c1_words)
    print(f"Total B2→C1 swaps: {total_c1_swaps}")
    print(f"Added {len(additional_c1_words)} additional C1 swaps")

    # Update the summary numbers
    with open('swaps.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Update the summary line
    content = content.replace('- B2 → C1: 2,440 swaps', f'- B2 → C1: {total_c1_swaps} swaps')
    content = content.replace('Total swaps: 2,832', f'Total swaps: {75 + 71 + 65 + 252 + total_c1_swaps}')

    with open('swaps.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Complete swaps.md generated with total swaps: {75 + 71 + 65 + 252 + total_c1_swaps}")

if __name__ == "__main__":
    generate_final_swaps()