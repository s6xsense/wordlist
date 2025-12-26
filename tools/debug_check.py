import re

WORD_RE = re.compile(r"^[a-z]+$")
VOWEL_RE = re.compile(r"[aeiouy]")

def is_valid_word(w: str) -> bool:
    return len(w) >= 2 and bool(WORD_RE.match(w)) and bool(VOWEL_RE.search(w))

print(f"Checking 'series.1': {is_valid_word('series.1')}")
print(f"Checking 'seriesof': {is_valid_word('seriesof')}")
print(f"Checking 'gymslip': {is_valid_word('gymslip')}")

with open(r"c:\Project\Outside\s6xsense\wordlist\wordlist\nouns.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(f"'gymslip' in nouns.txt: {'gymslip' in content.splitlines()}")
    print(f"'series.1' in nouns.txt: {'series.1' in content.splitlines()}")
