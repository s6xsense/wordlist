import re
import os
import sys

def is_valid_word(word):
    # 1. Strict a-z (implies no space, dash, apostrophe, symbols, numbers)
    if not re.fullmatch(r'^[a-z]+$', word):
        return False
    
    # 2. Length check (min 2 chars)
    if len(word) < 2:
        return False

    # 3. Must contain at least one vowel (including y)
    if not re.search(r'[aeiouy]', word):
        return False

    # 4. No repeated char spam (max 2 consecutive identical chars allowed)
    # e.g. "aa" ok, "aaa" bad.
    if re.search(r'(.)\1\1', word):
        return False

    # 5. Anti-consonant cluster extreme (limit to < 7 consecutive consonants)
    # English words can have complex clusters (e.g. 'catchphrase' -> 'tchphr' = 6)
    # So we reject 7 or more.
    if re.search(r'[bcdfghjklmnpqrstvwxz]{7,}', word):
        return False

    return True

def clean_reference(input_path, output_path):
    print(f"Cleaning {input_path}...")
    
    unique_words = set()
    total_lines = 0
    valid_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                # Lowercase and strip
                word = line.strip().lower()
                
                if is_valid_word(word):
                    unique_words.add(word)
                    valid_count += 1
                
                if total_lines % 100000 == 0:
                    print(f"Processed {total_lines} lines...")
                    
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        return

    print(f"Finished processing. Total lines: {total_lines}")
    print(f"Unique valid words: {len(unique_words)}")
    
    # Sort A-Z
    sorted_words = sorted(list(unique_words))
    
    print(f"Writing to {output_path}...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for w in sorted_words:
                f.write(w + '\n')
        print("Done!")
    except Exception as e:
        print(f"Error writing file: {e}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, '1000000.txt')
    output_file = os.path.join(base_dir, '1000000_clean.txt')
    
    clean_reference(input_file, output_file)

if __name__ == "__main__":
    main()
