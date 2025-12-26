from itertools import permutations
from typing import Iterable, List, Optional
from nltk.corpus import wordnet as wn
import nltk

# Tool to solve Apple News+ Quartiles game
# Game format: 5 rows and 4 cols of 2-3 letter word fragments, which can themselves be words.
# Goal: Combine fragments to form all possible words, in particular the 5 fragment words (of which there are only 5)

# Ensure WordNet is downloaded
try:
    wn.synsets("test")
except LookupError:
    nltk.download("wordnet", quiet=True)

# Load secondary spell-checker for cross-validation
try:
    from spellchecker import SpellChecker
    _SPELL = SpellChecker(language='en')
except ImportError:
    _SPELL = None

# Load tertiary spell-checker (enchant) for triple cross-validation
try:
    import enchant
    _ENCHANT = enchant.Dict("en_US")
except (ImportError, Exception):
    _ENCHANT = None

# ANSI color codes
_GREEN = '\033[92m'
_RED = '\033[91m'
_YELLOW = '\033[93m'
_RESET = '\033[0m'

def check(w: str, debug: bool = False) -> str:
    """
    Returns validation status for a word using triple cross-validation.
    Stricter for shorter words (≤3 chars) which rarely show as green.
    
    :param w: Word to check.
    :type w: str
    :param debug: If True, print validation details
    :type debug: bool
    :return: 'valid' (green - all pass), 'unsure' (yellow - 2 pass), or 'invalid' (red - 1 or fewer pass)
    :rtype: str
    """
    if not w:
        return 'invalid'
    wl = w.lower()
    
    validators_passed = 0
    wordnet_valid = False
    spell_valid = False
    enchant_valid = False
    
    # Check NLTK WordNet
    if wn.synsets(wl):
        validators_passed += 1
        wordnet_valid = True
    
    # Check pyspellchecker if available
    if _SPELL:
        if wl not in _SPELL.unknown({wl}):
            validators_passed += 1
            spell_valid = True
    
    # Check pyenchant if available
    if _ENCHANT:
        if _ENCHANT.check(wl):
            validators_passed += 1
            enchant_valid = True
    
    if debug:
        print(f"\n{wl}: WordNet={wordnet_valid}, SpellChecker={spell_valid}, Enchant={enchant_valid}, Total={validators_passed}")
    
    # Stricter validation for short words (≤3 chars)
    is_short = len(wl) <= 3
    total_validators = 2 + (1 if _ENCHANT else 0)
    
    if is_short:
        # Short words: require all validators + must be in WordNet
        if validators_passed == total_validators and wordnet_valid:
            return 'valid'
        elif validators_passed >= 2 and wordnet_valid:
            return 'unsure'
        else:
            return 'invalid'
    else:
        # Longer words: standard validation
        if validators_passed == total_validators:
            return 'valid'
        elif validators_passed >= total_validators - 1 and wordnet_valid:
            return 'unsure'
        else:
            return 'invalid'

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
        
        # Ask if user wants debug mode
        debug_input = input("Show validation details? (y/n, default=n): ").lower().strip()
        debug_mode = debug_input == 'y'

        candidates = concat(fragments, minParts, maxParts)
        results = {}
        for w in candidates:
            status = check(w, debug=debug_mode)
            results[w] = status

        # Filter and color-code output
        valid_words = {w for w, status in results.items() if status == 'valid'}
        unsure_words = {w for w, status in results.items() if status == 'unsure'}
        
        if valid_words or unsure_words:
            output = sorted(valid_words | unsure_words, key=lambda s: (len(s), s))
            for w in output:
                if results[w] == 'valid':
                    print(f"{_GREEN}{w}{_RESET}")
                elif results[w] == 'unsure':
                    print(f"{_YELLOW}{w}{_RESET}")
            print(f"Total valid words: {len(valid_words)}")
            if unsure_words:
                print(f"Total unsure words: {len(unsure_words)}")
        else:
            print("No valid words found.")

if __name__ == "__main__":
    main()