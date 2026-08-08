#!/usr/bin/env python3
"""SURFACE detector for inverted-conditional fractures -- a residual class the
parse-based bidirectional gate is BLIND to.

Why the gate misses it: an inverted conditional ("were it expedient, we could
prophesy"; "were it not for him, we must have perished") often mis-parses (stanza
doesn't recognize the subject-aux inversion as a conditional), so the protasis ends
up severed from its apodosis across a line boundary. BOTH resulting lines look like
complete clauses individually, so a per-line fragment classifier sees nothing -- the
defect is a MIS-PAIRING, not a within-line fragment. But it has a clean SURFACE
signature, independent of the (garbled) parse: a non-final line that ENDS with a
short dangling inverted-conditional protasis.

Pattern: clause-initial subject-aux inversion -- "were it/he/they/we/I/there ..." or
"had we/I/they/he/it ..." (NOT "had not", which is past-perfect narration, not a
conditional). Flagged when such a protasis ends a non-final line.

Run: PYTHONIOENCODING=utf-8 PYTHONPATH=../atu-method .venv/Scripts/python.exe -m scripts.scan_inverted_conditionals
"""
import re
import scripts.bofm_generate as G

BOOKS = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni', 'words-of-mormon',
         'mosiah', 'alma', 'helaman', '3nephi', '4nephi', 'mormon', 'ether', 'moroni']

# inverted-conditional protasis = subject-aux inversion. EXCLUDES "had not" (past
# perfect: "he had not exacted" is narration, not a conditional).
INV = re.compile(r"(?i)\b(were (?:it|he|they|we|I|there)|had (?:we|I|they|he|it))\b")


def main():
    hits = []
    for b in BOOKS:
        v = G.read_v0(b)
        p = G.parse_book(b)
        for key in sorted(v.keys()):
            lines = G.deployed_atu_lines(b, key[0], key[1], v[key], p.get(key, []))
            for li in range(len(lines) - 1):          # non-final lines only
                ln = lines[li]
                m = INV.search(ln)
                if not m:
                    continue
                tail = ln[m.start():]                  # protasis onward
                # dangling: the protasis is short and ends the line with a comma,
                # i.e. its apodosis is NOT on this line (it's the next).
                if len(tail.split()) <= 7 and ln.rstrip().endswith(","):
                    hits.append((b, key[0], key[1], tail.strip(), lines[li + 1][:40]))

    print(f"Inverted-conditional fractures (protasis dangling at line end): {len(hits)}")
    for b, c, v, prot, nxt in hits:
        print(f"   {b} {c}:{v}   ...{prot!r}  |  NEXT: {nxt!r}")
    if not hits:
        print("   (none -- class clear)")
    return 1 if hits else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
