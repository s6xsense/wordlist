import re
import sys

WORD_RE = re.compile(r"^[a-z]+$")

def is_valid_word(w: str) -> bool:
    # re.match with $ should check full string
    return bool(WORD_RE.match(w))

print(f"Checking 'series.1': {is_valid_word('series.1')}")
print(f"Checking 'series': {is_valid_word('series')}")

try:
    with open(r"c:\Project\Outside\s6xsense\wordlist\wordlist\nouns.txt", "r", encoding="utf-8") as f:
        found_series_1 = False
        found_gymslip = False
        for i, line in enumerate(f):
            w = line.strip()
            if w == 'series.1':
                found_series_1 = True
            if w == 'gymslip':
                found_gymslip = True
            if found_series_1 and found_gymslip:
                break
            if i > 1000000: break
        
        print(f"'series.1' found in nouns.txt: {found_series_1}")
        print(f"'gymslip' found in nouns.txt: {found_gymslip}")
except Exception as e:
    print(f"Error: {e}")
