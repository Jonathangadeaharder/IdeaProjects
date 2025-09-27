#!/usr/bin/env python3
"""
Script to convert space-separated word frequency data to CSV format.
Each row will contain: number,word
"""

def convert_to_csv(input_file, output_file):
    """
    Convert space-separated frequency data to CSV format.
    
    Args:
        input_file (str): Path to input file with space-separated data
        output_file (str): Path to output CSV file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split by spaces to get all tokens
        tokens = content.split()
        
        # Group tokens in pairs (number, word)
        csv_lines = []
        for i in range(0, len(tokens), 2):
            if i + 1 < len(tokens):
                number = tokens[i]
                word = tokens[i + 1]
                csv_lines.append(f"{number},{word}")
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(csv_lines))
        
        print(f"Successfully converted {len(csv_lines)} entries to CSV format")
        print(f"Output saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    input_file = "10K"
    output_file = "10K_csv.csv"
    
    print("Converting space-separated data to CSV format...")
    convert_to_csv(input_file, output_file)