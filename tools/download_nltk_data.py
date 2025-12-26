import nltk

try:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('brown')
    nltk.download('wordnet')
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger_eng')
    print("Downloads complete.")
except Exception as e:
    print(f"Error downloading: {e}")
