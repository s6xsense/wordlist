import os
import re
import glob

def extract_words_from_file(input_path):
    print(f"Reading from: {input_path}")
    words = set()
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Look for pattern: Word: <word>
                match = re.search(r"Word:\s*(\w+)", line)
                if match:
                    word = match.group(1).strip().lower()
                    words.add(word)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
    return words

def main():
    base_dir = r"c:\Project\Outside\s6xsense\wordlist"
    output_dir = os.path.join(base_dir, "fail_filter")
    output_file = os.path.join(output_dir, "fail1_clean.txt")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Load existing clean words (to prevent duplicates if run multiple times)
    all_words = set()
    if os.path.exists(output_file):
        print(f"Loading existing words from {output_file}...")
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                w = line.strip().lower()
                if w:
                    all_words.add(w)

    # 2. Find all fail*.txt files in the base directory
    fail_files = glob.glob(os.path.join(base_dir, "fail*.txt"))
    
    if not fail_files:
        print("No fail*.txt files found.")
        return

    print(f"Found {len(fail_files)} fail files: {[os.path.basename(f) for f in fail_files]}")

    # 3. Extract words from each file
    new_words_count = 0
    for file_path in fail_files:
        words = extract_words_from_file(file_path)
        for w in words:
            if w not in all_words:
                all_words.add(w)
                new_words_count += 1
    
    print(f"Found {new_words_count} new unique words.")

    # 4. Write back to single output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for w in sorted(list(all_words)):
                f.write(w + '\n')
        print(f"Successfully wrote {len(all_words)} unique words to: {output_file}")
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
