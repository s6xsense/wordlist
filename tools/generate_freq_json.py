import os
import json
import math
from collections import defaultdict
from wordfreq import zipf_frequency
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# Global Bigram Model
bigram_probs = {}
min_log_prob = -10.0

# Initialize Lemmatizer
lemmatizer = WordNetLemmatizer()

def train_bigram_model(reference_file):
    print("Training bigram model for word-likeness...")
    global bigram_probs, min_log_prob
    
    counts = defaultdict(int)
    total_counts = defaultdict(int)
    
    try:
        with open(reference_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if not word: continue
                
                # Only use "common" words for training the model to capture "good" English patterns
                # Zipf > 4.0 (approx > 50% on our scale) is a good threshold for common words
                z = zipf_frequency(word, 'en')
                if z < 4.0:
                    continue
                
                # Add start/end tokens
                padded = "^" + word + "$"
                for i in range(len(padded) - 1):
                    bg = padded[i:i+2]
                    counts[bg] += 1
                    total_counts[padded[i]] += 1
                    
    except FileNotFoundError:
        print("Reference file not found. Skipping bigram training.")
        return

    # Calculate probabilities
    bigram_probs = {}
    for bg, count in counts.items():
        first_char = bg[0]
        prob = count / total_counts[first_char]
        bigram_probs[bg] = math.log(prob)
    
    # Define a minimum probability for unseen bigrams
    min_log_prob = -15.0 
    print(f"Bigram model trained. {len(bigram_probs)} bigrams learned.")

def calculate_likeness(word):
    if not bigram_probs:
        return 0.0
        
    padded = "^" + word + "$"
    log_sum = 0
    
    for i in range(len(padded) - 1):
        bg = padded[i:i+2]
        log_sum += bigram_probs.get(bg, min_log_prob)
    
    # Average log probability per transition
    avg_log_prob = log_sum / (len(padded) - 1)
    
    # Normalize to 0-100 scale
    # Heuristic: 
    # Max theoretical log prob is 0 (prob 1.0) -> score 100
    # Min typical log prob is around -10 -> score 0
    # Let's map [-8, -1.5] to [0, 100] roughly
    
    # Best avg log prob seen in English is usually around -2.0 to -2.5
    # Worst (random strings) is around -10 or lower.
    
    lower_bound = -7.0
    upper_bound = -1.5
    
    score = (avg_log_prob - lower_bound) / (upper_bound - lower_bound) * 100
    
    if score < 0: score = 0.0
    if score > 100: score = 100.0
    
    return round(score, 2)

def get_freq_score(word):
    z_score = zipf_frequency(word, 'en')
    score = round((z_score / 8.0) * 100, 2)
    if score > 100: score = 100.0
    return score

def get_boosted_freq(word, pos_tag=None):
    # 1. Base Score
    score = get_freq_score(word)
    
    # If score is already decent, keep it.
    if score > 5.0:
        return score
        
    # 2. Try Lemmatization boost if score is low
    if pos_tag:
        try:
            lemma = lemmatizer.lemmatize(word, pos_tag)
            if lemma != word:
                lemma_score = get_freq_score(lemma)
                
                # If lemma is significantly more common, inherit some of its score
                if lemma_score > score:
                    # Boost factor: Inflected forms are rarer than base forms.
                    # We assume ~70% of the base form's popularity is a reasonable floor 
                    # for a valid inflected form that just happens to be missing from freq list.
                    boosted = lemma_score * 0.70
                    if boosted > score:
                        # print(f"Boosting '{word}' ({score}) -> ({boosted:.2f}) using lemma '{lemma}' ({lemma_score})")
                        score = round(boosted, 2)
        except Exception:
            pass
            
    # Minimum floor for valid words
    if score == 0.0:
        score = 0.01
        
    return score

def generate_json_with_scores(input_file, output_file):
    filename = os.path.basename(input_file)
    print(f"Processing {filename}...")
    
    # Determine POS tag for lemmatization
    pos_tag = None
    if 'verb' in filename:
        pos_tag = wordnet.VERB
    elif 'noun' in filename:
        pos_tag = wordnet.NOUN
    elif 'adjective' in filename:
        pos_tag = wordnet.ADJ
    elif 'adverb' in filename:
        pos_tag = wordnet.ADV
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    data = {}
    
    for word in words:
        # 1. Frequency Score (with smart boosting)
        freq_score = get_boosted_freq(word, pos_tag)
        
        # 2. Likeness Score (0-100)
        like_score = calculate_likeness(word)
        
        # Structure: Object with two scores
        data[word] = {
            "freq": freq_score,
            "like": like_score
        }

    # Sort alphabetically
    sorted_data = dict(sorted(data.items()))

    # Write JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=2, ensure_ascii=False)
        print(f" -> Wrote {len(sorted_data)} items to {os.path.basename(output_file)}")
    except Exception as e:
        print(f"Error writing JSON: {e}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, 'wordlist_new')
    output_dir = os.path.join(input_dir, 'json')
    reference_file = os.path.join(base_dir, '1000000_clean.txt')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Train model first
    train_bigram_model(reference_file)

    # Process all txt files in wordlist_new
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.txt', '.json'))
            generate_json_with_scores(input_path, output_path)

    print("\nAll done! JSON files with frequency and likeness scores generated in wordlist_new/json/")

if __name__ == "__main__":
    main()
