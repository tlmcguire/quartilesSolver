from nltk.corpus import wordnet as wn
from itertools import permutations
from typing import Iterable, List, Optional
import nltk

_WORDNET_READY = False


def ensure_wordnet() -> None:
    """Make sure the WordNet corpus is available locally."""
    global _WORDNET_READY
    if _WORDNET_READY:
        return
    try:
        wn.synsets("test")
        _WORDNET_READY = True
    except LookupError:
        try:
            nltk.download("wordnet", quiet=True, raise_on_error=True)
        except ValueError:
            # macOS python.org builds sometimes lack system certs; try certifi bundle
            try:
                import ssl
                import certifi

                # Reset in case it was set to a non-callable SSLContext instance
                ssl._create_default_https_context = ssl.create_default_context
                ssl._create_default_https_context = lambda *_, **__: ssl.create_default_context(cafile=certifi.where())
                nltk.download("wordnet", quiet=True, raise_on_error=True)
            except Exception:
                raise
        wn.synsets("test")
        _WORDNET_READY = True

# Tool to solve Apple News+ Quartiles game
# Game format: 5 rows and 4 cols of 2-3 letter word fragments, which can themselves be words.
# Goal: Combine fragments to form all possible words, in particular the 5 fragment words (of which there are only 5)

def check(w: str) -> bool:
    """
    Returns true if 'w' is a valid English word.
    
    :param w: Word to check.
    :type w: str
    :return: True if valid, false if invalid
    :rtype: bool
    """
    ensure_wordnet()
    if not w:
        return False
    wl = w.lower()
    # require WordNet lemma matches the exact surface form and has some corpus frequency
    syns = wn.synsets(wl)
    if not syns:
        return False
    lemma_counts = [l.count() for s in syns for l in s.lemmas() if l.name().lower() == wl]
    if lemma_counts and max(lemma_counts) >= 2:
        return True
    # fallback to morphological variant if nothing matched exactly but WordNet knows the root
    lemma = wn.morphy(wl)
    if lemma and wn.synsets(lemma):
        return True
    return False  # invalid

def concat(fragments: Iterable[str], minParts: int=1, maxParts: Optional[int] = None) -> List[str]:
    """
    Returns a list of concatenated permutations of distinct fragments.
    
    :param fragments: 
    :type fragments: Iterable[str]
    :param minParts: minimum number of fragments in a concatenation (>=1)
    :type minParts: int
    :param maxParts: maximum number of fragments in a concatenation (<= len(fragments)). If none, uses len(fragments).
    :type maxParts: Optional[int]
    :return: Description
    :rtype: List[str]
    """
    frags = list(fragments)
    n = len(frags)
    if n == 0:
        return []
    if maxParts is None:
        maxParts = n
    minParts = max(1, int(minParts))
    maxParts = min(n, int(maxParts))
    if minParts > maxParts:
        return []
    
    results: List[str] = []
    for k in range(minParts, maxParts + 1):
        for perm in permutations(frags, k):
            results.append("".join(perm))
    return results

def main():
    while True:
        raw = input("Enter all word fragments separated by spaces (or 'q' to quit): ").lower().strip()
        if not raw:
            print("Enter at least one fragment.")
            continue
        if raw.lower() in {"q"}:
            break

        fragments = raw.split()
        minParts, maxParts = 1, 4

        ensure_wordnet()
        
        candidates = concat(fragments, minParts, maxParts)
        valid = sorted({w for w in candidates if check(w)}, key=lambda s: (len(s), s))

        if valid:
            for w in valid:
                print(w)
            print(f"Total valid words: {len(valid)}")
        else:
            print("No valid words found.")

if __name__ == "__main__":
    main()