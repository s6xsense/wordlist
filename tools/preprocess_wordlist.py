import argparse
import json
import sys
import re

try:
    from wordfreq import zipf_frequency
except Exception as e:
    zipf_frequency = None


WORD_RE = re.compile(r"^[a-z]+$")
VOWEL_RE = re.compile(r"[aeiouy]")


def normalize_word(w: str) -> str:
    return w.strip().lower()


def is_valid_word(w: str) -> bool:
    return len(w) >= 2 and bool(WORD_RE.match(w)) and bool(VOWEL_RE.search(w))


def compute_freq(word: str, lang: str = "en", decimals: int = 2) -> float:
    w = normalize_word(word)
    if not w or not is_valid_word(w):
        return 0.0
    if zipf_frequency is None:
        return 0.0
    try:
        val = float(zipf_frequency(w, lang))
    except Exception:
        val = 0.0
    # round to requested decimals
    return round(val, decimals)


def preprocess(input_path: str, output_path: str, lang: str = "en", decimals: int = 2, min_freq: float = 0.0):
    pairs = []
    seen = set()
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            w = normalize_word(line)
            if not w or w in seen or not is_valid_word(w):
                continue
            seen.add(w)
            val = compute_freq(w, lang=lang, decimals=decimals)
            if val > min_freq:
                pairs.append((w, val))
    # sort descending by frequency for stable writing order
    pairs.sort(key=lambda x: x[1], reverse=True)
    mapping = {w: v for (w, v) in pairs}
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(mapping, out, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Preprocess wordlist (txt) to JSON using wordfreq zipf frequency.")
    parser.add_argument("input", help="Path to input txt (one word per line)")
    parser.add_argument("output", help="Path to output JSON mapping")
    parser.add_argument("--lang", default="en", help="Language code for wordfreq (default: en)")
    parser.add_argument("--decimals", type=int, default=2, help="Rounding decimals (default: 2)")
    parser.add_argument("--min-freq", type=float, default=0.0, help="Filter out entries with zipf < min-freq (default: 0.0)")
    args = parser.parse_args()

    if zipf_frequency is None:
        print("ERROR: 'wordfreq' library not available. Install with: python -m pip install wordfreq", file=sys.stderr)
        sys.exit(1)

    preprocess(args.input, args.output, lang=args.lang, decimals=args.decimals, min_freq=args.min_freq)
    print(f"Wrote JSON to {args.output}")


if __name__ == "__main__":
    main()
