with open('10K', 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split()
words = []

# The freq_word is at indices 2, 5, 8, ... (every third starting from 2)
for i in range(2, len(parts), 3):
    freq_word = parts[i]
    if ',' in freq_word:
        word = freq_word.split(',')[1]
        words.append(word)

# Append to 10K_csv.csv
with open('10K_csv.csv', 'a', encoding='utf-8') as f:
    for word in words:
        f.write(word + '\n')