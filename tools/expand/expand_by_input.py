import argparse
import bisect
import re
import sys
import os

# Strict rules
WORD_RE = re.compile(r"^[a-z]+$")
VOWEL_RE = re.compile(r"[aeiouy]")

def normalize_word(w: str) -> str:
    return w.strip().lower()

def is_valid_word(w: str) -> bool:
    return len(w) >= 2 and bool(WORD_RE.fullmatch(w)) and bool(VOWEL_RE.search(w))

def load_wordlist(path):
    words = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                w = normalize_word(line)
                if is_valid_word(w):
                    words.add(w)
    except FileNotFoundError:
        print(f"Warning: File not found: {path}")
    return words

def expand_specific_word(seed_word, reference_path, target_dirs):
    seed = normalize_word(seed_word)
    if not is_valid_word(seed):
        print(f"Error: '{seed}' is not a valid word format (must be a-z, >=2 chars, has vowel).")
        return

    print(f"Expanding seed word: '{seed}'")

    # 1. Load Reference (1000000.txt)
    print(f"Loading reference from {reference_path}...")
    try:
        ref_words_raw = load_wordlist(reference_path)
        ref_words_sorted = sorted(list(ref_words_raw))
        print(f"Loaded {len(ref_words_sorted)} unique valid reference words.")
    except Exception as e:
        print(f"Error loading reference: {e}")
        return

    # 2. Find matches in reference
    matches = set()
    idx = bisect.bisect_left(ref_words_sorted, seed)
    
    print(f"Scanning reference for words STRICTLY starting with '{seed}'...")
    
    while idx < len(ref_words_sorted):
        candidate = ref_words_sorted[idx]
        
        # STRICT PREFIX CHECK
        if candidate.startswith(seed):
            # Additional strict filtering (no repeated chars, valid word format)
            if not re.search(r'(.)\1\1', candidate) and is_valid_word(candidate):
                matches.add(candidate)
            idx += 1
        else:
            # Since the list is sorted, as soon as we find a word that DOES NOT 
            # start with the seed, we can stop. All subsequent words will also 
            # not match.
            # Example: seed='gym', candidate='gynaecology' -> Stop.
            # Example: seed='gym', candidate='energy' -> would never be reached/checked here if list is sorted correctly.
            break
    
    if not matches:
        print(f"No matches found in reference for seed '{seed}'.")
        return

    print(f"Found {len(matches)} matches in reference (e.g. {sorted(list(matches))[:5]}).")
    print(f"Verified: All {len(matches)} matches start with '{seed}'.")

    # 3. Check ALL txt files in target directories
    # Logic: If a txt file ALREADY contains the seed word (or related forms), 
    # we assume it's the right place to put the expansions.
    # OR: The user asked to "cari kata di semua file txt yang ada gym lalu expand"
    # This implies: Find which file contains 'gym', then add the matches to THAT file.

    target_files_updated = []

    for target_dir in target_dirs:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".txt") and file != os.path.basename(reference_path):
                    file_path = os.path.join(root, file)
                    
                    try:
                        current_words = load_wordlist(file_path)
                        
                        # Check if seed exists in this file
                        # Or maybe check if ANY of the matches exist? 
                        # User said: "cari kata di semua file txt yang ada gym"
                        # So strictly: does 'gym' exist in nouns.txt? yes -> add matches.
                        
                        if seed in current_words:
                            print(f"Found seed '{seed}' in {file_path}. Adding matches...")
                            
                            # Add matches
                            original_count = len(current_words)
                            updated_words = current_words.union(matches)
                            added_count = len(updated_words) - original_count
                            
                            if added_count > 0:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    for w in sorted(list(updated_words)):
                                        f.write(w + '\n')
                                print(f"  -> Added {added_count} new words to {file}.")
                                target_files_updated.append(file_path)
                            else:
                                print(f"  -> All matches already exist in {file}.")
                        else:
                            # Optional: What if 'gym' isn't there but 'gyms' is?
                            # For now, strict exact match on seed as per instruction "ada gym"
                            pass

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    # 4. Trigger Preprocessing for updated files
    if target_files_updated:
        print("\nTriggering preprocessing for updated files...")
        for txt_path in target_files_updated:
            json_path = txt_path.replace('.txt', '.json')
            cmd = f"python tools/preprocess_wordlist.py {txt_path} {json_path}"
            print(f"Running: {cmd}")
            os.system(cmd)
            
def main():
    parser = argparse.ArgumentParser(description="Expand specific seed word across wordlists.")
    parser.add_argument("seed", nargs="?", help="The word to expand (e.g. 'gym'). If omitted, you will be prompted.")
    parser.add_argument("--reference", default=r"c:\Project\Outside\s6xsense\wordlist\1000000.txt", help="Path to reference txt")
    parser.add_argument("--target_dir", default=r"c:\Project\Outside\s6xsense\wordlist\wordlist", help="Directory containing target wordlists")
    args = parser.parse_args()
    
    seed = args.seed
    if not seed:
        try:
            seed = input("Enter the word to expand: ").strip()
        except KeyboardInterrupt:
            sys.exit(0)
            
    if not seed:
        print("No seed word provided. Exiting.")
        sys.exit(1)
    
    expand_specific_word(seed, args.reference, [args.target_dir])

if __name__ == "__main__":
    main()
