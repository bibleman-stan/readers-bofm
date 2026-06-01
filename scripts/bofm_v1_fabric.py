#!/usr/bin/env python3
"""BoFM v1 — OUR FABRIC. Clause-atoms derived from the UD parse (stanza CoNLL-U)
the way sblgnt_v1_fabric does from lowfat: each token attaches to the nearest
ancestor that heads a clause; clause-atoms are emitted in surface order. This is
the English instantiation of the mechanical-first v1 (no foreign-language layer,
no reconciler — the parse is over the display text itself).

A token HEADS a clause when its UD relation to its parent is clause-level:
  root, advcl(:relcl), acl(:relcl), ccomp, csubj(:pass), parataxis, and a
  coordinate (conj) whose head-word is a VERB/AUX (coordinated finite verbs
  split). xcomp (open complement, e.g. "began to teach") BINDS to its governor.

Usage (needs atu-method on PYTHONPATH):
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_v1_fabric.py 1nephi 0 2
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from atu_method.parsing.conllu_query import load_conllu  # noqa: E402

CONLLU = REPO / "data" / "parses" / "ensemble" / "stanza"

# A clause-atom head is a clause that STANDS as its own ATU. Complements (ccomp:
# "I know that X" — canon R17 complement integrity) and adnominal/relative clauses
# (acl, acl:relcl: "the record which I make" — canon R19) BIND to their governor by
# default, so they are NOT heads here; the canon appliers refine the exceptions
# (recitative/declarative complements split; non-restrictive relatives split).
# NB: csubj is NOT a clause-head (a clausal subject binds to its predicate), and
# parataxis is handled explicitly below (own-subject test), so neither is listed.
CLAUSE_RELS = {"root", "advcl"}


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# advcl marks that introduce a FRAME (temporal/conditional/concessive) — these
# bind to their main clause (incomplete alone, fail the bidirectional test).
# Participial advcls (no mark, "having...") are also frames. Only CAUSAL (because)
# and PURPOSE (to/that) advcls break per canon R6/R7 (and R29 re-binds bare "to").
_FRAME_MARKS = {"when", "before", "after", "while", "whilst", "until", "as",
                "if", "unless", "though", "although", "since", "whereas"}
# Subordinators stanza often tags as advmod (ADV) rather than `mark`, esp. fronted
# temporal/relative adverbs — used to recognize a subordinated advcl by lemma.
_SUBORD_ADV = {"when", "after", "before", "while", "whilst", "until", "since",
               "whereas", "where", "whensoever", "whithersoever", "wherein"}

# Periodic-participial-beat rule (1Ne1:1 disease). A SUBJECTLESS PARTICIPIAL GROUND
# ("having been born", "having seen", "being stricken") is normally an integrated
# ground that BINDS to the clause it modifies. But when such a ground is introduced
# by a LEADING COORDINATOR (cc and/but/or; adversative-additive advmod
# nevertheless/yet; discourse INTJ yea), it opens a NEW periodic beat and stands as
# its own ATU — "...therefore I was taught; AND having seen many afflictions...;
# YEA, having had a great knowledge...". Without this, periodic sentences collapse
# every participial ground onto the matrix line (1Ne1:1 over-merged 3 grounds + 2
# clauses into one line). The aux signature is the gerund-participle 'having'/'being'
# ONLY -- bare 'been' also heads finite present-perfect passives ("I have been
# chosen and consecrated"), which are gapped coordination and must keep binding.
_PART_AUX = {"having", "being"}
_LEAD_CC = {"and", "but", "or", "nor"}
_LEAD_ADVMOD = {"nevertheless", "yet", "howbeit", "notwithstanding"}
_LEAD_INTJ = {"yea"}
# Verba dicendi (for the DEFERRED M2 direct-speech ccomp release; Alma-32:5 class).
# Kept for the focused M2 pass that must also solve inverted-tag subject-stranding
# ("thus saith / the Lord") before it can ship.
_VERBA_DICENDI = {"say", "speak", "cry", "answer", "command", "declare", "exhort",
                  "ask", "tell", "reply", "utter", "proclaim", "preach"}
# Light pronoun heads for the pronoun-head restrictive-relative bind (framework
# §2.1 relative-clause corollary): a restrictive relative whose antecedent is a
# bare pronoun ("blessed are THEY who humble themselves", "he THAT believeth",
# "those WHICH follow") leaves the head not uniquely identified if removed, so it
# binds — same principle as a noun head, which already binds via acl:relcl.
_LIGHT_PRON = {"they", "them", "he", "him", "she", "her", "those", "thee", "thou",
               "ye", "we", "us", "it", "such"}


def _children(tok, by_id):
    return [c for c in by_id.values() if _i(c.head) == _i(tok.id)]


def _is_participial_ground(tok, by_id):
    """Subjectless clause headed by a gerund-participle aux (having/being)."""
    kids = _children(tok, by_id)
    has_part_aux = any((c.deprel or "").startswith("aux")
                       and (c.form or "").lower() in _PART_AUX for c in kids)
    has_subj = any((c.deprel or "").split(":")[0] in ("nsubj", "csubj") for c in kids)
    return has_part_aux and not has_subj


def _has_leading_coordinator(tok, by_id):
    """A cc/discourse-connective child marking this clause as a new periodic beat."""
    for c in _children(tok, by_id):
        f = (c.form or "").lower()
        dep = c.deprel or ""
        if dep == "cc" and f in _LEAD_CC:
            return True
        if dep == "advmod" and f in _LEAD_ADVMOD:
            return True
        if dep == "discourse" and f in _LEAD_INTJ:
            return True
    return False


def _is_subordinated_participial(tok, by_id):
    """Carries a subordinating mark/SCONJ ("after having been", "without being
    brought") -- subordinated, so it binds to its matrix per the marked-advcl rule;
    the leading coordinator (e.g. an intensifying "yea") is resumption, not a beat."""
    return any(_i(c.head) == _i(tok.id) and ((c.deprel or "") == "mark" or c.upos == "SCONJ")
               for c in by_id.values())


def _is_subjected_gerund(tok, by_id):
    """A participial that has its OWN subject ("their being nourished") is a gerund
    nominalization / absolute, not a bare adverbial ground; its coordinate members
    are coordinate nominals, not new clausal beats."""
    has_part_aux = any((c.deprel or "").startswith("aux")
                       and (c.form or "").lower() in _PART_AUX
                       for c in _children(tok, by_id))
    has_subj = any((c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                   for c in _children(tok, by_id))
    return has_part_aux and has_subj


def _is_aictp_frame(verb, by_id):
    """AICTP narrative frame: a 'come' verb with an xcomp 'pass' ("(it) came to
    pass"). Semantically empty (Hebrew wayhi temporal frame); the main clause it
    introduces binds to it as one ATU -- whether rendered with 'that' (parataxis) or
    'and' (conj). The 'and'/'that' split is a KJV translation artifact of one Hebrew
    construction (wayhi + waw/ki)."""
    return (verb is not None and (verb.lemma or "").lower() == "come"
            and any(_i(c.head) == _i(verb.id) and (c.lemma or "").lower() == "pass"
                    and (c.deprel or "").split(":")[0] == "xcomp"
                    for c in by_id.values()))


def _is_finite_clause(verb, by_id):
    """Finite main-clause head: NOT a participial. A participial ("having dwelt",
    "being raised", a bare "-ing") is non-finite and cannot be the displaced main
    clause of an AICTP frame -- it is a parenthetical/circumstantial aside."""
    if (verb.form or "").lower().endswith("ing"):
        return False
    return not any(_i(c.head) == _i(verb.id) and (c.deprel or "").startswith("aux")
                   and (c.form or "").lower() in ("having", "being")
                   for c in by_id.values())


def _aictp_displaced_main(frame, by_id):
    """The single clause an empty AICTP frame binds: the FIRST (lowest-id) FINITE
    parataxis/conj-VERB child. A participial parenthetical ("(my father, Lehi, having
    dwelt...)", 1Ne1:4) is non-finite -> not it; a SUBSEQUENT finite coordinate
    ("...and he saw and heard", 1Ne1:6) is later -> not it (splits normally)."""
    cands = [_i(c.id) for c in by_id.values()
             if _i(c.head) == _i(frame.id)
             and (c.deprel or "").split(":")[0] in ("parataxis", "conj")
             and c.upos in ("VERB", "AUX")
             and _is_finite_clause(c, by_id)]
    return min(cands) if cands else None


# New-beat connectives: a content clause OPENED by one of these is a distinct
# discourse beat (resumption/contrast/explanation), NOT the reported proposition of
# the speech verb -- so the verbum-dicendi proposition bind must NOT swallow it.
# "I say unto you, Yea; NEVERTHELESS it hath not grown..." (Alma 32:29) and
# "I say unto you, Yea; FOR every seed bringeth forth..." (Alma 32:31): the
# nevertheless-/for-clause stands; only the short "Yea" answer is the proposition.
# Keyed on the connective LEMMA (punctuation-invariant): the comma/semicolon that
# happens to precede it is never consulted -- the connective token is.
_BEAT_CONNECTIVE = {"nevertheless", "yet", "howbeit", "notwithstanding", "but",
                    "for", "wherefore", "therefore", "yea", "and", "or", "nor",
                    "otherwise"}


def _opens_new_beat(tok, by_id):
    """The clause `tok` heads opens with a leading new-beat connective (a cc /
    adversative-additive advmod / discourse / 'for'-mark child positioned at or
    before the clause head). Punctuation-invariant: tests the connective lemma, not
    the comma. Used by the verbum-dicendi proposition bind to keep a distinct
    following beat (nevertheless.../for...) from being swallowed into 'I say'."""
    for c in _children(tok, by_id):
        dep = (c.deprel or "").split(":")[0]
        # Check BOTH lemma AND surface form against the registry: stanza lemmatizes
        # "wherefore" -> "so" (and "therefore" can normalize similarly), so a lemma-only
        # test missed the leading "wherefore" beat-connective on 2Ne 25:29. The comma/
        # semicolon before it is never consulted -- only the connective lexeme.
        lem = (c.lemma or "").lower()
        form = (c.form or "").lower()
        if dep in ("cc", "advmod", "discourse", "mark") \
           and (lem in _BEAT_CONNECTIVE or form in _BEAT_CONNECTIVE) \
           and _i(c.id) is not None and _i(tok.id) is not None and _i(c.id) <= _i(tok.id):
            return True
    return False


def _has_own_subject(tok, by_id):
    """tok governs its OWN referential subject (nsubj/csubj/nsubj:pass) -- an expletive
    `expl` ("it is well") or a shared subject attached to a coordinate's first conjunct
    does NOT count, so a coordinate that merely shares the matrix subject is not flagged
    independent."""
    return any((g.deprel or "").split(":")[0] in ("nsubj", "csubj")
               for g in _children(tok, by_id))


def _is_verbal_independent_predication(c, by_id):
    """`c` is an independent finite VERB/AUX clause: a finite VERB/AUX with its OWN
    subject (or another speech verb). Used for parataxis/advcl/conj-VERB siblings."""
    return c.upos in ("VERB", "AUX") and (
        _has_own_subject(c, by_id) or (c.lemma or "").lower() in _VERBA_DICENDI)


def _is_copular_independent_predication(c, by_id):
    """`c` is an independent COPULAR clause: a predicate-nominal/adjective head
    (PRON/NOUN/PROPN/ADJ) carrying a `cop` child, with its own subject ("the Lamanites
    ARE upon us", Alma 52:11). The conj-head is then the predicate word, not a VERB, so
    the old VERB/AUX-only test missed it. Punctuation-invariant (upos + cop presence)."""
    if c.upos not in ("PRON", "NOUN", "PROPN", "ADJ"):
        return False
    has_cop = any((g.deprel or "").split(":")[0] == "cop" for g in _children(c, by_id))
    return has_cop and _has_own_subject(c, by_id)


def _is_finite_independent_predication(c, by_id):
    """`c` is an independent finite clause -- verbal OR copular."""
    return (_is_verbal_independent_predication(c, by_id)
            or _is_copular_independent_predication(c, by_id))


def _is_multiclause_quote(tok, by_id):
    """The clause `tok` heads is a distinct MULTI-CLAUSE direct-discourse performance
    (its own paragraph-scale ATU set), NOT a single reported proposition. Signal: the
    proposition itself governs a FURTHER finite independent predication beyond itself --
    a second standalone clause that the speech frame should not swallow. A genuine
    single reported proposition ("it is well that ye are cast out...", "ye shall have
    power ... and shall smite ...") governs only BOUND complements/relatives/frames and
    subject-sharing coordinates, with no independent sibling clause.

    Three attachment configurations count as a further independent predication
    (ccomp-aware + copular-aware, per the §7.3 audit on Alma 9:19 / Alma 52:11):
      - a parataxis/conj/advcl clause that is finite-independent (VERB/AUX with own
        subject, or another speech verb);
      - a SUBJECTED ccomp -- a complement clause carrying its OWN subject ("[he would]
        suffer THAT THE LAMANITES might destroy ...", Alma 9:19; "[I say] THAT the right
        way is ..." stays a single complement, but a ccomp with a further independent
        clause is caught recursively);
      - a COPULAR coordinate whose conj-head is a predicate-nominal/adjective ("but
        behold, THE LAMANITES ARE upon us", Alma 52:11 -- conj-head is the PRON `us` with
        a `cop`, which the old VERB/AUX-only test missed).
    This is the complement-vs-quote discriminator (framework §2.1) keyed structurally,
    not on punctuation -- analogous to the GNT engine's recitative qflag quote-protection."""
    for c in _children(tok, by_id):
        dep = (c.deprel or "").split(":")[0]
        # parataxis/advcl sibling -> a finite VERB clause with its own subject. (NOT
        # copular here: a parataxis copular purpose-continuation "..., that ye may be
        # humble" is a normal split-on-own-subject sibling, not a quote performance --
        # flagging it would wrongly pull the FIRST proposition off the speech line,
        # Alma 32:12.)
        if dep in ("parataxis", "advcl") and _is_verbal_independent_predication(c, by_id):
            return True
        # conj coordinate -> independent VERB clause OR copular predicate-nominal
        # ("but behold, the Lamanites ARE upon us", Alma 52:11). A conj that merely
        # SHARES the matrix subject (Helaman 10:6 "... and shall smite the earth") is
        # not independent -> not flagged.
        if dep == "conj" and _is_finite_independent_predication(c, by_id):
            return True
        # a SUBJECTED ccomp is a further independent predication ("[he would] suffer
        # THAT THE LAMANITES might destroy ...", Alma 9:19). A SUBJECTLESS ccomp /
        # to-infinitival complement ("I declare ... that ye shall have power") is the
        # single reported complement and still binds.
        if dep == "ccomp" and _has_own_subject(c, by_id):
            return True
        # recurse one level through a bound, NON-independent subordinate (a lone
        # ccomp/advcl/conj that is not itself independent) so a further independent
        # clause nested under it is still detected.
        if dep in ("ccomp", "advcl", "conj") and not _is_finite_independent_predication(c, by_id):
            for g in _children(c, by_id):
                gdep = (g.deprel or "").split(":")[0]
                if gdep in ("parataxis", "conj") and _is_finite_independent_predication(g, by_id):
                    return True
    return False


def _relcl_antecedent_is_light_pron(tok, by_id):
    """The antecedent of a relative clause is a light pronoun. Two attachment
    shapes: (1) the relcl is acl:relcl directly under the pronoun ("he THAT
    believeth" -> head is the PRON); (2) stanza attaches the relcl as advcl:relcl
    under the matrix PREDICATE verb of a copular/passive clause ("blessed are they
    who humble themselves" -> head is the verb 'blessed', whose nsubj is 'they').
    In shape (2) the true antecedent is the matrix subject pronoun."""
    head = by_id.get(_i(tok.head))
    if head is None:
        return False
    if head.upos == "PRON" and (head.form or "").lower() in _LIGHT_PRON:
        return True
    # shape (2): relcl pinned to a predicate verb -> antecedent is that verb's subject
    if head.upos in ("VERB", "AUX", "ADJ"):
        subj = next((c for c in _children(head, by_id)
                     if (c.deprel or "").split(":")[0] in ("nsubj", "csubj")), None)
        if subj is not None and subj.upos == "PRON" and (subj.form or "").lower() in _LIGHT_PRON:
            return True
    return False


def is_clause_head(tok, by_id=None):
    base = (tok.deprel or "").split(":")[0]
    # Pronoun-head restrictive-relative bind (framework §2.1 corollary). A noun-head
    # relative already binds (acl:relcl falls through to bind below); the gap is the
    # LIGHT-PRONOUN head ("blessed are they WHO humble themselves" = one ATU). Such a
    # relcl is mis-routable: stanza tags it acl:relcl (binds anyway) OR advcl:relcl
    # pinned to the matrix predicate verb (would hit the advcl branch and split on the
    # relative's own 'who' subject). Intercept both here so the pronoun-head relative
    # binds to its head regardless of the relcl deprel variant. (Alma 32:16 task A.)
    if "relcl" in (tok.deprel or "") and by_id is not None \
       and _relcl_antecedent_is_light_pron(tok, by_id):
        return False
    # Coordinator-led participial beat: a subjectless participial GROUND
    # (advcl/conj/parataxis) introduced by a leading coordinator opens its own ATU.
    # Checked before the bind-defaults below so it intercepts the periodic over-merge
    # (1Ne1:1 collapsed 3 grounds + 2 clauses onto one line). It fires ONLY on a
    # genuine adverbial ground; three principled exclusions (each already encoded
    # elsewhere as a bind) keep it from over-firing on participials that aren't:
    #   - ADNOMINAL: head is a NOUN/PRON ("all these, having been punished") -> the
    #     participle modifies a noun, binds like a relative (acl principle, WoM1:16);
    #   - SUBORDINATED: carries a mark/SCONJ ("yea, after having been favored") ->
    #     marked-advcl rule binds it (Alma9:20/32:16);
    #   - COORDINATE-OF-GERUND: a conj whose head is a subjected gerund ("their being
    #     nourished AND being carried") is a coordinate nominal, not a clause (1Ne22:8).
    if base in ("advcl", "conj", "parataxis") and by_id is not None:
        if _is_participial_ground(tok, by_id) and _has_leading_coordinator(tok, by_id):
            head = by_id.get(_i(tok.head))
            adnominal = head is not None and head.upos in ("NOUN", "PROPN", "PRON")
            coord_gerund = base == "conj" and head is not None and _is_subjected_gerund(head, by_id)
            if not (adnominal or _is_subordinated_participial(tok, by_id) or coord_gerund):
                return True
    # advcl: a MARKED adverbial clause is subordinate and cannot stand alone, so it
    # BINDS -- this holds for every mark, not just temporal/conditional frames:
    # causal "because", purpose/result "that"/"so"/"insomuch", concessive
    # "though", temporal "when/after/while". The prior R6/R7 causal/purpose BREAK
    # manufactured the stranded "because thou art merciful," / "that they might
    # take it away" fragments the bidirectional audit flagged (338 "that" + 70
    # "because"). An UNMARKED advcl splits ONLY if it is a finite clause with its
    # OWN subject (an asyndetic parallel colon, e.g. Hebrew-poetry "the Lord shall
    # comfort Zion // he will comfort her waste places"); a subjectless unmarked
    # advcl is participial ("having seen many afflictions") -> bind.
    if base == "advcl" and by_id is not None:
        # A clause is subordinated if it carries a subordinator. stanza tags these
        # inconsistently -- "because"/"that"/"if" as `mark`, but fronted temporal
        # "when"/"after"/"before" often as `advmod` (ADV) -- so detect by deprel
        # OR by subordinator lemma, not by `mark` alone (else "And when the Jews
        # heard these things" splits as a fronted-frame fragment).
        subordinated = any(
            _i(c.head) == _i(tok.id) and (
                (c.deprel or "") == "mark"
                or c.upos == "SCONJ"
                or ((c.deprel or "").split(":")[0] == "advmod"
                    and (c.lemma or c.form or "").lower() in _SUBORD_ADV))
            for c in by_id.values())
        own_subj = any(_i(c.head) == _i(tok.id)
                       and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                       for c in by_id.values())
        if subordinated:
            # EME causal 'for' (stanza mistags as SCONJ/mark) with its OWN subject is
            # an independent explanatory predication (causal coordinator = Hebrew ki),
            # not a bound subordinate -> it splits. A bare/gapped 'for'-clause, any
            # genuinely subordinating mark (when/that/because/if), and the carve-outs
            # below still bind. (Alma-32:5 class, M1 — the for-causal mechanism.)
            for_marks = [c for c in by_id.values() if _i(c.head) == _i(tok.id)
                         and (c.form or "").lower() == "for"
                         and ((c.deprel or "") == "mark" or c.upos == "SCONJ")]
            # Carve-outs (each leaks a fragment if split, per the M1 audit):
            #  - participial ("for he HAVING been taught" -> no finite verb): bind;
            #  - a SECOND subordinator beyond 'for' ("for AS ... even so", "for ... SAVE"
            #    -> correlative/conditional whose apodosis is the next beat): bind.
            participial = any((c.deprel or "").startswith("aux")
                              and (c.form or "").lower() in _PART_AUX
                              for c in by_id.values()
                              if _i(c.head) == _i(tok.id))
            other_sub = any(_i(c.head) == _i(tok.id) and (c.form or "").lower() != "for"
                            and ((c.deprel or "") == "mark" or c.upos == "SCONJ"
                                 or ((c.deprel or "").split(":")[0] == "advmod"
                                     and (c.lemma or c.form or "").lower() in _SUBORD_ADV))
                            for c in by_id.values())
            if for_marks and own_subj and not participial and not other_sub:
                return True
            return False   # marked/subordinated clause -> bind
        return own_subj    # unmarked: finite parallel colon splits, participial binds
    # AICTP frame (Hebrew B5 / canon R1): "(it) came to pass [that] X" is a
    # semantically-empty narrative frame — bare "And it came to pass" fails the
    # bidirectional ATU test, so the main clause it introduces (parsed as a
    # parataxis under "came...to pass") BINDS to it as one ATU. The rule-count
    # doesn't reward this (canon gap), but the bidirectional test mandates it.
    if base == "parataxis" and by_id is not None:
        h = by_id.get(_i(tok.head))
        if h is not None and (h.lemma or "").lower() == "come" and any(
                _i(c.head) == _i(h.id) and (c.lemma or "").lower() == "pass"
                and (c.deprel or "").split(":")[0] == "xcomp"
                for c in by_id.values()):
            return False   # AICTP frame
        # Verbum-dicendi reported-proposition bind (framework §2.1: the performative
        # assertion-matrix). A FINITE content clause attached as `parataxis` to a
        # speech verb is that verb's reported PROPOSITION -- "I say unto you, [that]
        # it is well that ye are cast out..." (Alma 32:12). The performative "I say"
        # begs "say WHAT?"; its open valency is filled by the proposition, so the two
        # are ONE ATU. stanza routes the content to `parataxis` (not `ccomp`) purely
        # because of the editorial comma after "you"; per the punctuation-zero-force
        # corollary parataxis==ccomp here -- so we KEY on the speech-verb lemma + a
        # finite parataxis child, NEVER on the comma. Two guards keep this from
        # piercing a genuine distinct quote (the recitative-pierce risk, analogous to
        # the GNT recitative qflag): (1) a clause OPENED by a new-beat connective
        # (nevertheless/for/yea...) is a distinct following beat, not the proposition
        # (Alma 32:29/32:31 -- the short "Yea" answer binds, the nevertheless-/for-
        # beat stands); (2) a MULTI-CLAUSE quoted performance (>=1 independent sibling
        # predication) is its own paragraph-scale discourse and stands (Alma 10:17
        # "O ye wicked...; for ye are laying...; for ye are laying..."). And (3) ONLY
        # the FIRST (lowest-id) parataxis child of the speech verb is the reported
        # proposition; LATER parataxis siblings are distinct quoted clauses of an
        # ongoing performance and stand on their own (Alma 14:11 "...The Spirit
        # constraineth me..." binds, but the later parataxis "for behold the Lord
        # receiveth them up..." -- with its OWN subject 'the Lord' -- is a separate
        # beat, even though stanza dropped its 'for' off the verb). A single reported
        # proposition (finite, first, no new-beat opener, no independent siblings)
        # binds.
        para_sibs = [_i(c.id) for c in by_id.values()
                     if _i(c.head) == _i(tok.head)
                     and (c.deprel or "").split(":")[0] == "parataxis"]
        is_first = bool(para_sibs) and _i(tok.id) == min(para_sibs)
        # (4) the proposition itself must NOT be a verbum dicendi: a parataxis whose
        # own head is a speech verb AND which is ITSELF a speech verb is a nested/
        # closing speech TAG ("...against the men of my people, SAITH the Lord of
        # Hosts" -- Jacob 2:32, the postposed-subject inverted tag), a quote FRAME, not
        # the reported content. It falls through to the own-subject test below (its
        # postposed subject makes it an independent tag clause -> splits).
        if h is not None and (h.lemma or "").lower() in _VERBA_DICENDI \
           and (tok.lemma or "").lower() not in _VERBA_DICENDI \
           and is_first \
           and _is_finite_clause(tok, by_id) \
           and not _opens_new_beat(tok, by_id) \
           and not _is_multiclause_quote(tok, by_id):
            return False   # reported proposition -> binds to the speech verb
        # stanza over-uses `parataxis` for appositive NPs ("a fire which cannot be
        # consumed", "even an unquenchable fire") and bare-infinitival elaborations
        # ("yea, to preach unto all") that cannot stand alone. A parataxis splits
        # ONLY if it is a genuine independent clause with its OWN subject; an
        # appositive / bare-infinitive / subjectless parataxis binds (same
        # own-subject discriminator as coordinate verbs).
        own_subj = any(_i(c.head) == _i(tok.id)
                       and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                       for c in by_id.values())
        return own_subj
    # Direct-speech ccomp release (Alma-32:5 class, M2). ccomp normally BINDS (R17
    # complement integrity: "I know THAT X"). But a ccomp under a verbum dicendi is
    # QUOTED SPEECH -- multi-clause discourse, not one integrated complement -- so it
    # stands as a clause-head and its internal clause-atoms (the quoted question, the
    # causal explanations) surface normally. Matrix lemma is the discriminator.
    if base == "ccomp" and by_id is not None:
        h = by_id.get(_i(tok.head))
        # (a) Only DIRECT quotation releases; indirect "say THAT X" keeps the 'that'
        #     complementizer and binds per R17. Equivalently, ANY subordinating
        #     mark child ("ask IF ye have read", "wonder WHETHER", "ask WHEN") is
        #     an interrogative/clausal complement, not a quotation — bind.
        has_subord = any(_i(c.head) == _i(tok.id)
                         and ((c.deprel or "") == "mark" or c.upos == "SCONJ")
                         for c in by_id.values())
        has_that = has_subord  # backward-compat alias for the subsequent check
        # (b) Don't release when the speech verb is itself in a relative/adnominal
        #     clause ("the word WHICH SAITH ..."): releasing strands the relativizer.
        h_in_relcl = h is not None and ("relcl" in (h.deprel or "")
                                        or (h.deprel or "").split(":")[0] == "acl")
        # (c) The inverted prophetic-formula ("thus saith THE LORD, I have led...") is
        #     repaired UPSTREAM by parse_repair.R-INV (the postposed subject is
        #     re-attached to the speech verb before the rules run), so direct speech
        #     ALWAYS releases here -- including with a vocative ("saying: Enos, thy sins
        #     are forgiven"; "said: Lord, how is it done?"). No inverted guard: it only
        #     blocked legitimate vocative/pronoun releases (Enos 1:5/1:8/1:10).
        if h is not None and (h.lemma or "").lower() in _VERBA_DICENDI \
           and not has_that and not h_in_relcl:
            return True
    if base in CLAUSE_RELS:
        return True
    if base == "conj" and tok.upos in ("VERB", "AUX"):
        # Coordinate finite verbs: a conjunct BINDS iff it has NO SUBJECT of its
        # own. A subjectless conjunct shares (gaps) the head's subject — it is a
        # subjectless predicate that cannot stand alone as one thought ("and heard
        # much", "and dwelt upon a rock", "and stoned, and slain", "and spake unto
        # his children"), so it must bind regardless of what objects/obliques it
        # carries or how long the chain is. A conjunct with its OWN overt subject
        # is an independent predication ("he came, and they departed") -> split.
        #
        # This is the EARNED port of Hebrew B7: B7 binds on incompleteness/bareness
        # of the member, NOT on count. Hebrew has no N>=3 cliff — wayyiqtol chains
        # split per COMPLETE predication. The BoFM §3.5.2 count cliff (N=2 binds /
        # N>=3 splits) and the own_args gate were unvalidated proxies that the
        # 5-genre bidirectional audit + the Hebrew mechanism both falsify (they
        # manufactured bare-fragment lines). Discriminator = own-subject, ported
        # from B7 bareness + R12 shared-ellipsis. Errs toward bind (safer).
        if by_id is not None:
            # AICTP "and"-form: the FIRST coordinate main clause of an empty
            # "(it) came to pass" frame is the displaced main predication and BINDS
            # to the frame (one ATU), exactly like the "that"-form parataxis. Later
            # coordinate clauses split normally. (Hebrew wayhi + waw == wayhi + ki.)
            head = by_id.get(_i(tok.head))
            if _is_aictp_frame(head, by_id) and _aictp_displaced_main(head, by_id) == _i(tok.id):
                return False   # the displaced main clause of the AICTP frame -> bind
            # A subsequent finite coordinate after the main clause (1Ne1:6 "...and he
            # saw and heard") is NOT the displaced main -> falls through, splits below.
            own_subj = any(_i(c.head) == _i(tok.id)
                           and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                           for c in by_id.values())
            if not own_subj:
                # Reframed-coordinate carve-out: a subjectless conjunct that
                # carries its own FRAME mark (if/when/as/though/...) OR an
                # advcl-frame child with a FRAME mark is NOT gapped ellipsis —
                # it opens a distinct thought-frame ("..., but if X, [then] Y"
                # / "...and as X, Y"). Restricted to _FRAME_MARKS so
                # infinitival purpose "to atone" + xcomp does NOT trigger
                # (Alma 33:22 "and die to atone" must stay bound). Alma 33:22
                # (if/but-if conditional pair) + Alma 33:23 (matrix + as-frame
                # imperative) class.
                tok_pos = _i(tok.id) or 0
                # FRAME mark/advmod accepts SCONJ-mark, ADV-advmod tagged
                # forms in _FRAME_MARKS (Stanza inconsistently tags when/if
                # as mark vs advmod depending on syntactic environment).
                def _is_frame_marker(c):
                    return ((c.form or "").lower() in _FRAME_MARKS
                            and ((c.deprel or "") in ("mark", "advmod")
                                 or c.upos in ("SCONJ", "ADV")))
                own_frame_mark = any(_i(c.head) == _i(tok.id)
                                     and _is_frame_marker(c)
                                     and (_i(c.id) or 0) < tok_pos
                                     for c in by_id.values())
                if own_frame_mark:
                    return True
                advcl_with_frame_mark = any(
                    _i(c.head) == _i(tok.id)
                    and (c.deprel or "").split(":")[0] == "advcl"
                    and (_i(c.id) or 0) < tok_pos
                    and any(_i(g.head) == _i(c.id) and _is_frame_marker(g)
                            for g in by_id.values())
                    for c in by_id.values())
                if advcl_with_frame_mark:
                    return True
                return False   # subjectless conjunct (gapped subject) -> bind
        return True            # own overt subject -> independent predication -> split
    # Relative clause (acl:relcl) always BINDS to its antecedent. A relativizer-
    # headed clause ("whom he hath chosen", "which I make", "that follow after
    # righteousness") opens with a relative pronoun bound to its antecedent and
    # CANNOT stand alone (fails the bidirectional forward test) -- this holds for
    # restrictive AND non-restrictive relatives alike (", who were a stiffnecked
    # people" is just as much a relativizer fragment). Hebrew B3 / Greek
    # restrictive-ὅς converge here. The prior R19 cataphoric exception (split when
    # the antecedent is PRON/DET, "those whom...") manufactured the 921 stranded-
    # relative fragments the audit flagged, so it is retired. acl:relcl is never a
    # clause-head; it falls through to bind.
    return False


def clause_atoms(sent):
    """Return [[tok,...], ...] — tokens grouped by nearest clause-head ancestor,
    clause-atoms in surface order, tokens within each in surface order."""
    by_id = {_i(t.id): t for t in sent.tokens if _i(t.id) is not None}

    def head_of(tok):
        cur, seen = tok, set()
        while cur is not None and _i(cur.id) not in seen:
            seen.add(_i(cur.id))
            if is_clause_head(cur, by_id) or _i(cur.head) in (0, None):
                return _i(cur.id)
            cur = by_id.get(_i(cur.head))
        return _i(tok.id)

    groups = {}
    for t in sent.tokens:
        if _i(t.id) is None:        # skip multiword-token ranges (e.g. "5-6")
            continue
        groups.setdefault(head_of(t), []).append(t)
    atoms = sorted(groups.values(), key=lambda ts: _i(ts[0].id))
    for ts in atoms:
        ts.sort(key=lambda t: _i(t.id))
    return atoms


def _text(ts):
    out = []
    for t in ts:
        out.append(t.form)
    return " ".join(out)


def emit_surface(sent):
    """Surface-ORDER display lines (ported from the GNT engine): a line is a
    maximal run of surface-consecutive tokens sharing one clause-atom id, so the
    rendered text == source order even when a clause is discontinuous. This is
    the PURE-METHOD initial segmentation — derived only from the UD parse, with
    zero dependence on the hand-edited v2-mine breaks."""
    atoms = clause_atoms(sent)
    lid = {}
    for i, ts in enumerate(atoms):
        for t in ts:
            lid[_i(t.id)] = i
    toks = sorted((t for t in sent.tokens if _i(t.id) is not None),
                  key=lambda t: _i(t.id))
    lines, cur, cur_lid = [], [], None
    for t in toks:
        li = lid[_i(t.id)]
        if li != cur_lid and cur:
            lines.append(cur); cur = []
        cur.append(t); cur_lid = li
    if cur:
        lines.append(cur)
    return [_text(ts) for ts in lines]


def main():
    book = sys.argv[1] if len(sys.argv) > 1 else "1nephi"
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else lo + 1
    sents = load_conllu(str(CONLLU / f"{book}.conllu"))
    for sid in range(lo, hi):
        if sid >= len(sents):
            break
        sent = sents[sid]
        print(f"=== {book} sent {sid} (surface-order pure-method ATU lines) ===")
        for line in emit_surface(sent):
            print(f"  {line}")
        print()


if __name__ == "__main__":
    main()
