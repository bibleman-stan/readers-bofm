#!/usr/bin/env python3
"""
Sense-Line Reformatter v5: Skousen → Stan
==========================================

INSTRUCTIONS FOR CLAUDE:
When the user uploads this script along with a .txt file, do the following:
1. Run this script against the uploaded .txt file.
   Command: python3 senseline_reformat_v5.py INPUT.txt OUTPUT.txt
2. Show the stats (printed to stdout).
3. Show the first 3-4 verses of the output so the user can spot-check.
4. Deliver the output file.
5. Wait for the user to spot-check and point out problems.
   Each problem they find is either:
   (a) a new mechanical rule to add to this script, or
   (b) confirmation that something is genuinely editorial.
   Work with the user to determine which, then update the script if needed.

The input is Skousen-formatted Book of Mormon text: verse markers (e.g. "1:1")
on their own line, followed by sense-lines, separated by blank lines between verses.

Deterministic mechanical passes. Same input → same output every time.

Rules applied in order:
  M0:  Em dash trailing word reattachment
  M1:  AICTP isolation
  M2:  Behold mid-line hinge split
  M3:  Yea trailing → launching
  M4:  Insomuch split
  M5:  Vocative split
  M6:  According-to split (lines >58)
  M7:  Speech verb + content word split (lines ≥48)
  M8:  ", and [subject pronoun]" split (lines 45-70, non-triad)
  M9:  Subject-predicate split at modal verbs (lines >70)
  M10: Long-line pattern-priority split (lines >70)
  M11: Speech frame split ("said he," → speech on new line)
  M12: "in [gerund]" split (any length)
  M13: "made an end of [gerund]" split (any length)
  M14: Inverted conditional consequence split ("had we... / we should...")
  M15: Passive verb + directional prep split (lines ≥50, excludes motion verbs)
  M16: Deity appositive split (DEITY, DEITY → separate lines, ≥40 chars)
"""

import re
import sys

# ============================================================
# CONFIGURATION
# ============================================================

SPEECH_VERBS = [
    'sufficeth me to say', 'made known', 'make known',
    'spake', 'spoke', 'speak', 'speaketh', 'spoken',
    'said', 'say', 'saith',
    'rehearsed', 'testified', 'testify', 'testifieth',
    'prophesy', 'prophesied', 'prophesieth',
    'preached', 'preach',
    'taught', 'teach', 'teacheth',
    'told', 'tell',
    'cried', 'cry',
    'declared', 'declare',
    'witnessed', 'witnessing', 'witness',
    'written', 'write', 'writeth',
    'showed', 'show', 'showeth',
]
SPEECH_VERBS.sort(key=len, reverse=True)
VERB_PAT = '|'.join(re.escape(v) for v in SPEECH_VERBS)
RECIPIENT_PAT = (
    r'(?:\s+(?:unto|to)\s+(?:them|him|her|you|us|me|all'
    r'|the\s+\w+|his\s+\w+|my\s+\w+|thy\s+\w+|our\s+\w+|\w+))?'
)

CONTENT_AFTER_THAT = [
    'he ', 'she ', 'they ', 'ye ', 'I ', 'we ', 'it ',
    'the ', 'a ', 'an ', 'as ', 'there ', 'this ', 'those ',
    'when ', 'if ', 'in ', 'all ', 'my ', 'his ', 'her ', 'our ',
    'your ', 'thy ', 'their ', 'no ', 'not ', 'from ',
]

VOCATIVE_ADDRESSES = [
    'my beloved brethren', 'my brethren', 'my sons', 'my son',
    'my people', 'Lord', 'house of Israel', 'ye people',
    'captive daughter of Zion',
]
_voc_alts = '|'.join(re.escape(a) for a in sorted(VOCATIVE_ADDRESSES, key=len, reverse=True))
VOCATIVE_PAT = re.compile(
    rf'^(O[, ]+(?:{_voc_alts})[,!]?)\s+(.{{15,}})$',
    re.IGNORECASE
)

BREAK_PATTERNS_COMMA = [
    (r':\s', 'after'),
    (r';\s', 'after'),
    (r'--', 'after'),
    (r',\s+(and\s)', 'before_word'),
    (r',\s+(that\s)', 'before_word'),
    (r',\s+(which\s)', 'before_word'),
    (r',\s+(but\s)', 'before_word'),
    (r',\s+(for\s)', 'before_word'),
    (r',\s+(because\s)', 'before_word'),
    (r',\s+(even\s)', 'before_word'),
    (r',\s+(save\s)', 'before_word'),
    (r',\s+(unto\s)', 'before_word'),
    (r',\s+(upon\s)', 'before_word'),
    (r',\s+(from\s)', 'before_word'),
    (r',\s+(in\s)', 'before_word'),
    (r',\s+(to\s)', 'before_word'),
    (r',\s+(or\s)', 'before_word'),
    (r',\s+(nor\s)', 'before_word'),
    (r',\s+(neither\s)', 'before_word'),
    (r',\s+(until\s)', 'before_word'),
    (r',\s+(after\s)', 'before_word'),
    (r',\s+(before\s)', 'before_word'),
    (r',\s+(lest\s)', 'before_word'),
    (r',\s+(saith\s)', 'before_word'),
    (r',\s+(according\s)', 'before_word'),
]

BREAK_PATTERNS_NOCOMMA = [
    (r'\s+(unto the\s)', 'before'),
    (r'\s+(upon the\s)', 'before'),
    (r'\s+(from the\s)', 'before'),
    (r'\s+(into the\s)', 'before'),
    (r'\s+(in the\s)', 'before'),
    (r'\s+(by the\s)', 'before'),
    (r'\s+(among the\s)', 'before'),
    (r'\s+(among all\s)', 'before'),
    (r'\s+(before the\s)', 'before'),
    (r'\s+(after the\s)', 'before'),
    (r'\s+(against the\s)', 'before'),
    (r'\s+(concerning\s)', 'before'),
    (r'\s+(down to\s)', 'before'),
    (r'\s+(out of\s)', 'before'),
    (r'\s+(save it be\s)', 'before'),
]

MODALS_PAT = re.compile(
    r'\b(shall |will |should |would |must |can |could |may |might )'
)
SPEECH_NEAR_PAT = re.compile(r'(said|saith|spake|spoke|say |says )')


# ============================================================
# M0: EM DASH TRAILING WORD REATTACHMENT
# ============================================================

def m0_emdash_trailing(lines):
    """Line ending --word: move word to start of next line."""
    result = list(lines)
    i = 0
    while i < len(result) - 1:
        m = re.match(r'^(.+)--([\w]+[,;.]?)$', result[i])
        if m:
            result[i] = m.group(1) + '--'
            result[i + 1] = m.group(2) + ' ' + result[i + 1]
        i += 1
    return result


# ============================================================
# M1: AICTP ISOLATION
# ============================================================

AICTP_FORMULAS = [
    'And now it came to pass that ',
    'And it came to pass that ',
    'For it came to pass that ',
    'Wherefore it came to pass that ',
    'And it came to pass, ',
]

def m1_aictp(lines):
    """AICTP on its own line when total > 42 chars."""
    result = []
    for line in lines:
        handled = False
        for formula in AICTP_FORMULAS:
            if line.startswith(formula) and len(line) > 42:
                result.append(formula.rstrip())
                result.append(line[len(formula):])
                handled = True
                break
        if handled:
            continue
        if (line.startswith('And it came to pass ')
                and not line.startswith('And it came to pass that')
                and len(line) > 40):
            result.append('And it came to pass')
            result.append(line[len('And it came to pass '):])
            continue
        result.append(line)
    return result


# ============================================================
# M2: BEHOLD MID-LINE HINGE
# ============================================================

def m2_behold_hinge(lines):
    """Mid-line behold after punctuation: split before behold."""
    result = []
    for line in lines:
        m = re.search(
            r'^(.{15,}?)(,\s+|;\s+|--\s*)(behold[,;]?\s.+)$',
            line, re.IGNORECASE
        )
        if m and len(m.group(1)) >= 15 and len(m.group(3)) >= 15:
            result.append(m.group(1) + m.group(2).rstrip())
            result.append(m.group(3))
        else:
            result.append(line)
    return result


# ============================================================
# M3: YEA TRAILING → LAUNCHING
# ============================================================

def m3_yea_trailing(lines):
    """', yea,' and '--yea,' move yea to next line."""
    result = []
    for line in lines:
        m = re.search(r'^(.{10,}?),\s+(yea,\s+.+)$', line)
        if m:
            result.append(m.group(1) + ',')
            result.append(m.group(2))
            continue
        m = re.search(r'^(.{10,?})--\s*(yea,\s+.+)$', line)
        if m:
            result.append(m.group(1) + '--')
            result.append(m.group(2))
            continue
        result.append(line)
    return result


# ============================================================
# M4: INSOMUCH SPLIT
# ============================================================

def m4_insomuch(lines):
    """'insomuch that' starts its own line."""
    result = []
    for line in lines:
        m = re.search(
            r'^(.{10,}?)\s+(insomuch\s+that\s+.+)$', line, re.IGNORECASE
        )
        if m:
            result.append(m.group(1))
            result.append(m.group(2))
        else:
            result.append(line)
    return result


# ============================================================
# M5: VOCATIVE SPLIT
# ============================================================

def m5_vocative(lines):
    """'O, my beloved brethren,' gets its own line."""
    result = []
    for line in lines:
        if len(line) > 40:
            m = VOCATIVE_PAT.match(line)
            if m:
                result.append(m.group(1))
                result.append(m.group(2))
                continue
        result.append(line)
    return result


# ============================================================
# M6: ACCORDING-TO SPLIT
# ============================================================

def m6_according_to(lines):
    """', according to' splits on lines > 58 chars."""
    result = []
    for line in lines:
        if len(line) > 58:
            m = re.search(r'^(.{20,}?),\s+(according to\s.+)$', line)
            if m:
                result.append(m.group(1) + ',')
                result.append(m.group(2))
                continue
        result.append(line)
    return result


# ============================================================
# M7: SPEECH VERB + CONTENT WORD SPLIT
# ============================================================

def m7_speech_content(lines):
    """Speech verb + recipient + content word: split before content."""
    result = []
    for line in lines:
        if len(line) < 48:
            result.append(line)
            continue
        split = _find_speech_content_split(line)
        if split:
            result.append(split[0])
            result.append(split[1])
        else:
            result.append(line)
    return result


def _find_speech_content_split(line):
    for content_word, extra_check in [
        ('concerning', None),
        ('how', None),
        ('that', 'content_clause_check'),
        ('all things what', None),
        ('all things that', None),
    ]:
        pat = rf'(?:{VERB_PAT}){RECIPIENT_PAT}\s*,?\s+({re.escape(content_word)}\s)'
        m = re.search(pat, line, re.IGNORECASE)
        if not m:
            continue

        idx = m.start(1)

        if extra_check == 'content_clause_check':
            after = line[idx + 5:]
            if not any(after.startswith(s) for s in CONTENT_AFTER_THAT):
                continue

        left = line[:idx].rstrip(', ')
        right = line[idx:]
        if len(left) >= 18 and len(right) >= 18:
            return (left, right)

    return None


# ============================================================
# M8: ", AND [SUBJECT PRONOUN]" SPLIT
# ============================================================

_AND_PRONOUN_PAT = re.compile(r', and (I |he |she |they |we |ye |it |thou )')

def m8_and_pronoun(lines):
    """', and [subject pronoun]' on lines 45-70, skipping triads."""
    result = []
    for line in lines:
        if 45 <= len(line) <= 70:
            if len(re.findall(r', and ', line)) >= 2:
                result.append(line)
                continue
            m = _AND_PRONOUN_PAT.search(line)
            if m and m.start() >= 18 and (len(line) - m.start() - 1) >= 18:
                left = line[:m.start() + 1]
                right = line[m.start() + 2:]
                result.append(left)
                result.append(right)
                continue
        result.append(line)
    return result


# ============================================================
# M9: SUBJECT-PREDICATE SPLIT AT MODAL VERBS
# ============================================================

def m9_subject_predicate(lines):
    """Long subject + modal verb on lines > 70: split before modal."""
    result = []
    for line in lines:
        if len(line) <= 70:
            result.append(line)
            continue

        split_done = False
        for m in MODALS_PAT.finditer(line):
            pos = m.start()
            left = line[:pos].rstrip()
            right = line[pos:]

            # Guard: left side ≥ 30 (genuinely long subject)
            if len(left) < 30:
                continue
            # Guard: right side ≥ 20
            if len(right) < 20:
                continue
            # Guard: no comma within 5 chars before modal
            if ',' in line[max(0, pos - 5):pos]:
                continue
            # Guard: no "that" within 10 chars before (it's a that-clause)
            if 'that ' in line[max(0, pos - 10):pos]:
                continue
            # Guard: no speech verb within 15 chars before (reported speech)
            if SPEECH_NEAR_PAT.search(line[max(0, pos - 15):pos]):
                continue
            # Guard: no "save" or "if" within 10 chars before (conditional)
            near = line[max(0, pos - 10):pos]
            if 'save ' in near or ' if ' in near:
                continue

            result.append(left)
            result.append(right)
            split_done = True
            break

        if not split_done:
            result.append(line)
    return result


# ============================================================
# M10: LONG-LINE PATTERN-PRIORITY SPLIT
# ============================================================

def _best_pos(line, matches, pos_fn, min_left=18, min_right=15):
    """Find match closest to center that satisfies min half lengths."""
    center = len(line) / 2
    best = None
    best_dist = float('inf')
    for m in matches:
        pos = pos_fn(m)
        if pos >= min_left and (len(line) - pos) >= min_right:
            dist = abs(pos - center)
            if dist < best_dist:
                best_dist = dist
                best = pos
    return best


def _find_long_line_break(line, threshold=70):
    """Pattern-priority break for lines over threshold."""
    if len(line) <= threshold:
        return None

    # Comma-based patterns
    for pat, btype in BREAK_PATTERNS_COMMA:
        matches = list(re.finditer(pat, line))
        if not matches:
            continue
        if btype == 'after':
            pos = _best_pos(line, matches, lambda m: m.end())
        elif btype == 'before_word':
            pos = _best_pos(line, matches, lambda m: m.start() + 1)
        else:
            pos = None
        if pos:
            return pos

    # Bare "that" + content word (>70)
    matches = list(re.finditer(r'(?<!,)\s(that\s)', line))
    valid = [m for m in matches
             if any(line[m.end():].startswith(s) for s in CONTENT_AFTER_THAT)]
    if valid:
        pos = _best_pos(line, valid, lambda m: m.start() + 1)
        if pos:
            return pos

    # Non-comma prep patterns (>75 only)
    if len(line) > 75:
        for pat, _ in BREAK_PATTERNS_NOCOMMA:
            matches = list(re.finditer(pat, line))
            if matches:
                pos = _best_pos(line, matches, lambda m: m.start() + 1)
                if pos:
                    return pos

        # Fallback: any comma
        matches = list(re.finditer(r',\s+', line))
        if matches:
            pos = _best_pos(line, matches, lambda m: m.start() + 1)
            if pos:
                return pos

    return None


def m10_split_long(lines, threshold=70):
    """Split lines over threshold using pattern priority."""
    result = []
    for line in lines:
        if len(line) <= threshold:
            result.append(line)
            continue
        pos = _find_long_line_break(line, threshold)
        if pos:
            left = line[:pos].rstrip()
            right = line[pos:].lstrip()
            for part in [left, right]:
                if len(part) > threshold:
                    result.extend(m10_split_long([part], threshold))
                else:
                    result.append(part)
        else:
            result.append(line)
    return result


# ============================================================
# M11: SPEECH FRAME SPLIT
# ============================================================

_SPEECH_FRAME_PAT = re.compile(
    r'^(.+(?:'
    # Inverted: "said he," / "saith she,"
    r'(?:said|saith)\s+(?:he|she|they|I)'
    r'|'
    # Normal: "God hath said," / "the Lord saith," / "he said,"
    r'(?:God|the Lord God|the Lord|Christ|the Messiah|the Spirit|he|she|they|I)\s+(?:hath |has |had )?(?:said|saith|spake|declared)'
    r'),)\s+(.{10,})$'
)

def m11_speech_frame(lines):
    """'said he,' / 'saith he,' → speech starts new line."""
    result = []
    for line in lines:
        m = _SPEECH_FRAME_PAT.match(line)
        if m:
            result.append(m.group(1))
            result.append(m.group(2))
        else:
            result.append(line)
    return result


# ============================================================
# M12: "IN [GERUND]" SPLIT
# ============================================================

_IN_GERUND_PAT = re.compile(r'^(.{15,}?)\s+(in\s+\w+ing\b.+)$')

def m12_in_gerund(lines):
    """Complete phrase + 'in [gerund]' → split before 'in'."""
    result = []
    for line in lines:
        m = _IN_GERUND_PAT.match(line)
        if m and len(m.group(2)) >= 10:
            result.append(m.group(1))
            result.append(m.group(2))
        else:
            result.append(line)
    return result


# ============================================================
# M13: "MADE AN END OF [GERUND]" SPLIT
# ============================================================

_END_OF_GERUND_PAT = re.compile(r'^(.+made an end)\s+(of\s+\w+ing\b.+)$')

def m13_end_of_gerund(lines):
    """'made an end of [gerund]' → split before 'of'."""
    result = []
    for line in lines:
        m = _END_OF_GERUND_PAT.match(line)
        if m:
            result.append(m.group(1))
            result.append(m.group(2))
        else:
            result.append(line)
    return result


# ============================================================
# M14: INVERTED CONDITIONAL CONSEQUENCE SPLIT
# ============================================================

_PRONOUNS_SET = r'(?:we|they|he|I|ye|she|it|thou)'
_MODALS_SET = r'(?:shall|should|would|will|must|could|may|might)'

def m14_inverted_conditional(lines):
    """'had we remained in X / we should have...' — consequence on new line."""
    result = []
    for line in lines:
        if len(line) < 40:
            result.append(line)
            continue
        # Check for inverted conditional in first 30 chars
        if not re.match(rf'.*\bhad\s+{_PRONOUNS_SET}\b', line[:30]):
            result.append(line)
            continue
        # Find consequence: pronoun + modal later in the line
        m = re.search(
            rf'\b({_PRONOUNS_SET})\s+({_MODALS_SET})\b',
            line[25:]
        )
        if m:
            split_pos = 25 + m.start()
            # No comma between
            if ',' not in line[split_pos - 5:split_pos]:
                left = line[:split_pos].rstrip()
                right = line[split_pos:]
                if len(left) >= 20 and len(right) >= 15:
                    result.append(left)
                    result.append(right)
                    continue
        result.append(line)
    return result


# ============================================================
# M15: PASSIVE VERB + DIRECTIONAL PREP SPLIT
# ============================================================

_MOTION_VERBS = {
    'scattered', 'driven', 'led', 'turned', 'sent', 'taken',
    'cast', 'placed', 'put',
}

_PASSIVE_PREP_PAT = re.compile(
    r'^(.+(?:is|are|was|were|been|be)\s+(?!not\b)(\w+(?:ed|en|t|wn)))\s+'
    r'((?:unto|upon|for|from|by|among|against|into|out of)\s+.+)$'
)

def m15_passive_prep(lines):
    """Complete passive verb + directional prep: split before prep."""
    result = []
    for line in lines:
        if len(line) < 50:
            result.append(line)
            continue
        m = _PASSIVE_PREP_PAT.match(line)
        if m:
            participle = m.group(2)
            left, right = m.group(1), m.group(3)
            if (participle not in _MOTION_VERBS
                    and len(left) >= 18 and len(right) >= 15):
                result.append(left)
                result.append(right)
                continue
        result.append(line)
    return result


# ============================================================
# M16: DEITY APPOSITIVE SPLIT
# ============================================================

_DEITY_TITLES = [
    'the Lord God Omnipotent', 'the Lord God Almighty',
    'the Lord Jesus Christ', 'the Son of God', 'Son of God',
    'the Holy One of Israel', 'Holy One of Israel',
    'the God of Abraham', 'the God of Isaac', 'the God of Jacob',
    'the God of Israel', 'God of Israel',
    'the Lamb of God', 'Lamb of God',
    'the Most High God', 'Most High God',
    'the Mighty One of Israel', 'the Mighty One of Jacob',
    'the Eternal Father', 'Eternal Father',
    'the Lord God', 'Lord God',
    'the Holy One', 'the Mighty One', 'the Mighty God',
    'The Mighty God', 'the Most High', 'the Almighty',
    'the Messiah', 'the true Messiah',
    'the Redeemer', 'the Savior', 'the Creator',
    'the Holy Spirit', 'the Holy Ghost',
    'the Everlasting Father', 'The Everlasting Father',
    'the Prince of Peace', 'The Prince of Peace',
    'the Lord of Hosts', 'Lord of Hosts',
    'the Great Creator', 'the Eternal Judge',
    'the Good Shepherd', 'the Mediator',
    'the king of heaven',
    'the rock of my righteousness',
    'the Lord', 'the Father', 'the Son', 'the Lamb',
    'Christ', 'Jesus Christ', 'Jesus', 'Messiah', 'God',
    'their Redeemer', 'their God', 'our Redeemer', 'our God',
    'my Redeemer', 'my God', 'my Savior',
    'thy Redeemer', 'thy Savior', 'thy God',
    'your Redeemer', 'your God', 'his God',
]

# Sort longest-first for regex matching
_DEITY_TITLES.sort(key=len, reverse=True)
_DEITY_RE_STR = '|'.join(re.escape(t) for t in _DEITY_TITLES)
_DEITY_APPOS_PAT = re.compile(
    r'^(.*?\b(?:' + _DEITY_RE_STR + r')),\s+((?:' + _DEITY_RE_STR + r')\b.*)$'
)


def m16_deity_appositive(lines):
    """Split DEITY, DEITY appositive patterns onto separate lines."""
    result = []
    for line in lines:
        if len(line) < 30:
            result.append(line)
            continue
        changed = True
        current = line
        while changed:
            changed = False
            m = _DEITY_APPOS_PAT.match(current)
            if m:
                left, right = m.group(1) + ',', m.group(2)
                result.append(left)
                current = right
                changed = True
        result.append(current)
    return result


# ============================================================
# PIPELINE
# ============================================================

PIPELINE = [
    ('M0:  emdash trailing',      m0_emdash_trailing),
    ('M1:  AICTP isolation',      m1_aictp),
    ('M2:  behold hinge',         m2_behold_hinge),
    ('M3:  yea trailing',         m3_yea_trailing),
    ('M4:  insomuch split',       m4_insomuch),
    ('M5:  vocative split',       m5_vocative),
    ('M6:  according-to split',   m6_according_to),
    ('M7:  speech+content split', m7_speech_content),
    ('M8:  and+pronoun split',    m8_and_pronoun),
    ('M9:  subject-predicate',    m9_subject_predicate),
    ('M10: long-line split',      lambda lines: m10_split_long(lines, 70)),
    ('M11: speech frame',         m11_speech_frame),
    ('M12: in+gerund',            m12_in_gerund),
    ('M13: end of+gerund',        m13_end_of_gerund),
    ('M14: inverted conditional', m14_inverted_conditional),
    ('M15: passive+prep',         m15_passive_prep),
    ('M16: deity appositive',     m16_deity_appositive),
]


def process_verse(content_lines):
    """Apply all mechanical passes to a verse's content lines."""
    for name, fn in PIPELINE:
        content_lines = fn(content_lines)
    return content_lines


def process_file(input_path, output_path):
    with open(input_path) as f:
        content = f.read()

    blocks = content.strip().split('\n\n')
    output_blocks = []

    for block in blocks:
        block_lines = block.split('\n')

        verse_marker = None
        if re.match(r'^\d+:\d+$', block_lines[0].strip()):
            verse_marker = block_lines[0].strip()
            content_lines = block_lines[1:]
        else:
            content_lines = block_lines

        content_lines = process_verse(content_lines)

        if verse_marker:
            output_blocks.append(verse_marker + '\n' + '\n'.join(content_lines))
        else:
            output_blocks.append('\n'.join(content_lines))

    output = '\n\n'.join(output_blocks) + '\n'

    with open(output_path, 'w') as f:
        f.write(output)

    return output, blocks, output_blocks


def print_stats(output, orig_blocks, output_blocks):
    out_lines = [
        l.rstrip() for l in output.split('\n')
        if l.strip() and not re.match(r'^\d+:\d+$', l.strip())
    ]
    lengths = sorted(len(l) for l in out_lines)

    print(f"Total lines: {len(lengths)}")
    print(f"Mean: {sum(lengths) / len(lengths):.1f}")
    print(f"Median: {lengths[len(lengths) // 2]}")
    print(f"Over 70: {sum(1 for l in lengths if l > 70)}")
    print(f"Over 75: {sum(1 for l in lengths if l > 75)}")
    print(f"Under 15: {sum(1 for l in lengths if l < 15)}")

    remaining = [l for l in out_lines if len(l) > 75]
    if remaining:
        print(f"\nRemaining > 75 ({len(remaining)}):")
        for l in remaining:
            print(f"  [{len(l)}] {l}")

    changed = sum(
        1 for o, n in zip(orig_blocks, output_blocks)
        if o.strip() != n.strip()
    )
    print(f"\nChanged verses: {changed} of {len(orig_blocks)}")


if __name__ == '__main__':
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    output, orig_blocks, output_blocks = process_file(input_path, output_path)
    print_stats(output, orig_blocks, output_blocks)
