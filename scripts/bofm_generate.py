#!/usr/bin/env python3
"""BoFM pure-method generator — v0 -> UD -> clause-atoms -> surface-order ATU
lines, anchored ENTIRELY on v0 (LDS versification prose). Zero dependence on the
hand-edited v2-mine breaks: stanza parses each verse, bofm_v1_fabric segments by
UD clause structure, and lines render in surface order with exact original
punctuation (char-offset slice of the verse text). This is the initial PURE-
METHOD segmentation the BoFM canon appliers (apply_rule_*) then refine.

Usage (needs atu-method on PYTHONPATH, repo .venv):
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_generate.py 1nephi 1
  (book, chapter; omit chapter for whole book)
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from bofm_v1_fabric import clause_atoms  # noqa: E402  (duck-typed tokens)

V0 = REPO / "data" / "text-files" / "v0-bofm-original"
BOOKFILE = {
    "1nephi": "1_Nephi.txt", "2nephi": "2_Nephi.txt", "jacob": "Jacob.txt",
    "enos": "Enos.txt", "jarom": "Jarom.txt", "omni": "Omni.txt",
    "words-of-mormon": "Words_of_Mormon.txt", "mosiah": "Mosiah.txt",
    "alma": "Alma.txt", "helaman": "Helaman.txt", "3nephi": "3_Nephi.txt",
    "4nephi": "4_Nephi.txt", "mormon": "Mormon.txt", "ether": "Ether.txt",
    "moroni": "Moroni.txt",
}
_REF = re.compile(r"^(.+?) (\d+):(\d+)$")


class Tok:
    __slots__ = ("id", "head", "deprel", "upos", "lemma", "form", "start", "end")

    def __init__(self, w):
        self.id, self.head = w.id, w.head
        self.deprel, self.upos = w.deprel, w.upos
        self.lemma, self.form = w.lemma, w.text
        self.start, self.end = w.start_char, w.end_char

    @classmethod
    def from_dict(cls, d):
        t = cls.__new__(cls)
        (t.id, t.head, t.deprel, t.upos, t.lemma, t.form, t.start, t.end) = d
        return t

    def as_list(self):
        return [self.id, self.head, self.deprel, self.upos, self.lemma, self.form,
                self.start, self.end]


class Sent:
    def __init__(self, toks):
        self.tokens = toks


_tok = _parse = None


def _pipes():
    """Two stanza pipelines: a tokenizer (with sentence splitting) over the
    ORIGINAL EME text, and a pos/lemma/depparse pipeline run PRE-TOKENIZED over
    the archaic-normalized token stream. Splitting via the original tokenizer
    preserves sentence boundaries; feeding the parser pre-tokenized guarantees a
    1:1 token alignment so the corrected parse maps back onto the original
    surface (see archaic_normalize)."""
    global _tok, _parse
    if _tok is None:
        import stanza
        _tok = stanza.Pipeline("en", processors="tokenize",
                               verbose=False, download_method=None)
        _parse = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse",
                                 tokenize_pretokenized=True, verbose=False,
                                 download_method=None)
    return _tok, _parse


def _parse_verse(text):
    """Parse one verse -> [[Tok,...sentence...], ...]. Tokenize the original EME
    text, normalize each token's archaic morphology for the parser, parse
    pre-tokenized, then build Tok with the ORIGINAL surface+offsets and the
    corrected upos/deprel/head/lemma."""
    from archaic_normalize import normalize
    tok, parse = _pipes()
    sents = [s.words for s in tok(text).sentences]
    sents = [ws for ws in sents if ws]
    if not sents:
        return []
    normed = [[normalize(w.text) for w in ws] for ws in sents]
    doc = parse(normed)
    out = []
    for ows, psent in zip(sents, doc.sentences):
        toks = []
        for ow, pw in zip(ows, psent.words):
            t = Tok.__new__(Tok)
            t.id, t.head, t.deprel, t.upos = pw.id, pw.head, pw.deprel, pw.upos
            t.lemma, t.form = pw.lemma, ow.text
            t.start, t.end = ow.start_char, ow.end_char
            toks.append(t)
        out.append(toks)
    return out


def _build_parses(verses):
    """Batched parse of every verse in a book. Per-verse tokenize (needed for the
    correct WITHIN-VERSE char offsets the renderer slices on), then ONE
    pre-tokenized parse call over all of the book's sentences (stanza batches the
    neural depparse internally), then redistribute parsed sentences to verses.
    This replaces a full pipeline invocation per verse (6604 calls corpus-wide,
    whose per-call overhead, not the parsing, dominated the ~3.9s/verse cost)."""
    from collections import defaultdict
    from archaic_normalize import normalize
    tok, parse = _pipes()
    keys = sorted(verses)
    vsents, flat_norm, owner = [], [], []
    for ki, key in enumerate(keys):
        sents = [s.words for s in tok(verses[key]).sentences]
        sents = [ws for ws in sents if ws]
        vsents.append(sents)
        for ws in sents:
            flat_norm.append([normalize(w.text) for w in ws])
            owner.append(ki)
    parsed = parse(flat_norm).sentences if flat_norm else []
    by_key = defaultdict(list)
    for oi, psent in zip(owner, parsed):
        by_key[oi].append(psent)
    out = {}
    for ki, key in enumerate(keys):
        sents_out = []
        for ows, psent in zip(vsents[ki], by_key[ki]):
            toks = []
            for ow, pw in zip(ows, psent.words):
                t = Tok.__new__(Tok)
                t.id, t.head, t.deprel, t.upos = pw.id, pw.head, pw.deprel, pw.upos
                t.lemma, t.form = pw.lemma, ow.text
                t.start, t.end = ow.start_char, ow.end_char
                toks.append(t)
            sents_out.append(toks)
        out[key] = sents_out
    return out


def read_v0(book):
    """{(chap, verse): verse_text} from v0-bofm-original (verse-keyed prose)."""
    text = (V0 / BOOKFILE[book]).read_text(encoding="utf-8")
    out, ref = {}, None
    for line in text.splitlines():
        m = _REF.match(line.strip())
        if m:
            ref = (int(m.group(2)), int(m.group(3))); out[ref] = ""
        elif ref is not None and line.strip():
            out[ref] = (out[ref] + " " + line.strip()).strip()
    return out


CACHE_DIR = Path(os.environ["BOFM_V0_CACHE_DIR"]) if os.environ.get("BOFM_V0_CACHE_DIR") else REPO / "data" / "parses" / "v0-cache"


def parse_book(book):
    """{(chap,verse): [[Tok,...sentence...], ...]} for the whole book — UD parse
    of the v0 (LDS-versification) prose, CACHED to JSON so rule iteration doesn't
    re-run stanza (a full-book parse is minutes; the cache load is instant). The
    cache IS the v1 substrate; ensemble+Claude adjudication is the future quality
    lift that would replace what stanza writes here."""
    cache = CACHE_DIR / f"{book}.json"
    if cache.exists():
        raw = json.loads(cache.read_text(encoding="utf-8"))
        out = {tuple(int(x) for x in k.split(":")): [[Tok.from_dict(d) for d in s]
               for s in sents] for k, sents in raw.items()}
        _apply_parse_repairs(out)
        return out
    out = _build_parses(read_v0(book))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({f"{c}:{v}": [[t.as_list() for t in s] for s in sents]
                                 for (c, v), sents in out.items()}), encoding="utf-8")
    _apply_parse_repairs(out)
    return out


def _apply_parse_repairs(parsed):
    """Deterministic attachment repairs for systematic EME mis-parses, applied at
    load-time (idempotent; the cache stores raw stanza output, repairs ride on top).
    Same architectural slot as archaic_normalize, but for ATTACHMENT not morphology."""
    from parse_repair import repair
    repair(parsed)


def _merge_back(segs, i):
    """Merge segment i into the previous segment (surface-contiguous)."""
    segs[i - 1]["hi"] = segs[i]["hi"]
    segs[i - 1]["toks"].extend(segs[i]["toks"])
    del segs[i]


def _merge_forward(segs, i):
    """Merge segment i INTO the following segment i+1 (surface-contiguous): the
    forward-incomplete frame leads its apodosis. The result keeps segment i's
    lo/leading tokens and segment i+1's hi/trailing tokens."""
    segs[i + 1]["lo"] = segs[i]["lo"]
    segs[i + 1]["toks"] = segs[i]["toks"] + segs[i + 1]["toks"]
    del segs[i]


# Subordinating leaders that open a DEPENDENT (forward-governing) clause -- a clause
# that points forward to a main clause / apodosis it cannot stand without. `that`
# (complementizer/result) + the causal/conditional/temporal/concessive subordinators.
# Surface-lexeme keyed (punctuation-invariant; parse-robust -- does NOT depend on the
# advcl head-attachment, which stanza garbles when it mis-roots the apodosis).
_FORWARD_FRAME_LEADERS = {"that", "because", "if", "unless", "when", "whensoever",
                          "while", "whilst", "until", "though", "although", "since",
                          "whereas", "before", "after", "as", "lest", "save",
                          "insomuch", "forasmuch"}


def _seg_independent_predication(seg):
    """Does this segment carry an INDEPENDENT main predication of its OWN -- a clause
    that stands alone (deprel root / conj / parataxis) with its OWN subject, NOT a
    clause subordinated by an in-segment mark/SCONJ? Used to tell a forward-incomplete
    frame ("that because ye were compelled to be humble" -- only subordinate clauses)
    from a self-standing clause ("his faith and hope is vain" -- a copular main clause).
    Parse-robust + handles BOTH verbal and copular main clauses:
      - a VERB whose deprel is root/conj/parataxis, not governed by an in-segment
        subordinator (verbal main clause: "ye were blessed", "he went forth"); OR
      - a COPULAR predicate (ADJ/NOUN/PRON/PROPN with a `cop` child) whose deprel is
        root/conj/parataxis with its OWN subject ("his faith and hope IS vain") --
        the old VERB/AUX-only test skipped `cop` and wrongly called this a frame.
    A clause that is itself subordinated (advcl/acl/ccomp/xcomp/csubj, or governed by an
    in-segment forward-frame mark) does NOT count. Errs toward 'no independent
    predication' only when EVERY clause is subordinate."""
    ids = {str(t.id) for t in seg["toks"]}
    sub_marks = {str(t.id) for t in seg["toks"]
                 if ((t.deprel or "") == "mark" or t.upos == "SCONJ")
                 and (t.form or "").lower() in _FORWARD_FRAME_LEADERS}

    def _has_own_subject(head):
        return any(str(c.head) == str(head.id) and str(c.id) in ids
                   and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                   for c in seg["toks"])

    for t in seg["toks"]:
        base = (t.deprel or "").split(":")[0]
        if base not in ("root", "conj", "parataxis"):
            continue                              # not a main-clause head -> skip
        if str(t.head) in sub_marks:
            continue                              # subordinated by an in-seg frame mark
        # verbal main clause
        if t.upos in ("VERB", "AUX") and not (t.form or "").lower().endswith("ing"):
            return True
        # copular main clause: a predicate (ADJ/NOUN/PRON/PROPN/NUM) with a cop child
        # and its own subject ("his faith and hope is vain").
        if t.upos in ("ADJ", "NOUN", "PRON", "PROPN", "NUM"):
            has_cop = any(str(c.head) == str(t.id) and str(c.id) in ids
                          and (c.deprel or "").split(":")[0] == "cop" for c in seg["toks"])
            if has_cop and _has_own_subject(t):
                return True
    return False


def _is_forward_frame(seg):
    """The segment is a forward-incomplete FRAME (framework §2.1 + GNT R9 forward-frame
    analog): its content is ONLY forward-governing leaders + a DEPENDENT clause, with
    NO independent predication of its own -- so it must bind FORWARD to the following
    segment (its apodosis/matrix). Punctuation-invariant + parse-robust:"""
    # §2.2 parallel-subordinator-stack exemption: a 'that'-led segment that is
    # a member of a sentence-scoped parallel-stack (>=2 'that' members, AICTP-
    # filtered, single-complement-filtered per _detect_stack_leaders) owns its
    # own ATU line — do NOT forward-bind. Sentence-scoped (not per-Stanza-
    # segment), so immune to the punctuation-driven segmentation that killed
    # a28deab's per-segment gate.
    if seg.get("is_stack_member"):
        return False
    # (i) first content token is a forward-frame subordinating leader (that/because/
    # if/when/...) tagged mark/SCONJ; (ii) NOT a relative clause; (iii) no independent
    # main predication.
    content = [t for t in seg["toks"] if (t.form or "").strip(",;:.!?—–’\"()")]
    if not content:
        return False
    first = content[0]
    if (first.form or "").lower() not in _FORWARD_FRAME_LEADERS:
        return False
    # (i) the leader must be a genuine SUBORDINATOR mark/SCONJ -- not a relativizer.
    # stanza tags a complementizer/adverbial `that`/`because`/`if`/`when` as `mark`
    # (or SCONJ); a relative `that` is `nsubj`/`obj`/`mark`-under-relcl. Require the
    # leader to head a NON-relative clause as a subordinator.
    if not ((first.deprel or "") == "mark" or first.upos == "SCONJ"
            or (first.deprel or "").split(":")[0] == "advmod"):
        return False
    # (ii) reject a relative clause outright: a verb whose deprel carries `relcl`
    # ("that oppress thee", "which I make", "who humble themselves") binds BACKWARD to
    # its antecedent, never forward.
    if any("relcl" in (t.deprel or "") for t in seg["toks"]
           if t.upos in ("VERB", "AUX")):
        return False
    # (ii-b) reject a VERBUM-DICENDI frame ("if ye shall SAY ...", "that we SAID unto
    # our brethren ..."): the speech verb's complement is DIRECT SPEECH released onto
    # its own line by the existing verba-dicendi / M2 direct-speech rules. Binding the
    # conditional/complementizer forward would swallow the released quote and create a
    # within-verse inconsistency (2nephi 2:13 split the parallel "And if ye shall say /
    # there is no law", alma 26:23 released "we go up to the land of Nephi"). Defer to
    # the speech rules -- the frame stays as the speech layer renders it. Keyed on the
    # speech-verb lemma (punctuation-invariant), reusing the verba-dicendi registry.
    if any((t.lemma or "").lower() in _VERBA_DICENDI_GEN
           and t.upos in ("VERB", "AUX") for t in seg["toks"]):
        return False
    # must actually contain a (subordinate) verb -- a bare NP fragment is not a frame
    if not any(t.upos in ("VERB", "AUX") for t in content):
        return False
    return not _seg_independent_predication(seg)


_DISCOURSE_LEADERS = {"behold", "lo", "yea", "now", "and", "or", "but", "nor",
                      "wherefore", "therefore", "for"}


def _apodosis_is_coordinated(seg):
    """The candidate apodosis segment OPENS with a coordinating conjunction
    (`and`/`but`/`or`/`nor`, deprel `cc`) -- it is a clause CONJOINED to something
    PRIOR, not the frame's own apodosis. A forward frame must bind to a clause that is
    grammatically ITS completion ("because ye were compelled to be humble" -> "ye were
    blessed", first token a subject pronoun); it must NOT reach forward across a
    coordinator into a coordinate clause whose matrix lies elsewhere ("lest they should
    commit sin" -> "; AND this their great fear came ..." is a new coordinate clause,
    alma 27:23; "because he hath poured out his soul" -> "; AND he was numbered ...",
    the Isaiah-53 parallel cola, mosiah 14:12). Punctuation-invariant: keyed on the
    coordinator lexeme + `cc` deprel, never the preceding semicolon/comma."""
    content = [t for t in seg["toks"] if (t.form or "").strip(",;:.!?—–’\"()")]
    if not content:
        return False
    first = content[0]
    return (first.deprel or "").split(":")[0] == "cc" \
        and (first.form or "").lower() in ("and", "but", "or", "nor")


def _next_is_lone_leader(seg):
    """The candidate apodosis segment is JUST a discourse/coordinating leader
    ("behold", "yea", "now", "and") with no clause of its own (stanza sometimes tags a
    bare "behold" as VERB/root -> a one-word seg). Binding the frame INTO such a seg
    would strand the leader on the frame line ("as ... give way, behold,") instead of
    letting it lead the REAL apodosis that follows it (alma 57:20 / helaman 5:12 /
    ether 8:22). Don't fire across it -- the existing leader-fold pass will chain the
    leader onto its true apodosis, and the frame stays its own line (the deployed,
    no-regression state). Punctuation-invariant: keyed on the leader lexeme."""
    content = [t for t in seg["toks"] if (t.form or "").strip(",;:.!?—–’\"()")]
    if not content:
        return True
    return all((t.form or "").strip(",;:.!?—–’\"()").lower() in _DISCOURSE_LEADERS
               for t in content)


def _forward_frame_bind(segs):
    """Bind every forward-incomplete frame segment FORWARD into the next segment (its
    apodosis). Iterates so a `that` lone-leader seg + a `because ...` frame seg both
    fold onto the apodosis. CAUTION (no over-bind): fires ONLY when the frame seg
    genuinely lacks its own independent predication AND a following segment exists to
    carry the apodosis; never binds the LAST segment (nothing to bind to) and never a
    segment that already contains its own main clause."""
    i = 0
    while i < len(segs) - 1:
        if _is_forward_frame(segs[i]) and not _next_is_lone_leader(segs[i + 1]) \
           and not _apodosis_is_coordinated(segs[i + 1]):
            _merge_forward(segs, i)
            # do not advance: the merged segment now sits at i; re-test it in case it
            # is STILL forward-incomplete (a stacked frame), but guard against a
            # consolidated seg that now has its apodosis (independent predication).
        else:
            i += 1
    return segs


# ---------------------------------------------------------------------------
# BoFM MARKER REGISTRY (framework §2.2 — the explicit-marker break-license).
# This is the corpus's first registered registry instance. Each entry is a single
# discrete author lexeme that opens a sub-clausal amplification/restatement beat
# below the level the bidirectional test (A) would split. A marker LICENSES A
# BREAK on a colon that is ALREADY closure-eligible under (A) — it never certifies
# a fragment as a thought. Conditions enforced by _marker_split (per token):
#   (i)   single discrete author lexeme (matched on surface form);
#   (ii)  the marker-led colon is closure-eligible — propositionally complete minus
#         the marker, OR forward-closed by restoring a GAPPED FINITE VERB from the
#         immediately-prior parallel clause (a shared finite verb ONLY — not a
#         shared subject/object/PP);
#   (iii) the break is not already licensed by (A) (clause-level connectives that
#         head their own finite predication already split upstream in the fabric).
# Registered markers, each with bidirectional-test status + worked example:
#   - "yea"      : asseverative amplifier. Closure via elided matrix finite verb.
#                  Alma 32:16 "...is baptized ..., YEA, without being brought to
#                  know the word..." -> the yea-colon shares matrix "is baptized".
#   - "or rather": self-correction/restatement opener. Alma 32:16 "...without being
#                  compelled to be humble; OR RATHER, ... blessed is he that
#                  believeth..." (here the restated colon has its own copula 'is',
#                  so it is independently closure-eligible).
_MARKER_REGISTRY = {"yea", "or rather"}


_VERBA_DICENDI_GEN = {"say", "speak", "cry", "answer", "command", "declare",
                      "exhort", "ask", "tell", "reply", "utter", "proclaim", "preach"}
_SHORT_ANSWER = {"yea", "nay", "yes", "no"}


def _is_speech_frame_seg(seg):
    """The segment's predication is a verbum-dicendi finite verb ("I say unto you").
    Lemma-keyed (punctuation-invariant)."""
    return any((t.lemma or "").lower() in _VERBA_DICENDI_GEN
               and t.upos in ("VERB", "AUX") for t in seg["toks"])


def _answer_leads_forward(content):
    """The material AFTER a leading short answer (the rest of `content`) is itself a
    distinct forward beat the answer AMPLIFIES, not a beat the answer ANSWERS -- so the
    answer ("Yea") must lead it FORWARD (handled by the §2.2 marker-split), NOT be
    peeled backward onto the prior speech frame. Two configurations (the §7.3 audit's 3
    Alma mis-fires, e.g. 5:10 "...are they saved? Yea, / what grounds had they..."):
      - the post-answer material is itself an INDEPENDENT/PARALLEL QUESTION (a `?` token
        within this segment -- the answer fronts a rhetorical question, not a yes/no
        resolution);
      - the post-answer material is an `and`/`or`-LED PARALLEL clause within this
        segment (a coordinate continuation, not an answer body).
    Punctuation-invariant in DECISION: the `?` is the interrogative mood signal (a
    grammatical feature), and the cc lemma is read as a lexeme -- neither branches on a
    comma."""
    rest = content[1:]
    if any((t.form or "").strip() == "?" for t in rest):
        return True
    nxt = rest[0] if rest else None
    if nxt is not None and (nxt.deprel or "").split(":")[0] == "cc" \
       and (nxt.form or "").lower() in ("and", "or"):
        return True
    return False


def _speech_answer_peel(segs):
    """Peel a leading bare short answer ("Yea"/"Nay") off a new-beat segment onto the
    immediately-preceding speech-frame segment (framework §2.1 short-answer bind).
    Fires ONLY when: (i) the prior segment is a verbum-dicendi speech frame; (ii) this
    segment's FIRST content token is a registered short-answer discourse word; (iii)
    something else follows the answer in this segment (a distinct beat) -- if the
    answer is the whole segment it is already adjacent and the leader/render passes
    handle it; (iv) that following material is NOT an independent/parallel question or
    an `and`-led parallel (those mean the answer AMPLIFIES the next beat forward, not
    resolves the prior one -- let marker-split lead it forward instead; the §7.3 audit's
    3 Alma mis-fires). Moves the char boundary so the answer renders on the speech line
    and the trailing beat stays its own line. Punctuation between is carried by the
    backward-punctuation render pass; this never inspects the comma."""
    i = 1
    while i < len(segs):
        toks = segs[i]["toks"]
        content = [t for t in toks if (t.form or "").strip(",;:.!?—–’\"()")]
        if (len(content) >= 2
                and (content[0].form or "").strip(",;:.!?—–’\"()").lower() in _SHORT_ANSWER
                and (content[0].deprel or "").split(":")[0] == "discourse"
                and _is_speech_frame_seg(segs[i - 1])
                and not _answer_leads_forward(content)):
            answer = content[0]
            # move the answer token from seg i into seg i-1; reslice the boundary to
            # the answer's end so the speech line gains "..., Yea" and seg i begins at
            # the next content token.
            nxt = next((t for t in toks if int(t.start) > int(answer.end)), None)
            if nxt is not None:
                # extend the speech line up to the next content token so any
                # punctuation right after the answer ("Yea;") rides on the speech
                # line (it strips to "Yea;"); seg i restarts at the next content token.
                segs[i - 1]["hi"] = nxt.start
                segs[i - 1]["toks"] = segs[i - 1]["toks"] + [answer]
                segs[i]["lo"] = nxt.start
                segs[i]["toks"] = [t for t in toks if t is not answer]
        i += 1
    return segs


def _marker_split(segs):
    """Framework §2.2 break-license. Within each segment, find a registered marker
    token whose led colon is closure-eligible (i), and SPLIT the segment at the
    marker onto its own line. This is the framework's only break-GENERATING rule;
    it is quarantined to the closed registry + the closure-eligibility test below."""
    out = []
    for seg in segs:
        out.extend(_split_one(seg))
    return out


def _split_one(seg):
    """Split a single segment at EVERY closure-eligible registered marker (a verse
    can stack markers — Alma 32:16 has both 'or rather' and 'yea'). Recurse on the
    tail so a later marker in the same segment also splits."""
    toks = seg["toks"]
    for j, t in enumerate(toks):
        if j == 0:
            continue                           # a segment-leading marker is handled
                                               # by the yea-B / leader passes, not here
        form = (t.form or "").lower()
        two = (form + " " + (toks[j + 1].form or "").lower()) if j + 1 < len(toks) else ""
        is_marker = form in _MARKER_REGISTRY or two in _MARKER_REGISTRY
        if not is_marker:
            continue
        if _colon_closure_eligible(toks, j):
            lo_split = toks[j].start
            a = {"aid": seg["aid"], "lo": seg["lo"], "hi": lo_split, "toks": toks[:j]}
            b = {"aid": seg["aid"], "lo": lo_split, "hi": seg["hi"], "toks": toks[j:]}
            return [a] + _split_one(b)
    return [seg]


def _colon_closure_eligible(toks, j):
    """Is the marker-led colon (tokens[j:] within this segment) closure-eligible
    under framework §2.2(ii)? TRUE iff EITHER:
      (a) the colon is propositionally complete minus the marker — it contains its
          OWN finite verb (a tensed VERB/AUX that is not a bare participle/infinitive
          and not merely a subordinate-only predicate); OR
      (b) it is forward-closed by elision-restoring a GAPPED FINITE VERB from the
          immediately-prior parallel clause: the colon's predication is an advcl /
          oblique whose governing matrix verb (a FINITE VERB/AUX) lies in the
          pre-marker tokens — the colon shares that one finite verb. A shared
          subject / object / PP does NOT qualify (that would re-admit parallel-cola
          splitting §2 forbids), so we require a recoverable governing FINITE VERB,
          not just any shared head."""
    colon = toks[j:]
    before = toks[:j]
    colon_ids = {str(t.id) for t in colon}
    before_ids = {str(t.id) for t in before}
    # Shared-ARGUMENT guard (§2.2(ii): a shared subject/object/PP does NOT license a
    # break). If the marker attaches to a NOMINAL (NOUN/PROPN/PRON) -- "yea, the Lord,
    # and the weapons of his indignation..." (2Ne23:5: yea->'Lord', an apposed/
    # coordinated SUBJECT NP) -- the colon is argument-NP amplification, not a
    # predication beat, even if an incidental purpose-infinitive ('to destroy') trails
    # it. Such a colon shares an ARGUMENT, not a gapped finite verb -> NOT eligible.
    marker = toks[j]
    mgov = next((t for t in toks if str(t.id) == str(marker.head)), None)
    if mgov is not None and mgov.upos in ("NOUN", "PROPN", "PRON", "NUM"):
        return False
    # The colon's TOP-LEVEL head clause = the colon verb whose head lies OUTSIDE the
    # colon (a verb governed from `before`, or a root). A verb whose head is itself
    # inside the colon is subordinate WITHIN the colon (e.g. a relative-clause verb)
    # and does NOT make the colon closure-eligible on its own.
    top_verbs = [t for t in colon if t.upos in ("VERB", "AUX")
                 and str(t.head) not in colon_ids]
    if not top_verbs:
        return False                           # no top-level predication -> not eligible
    head_verb = min(top_verbs, key=lambda t: int(t.id))
    # (a) propositionally complete minus the marker: the colon's top-level predication
    # is finite AND carries its OWN subject within the colon (e.g. "yea, IT BEGINNETH
    # to enlighten" -> own nsubj 'it' + finite 'beginneth"). A bare past participle /
    # gerund without its own subject is NOT independently complete.
    own_subj = any(str(c.head) == str(head_verb.id)
                   and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                   and str(c.id) in colon_ids for c in colon)
    if own_subj and _is_finite(head_verb, toks):
        return True
    # (b) forward-closed by elision-restoring a GAPPED FINITE VERB from the prior
    # parallel clause: the colon's top predication is a subordinate/oblique
    # (advcl/obl/acl) whose GOVERNING matrix verb is a FINITE VERB/AUX in `before`
    # -- the colon shares that one finite verb (Alma 32:16: yea-colon 'brought' is an
    # advcl under the matrix finite 'is baptized', which sits in `before`). A shared
    # subject/object/PP does NOT qualify: we require the governor to be a finite VERB.
    gov = next((t for t in before if str(t.id) == str(head_verb.head)), None)
    if gov is not None and gov.upos in ("VERB", "AUX") and _is_finite(gov, toks):
        return True
    return False


# Common EME strong/irregular past participles that surface bare (no -ed) — used by
# _is_finite so a relative-clause participle chain ("whom they had cast out, and
# stoned, and slain") is not mistaken for an independent finite predication.
_STRONG_PARTICIPLES = {"slain", "cast", "brought", "begun", "done", "spoken", "given",
                       "taken", "known", "shown", "written", "driven", "smitten",
                       "born", "borne", "chosen", "broken", "fallen", "gone", "seen"}


def _is_finite(t, toks):
    """Is verb-token `t` FINITE (tensed) within `toks`? Finiteness can live on the
    verb itself (a tensed lexical verb: 'beginneth', 'sought', 'know') OR on a
    governing AUX child (periphrastic 'IS baptized', 'HAD cast', 'WILL believe').
    A BARE participle with NO finite aux of its own ('-ing'; a coordinated past
    participle 'stoned'/'slain' that only shares the head conjunct's aux) is
    non-finite -> the colon it heads is not independently closure-eligible. Errs
    toward non-finite (the safe / non-splitting default)."""
    f = (t.form or "").lower()
    if t.upos == "AUX":
        return not f.endswith("ing")           # 'is/are/was/will/hath/had' finite; 'being' not
    if f.endswith("ing"):
        return False
    # a finite aux DIRECTLY governed by this verb supplies tense ("is baptized").
    has_finite_aux = any(str(c.head) == str(t.id)
                         and (c.deprel or "").startswith("aux")
                         and (c.form or "").lower() not in ("being", "having")
                         for c in toks)
    if has_finite_aux:
        return True
    # otherwise the verb must be tensed on its own surface. Bare past participles
    # (-ed / strong participle) without an aux are non-finite.
    if f.endswith("eth") or f.endswith("est"):
        return True                            # archaic 3sg/2sg present -> finite
    if f.endswith("ed") or f in _STRONG_PARTICIPLES:
        return False
    return True                                # default: treat as a tensed finite verb


_PARALLEL_STACK_EXCLUDE_VERBS = _VERBA_DICENDI_GEN | {
    "know", "see", "perceive", "remember", "forget", "think", "suppose",
    "believe", "trust", "judge", "deem", "behold", "learn", "understand",
    "observe", "swear", "vow", "doubt", "marvel", "rejoice", "find",
    "show", "hear", "witness", "promise", "desire", "would", "will",
    "wish", "hope", "fear", "plead", "command", "cause", "suffer",
}


def _detect_stack_leaders(sentences):
    """§2.2 parallel-subordinator-stack detection. Sentence-scoped (NOT per-
    Stanza-segment): immune to the punctuation-driven segmentation that killed
    a28deab's per-segment count gate.

    A 'that'-mark token leads a §2.2 stack-member ATU iff:
      1. There are >=2 such 'that'-marks in the SAME sentence,
      2. The mark is NOT preceded (within 5 content tokens) by 'to pass' (the
         AICTP discourse-frame; the 'that'-clause binds to the frame),
      3. The mark is NOT immediately preceded (within 2 non-PUNCT tokens) by
         a single-complement-taking verb/aux (verbum-dicendi, cognition,
         volitional, causative — would/say/command/cause/suffer/etc.). Such
         a 'that'-clause is the verb's single content complement and BINDS.

    Returns: set of (sent_idx, token_id) pairs that should LEAD a stack-member
    ATU line."""
    leaders = set()
    for si, toks in enumerate(sentences):
        by_pos = sorted(toks, key=lambda t: int(t.id))
        candidates = []
        for i, t in enumerate(by_pos):
            if (t.form or "").lower() != "that":
                continue
            if (t.deprel or "") != "mark" and t.upos != "SCONJ":
                continue
            content_window = [by_pos[j] for j in range(max(0, i - 5), i)
                              if by_pos[j].upos != "PUNCT"]
            prev_text = " ".join((w.form or "").lower() for w in content_window)
            if "to pass" in prev_text:
                continue
            seen_nonpunct = 0
            single_comp = False
            for j in range(i - 1, -1, -1):
                if by_pos[j].upos == "PUNCT":
                    continue
                if by_pos[j].upos in ("VERB", "AUX"):
                    lemma = (by_pos[j].lemma or "").lower()
                    if lemma in _PARALLEL_STACK_EXCLUDE_VERBS:
                        single_comp = True
                    break
                seen_nonpunct += 1
                if seen_nonpunct >= 3:
                    break
            if single_comp:
                continue
            candidates.append(t)
        if len(candidates) >= 2:
            for t in candidates:
                leaders.add((si, t.id))
    return leaders


def _mark_stack_members(segs, stack_leaders):
    """Tag each segment that contains a stack-leader 'that' token. These
    segments are exempt from _forward_frame_bind (they own their own line)."""
    leader_ids_by_sent = {}
    for si, tid in stack_leaders:
        leader_ids_by_sent.setdefault(si, set()).add(tid)
    for seg in segs:
        si = seg.get("sent_idx")
        if si is None:
            continue
        leaders_in_sent = leader_ids_by_sent.get(si, set())
        if any(t.id in leaders_in_sent for t in seg["toks"]):
            seg["is_stack_member"] = True


def _split_at_stack_leaders(segs, stack_leaders):
    """§2.2 break-generating pass: SPLIT a segment at each stack-leader 'that'
    token. The leader's clause becomes its own segment. Subsequent stack-leaders
    in the same original segment each get their own split-out segment.

    Operates on the segment list in place. Each resulting stack-led segment is
    tagged is_stack_member=True so _forward_frame_bind leaves it alone."""
    leader_ids_by_sent = {}
    for si, tid in stack_leaders:
        leader_ids_by_sent.setdefault(si, set()).add(tid)
    out = []
    for seg in segs:
        si = seg.get("sent_idx")
        leaders_in_sent = leader_ids_by_sent.get(si, set()) if si is not None else set()
        if not leaders_in_sent:
            out.append(seg); continue
        toks = seg["toks"]
        raw_positions = [pi for pi, t in enumerate(toks) if t.id in leaders_in_sent]
        if not raw_positions:
            out.append(seg); continue
        split_positions = []
        for sp in raw_positions:
            actual = sp
            j = sp - 1
            while j >= 0 and toks[j].upos == "PUNCT":
                j -= 1
            if j >= 0 and toks[j].upos == "CCONJ" \
               and (toks[j].form or "").lower() in ("and", "or", "but", "nor"):
                actual = j
            split_positions.append(actual)
        prev_end = 0
        for sp in split_positions:
            if sp > prev_end:
                head_toks = toks[prev_end:sp]
                if head_toks:
                    head_seg = {"aid": seg["aid"], "sent_idx": si,
                                "lo": head_toks[0].start, "hi": head_toks[-1].end,
                                "toks": head_toks}
                    if prev_end > 0:
                        head_seg["is_stack_member"] = True
                    out.append(head_seg)
            prev_end = sp
        tail = toks[prev_end:]
        if tail:
            tail_seg = {"aid": seg["aid"], "sent_idx": si,
                        "lo": tail[0].start, "hi": tail[-1].end,
                        "toks": tail, "is_stack_member": True}
            out.append(tail_seg)
    segs[:] = out


def _rule_passes(segs, sentences=None):
    """UD-aware canon binding rules, applied as segment merges on the pure-method
    segmentation (ported into the generator — operates ONLY on pure-method data,
    never the hand-edits; validated against the canon detectors via run_all)."""
    if sentences is not None:
        stack_leaders = _detect_stack_leaders(sentences)
        _split_at_stack_leaders(segs, stack_leaders)
        _mark_stack_members(segs, stack_leaders)
    # R29 (bare infinitival orphan integrity): an infinitive segment opening with
    # "to <VERB|AUX>" is not its own thought — it binds to its governor in the
    # prior segment ("I ordain you to be a teacher) / to preach repentance").
    i = 1
    while i < len(segs):
        toks = segs[i]["toks"]
        if len(toks) >= 2 and toks[0].form.lower() == "to" and toks[1].upos in ("VERB", "AUX"):
            _merge_back(segs, i)
        else:
            i += 1
    # yea-B (interjection consistency): a "yea"-led segment that carries NO
    # independent predication is an epexegetical amplifier ("yea, even in a dream";
    # "yea, concerning that which was to come"; "yea, which the Lord had shown") --
    # a sub-clausal restatement, not its own thought -> merge back into what it
    # amplifies. A "yea" leading a complete clause ("Yea, I make a record"; "yea,
    # even he can slay fifty") has a root/conj/parataxis verb and stays its own ATU.
    # Independent predication = a VERB/AUX whose clause relation stands alone
    # (root/conj/parataxis); relative (acl:relcl) and bare phrases do not qualify.
    i = 1
    while i < len(segs):
        toks = segs[i]["toks"]
        first = next((t for t in toks if (t.form or "").strip()), None)
        is_yea = first is not None and (first.form or "").lower() == "yea"
        has_indep = any(t.upos in ("VERB", "AUX")
                        and (t.deprel or "").split(":")[0] in ("root", "conj", "parataxis")
                        for t in toks)
        if is_yea and not has_indep:
            _merge_back(segs, i)
        else:
            i += 1
    # AICTP frame binds FORWARD (Hebrew B5): a segment whose only verbs are the
    # empty frame "came to pass" is not a thought on its own (fails the
    # bidirectional test) -> merge into the clause it introduces.
    def _bare_aictp(seg):
        verbs = [t for t in seg["toks"] if t.upos in ("VERB", "AUX")]
        return bool(verbs) and {(t.lemma or "").lower() for t in verbs} <= {"come", "pass"}
    out, carry = [], None
    for seg in segs:
        if carry is not None:
            seg = {"aid": seg["aid"], "lo": carry["lo"], "hi": seg["hi"],
                   "toks": carry["toks"] + seg["toks"]}
            carry = None
        if _bare_aictp(seg):
            carry = seg
        else:
            out.append(seg)
    if carry is not None:
        out.append(carry)
    # Verbum-dicendi short-answer bind (framework §2.1, companion to the fabric's
    # reported-proposition parataxis bind). A bare short answer ("Yea"/"Nay"/"Yes"/
    # "No") is the reported PROPOSITION of the preceding "I say unto you" -- it begs
    # nothing and IS the content of the saying. stanza tags the answer `discourse`
    # and (when a distinct beat follows) attaches it to that following beat's verb,
    # so it lands at the HEAD of the new-beat segment ("Yea; nevertheless it hath not
    # grown...", Alma 32:29; "Yea; for every seed bringeth forth...", 32:31) instead
    # of on the "I say" line. Peel the leading answer token onto the speech-frame
    # segment; the nevertheless-/for-beat stands as its own line. Keyed on the answer
    # LEMMA + the prior segment being a speech frame -- never on the comma (the comma
    # rides backward in rendering). When the answer's beat-clause is the whole segment
    # tail it is left intact (only the bare answer word moves).
    out = _speech_answer_peel(out)
    # Forward-frame bind (framework §2.1 forward-incompleteness; BoFM analog of GNT R9
    # forward-frame + "no line is only a forward-governing leader"). A segment that is
    # ONLY forward-governing leaders + a dependent clause, with NO independent
    # predication of its own ("that because ye were compelled to be humble" -- Alma
    # 32:14), binds FORWARD to the next segment (its apodosis "ye were blessed"). Keyed
    # on surface forward-incompleteness (leader lexeme + all-verbs-subordinate), NOT on
    # the advcl head-attachment (stanza garbles that here -- it spuriously rooted
    # "blessed" + hung the because-advcl on the later "suppose"), so it is parse-robust.
    out = _forward_frame_bind(out)
    # MARKER REGISTRY break-license (framework §2.2) runs LAST, after all merges:
    # it splits a consolidated segment at a registered marker ("yea", "or rather")
    # when the marker-led colon is closure-eligible. This is break-GENERATING, so it
    # must see the post-merge segment shape (the yea-colon may sit MID-segment, e.g.
    # Alma 32:16's "...is baptized ..., yea, without being brought...").
    out = _marker_split(out)
    return out


def verse_atu_lines(verse_text, sentences):
    """Pure-method ATU lines for one verse: surface-order display segments, each
    sliced verbatim from verse_text (exact punctuation/spacing preserved).
    `sentences` is the pre-parsed UD (list of per-sentence Tok lists)."""
    # Build surface-contiguous display SEGMENTS that keep their tokens, so the
    # UD-aware binding rule-passes can operate before we render to text.
    spans = []                       # (start, end, atom_id, sent_idx, Tok)
    aid = 0
    for si, toks in enumerate(sentences):
        for atom in clause_atoms(Sent(toks)):
            for t in atom:
                spans.append((t.start, t.end, aid, si, t))
            aid += 1
    spans.sort(key=lambda s: s[0])
    segs = []                        # each: {'lo','hi','aid','sent_idx','toks'}
    for start, end, a, si, t in spans:
        if segs and a == segs[-1]["aid"]:
            segs[-1]["hi"] = end; segs[-1]["toks"].append(t)
        else:
            segs.append({"aid": a, "sent_idx": si, "lo": start, "hi": end, "toks": [t]})
    segs = _rule_passes(segs, sentences)
    lines = [verse_text[s["lo"]:s["hi"]].strip() for s in segs]
    lines = [ln for ln in lines if ln]
    # Punctuation attaches BACKWARD (Stan's convention: a line ends with its
    # punctuation, never opens with it). Move any leading ,;:.!?)— onto the
    # previous line; this is a rendering concern, distinct from the canon's
    # rule-level merges (R9 cc-forward, etc.) applied downstream.
    fixed = []
    for ln in lines:
        m = re.match(r"^([,;:.!?)—–’\"]+)\s*(.*)$", ln)
        if m and fixed:
            fixed[-1] = fixed[-1] + m.group(1)
            rest = m.group(2).strip()
            if rest:
                fixed.append(rest)
        else:
            fixed.append(ln)
    # R9 + opener-integrity: a line that is ONLY a leader word (coordinating
    # conjunction or a subordinate/relative opener) never stands alone — it LEADS
    # its content, so merge it forward into the clause it introduces.
    _LEADERS = {"and", "or", "but", "nor", "yet", "yea",     # coordinators / launchers (R9, M3)
                "that", "which", "who", "whom", "whose",     # relativizers / complementizer
                "when", "where", "while", "if", "because",   # subordinate openers
                "behold", "lo", "wherefore", "now", "for"}   # discourse launchers — lead, never alone
    _SPEECH_FRAME = {"saying", "saith"}                      # speech-frame -> binds BACKWARD to its verb

    def _all_leaders(s):
        words = [w.strip(",;:.!?—–’\"()").lower() for w in s.split()]
        words = [w for w in words if w]
        return bool(words) and all(w in _LEADERS for w in words)

    out = []
    carry = ""
    for ln in fixed:
        ln = (carry + " " + ln).strip() if carry else ln
        carry = ""
        bare = ln.strip().lower().rstrip(",;:.!?")
        if bare in _SPEECH_FRAME and out:   # lone "saying"/"saith" binds backward to the speech verb
            out[-1] = out[-1].rstrip() + " " + ln.strip()
        elif _all_leaders(ln):              # content-less launcher ("yea, and", "and behold") leads forward
            carry = ln
        else:
            out.append(ln)
    if carry:
        (out.append(carry) if not out else out.__setitem__(-1, out[-1] + " " + carry))
    # A line with no alphanumeric content (a lone "--" / stray punctuation) is not
    # an idea-unit; the glyph rides backward onto the previous line (punctuation
    # has no force, so this is pure rendering, never an ATU boundary).
    cleaned = []
    for ln in out:
        if not re.search(r"[0-9A-Za-z]", ln):
            if cleaned:
                cleaned[-1] = (cleaned[-1].rstrip() + " " + ln.strip()).rstrip()
        else:
            cleaned.append(ln)
    return cleaned


ADJUDICATED = REPO / "data" / "text-files" / "v2-adjudicated" / "overrides.json"
_OVERRIDES = None


def _overrides():
    """v2 LLM-adjudication layer (pipeline spec): hand-/LLM-corrected ATU line-breaks
    for the residual verses whose PARSE is too garbled for the mechanical rules
    (subject-fractures, verbless quotes). Keyed 'book c:v' -> [lines]."""
    global _OVERRIDES
    if os.environ.get("BOFM_BYPASS_OVERRIDES"):
        return {}
    if _OVERRIDES is None:
        _OVERRIDES = json.loads(ADJUDICATED.read_text(encoding="utf-8")) if ADJUDICATED.exists() else {}
    return _OVERRIDES


def _alnum(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _apply_override(verse_text, ref):
    """Return adjudicated lines IFF they re-segment ONLY (token-exact: the lines must
    reassemble to the verse alnum-for-alnum). An override can move line breaks, never
    change a word -- a mismatch is rejected and the mechanical pipeline runs."""
    ov = _overrides().get(ref)
    if not ov:
        return None
    if _alnum(" ".join(ov)) != _alnum(verse_text):
        print(f"  !! adjudication override REJECTED (text mismatch): {ref}", file=sys.stderr, flush=True)
        return None
    return ov


def deployed_atu_lines(book, c, v, verse_text, sentences):
    """The DEPLOYED ATU lines for a verse: the adjudication override if present (and
    token-exact), else the mechanical pipeline. Gate + detectors call this so they
    measure what actually ships, not the bare mechanical substrate."""
    ov = _apply_override(verse_text, f"{book} {c}:{v}")
    return ov if ov is not None else verse_atu_lines(verse_text, sentences)


def generate(book, chap=None):
    verses = read_v0(book)
    parsed = parse_book(book)
    out = []
    for (c, v) in sorted(verses):
        if chap is not None and c != chap:
            continue
        out.append(f"{c}:{v}")
        ov = _apply_override(verses[(c, v)], f"{book} {c}:{v}")
        out.extend(ov if ov is not None else
                   verse_atu_lines(verses[(c, v)], parsed.get((c, v), [])))
        out.append("")
    return out


OUT_DIR = REPO / "data" / "text-files" / "v2"


def _v2_target(book):
    """The deployed v2 source path for a book, read from booklist.txt (the
    canonical book_id -> file map the build + validators use). The pipeline
    writes directly here, so the v2 source IS the pipeline output (no draft)."""
    for ln in (REPO / "booklist.txt").read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        bid, path = ln.split(None, 1)
        if bid == book:
            return REPO / path.strip()
    raise KeyError(f"{book} not in booklist.txt")


CONLLU_OUT = REPO / "data" / "parses" / "v0-cache-conllu"


def write_conllu(book):
    """Emit the cached v0 parse as standard CoNLL-U keyed to match the pure-method
    v-file (so the canon validators can score the pure-method edition via the
    BOFM_CONLLU_DIR override). # text = the verbatim verse-text span so
    line_mapping's char-anchor locks onto the v-file content."""
    verses = read_v0(book)
    parsed = parse_book(book)
    out, sid = [], 0
    for (c, v) in sorted(verses):
        vtext = verses[(c, v)]
        for sent in parsed.get((c, v), []):
            if not sent:
                continue
            lo, hi = min(t.start for t in sent), max(t.end for t in sent)
            out.append(f"# sent_id = {sid}")
            out.append(f"# text = {vtext[lo:hi]}")
            for t in sent:
                out.append("\t".join([str(t.id), t.form, t.lemma, t.upos, "_", "_",
                                       str(t.head), t.deprel, "_", "_"]))
            out.append("")
            sid += 1
    CONLLU_OUT.mkdir(parents=True, exist_ok=True)
    p = CONLLU_OUT / f"{book}.conllu"
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return p


def write_book(book):
    """Generate the whole book and write a pure-method v-file (v2-mine format:
    verse marker + one ATU per line). Draft layer, parallel to v2-mine — the
    systematic PRE-applier segmentation the canon appliers refine next."""
    lines = generate(book)
    path = _v2_target(book)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def build_all():
    """One-command pure-method build: for every book, parse (cached; archaic-
    normalized, batched) -> regenerate the v2-puremethod-draft v-file -> emit the
    aligned CoNLL-U. Run `scripts/bofm_bidir_gate.py` after to measure. This is
    the repeatable pipeline (v0 -> v1 parse cache -> v2 draft); the canon appliers
    and build_book.py HTML build consume the draft downstream."""
    for b in BOOKFILE:
        parse_book(b)            # cache hit unless data/parses/v0-cache cleared
        write_book(b)
        write_conllu(b)
        print(f"built {b}", flush=True)
    print(f"DONE: {len(BOOKFILE)} books -> {OUT_DIR}")


def main():
    if "--all" in sys.argv:
        build_all()
        return
    if "--write" in sys.argv:
        book = sys.argv[1]
        print(f"wrote {write_book(book)}")
        return
    book = sys.argv[1] if len(sys.argv) > 1 else "1nephi"
    chap = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print("\n".join(generate(book, chap)))


if __name__ == "__main__":
    main()
