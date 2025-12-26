from nltk.corpus import wordnet as wn
from itertools import permutations
from typing import Iterable, List, Optional

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
    if not w: 
        return False
    wl = w.lower()
    # direct lookup
    if wn.synsets(wl):
        return True
    # try common morphological variants: single/plural/verb forms
    lemma = wn.morphy(wl)
    if lemma and wn.morphy(wl):
        return True
    return False # invalid

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
        words = input("Enter all word fragments separated with spaces: ").split() # input words, split into list
        if words.len() == 20:
            break
        else:
            print("Incorrect format: please input all 20 words separated with spaces.")


    pass