"""§2.2 parallel-subordinator-stack leader detection for validators.

Mirrors bofm_generate.py's _detect_stack_leaders but works on the validator's
conllu_query token API. Returns the set of token IDs in a sentence that lead
a §2.2 stack-member ATU (these tokens' "that"-mark + clause are licensed
splits per framework §2.2 and should be exempted from §2.1-default rule
violations).

Usage:
    from validators.colometry.stack_detection import stack_leader_ids
    leaders = stack_leader_ids(sent.tokens)  # set of token IDs
    if mark.id in leaders:
        skip_violation()  # this 'that' is a §2.2 stack member, not a rule_17 case
"""

_VERBA_DICENDI = {"say", "speak", "cry", "answer", "command", "declare",
                  "exhort", "ask", "tell", "reply", "utter", "proclaim", "preach"}
_STACK_EXCLUDE_VERBS = _VERBA_DICENDI | {
    "know", "see", "perceive", "remember", "forget", "think", "suppose",
    "believe", "trust", "judge", "deem", "behold", "learn", "understand",
    "observe", "swear", "vow", "doubt", "marvel", "rejoice", "find",
    "show", "hear", "witness", "promise", "desire", "would", "will",
    "wish", "hope", "fear", "plead", "command", "cause", "suffer",
}


def stack_leader_ids(tokens):
    """Token list (duck-typed: id, form, deprel, upos, lemma) -> set of IDs
    that lead a §2.2 stack-member ATU.

    Rule: >=2 'that'-mark/SCONJ tokens in sentence, each NOT preceded within
    5 content tokens by 'to pass' (AICTP), each NOT immediately preceded
    (within 2 non-PUNCT tokens) by a single-complement verb.
    """
    def _i(x):
        try:
            return int(x)
        except (TypeError, ValueError):
            return None

    by_pos = sorted(tokens, key=lambda t: _i(t.id) or 0)
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
                if lemma in _STACK_EXCLUDE_VERBS:
                    single_comp = True
                break
            seen_nonpunct += 1
            if seen_nonpunct >= 3:
                break
        if single_comp:
            continue
        candidates.append(t)
    if len(candidates) >= 2:
        return {t.id for t in candidates}
    return set()
