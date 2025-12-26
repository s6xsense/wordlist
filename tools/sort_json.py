import json
import os
import glob

def sort_json_keys(file_path):
    print(f"Sorting keys for: {os.path.basename(file_path)}")
    try:
        # Load JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Sort keys alphabetically
        sorted_data = dict(sorted(data.items()))
        
        # Write back to file with proper indentation
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=2, ensure_ascii=False)
            
        print(f" -> Successfully sorted {len(sorted_data)} keys.")
        return True
    except Exception as e:
        print(f" -> Error processing {file_path}: {e}")
        return False

def main():
    # Detect preprocessed folder (try both 'wordlist/preprocessed' and 'wordlist/wordlist' 
    # since user mentioned 'wordlist/preprocessed' but previous context showed 'wordlist/wordlist')
    # Actually, based on previous context, the JSONs seem to be in 'wordlist/wordlist' 
    # but user input says 'wordlist/preprocessed'. I will check both or assume user path.
    
    # Assuming user path is correct or relative to project root.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Target files based on user input example
    # Check if 'preprocessed' folder exists, otherwise fallback to 'wordlist'
    
    potential_dirs = [
        os.path.join(base_dir, 'preprocessed'),
        os.path.join(base_dir, 'wordlist')
    ]
    
    target_dir = None
    for d in potential_dirs:
        if os.path.exists(d):
            # Check if it contains json files
            if glob.glob(os.path.join(d, "*.json")):
                target_dir = d
                break
    
    if not target_dir:
        print("Error: Could not find directory containing JSON files.")
        return

    print(f"Target directory: {target_dir}")
    
    json_files = glob.glob(os.path.join(target_dir, "*.json"))
    
    if not json_files:
        print("No JSON files found.")
        return

    for json_file in json_files:
        sort_json_keys(json_file)

    print("\nAll files sorted alphabetically (A-Z).")

if __name__ == "__main__":
    main()
