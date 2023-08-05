# TODO items:
# leetspeak

import re
import os.path
import pkg_resources


def _data_file(filename):
    return pkg_resources.resource_filename(__name__, filename)


profane_words = set()
obvious_profane_words = set()
with open(_data_file('profane_words.txt')) as f:
    for line in f.readlines():
        word = line.strip().lower()
        if word == '':
            continue
        # Particularly bad profanity is marked with a star.
        if word.startswith('*'):
            word = word.lstrip('*')
            obvious_profane_words.add(word)
        # Words of length six or more are considered obvious as well.
        if len(word) >= 6:
            obvious_profane_words.add(word)
        profane_words.add(word)

word_frequency = {}
with open(_data_file('word_frequency.txt')) as f:
    for line in f.readlines():
        row = line.strip().lower().split()
        freq = float(row[0])
        word = row[1]
        word_frequency[word] = freq


def is_profane(text):
    return (
        _is_profane(text) or
        _is_profane(remove_leet(text))
    )


def _is_profane(text):
    # Preprocessing.
    text = text.lower()
    text = re.sub(r'[^a-z]+', ' ', text)
    text = text.strip()

    # Find substrings that are obvious profane words, even if we don't
    # understand the remainder of the string.
    for word in obvious_profane_words:
        if word in text:
            return True

    # Try to split the text and find individual profane words.
    words = split_words(text)
    for word in words:
        if word in profane_words:
            return True

    return False


def split_words(text):
    def _split_words(text, cache):
        # Reference:
        # http://stackoverflow.com/questions/2174093/python-word-splitting
        if text in cache:
            return cache[text]
        if not text:
            return 1, []
        best_freq, best_split = word_frequency.get(text, 0), [text]
        for i in range(1, len(text)):
            word, remainder = text[:i], text[i:]
            freq = word_frequency.get(word, None)
            if freq:
                # Penalize short words.
                if len(word) == 1:
                    freq /= 1000
                remainder_freq, remainder = _split_words(remainder, cache)
                freq *= remainder_freq
                if freq > best_freq:
                    best_freq = freq
                    best_split = [word] + remainder
        cache[text] = (best_freq, best_split)
        return cache[text]

    total_freq = 1.0
    words = []
    for chunk in text.split():
        freq, split = _split_words(chunk, {})
        total_freq *= freq
        words.extend(split)

    return words


def remove_leet(text):
    tr = {
        '0': 'o',
        '1': 'i',
        '|': 'i',
        '3': 'e',
        '5': 's',
    }
    return ''.join(
        tr.get(c, c)
        for c in text
    )


if __name__ == '__main__':
    import sys
    import os

    good = []
    bad = []

    filename = sys.argv[1]
    with open(filename) as f:
        seen = set()
        for line in f.readlines():
            line = line.strip()
            if line == '':
                continue
            if line in seen:
                continue
            seen.add(line)
            if is_profane(line):
                bad.append(line)
            else:
                good.append(line)

    with open(os.path.basename(filename) + '.good', 'w') as f:
        for line in good:
            f.write(line + '\n')

    with open(os.path.basename(filename) + '.bad', 'w') as f:
        for line in bad:
            f.write(line + '\n')
