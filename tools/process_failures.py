import os
import subprocess
import sys

def main():
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    extract_script = os.path.join(tools_dir, 'fail', 'extract_failed_words.py')
    remove_script = os.path.join(tools_dir, 'fail', 'remove_failed_words.py')

    print("=== Step 1: Extracting failed words ===")
    try:
        subprocess.run([sys.executable, extract_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting failed words: {e}")
        return

    print("\n=== Step 2: Removing failed words and Updating JSONs ===")
    try:
        subprocess.run([sys.executable, remove_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error removing failed words: {e}")
        return

    print("\nAll done!")

if __name__ == "__main__":
    main()
