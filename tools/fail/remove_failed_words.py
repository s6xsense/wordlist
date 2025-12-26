import os
import sys
import subprocess

def load_blacklist(path):
    blacklist = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                w = line.strip().lower()
                if w:
                    blacklist.add(w)
    except FileNotFoundError:
        print(f"Error: Blacklist file not found: {path}")
    return blacklist

def clean_file(file_path, blacklist):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_count = len(lines)
        new_lines = []
        removed_words = []

        for line in lines:
            word = line.strip().lower()
            if word in blacklist:
                removed_words.append(word)
            else:
                new_lines.append(line)
        
        if len(new_lines) < original_count:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Cleaned {os.path.basename(file_path)}: Removed {len(removed_words)} words ({', '.join(removed_words[:5])}...)")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    blacklist_path = os.path.join(base_dir, 'fail_filter', 'fail1_clean.txt')
    wordlist_dir = os.path.join(base_dir, 'wordlist')
    preprocess_script = os.path.join(base_dir, 'tools', 'preprocess_all.py')

    print(f"Loading blacklist from {blacklist_path}...")
    blacklist = load_blacklist(blacklist_path)
    if not blacklist:
        print("Blacklist is empty or not found. Exiting.")
        return
    
    print(f"Loaded {len(blacklist)} words to remove.")

    files_updated = False
    for filename in os.listdir(wordlist_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(wordlist_dir, filename)
            if clean_file(file_path, blacklist):
                files_updated = True
    
    if files_updated:
        print("\nSome files were modified. Updating JSON files...")
        subprocess.run([sys.executable, preprocess_script], check=True)
    else:
        print("\nNo words from the blacklist were found in the wordlists.")

if __name__ == "__main__":
    main()
