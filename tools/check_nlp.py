try:
    import nltk
    print("nltk imported")
    try:
        from nltk.corpus import wordnet
        print("wordnet available")
    except ImportError:
        print("wordnet import failed")
    except LookupError:
        print("wordnet data missing")
except ImportError:
    print("nltk not installed")

try:
    import spacy
    print("spacy imported")
except ImportError:
    print("spacy not installed")
