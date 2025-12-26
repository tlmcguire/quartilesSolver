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
        invalid_words = {w for w, status in results.items() if status == 'invalid'}
        
        if valid_words or unsure_words:
            output = sorted(valid_words | unsure_words, key=lambda s: (len(s), s))
            for w in output:
                if results[w] == 'valid':
                    print(f"{_GREEN}{w}{_RESET}")
                elif results[w] == 'unsure':
                    print(f"{_YELLOW}{w}{_RESET}")
            
            # Calculate stats
            all_good_words = list(valid_words | unsure_words)
            total_candidates = len(results)
            
            if all_good_words:
                longest = max(all_good_words, key=len)
                shortest = min(all_good_words, key=len)
                avg_length = sum(len(w) for w in all_good_words) / len(all_good_words)
                
                # Count by length
                from collections import Counter
                length_dist = Counter(len(w) for w in all_good_words)
                
                # Calculate vowel stats
                vowels = 'aeiou'
                total_letters = sum(len(w) for w in all_good_words)
                vowel_count = sum(sum(1 for c in w if c.lower() in vowels) for w in all_good_words)
                vowel_pct = (vowel_count / total_letters * 100) if total_letters > 0 else 0
                
                # Success rate
                success_rate = (len(all_good_words) / total_candidates * 100) if total_candidates > 0 else 0
                valid_rate = (len(valid_words) / len(all_good_words) * 100) if all_good_words else 0
                
                # Most common starting letters
                starting_letters = Counter(w[0].lower() for w in all_good_words)
                top_starters = starting_letters.most_common(3)
                
                print(f"\n--- Statistics ---")
                print(f"Total candidates checked: {total_candidates}")
                print(f"Success rate: {success_rate:.2f}% ({len(all_good_words)} found)")
                print(f"  Valid (green): {len(valid_words)} ({valid_rate:.1f}% of found)")
                if unsure_words:
                    unsure_rate = (len(unsure_words) / len(all_good_words) * 100) if all_good_words else 0
                    print(f"  Unsure (yellow): {len(unsure_words)} ({unsure_rate:.1f}% of found)")
                print(f"  Invalid: {len(invalid_words)}")
                print(f"\nLongest word: {_GREEN}{longest}{_RESET} ({len(longest)} letters)")
                print(f"Shortest word: {_YELLOW}{shortest}{_RESET} ({len(shortest)} letters)")
                print(f"Average length: {avg_length:.1f} letters")
                print(f"Vowel content: {vowel_pct:.1f}% ({vowel_count}/{total_letters} letters)")
                print(f"Length distribution: {dict(sorted(length_dist.items()))}")
                print(f"Top starting letters: {', '.join(f'{letter}({count})' for letter, count in top_starters)}")
            else:
                print(f"\n--- Statistics ---")
                print(f"Total candidates checked: {total_candidates}")
                print(f"Total valid words: {len(valid_words)}")
                if unsure_words:
                    print(f"Total unsure words: {len(unsure_words)}")
                if invalid_words:
                    print(f"Total invalid words: {len(invalid_words)}")
        else:
            print("No valid words found.")
            if invalid_words:
                print(f"Total invalid words: {len(invalid_words)}")

if __name__ == "__main__":
    main()