# quartilesSolver

Solves the Apple News+ Quartiles game by finding valid English words from 2-3 letter fragments.

## Requirements

- Python 3.6+
- `nltk` with WordNet corpus
- `pyspellchecker` (optional, improves accuracy)
- `pyenchant` (optional, improves accuracy)

## Usage

Run `python3 main.py` and enter fragments separated by spaces.

Results show valid (green) and unsure (yellow) words. Invalid words are counted but not displayed.

## Features

- Triple cross-validation (WordNet, pyspellchecker, pyenchant)
- Color-coded confidence levels
- Statistics: success rate, length distribution, vowel content, top starting letters
- Debug mode for validation details

**Note:** Validation is not 100% accurate. Dictionary coverage varies and some valid/invalid words may be misclassified.