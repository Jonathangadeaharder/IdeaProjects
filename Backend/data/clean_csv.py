with open('10K_csv.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

cleaned_lines = []
for line in lines:
    if ',' in line:
        parts = line.split(',')
        if len(parts) >= 2:
            word = parts[1].strip()
            cleaned_lines.append(word + '\n')
    else:
        # If no comma, perhaps it's already cleaned or error
        cleaned_lines.append(line.strip() + '\n')

with open('10K_csv.csv', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)