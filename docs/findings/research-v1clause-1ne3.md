# v1-clause — a parallel clause-level layer for BoFM

**Nothing here ships.** `data/text-files/v1-clause/` is a parallel render. It is not in
`booklist.txt`, so `build_book.py` and the validators never see it; `data/text-files/v2/`,
`data/text-files/v2-adjudicated/overrides.json`, `books/`, and `sw.js` were not touched.

## What v1 is

`scripts/bofm_generate.py --stage v1` runs framework §3's **v1** stage and stops:
`bofm_v1_fabric.clause_atoms` segmentation with `_rule_passes` skipped. Default stays
`--stage v2`, byte-identical to before (verified against `git show HEAD` on 1nephi,
enos, moroni).

Skipping `_rule_passes` removes **both directions** of the binding layer, which is the
headline result below: it drops the merges (R29 infinitival, yea-B, AICTP, short-answer
peel, forward-frame bind) *and* the two break-generating passes (§2.2 marker split,
parallel-subordinator stack split). v1 also skips `data/text-files/v2-adjudicated/overrides.json` and
`data/text-files/v2-adjudicated/cross-verse-merges.json`, which are v2-only judgment layers keyed to v2 line shapes.

Retained in v1 because they are rendering, not binding — none merges two clause atoms
on grammatical grounds: line-final-CCONJ travel, backward punctuation attachment,
lone-leader carry, and the no-alnum-content sweep. Without the last two a clause-level
view would contain lines that are only `and` or `--`, which are not clauses and would
corrupt every length statistic taken over them.

## Text parity — verified

| check | result |
|---|---|
| v1 per-verse vs v0 source, alnum-exact | **618 / 618 verses identical** |
| v1 whole-book character stream vs v0 | **identical** (102,188 alnum chars) |
| v1 whole-book character stream vs deployed v2 | **identical** |
| `--stage v2` output vs `git show HEAD` output | **identical**, 3 books |

Only break positions move.

## Marschall bands — 1 Nephi, whole book

Counter: `scripts/marschall_view.py` `syllables()`, unchanged, so these are comparable
to `docs/findings/research-marschall-1ne3.md`.

| band | v2 deployed | v1 clause |
|---|---|---|
| &lt;7 — comma (L1) | 135 (9%) | 133 (9%) |
| 7–9 — comma/colon (L1) | 151 (10%) | 142 (10%) |
| 10–25 — standard colon (T1) | 783 (51%) | 755 (51%) |
| 26–35 — long colon (L2 ok) | 214 (14%) | 211 (14%) |
| &gt;35 — **L2 VIOLATION** | 238 (16%) | 244 (16%) |
| **total lines** | **1521** | **1485** |
| median syllables | 17 | 17 |
| mean syllables | 21.5 | 22.0 |
| over T1 ceiling (&gt;25) | 452 (30%) | 455 (31%) |
| longest line | 139 syll | 170 syll |

## Marschall bands — 1 Nephi 3

| band | v2 deployed | v1 clause | marschall |
|---|---|---|---|
| &lt;7 — comma (L1) | 3 (4%) | 5 (7%) | 14 (16%) |
| 7–9 — comma/colon (L1) | 9 (12%) | 6 (9%) | 13 (15%) |
| 10–25 — standard colon (T1) | 40 (56%) | 37 (54%) | 46 (52%) |
| 26–35 — long colon (L2 ok) | 13 (18%) | 12 (17%) | 15 (17%) |
| &gt;35 — **L2 VIOLATION** | 7 (10%) | 9 (13%) | 1 (1%) |
| **total lines** | **72** | **69** | **89** |
| median syllables | 16 | 16 | 15 |
| mean syllables | 19.6 | 20.4 | 15.9 |
| over T1 ceiling (&gt;25) | 20 (28%) | 21 (30%) | 16 (18%) |
| longest line | 60 syll | 60 syll | 39 syll |

The v2 column reproduces the committed probe exactly — 72 lines, 20 over the T1
ceiling (28%), 7 L2 violations (10%), 89 Marschall cola — which confirms the counter is
the same one.

## The result

**v1 is coarser than v2, not finer.** 1 Nephi: 1485 clause lines against
1521 deployed ATU lines. Its L2 violation rate is slightly *worse*
(244 vs 238
lines over 35 syllables), and its longest single unit is 1 Ne 19:10 at **170 syllables**
— one clause atom, nearly five times Marschall's Law ceiling.

Both layers sit far outside Marschall's distribution: ~16% of lines break L2 in each,
and ~30% exceed the T1 colon ceiling. Marschall's own criteria applied over the same
text yield 89 cola for 1 Ne 3 against v2's 72 and v1's 69.
If the goal is a shorter, breath-scale line, **the clause layer is not where it lives** —
clause atoms in this corpus are frequently long, and v2's break-generating passes are
already doing more segmenting work than the raw fabric does.

## 1 Nephi 3 — three ways

Units: **v2 deployed 72** | **v1 clause 69** | **marschall 89**. Syllable counts in parentheses; ⚠ marks an L2 violation.

### 3:1

*v2 deployed* (1)

- (24) And it came to pass that I, Nephi, returned from speaking with the Lord, to the tent of my father.

*v1 clause* (1)

- (24) And it came to pass that I, Nephi, returned from speaking with the Lord, to the tent of my father.

*marschall* (1)

- (24) And it came to pass that I, Nephi, returned from speaking with the Lord, to the tent of my father.

### 3:2

*v2 deployed* (2)

- (12) And it came to pass that he spake unto me, saying:
- (31) Behold I have dreamed a dream, in the which the Lord hath commanded me that thou and thy brethren shall return to Jerusalem.

*v1 clause* (1)

- (43) ⚠ And it came to pass that he spake unto me, saying: Behold I have dreamed a dream, in the which the Lord hath commanded me that thou and thy brethren shall return to Jerusalem.

*marschall* (2)

- (12) And it came to pass that he spake unto me, saying:
- (31) Behold I have dreamed a dream, in the which the Lord hath commanded me that thou and thy brethren shall return to Jerusalem.

### 3:3

*v2 deployed* (2)

- (26) For behold, Laban hath the record of the Jews and also a genealogy of my forefathers,
- (12) and they are engraven upon plates of brass.

*v1 clause* (2)

- (26) For behold, Laban hath the record of the Jews and also a genealogy of my forefathers,
- (12) and they are engraven upon plates of brass.

*marschall* (2)

- (26) For behold, Laban hath the record of the Jews and also a genealogy of my forefathers,
- (12) and they are engraven upon plates of brass.

### 3:4

*v2 deployed* (1)

- (42) ⚠ Wherefore, the Lord hath commanded me that thou and thy brothers should go unto the house of Laban, and seek the records, and bring them down hither into the wilderness.

*v1 clause* (1)

- (42) ⚠ Wherefore, the Lord hath commanded me that thou and thy brothers should go unto the house of Laban, and seek the records, and bring them down hither into the wilderness.

*marschall* (2)

- (25) Wherefore, the Lord hath commanded me that thou and thy brothers should go unto the house of Laban,
- (17) and seek the records, and bring them down hither into the wilderness.

### 3:5

*v2 deployed* (3)

- (10) And now, behold thy brothers murmur, saying
- (12) it is a hard thing which I have required of them;
- (21) but behold I have not required it of them, but it is a commandment of the Lord.

*v1 clause* (4)

- (10) And now, behold thy brothers murmur, saying
- (12) it is a hard thing which I have required of them;
- (11) but behold I have not required it of them,
- (10) but it is a commandment of the Lord.

*marschall* (4)

- (10) And now, behold thy brothers murmur, saying
- (5) it is a hard thing
- (7) which I have required of them;
- (21) but behold I have not required it of them, but it is a commandment of the Lord.

### 3:6

*v2 deployed* (2)

- (6) Therefore go, my son,
- (16) and thou shalt be favored of the Lord, because thou hast not murmured.

*v1 clause* (2)

- (6) Therefore go, my son,
- (16) and thou shalt be favored of the Lord, because thou hast not murmured.

*marschall* (2)

- (6) Therefore go, my son,
- (16) and thou shalt be favored of the Lord, because thou hast not murmured.

### 3:7

*v2 deployed* (3)

- (15) And it came to pass that I, Nephi, said unto my father:
- (14) I will go and do the things which the Lord hath commanded,
- (42) ⚠ for I know that the Lord giveth no commandments unto the children of men, save he shall prepare a way for them that they may accomplish the thing which he commandeth them.

*v1 clause* (3)

- (15) And it came to pass that I, Nephi, said unto my father:
- (14) I will go and do the things which the Lord hath commanded,
- (42) ⚠ for I know that the Lord giveth no commandments unto the children of men, save he shall prepare a way for them that they may accomplish the thing which he commandeth them.

*marschall* (6)

- (15) And it came to pass that I, Nephi, said unto my father:
- (3) I will go
- (4) and do the things
- (7) which the Lord hath commanded,
- (19) for I know that the Lord giveth no commandments unto the children of men,
- (23) save he shall prepare a way for them that they may accomplish the thing which he commandeth them.

### 3:8

*v2 deployed* (2)

- (21) And it came to pass that when my father had heard these words he was exceedingly glad,
- (11) for he knew that I had been blessed of the Lord.

*v1 clause* (2)

- (21) And it came to pass that when my father had heard these words he was exceedingly glad,
- (11) for he knew that I had been blessed of the Lord.

*marschall* (5)

- (3) And it came
- (3) to pass that
- (15) when my father had heard these words he was exceedingly glad,
- (3) for he knew
- (8) that I had been blessed of the Lord.

### 3:9

*v2 deployed* (1)

- (31) And I, Nephi, and my brethren took our journey in the wilderness, with our tents, to go up to the land of Jerusalem.

*v1 clause* (1)

- (31) And I, Nephi, and my brethren took our journey in the wilderness, with our tents, to go up to the land of Jerusalem.

*marschall* (1)

- (31) And I, Nephi, and my brethren took our journey in the wilderness, with our tents, to go up to the land of Jerusalem.

### 3:10

*v2 deployed* (1)

- (32) And it came to pass that when we had gone up to the land of Jerusalem, I and my brethren did consult one with another.

*v1 clause* (1)

- (32) And it came to pass that when we had gone up to the land of Jerusalem, I and my brethren did consult one with another.

*marschall* (1)

- (32) And it came to pass that when we had gone up to the land of Jerusalem, I and my brethren did consult one with another.

### 3:11

*v2 deployed* (4)

- (4) And we cast lots
- (13) --who of us should go in unto the house of Laban.
- (25) And it came to pass that the lot fell upon Laman; and Laman went in unto the house of Laban,
- (11) and he talked with him as he sat in his house.

*v1 clause* (4)

- (4) And we cast lots
- (13) --who of us should go in unto the house of Laban.
- (25) And it came to pass that the lot fell upon Laman; and Laman went in unto the house of Laban,
- (11) and he talked with him as he sat in his house.

*marschall* (5)

- (4) And we cast lots
- (13) --who of us should go in unto the house of Laban.
- (25) And it came to pass that the lot fell upon Laman; and Laman went in unto the house of Laban,
- (5) and he talked with him
- (6) as he sat in his house.

### 3:12

*v2 deployed* (1)

- (34) And he desired of Laban the records which were engraven upon the plates of brass, which contained the genealogy of my father.

*v1 clause* (1)

- (34) And he desired of Laban the records which were engraven upon the plates of brass, which contained the genealogy of my father.

*marschall* (1)

- (34) And he desired of Laban the records which were engraven upon the plates of brass, which contained the genealogy of my father.

### 3:13

*v2 deployed* (5)

- (21) And behold, it came to pass that Laban was angry, and thrust him out from his presence;
- (11) and he would not that he should have the records.
- (8) Wherefore, he said unto him:
- (7) Behold thou art a robber,
- (5) and I will slay thee.

*v1 clause* (5)

- (21) And behold, it came to pass that Laban was angry, and thrust him out from his presence;
- (11) and he would not that he should have the records.
- (8) Wherefore, he said unto him:
- (7) Behold thou art a robber,
- (5) and I will slay thee.

*marschall* (5)

- (21) And behold, it came to pass that Laban was angry, and thrust him out from his presence;
- (11) and he would not that he should have the records.
- (8) Wherefore, he said unto him:
- (7) Behold thou art a robber,
- (5) and I will slay thee.

### 3:14

*v2 deployed* (2)

- (21) But Laman fled out of his presence, and told the things which Laban had done, unto us.
- (33) And we began to be exceedingly sorrowful, and my brethren were about to return unto my father in the wilderness.

*v1 clause* (3)

- (21) But Laman fled out of his presence, and told the things which Laban had done, unto us.
- (13) And we began to be exceedingly sorrowful,
- (20) and my brethren were about to return unto my father in the wilderness.

*marschall* (2)

- (21) But Laman fled out of his presence, and told the things which Laban had done, unto us.
- (33) And we began to be exceedingly sorrowful, and my brethren were about to return unto my father in the wilderness.

### 3:15

*v2 deployed* (3)

- (8) But behold I said unto them
- (10) that: As the Lord liveth, and as we live,
- (32) we will not go down unto our father in the wilderness until we have accomplished the thing which the Lord hath commanded us.

*v1 clause* (4)

- (8) But behold I said unto them
- (6) that: As the Lord liveth,
- (4) and as we live,
- (32) we will not go down unto our father in the wilderness until we have accomplished the thing which the Lord hath commanded us.

*marschall* (3)

- (8) But behold I said unto them
- (10) that: As the Lord liveth, and as we live,
- (32) we will not go down unto our father in the wilderness until we have accomplished the thing which the Lord hath commanded us.

### 3:16

*v2 deployed* (3)

- (36) ⚠ Wherefore, let us be faithful in keeping the commandments of the Lord; therefore let us go down to the land of our father's inheritance,
- (16) for behold he left gold and silver, and all manner of riches.
- (16) And all this he hath done because of the commandments of the Lord.

*v1 clause* (3)

- (36) ⚠ Wherefore, let us be faithful in keeping the commandments of the Lord; therefore let us go down to the land of our father's inheritance,
- (16) for behold he left gold and silver, and all manner of riches.
- (16) And all this he hath done because of the commandments of the Lord.

*marschall* (4)

- (18) Wherefore, let us be faithful in keeping the commandments of the Lord;
- (18) therefore let us go down to the land of our father's inheritance,
- (16) for behold he left gold and silver, and all manner of riches.
- (16) And all this he hath done because of the commandments of the Lord.

### 3:17

*v2 deployed* (1)

- (22) For he knew that Jerusalem must be destroyed, because of the wickedness of the people.

*v1 clause* (1)

- (22) For he knew that Jerusalem must be destroyed, because of the wickedness of the people.

*marschall* (1)

- (22) For he knew that Jerusalem must be destroyed, because of the wickedness of the people.

### 3:18

*v2 deployed* (3)

- (14) For behold, they have rejected the words of the prophets.
- (34) Wherefore, if my father should dwell in the land after he hath been commanded to flee out of the land, behold, he would also perish.
- (14) Wherefore, it must needs be that he flee out of the land.

*v1 clause* (3)

- (14) For behold, they have rejected the words of the prophets.
- (34) Wherefore, if my father should dwell in the land after he hath been commanded to flee out of the land, behold, he would also perish.
- (14) Wherefore, it must needs be that he flee out of the land.

*marschall* (3)

- (14) For behold, they have rejected the words of the prophets.
- (34) Wherefore, if my father should dwell in the land after he hath been commanded to flee out of the land, behold, he would also perish.
- (14) Wherefore, it must needs be that he flee out of the land.

### 3:19

*v2 deployed* (3)

- (9) And behold, it is wisdom in God
- (8) that we should obtain these records,
- (17) that we may preserve unto our children the language of our fathers;

*v1 clause* (1)

- (34) And behold, it is wisdom in God that we should obtain these records, that we may preserve unto our children the language of our fathers;

*marschall* (3)

- (9) And behold, it is wisdom in God
- (8) that we should obtain these records,
- (17) that we may preserve unto our children the language of our fathers;

### 3:20

*v2 deployed* (1)

- (60) ⚠ And also that we may preserve unto them the words which have been spoken by the mouth of all the holy prophets, which have been delivered unto them by the Spirit and power of God, since the world began, even down unto this present time.

*v1 clause* (1)

- (60) ⚠ And also that we may preserve unto them the words which have been spoken by the mouth of all the holy prophets, which have been delivered unto them by the Spirit and power of God, since the world began, even down unto this present time.

*marschall* (2)

- (28) And also that we may preserve unto them the words which have been spoken by the mouth of all the holy prophets,
- (32) which have been delivered unto them by the Spirit and power of God, since the world began, even down unto this present time.

### 3:21

*v2 deployed* (1)

- (36) ⚠ And it came to pass that after this manner of language did I persuade my brethren, that they might be faithful in keeping the commandments of God.

*v1 clause* (1)

- (36) ⚠ And it came to pass that after this manner of language did I persuade my brethren, that they might be faithful in keeping the commandments of God.

*marschall* (2)

- (21) And it came to pass that after this manner of language did I persuade my brethren,
- (15) that they might be faithful in keeping the commandments of God.

### 3:22

*v2 deployed* (1)

- (37) ⚠ And it came to pass that we went down to the land of our inheritance, and we did gather together our gold, and our silver, and our precious things.

*v1 clause* (1)

- (37) ⚠ And it came to pass that we went down to the land of our inheritance, and we did gather together our gold, and our silver, and our precious things.

*marschall* (2)

- (18) And it came to pass that we went down to the land of our inheritance,
- (19) and we did gather together our gold, and our silver, and our precious things.

### 3:23

*v2 deployed* (1)

- (24) And after we had gathered these things together, we went up again unto the house of Laban.

*v1 clause* (1)

- (24) And after we had gathered these things together, we went up again unto the house of Laban.

*marschall* (1)

- (24) And after we had gathered these things together, we went up again unto the house of Laban.

### 3:24

*v2 deployed* (1)

- (59) ⚠ And it came to pass that we went in unto Laban, and desired him that he would give unto us the records which were engraven upon the plates of brass, for which we would give unto him our gold, and our silver, and all our precious things.

*v1 clause* (1)

- (59) ⚠ And it came to pass that we went in unto Laban, and desired him that he would give unto us the records which were engraven upon the plates of brass, for which we would give unto him our gold, and our silver, and all our precious things.

*marschall* (2)

- (39) ⚠ And it came to pass that we went in unto Laban, and desired him that he would give unto us the records which were engraven upon the plates of brass,
- (20) for which we would give unto him our gold, and our silver, and all our precious things.

### 3:25

*v2 deployed* (4)

- (14) And it came to pass that when Laban saw our property,
- (18) and that it was exceedingly great, he did lust after it, insomuch
- (13) that he thrust us out, and sent his servants to slay us,
- (9) that he might obtain our property.

*v1 clause* (1)

- (54) ⚠ And it came to pass that when Laban saw our property, and that it was exceedingly great, he did lust after it, insomuch that he thrust us out, and sent his servants to slay us, that he might obtain our property.

*marschall* (7)

- (3) And it came
- (2) to pass
- (1) that
- (8) when Laban saw our property,
- (18) and that it was exceedingly great, he did lust after it, insomuch
- (13) that he thrust us out, and sent his servants to slay us,
- (9) that he might obtain our property.

### 3:26

*v2 deployed* (2)

- (30) And it came to pass that we did flee before the servants of Laban, and we were obliged to leave behind our property,
- (10) and it fell into the hands of Laban.

*v1 clause* (2)

- (30) And it came to pass that we did flee before the servants of Laban, and we were obliged to leave behind our property,
- (10) and it fell into the hands of Laban.

*marschall* (2)

- (30) And it came to pass that we did flee before the servants of Laban, and we were obliged to leave behind our property,
- (10) and it fell into the hands of Laban.

### 3:27

*v2 deployed* (2)

- (27) And it came to pass that we fled into the wilderness, and the servants of Laban did not overtake us,
- (14) and we hid ourselves in the cavity of a rock.

*v1 clause* (2)

- (27) And it came to pass that we fled into the wilderness, and the servants of Laban did not overtake us,
- (14) and we hid ourselves in the cavity of a rock.

*marschall* (2)

- (27) And it came to pass that we fled into the wilderness, and the servants of Laban did not overtake us,
- (14) and we hid ourselves in the cavity of a rock.

### 3:28

*v2 deployed* (4)

- (26) And it came to pass that Laman was angry with me, and also with my father; and also was Lemuel,
- (11) for he hearkened unto the words of Laman.
- (22) Wherefore Laman and Lemuel did speak many hard words unto us, their younger brothers,
- (10) and they did smite us even with a rod.

*v1 clause* (4)

- (26) And it came to pass that Laman was angry with me, and also with my father; and also was Lemuel,
- (11) for he hearkened unto the words of Laman.
- (22) Wherefore Laman and Lemuel did speak many hard words unto us, their younger brothers,
- (10) and they did smite us even with a rod.

*marschall* (4)

- (26) And it came to pass that Laman was angry with me, and also with my father; and also was Lemuel,
- (11) for he hearkened unto the words of Laman.
- (22) Wherefore Laman and Lemuel did speak many hard words unto us, their younger brothers,
- (10) and they did smite us even with a rod.

### 3:29

*v2 deployed* (6)

- (26) And it came to pass as they smote us with a rod, behold, an angel of the Lord came and stood before them,
- (7) and he spake unto them, saying:
- (12) Why do ye smite your younger brother with a rod?
- (28) Know ye not that the Lord hath chosen him to be a ruler over you, and this because of your iniquities?
- (13) Behold ye shall go up to Jerusalem again,
- (13) and the Lord will deliver Laban into your hands.

*v1 clause* (6)

- (26) And it came to pass as they smote us with a rod, behold, an angel of the Lord came and stood before them,
- (7) and he spake unto them, saying:
- (12) Why do ye smite your younger brother with a rod?
- (28) Know ye not that the Lord hath chosen him to be a ruler over you, and this because of your iniquities?
- (13) Behold ye shall go up to Jerusalem again,
- (13) and the Lord will deliver Laban into your hands.

*marschall* (6)

- (26) And it came to pass as they smote us with a rod, behold, an angel of the Lord came and stood before them,
- (7) and he spake unto them, saying:
- (12) Why do ye smite your younger brother with a rod?
- (28) Know ye not that the Lord hath chosen him to be a ruler over you, and this because of your iniquities?
- (13) Behold ye shall go up to Jerusalem again,
- (13) and the Lord will deliver Laban into your hands.

### 3:30

*v2 deployed* (1)

- (16) And after the angel had spoken unto us, he departed.

*v1 clause* (1)

- (16) And after the angel had spoken unto us, he departed.

*marschall* (1)

- (16) And after the angel had spoken unto us, he departed.

### 3:31

*v2 deployed* (5)

- (23) And after the angel had departed, Laman and Lemuel again began to murmur, saying:
- (19) How is it possible that the Lord will deliver Laban into our hands?
- (8) Behold, he is a mighty man,
- (8) and he can command fifty, yea,
- (11) even he can slay fifty; then why not us?

*v1 clause* (5)

- (23) And after the angel had departed, Laman and Lemuel again began to murmur, saying:
- (19) How is it possible that the Lord will deliver Laban into our hands?
- (8) Behold, he is a mighty man,
- (7) and he can command fifty,
- (12) yea, even he can slay fifty; then why not us?

*marschall* (5)

- (23) And after the angel had departed, Laman and Lemuel again began to murmur, saying:
- (19) How is it possible that the Lord will deliver Laban into our hands?
- (8) Behold, he is a mighty man,
- (8) and he can command fifty, yea,
- (11) even he can slay fifty; then why not us?

