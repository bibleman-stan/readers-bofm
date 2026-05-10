"""
CoNLL-U loader + query primitives for the BofM parsed corpus.

Replaces the regex-based reconstruction of UD signatures used in the
Layer 2 / Layer 3 validators. Validators that previously matched FORM
strings against verb whitelists now query DEPREL / LEMMA / FEATS directly.

Usage:
    from validators.parsing.conllu_query import load_conllu

    sentences = load_conllu(Path("data/parses/llm-direct/enos.conllu"))
    for sent in sentences:
        for ccomp in sent.find(deprel="ccomp"):
            head = sent.head_of(ccomp)
            mark = sent.mark_of(ccomp)
            if head and mark and mark.lemma == "that":
                print(sent.sent_id, head.lemma, "->", ccomp.lemma)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional


@dataclass
class Token:
    id: int
    form: str
    lemma: str
    upos: str
    xpos: str
    feats: dict[str, str]
    head: int
    deprel: str
    deps: str
    misc: str


@dataclass
class Sentence:
    sent_id: str
    text: str
    tokens: list[Token]
    comments: dict[str, str] = field(default_factory=dict)

    def by_id(self, tid: int) -> Optional[Token]:
        for t in self.tokens:
            if t.id == tid:
                return t
        return None

    def head_of(self, t: Token) -> Optional[Token]:
        if t.head == 0:
            return None
        return self.by_id(t.head)

    def root(self) -> Optional[Token]:
        for t in self.tokens:
            if t.head == 0 and t.deprel == "root":
                return t
        return None

    def dependents_of(self, t: Token, deprel: Optional[str] = None) -> list[Token]:
        result = []
        for child in self.tokens:
            if child.head == t.id:
                if deprel is None or child.deprel == deprel:
                    result.append(child)
        return result

    def mark_of(self, t: Token) -> Optional[Token]:
        """The 'mark' dependent of t (typically the SCONJ marking a clause).
        Returns the first one if multiple (rare)."""
        marks = self.dependents_of(t, deprel="mark")
        return marks[0] if marks else None

    def aux_of(self, t: Token) -> list[Token]:
        """All 'aux' (and 'aux:pass') dependents of t."""
        return [c for c in self.tokens
                if c.head == t.id and c.deprel.startswith("aux")]

    def subtree(self, t: Token) -> list[Token]:
        """All tokens in the subtree rooted at t, in id order (inclusive of t)."""
        ids = {t.id}
        added = True
        while added:
            added = False
            for child in self.tokens:
                if child.head in ids and child.id not in ids:
                    ids.add(child.id)
                    added = True
        return sorted([tok for tok in self.tokens if tok.id in ids], key=lambda x: x.id)

    def find(self, *,
             deprel: Optional[str] = None,
             deprel_in: Optional[set[str]] = None,
             lemma: Optional[str] = None,
             lemma_in: Optional[set[str]] = None,
             form: Optional[str] = None,
             upos: Optional[str] = None,
             upos_in: Optional[set[str]] = None,
             head_lemma: Optional[str] = None,
             head_lemma_in: Optional[set[str]] = None,
             head_upos: Optional[str] = None,
             feats: Optional[dict[str, str]] = None,
             ) -> Iterator[Token]:
        """Match tokens against the given criteria. All provided criteria must hold (AND).

        Use *_in for set membership; use the singular form for an exact match.
        feats={"Mood": "Sub"} matches tokens whose FEATS dict contains Mood=Sub.
        """
        for t in self.tokens:
            if deprel is not None and t.deprel != deprel:
                continue
            if deprel_in is not None and t.deprel not in deprel_in:
                continue
            if lemma is not None and t.lemma != lemma:
                continue
            if lemma_in is not None and t.lemma not in lemma_in:
                continue
            if form is not None and t.form != form:
                continue
            if upos is not None and t.upos != upos:
                continue
            if upos_in is not None and t.upos not in upos_in:
                continue
            if head_lemma is not None or head_lemma_in is not None or head_upos is not None:
                head = self.head_of(t)
                if head is None:
                    continue
                if head_lemma is not None and head.lemma != head_lemma:
                    continue
                if head_lemma_in is not None and head.lemma not in head_lemma_in:
                    continue
                if head_upos is not None and head.upos != head_upos:
                    continue
            if feats is not None:
                if not all(t.feats.get(k) == v for k, v in feats.items()):
                    continue
            yield t


def _parse_token(line: str) -> Optional[Token]:
    cols = line.split("\t")
    if len(cols) < 10:
        return None
    if "-" in cols[0] or "." in cols[0]:
        return None
    feats: dict[str, str] = {}
    if cols[5] != "_":
        for f in cols[5].split("|"):
            if "=" in f:
                k, v = f.split("=", 1)
                feats[k] = v
    try:
        head = int(cols[6]) if cols[6] != "_" else 0
    except ValueError:
        head = 0
    return Token(
        id=int(cols[0]),
        form=cols[1],
        lemma=cols[2] if cols[2] != "_" else cols[1].lower(),
        upos=cols[3],
        xpos=cols[4],
        feats=feats,
        head=head,
        deprel=cols[7],
        deps=cols[8],
        misc=cols[9],
    )


def load_conllu(path: Path) -> list[Sentence]:
    """Load a CoNLL-U file into a list of Sentence objects."""
    sentences: list[Sentence] = []
    comments: dict[str, str] = {}
    tokens: list[Token] = []

    def flush():
        if tokens:
            sentences.append(Sentence(
                sent_id=comments.get("sent_id", ""),
                text=comments.get("text", ""),
                tokens=list(tokens),
                comments=dict(comments),
            ))

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line:
                flush()
                comments = {}
                tokens = []
                continue
            if line.startswith("#"):
                body = line[1:].strip()
                if " = " in body:
                    k, v = body.split(" = ", 1)
                    comments[k.strip()] = v
                elif " " in body:
                    k, v = body.split(None, 1)
                    comments[k] = v
                else:
                    comments[body] = ""
                continue
            tok = _parse_token(line)
            if tok is not None:
                tokens.append(tok)

    flush()
    return sentences


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python conllu_query.py <path-to-conllu>", file=sys.stderr)
        sys.exit(2)
    sents = load_conllu(Path(sys.argv[1]))
    print(f"Loaded {len(sents)} sentences, "
          f"{sum(len(s.tokens) for s in sents)} tokens.")
    if sents:
        s = sents[0]
        print(f"\nFirst sentence: sent_id={s.sent_id!r}")
        print(f"  text: {s.text[:80]}{'...' if len(s.text) > 80 else ''}")
        print(f"  tokens: {len(s.tokens)}")
        root = s.root()
        if root:
            print(f"  root: {root.id}/{root.form} (lemma={root.lemma}, upos={root.upos})")
