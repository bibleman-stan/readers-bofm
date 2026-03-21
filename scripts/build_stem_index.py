#!/usr/bin/env python3
"""
Build a stem index for smart search in the Book of Mormon reader.

Extracts every unique word from all 15 book HTML files, stems each one
using a Porter stemmer implementation, and produces a JSON map:
  { stem: [word1, word2, ...] }

Only groups with 2+ word forms are included (single-form stems are
handled by direct match at search time). The output is loaded client-side
so the search can expand "live" → ["live","lived","lives","living","lively"].

If the user wraps their query in "quotes", the frontend skips stem expansion
and does exact substring matching (current behavior preserved).
"""

import json
import os
import re
from collections import defaultdict

# ============================================================================
# Porter Stemmer — faithful implementation of the original algorithm
# Reference: Porter, M.F., 1980, "An algorithm for suffix stripping"
# ============================================================================

class PorterStemmer:
    """Attempt to strip common English suffixes to find the word stem."""

    def __init__(self):
        # Irregular forms that the stemmer can't handle well
        self.irregulars = {
            'dying': 'die', 'lying': 'lie', 'tying': 'tie',
        }

    @staticmethod
    def _cons(word, i):
        """True if word[i] is a consonant."""
        if word[i] in 'aeiou':
            return False
        if word[i] == 'y':
            return i == 0 or not PorterStemmer._cons(word, i - 1)
        return True

    @staticmethod
    def _m(word, j):
        """Measure: the number of VC sequences in word[0:j+1]."""
        n = 0
        i = 0
        length = j + 1
        # Skip initial consonants
        while i < length:
            if not PorterStemmer._cons(word, i):
                break
            i += 1
        while i < length:
            # Count vowels
            while i < length:
                if PorterStemmer._cons(word, i):
                    break
                i += 1
            if i >= length:
                break
            n += 1
            # Count consonants
            while i < length:
                if not PorterStemmer._cons(word, i):
                    break
                i += 1
        return n

    @staticmethod
    def _vowelinstem(word, j):
        """True if word[0:j+1] contains a vowel."""
        for i in range(j + 1):
            if not PorterStemmer._cons(word, i):
                return True
        return False

    @staticmethod
    def _doublec(word, j):
        """True if j,(j-1) are same consonant."""
        if j < 1 or word[j] != word[j - 1]:
            return False
        return PorterStemmer._cons(word, j)

    @staticmethod
    def _cvc(word, j):
        """True if (j-2,j-1,j) is consonant-vowel-consonant and j not in w,x,y."""
        if j < 2 or not PorterStemmer._cons(word, j) or PorterStemmer._cons(word, j - 1) or not PorterStemmer._cons(word, j - 2):
            return False
        return word[j] not in 'wxy'

    @staticmethod
    def _ends(word, s):
        """True if word ends with s; sets stem to word minus s."""
        if word.endswith(s):
            return word[:-len(s)]
        return None

    def stem(self, word):
        word = word.lower().strip()
        if len(word) <= 2:
            return word
        if word in self.irregulars:
            return self.irregulars[word]

        # Step 1a
        if word.endswith('sses'):
            word = word[:-2]
        elif word.endswith('ies'):
            word = word[:-2]
        elif word.endswith('ss'):
            pass
        elif word.endswith('s'):
            word = word[:-1]

        # Step 1b
        flag = False
        if word.endswith('eed'):
            stem = word[:-3]
            if self._m(word, len(word) - 4) > 0:
                word = word[:-1]
        elif word.endswith('ed'):
            stem = word[:-2]
            if self._vowelinstem(word, len(word) - 3):
                word = stem
                flag = True
            # else no change
        elif word.endswith('ing'):
            stem = word[:-3]
            if self._vowelinstem(word, len(word) - 4):
                word = stem
                flag = True

        if flag:
            if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
                word += 'e'
            elif len(word) >= 2 and self._doublec(word, len(word) - 1) and word[-1] not in 'lsz':
                word = word[:-1]
            elif self._m(word, len(word) - 1) == 1 and self._cvc(word, len(word) - 1):
                word += 'e'

        # Step 1c
        if word.endswith('y') and self._vowelinstem(word, len(word) - 2):
            word = word[:-1] + 'i'

        # Step 2
        step2_map = {
            'ational': 'ate', 'tional': 'tion', 'enci': 'ence', 'anci': 'ance',
            'izer': 'ize', 'abli': 'able', 'alli': 'al', 'entli': 'ent',
            'eli': 'e', 'ousli': 'ous', 'ization': 'ize', 'ation': 'ate',
            'ator': 'ate', 'alism': 'al', 'iveness': 'ive', 'fulness': 'ful',
            'ousness': 'ous', 'aliti': 'al', 'iviti': 'ive', 'biliti': 'ble',
        }
        for suffix, replacement in sorted(step2_map.items(), key=lambda x: -len(x[0])):
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self._m(word, len(word) - len(suffix) - 1) > 0:
                    word = stem + replacement
                break

        # Step 3
        step3_map = {
            'icate': 'ic', 'ative': '', 'alize': 'al', 'iciti': 'ic',
            'ical': 'ic', 'ful': '', 'ness': '',
        }
        for suffix, replacement in sorted(step3_map.items(), key=lambda x: -len(x[0])):
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self._m(word, len(word) - len(suffix) - 1) > 0:
                    word = stem + replacement
                break

        # Step 4
        step4_suffixes = [
            'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant',
            'ement', 'ment', 'ent', 'ion', 'ou', 'ism', 'ate', 'iti',
            'ous', 'ive', 'ize',
        ]
        for suffix in sorted(step4_suffixes, key=lambda x: -len(x)):
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self._m(word, len(word) - len(suffix) - 1) > 1:
                    if suffix == 'ion' and len(stem) > 0 and stem[-1] in 'st':
                        word = stem
                    elif suffix != 'ion':
                        word = stem
                break

        # Step 5a
        if word.endswith('e'):
            stem = word[:-1]
            m = self._m(word, len(word) - 2)
            if m > 1 or (m == 1 and not self._cvc(word, len(word) - 2)):
                word = stem

        # Step 5b
        if self._m(word, len(word) - 1) > 1 and self._doublec(word, len(word) - 1) and word[-1] == 'l':
            word = word[:-1]

        return word


# ============================================================================
# Extra: manual groups for known tricky cases in the BOM
# The stemmer handles most regular forms, but some irregular verbs and
# noun/verb relationships need manual help.
# ============================================================================

MANUAL_GROUPS = {
    # be forms
    'be': ['be', 'am', 'is', 'are', 'was', 'were', 'been', 'being'],
    # have forms
    'have': ['have', 'has', 'had', 'having', 'hast', 'hath'],
    # do forms
    'do': ['do', 'does', 'did', 'doing', 'done', 'doth', 'doeth', 'dost'],
    # go forms
    'go': ['go', 'goes', 'went', 'going', 'gone', 'goeth'],
    # come
    'come': ['come', 'comes', 'came', 'coming', 'cometh'],
    # say / speak
    'say': ['say', 'says', 'said', 'saying', 'saith', 'sayeth'],
    'speak': ['speak', 'speaks', 'spoke', 'spoken', 'speaking', 'speaketh'],
    # know
    'know': ['know', 'knows', 'knew', 'known', 'knowing', 'knoweth'],
    # see
    'see': ['see', 'sees', 'saw', 'seen', 'seeing', 'seeth'],
    # give
    'give': ['give', 'gives', 'gave', 'given', 'giving', 'giveth'],
    # take
    'take': ['take', 'takes', 'took', 'taken', 'taking', 'taketh'],
    # make
    'make': ['make', 'makes', 'made', 'making', 'maketh'],
    # think
    'think': ['think', 'thinks', 'thought', 'thinking'],
    # bring
    'bring': ['bring', 'brings', 'brought', 'bringing', 'bringeth'],
    # teach
    'teach': ['teach', 'teaches', 'taught', 'teaching'],
    # seek
    'seek': ['seek', 'seeks', 'sought', 'seeking', 'seeketh'],
    # write
    'write': ['write', 'writes', 'wrote', 'written', 'writing'],
    # eat
    'eat': ['eat', 'eats', 'ate', 'eaten', 'eating'],
    # die / death / dead
    'die': ['die', 'dies', 'died', 'dying', 'death', 'dead'],
    # live / life
    'live': ['live', 'lives', 'lived', 'living', 'lively', 'life', 'liveth'],
    # child / children
    'child': ['child', 'children'],
    # man / men
    'man': ['man', 'men'],
    # woman / women
    'woman': ['woman', 'women'],
    # people / person
    'people': ['people', 'peoples', 'person', 'persons'],
    # slay / slain
    'slay': ['slay', 'slays', 'slew', 'slain', 'slaying'],
    # smite
    'smite': ['smite', 'smites', 'smote', 'smitten', 'smiting'],
    # arise
    'arise': ['arise', 'arises', 'arose', 'arisen', 'arising'],
    # begin
    'begin': ['begin', 'begins', 'began', 'begun', 'beginning'],
    # fight
    'fight': ['fight', 'fights', 'fought', 'fighting'],
    # lead
    'lead': ['lead', 'leads', 'led', 'leading'],
    # fall
    'fall': ['fall', 'falls', 'fell', 'fallen', 'falling'],
    # bear
    'bear': ['bear', 'bears', 'bore', 'born', 'borne', 'bearing'],
    # choose
    'choose': ['choose', 'chooses', 'chose', 'chosen', 'choosing'],
    # forget
    'forget': ['forget', 'forgets', 'forgot', 'forgotten', 'forgetting'],
    # forsake
    'forsake': ['forsake', 'forsakes', 'forsook', 'forsaken', 'forsaking'],
    # hide
    'hide': ['hide', 'hides', 'hid', 'hidden', 'hiding'],
    # swear
    'swear': ['swear', 'swears', 'swore', 'sworn', 'swearing', 'sweareth'],
    # KJV-style verb forms
    'shall': ['shall', 'shalt'],
    'will': ['will', 'wilt'],
    'thou': ['thou', 'thee', 'thy', 'thine', 'thyself'],
    'ye': ['ye', 'you', 'your', 'yours', 'yourselves', 'yourself'],
    'we': ['we', 'us', 'our', 'ours', 'ourselves'],
    'they': ['they', 'them', 'their', 'theirs', 'themselves'],
    'he': ['he', 'him', 'his', 'himself'],
    'she': ['she', 'her', 'hers', 'herself'],
    'who': ['who', 'whom', 'whose'],
}


def extract_words_from_html(html_dir):
    """Extract all unique lowercase words from book HTML files."""
    words = set()
    word_re = re.compile(r"[a-zA-Z']+")

    for fname in sorted(os.listdir(html_dir)):
        if not fname.endswith('.html'):
            continue
        path = os.path.join(html_dir, fname)
        with open(path) as f:
            html = f.read()

        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Extract words (at least 2 chars, allow apostrophes inside)
        for m in word_re.finditer(text):
            w = m.group().lower().strip("'")
            if len(w) >= 2:
                words.add(w)

    return words


def build_stem_map(words):
    """
    Build stem → [word forms] map.
    Uses Porter stemmer for regular forms, then merges manual groups.
    """
    stemmer = PorterStemmer()
    stem_groups = defaultdict(set)

    # Build word → manual_group_key lookup
    manual_word_to_key = {}
    for key, forms in MANUAL_GROUPS.items():
        for form in forms:
            manual_word_to_key[form] = key

    # Words that are NOT archaic verb forms despite ending in -eth/-est
    NOT_ARCHAIC_ETH = {
        'nazareth', 'teeth', 'beneath', 'seth', 'ieth',  # ordinals
        'eightieth', 'fiftieth', 'fortieth', 'ninetieth', 'sixtieth',
        'thirtieth', 'twentieth',
    }
    NOT_ARCHAIC_EST = {
        'forest', 'harvest', 'honest', 'interest', 'manifest', 'priest',
        'request', 'tempest', 'molest', 'infest', 'arrest', 'protest',
        'wrest', 'eldest', 'greatest', 'smallest', 'strongest', 'weakest',
        'youngest', 'poorest', 'longest', 'fastest', 'darkest', 'chiefest',
        'grossest', 'vilest', 'clearest',
    }

    def strip_archaic(w):
        """Strip KJV-era -eth/-est suffixes to find base verb.
        Returns base form or None if not an archaic form."""
        if w.endswith('eth') and len(w) > 4 and w not in NOT_ARCHAIC_ETH:
            base = w[:-3]
            # Handle cases like 'cometh' → 'come' (add silent e)
            # and 'liveth' → 'live'
            if base + 'e' in words:
                return base + 'e'
            if base in words:
                return base
            # Handle 'ieth' → 'y' (e.g. 'crieth' → 'cry', 'prophesieth' → 'prophesy')
            if base.endswith('i'):
                ybase = base[:-1] + 'y'
                if ybase in words:
                    return ybase
            return base  # best guess
        if w.endswith('est') and len(w) > 4 and w not in NOT_ARCHAIC_EST:
            base = w[:-3]
            if base + 'e' in words:
                return base + 'e'
            if base in words:
                return base
            if base.endswith('i'):
                ybase = base[:-1] + 'y'
                if ybase in words:
                    return ybase
            # Handle 'sawest' → 'saw', 'knewest' → 'knew'
            if base + 'st' in words:
                return None  # e.g. 'knewest' — handled by manual groups
            return base
        return None

    # First pass: stem all words
    for w in words:
        if w in manual_word_to_key:
            # Use manual group key as stem
            stem_groups[manual_word_to_key[w]].add(w)
        else:
            stem = stemmer.stem(w)
            stem_groups[stem].add(w)

    # Second pass: resolve archaic -eth/-est forms
    # Group them with their base word's stem group
    for w in words:
        if w in manual_word_to_key:
            continue  # already handled
        base = strip_archaic(w)
        if base:
            # Find the stem group that contains the base word
            base_stem = stemmer.stem(base)
            if base in manual_word_to_key:
                base_stem = manual_word_to_key[base]
            # Add the archaic form to the base's group
            stem_groups[base_stem].add(w)
            if base in words:
                stem_groups[base_stem].add(base)

    # Merge: for manual groups, ensure the manual key's stem group exists
    # and add any stemmer-derived matches
    for key, forms in MANUAL_GROUPS.items():
        existing = stem_groups.get(key, set())
        for form in forms:
            if form in words:
                existing.add(form)
        if existing:
            stem_groups[key] = existing

    return stem_groups


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    html_dir = os.path.join(base, 'books')
    out_path = os.path.join(base, 'data', 'stem_index.json')

    print("Extracting vocabulary from book HTML files...")
    words = extract_words_from_html(html_dir)
    print(f"  {len(words)} unique words found")

    print("Building stem index...")
    stem_map = build_stem_map(words)

    # Only keep groups with 2+ members (single-word stems are identity lookups)
    multi = {stem: sorted(forms) for stem, forms in stem_map.items() if len(forms) >= 2}
    singles = len(stem_map) - len(multi)
    print(f"  {len(multi)} stem groups (2+ forms), {singles} single-form stems skipped")

    # Show some example groups
    examples = ['live', 'die', 'know', 'fight', 'come', 'say', 'begin']
    for ex in examples:
        if ex in multi:
            print(f"    {ex}: {multi[ex]}")

    # Write JSON
    with open(out_path, 'w') as f:
        json.dump(multi, f, separators=(',', ':'))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"\n  Output: {out_path} ({size_kb:.0f} KB)")


if __name__ == '__main__':
    main()
