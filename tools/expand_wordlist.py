import argparse
import bisect
import re
import sys
import os

# Strict rules from preprocess_wordlist.py
WORD_RE = re.compile(r"^[a-z]+$")
VOWEL_RE = re.compile(r"[aeiouy]")

def normalize_word(w: str) -> str:
    return w.strip().lower()

def is_valid_word(w: str) -> bool:
    # Use fullmatch to ensure the entire string matches the pattern
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
    return list(words)

def expand_file(target_path, reference_words_sorted):
    current_words = load_wordlist(target_path)
    if not current_words:
        print(f"Skipping empty or missing file: {target_path}")
        return

    current_set = set(current_words)
    original_count = len(current_set)
    
    # Sort seeds for deterministic processing (though we process all)
    sorted_seeds = sorted(list(current_set))
    
    new_words = set()
    
    print(f"Processing {os.path.basename(target_path)} with {original_count} seeds...")

    for seed in sorted_seeds:
        # Strict filtering: seed must be at least 3 chars long to be expanded
        if len(seed) < 3:
            continue

        # Find where seed would start in reference_words
        idx = bisect.bisect_left(reference_words_sorted, seed)
        
        # Iterate forward in reference_words
        while idx < len(reference_words_sorted):
            candidate = reference_words_sorted[idx]
            
            # Optimization: if candidate doesn't start with the first char of seed, 
            # and is lexicographically larger, we can stop early?
            # Actually, because sorted, all words starting with 'seed' are contiguous.
            # Once we find one that doesn't start with 'seed', we are done for this seed.
            
            if candidate.startswith(seed):
                # Strict filtering for candidate:
                # 1. No 3 consecutive identical chars (e.g. aaa, gymmm)
                # 2. Must be reasonably longer or same length (implicit since it contains seed)
                # 3. Must be a valid word (double check)
                if not re.search(r'(.)\1\1', candidate) and is_valid_word(candidate):
                    new_words.add(candidate)
                idx += 1
            else:
                # Since list is sorted, if candidate doesn't start with seed
                # and candidate >= seed (guaranteed by bisect + loop),
                # then no further words will start with seed.
                break
                
    # Merge
    final_set = current_set.union(new_words)
    
    # Write back
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            for w in sorted(list(final_set)):
                f.write(w + '\n')
        print(f"Expanded {os.path.basename(target_path)}: {original_count} -> {len(final_set)} words (+{len(final_set) - original_count})")
    except Exception as e:
        print(f"Error writing to {target_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Expand wordlists by finding similar words (prefix match) in a reference list.")
    parser.add_argument("reference", help="Path to reference txt (e.g. 1000000.txt)")
    parser.add_argument("targets", nargs="+", help="Paths to target txt files to expand")
    args = parser.parse_args()
    
    print(f"Loading reference from {args.reference}...")
    ref_words = load_wordlist(args.reference)
    # Filter unique and sort
    ref_words = sorted(list(set(ref_words)))
    print(f"Loaded {len(ref_words)} unique valid reference words.")
    
    for target in args.targets:
        expand_file(target, ref_words)

if __name__ == "__main__":
    main()
