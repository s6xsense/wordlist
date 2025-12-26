import os
import subprocess
import sys

def main():
    # Define directories
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wordlist_dir = os.path.join(base_dir, 'wordlist')
    tool_path = os.path.join(base_dir, 'tools', 'preprocess_wordlist.py')

    print(f"Scanning {wordlist_dir} for .txt files...")

    files_processed = 0
    for filename in os.listdir(wordlist_dir):
        if filename.endswith(".txt"):
            txt_path = os.path.join(wordlist_dir, filename)
            json_path = os.path.join(wordlist_dir, filename.replace(".txt", ".json"))
            
            print(f"Processing {filename} -> {os.path.basename(json_path)}...")
            
            # Construct command
            cmd = [sys.executable, tool_path, txt_path, json_path]
            
            try:
                subprocess.run(cmd, check=True)
                files_processed += 1
            except subprocess.CalledProcessError as e:
                print(f"Error processing {filename}: {e}")

    print(f"\nDone! Processed {files_processed} files.")

if __name__ == "__main__":
    main()
