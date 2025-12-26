import os
import nltk
from nltk.corpus import wordnet

def get_wordnet_pos(word):
    """
    Returns a set of POS tags found in WordNet for the given word.
    Map: n->noun, v->verb, a/s->adj, r->adv
    """
    synsets = wordnet.synsets(word)
    pos_found = set()
    for syn in synsets:
        p = syn.pos()
        if p == 'n':
            pos_found.add('noun')
        elif p == 'v':
            pos_found.add('verb')
        elif p in ['a', 's']:
            pos_found.add('adj')
        elif p == 'r':
            pos_found.add('adv')
    return pos_found

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, '1000000_clean.txt')
    output_dir = os.path.join(base_dir, 'wordlist_new')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Reading from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    print(f"Loaded {len(words)} words. Starting classification...")

    # Categories
    categorized = {
        'nouns': set(),
        'verbs': set(),
        'adjectives': set(),
        'adverbs': set(),
        'pronouns': set(),
        'uncategorized': set()
    }
    
    # Common English Pronouns list to help classification (NLTK tagger can be tricky with single words)
    PRONOUNS_LIST = {
        'i', 'me', 'my', 'mine', 'myself',
        'we', 'us', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself',
        'she', 'her', 'hers', 'herself',
        'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves',
        'this', 'that', 'these', 'those',
        'who', 'whom', 'whose', 'which', 'what',
        'anybody', 'anyone', 'anything',
        'each', 'either', 'everybody', 'everyone', 'everything',
        'neither', 'nobody', 'noone', 'nothing', 'one',
        'somebody', 'someone', 'something',
        'both', 'few', 'many', 'several',
        'all', 'any', 'most', 'none', 'some'
    }

    count = 0
    for word in words:
        count += 1
        if count % 10000 == 0:
            print(f"Processed {count}/{len(words)} words...")
            
        # Check explicit pronoun list first
        if word in PRONOUNS_LIST:
            categorized['pronouns'].add(word)
            continue

        pos_set = get_wordnet_pos(word)
        
        if not pos_set:
            # Fallback: try nltk pos_tag for single word (heuristic)
            # Note: pos_tag(['word']) often defaults to NN (Noun) if ambiguous
            # But let's try.
            tags = nltk.pos_tag([word])
            tag = tags[0][1]
            
            if tag in ['PRP', 'PRP$', 'WP', 'WP$']: # Pronoun tags
                categorized['pronouns'].add(word)
            elif tag.startswith('N'):
                pos_set.add('noun')
            elif tag.startswith('V'):
                pos_set.add('verb')
            elif tag.startswith('J'):
                pos_set.add('adj')
            elif tag.startswith('R'):
                pos_set.add('adv')
            else:
                categorized['uncategorized'].add(word)
                continue

        # Add to respective sets
        if 'noun' in pos_set:
            categorized['nouns'].add(word)
        if 'verb' in pos_set:
            categorized['verbs'].add(word)
        if 'adj' in pos_set:
            categorized['adjectives'].add(word)
        if 'adv' in pos_set:
            categorized['adverbs'].add(word)

    print("Classification done. Writing files...")

    # Write outputs
    files_map = {
        'nouns': 'nouns.txt',
        'verbs': 'verb.txt',
        'adjectives': 'adjectives.txt',
        'adverbs': 'adverbs.txt',
        'pronouns': 'pronouns.txt',
        'uncategorized': 'others.txt'
    }

    for cat, filename in files_map.items():
        out_path = os.path.join(output_dir, filename)
        data = sorted(list(categorized[cat]))
        print(f"Writing {len(data)} words to {filename}...")
        with open(out_path, 'w', encoding='utf-8') as f:
            for w in data:
                f.write(w + '\n')

    print("All done!")

if __name__ == "__main__":
    main()
