#!/usr/bin/env python3
"""
Book of Mormon Reading Edition — Modular Book Builder
Processes sense-line source files into individual book HTML fragments
for the modular site structure (books/*.html).

Usage:
  Single book:  python3 build_book.py BOOK_ID source.txt [--out books/]
  All books:    python3 build_book.py --all [--out books/]

The --all mode reads from a booklist.txt file (one "bookid filename" pair per line).

Output: books/BOOKID.html — a standalone fragment containing just the
<div id="book-BOOKID" class="book-content"> ... </div> block.
These drop directly into the modular shell's books/ folder.
"""

import re, sys, os, json
from pathlib import Path

# ============================================================================
# QUIET SWAPS — High-frequency archaic words that don't need dotted underlines.
# These still get swapped in Aid mode but won't have visual decoration,
# because they appear so often that underlining them creates visual noise.
# Uses lowercase canonical forms; matching is case-insensitive.
QUIET_ARCHAICS = {
    'unto', 'wherefore', 'ye', 'thee', 'thou', 'thy', 'thine', 'mine',
    'yea', 'nay', 'hath', 'doth', 'hast', 'shalt', 'dost', 'wilt',
    'canst', 'didst', 'shouldst', 'wouldst', 'wast', 'hadst', 'saidst',
    'nevertheless', 'exceedingly', 'exceeding', 'insomuch',
    'spake', 'beheld', 'smitten', 'smote',
    'hither', 'thither', 'whither', 'whence',
    'brethren', 'thereof', 'whereby', 'wherewith', 'amongst',
    'it came to pass', 'it shall come to pass',
}

# ============================================================================
# SWAP LEXICON — Single source of truth for all archaic word modernization
# ============================================================================

# AICTP (wayyehi) swaps — "it came to pass" → contextual modern equivalents
# These are handled specially in apply_swaps via regex (not word-boundary).
# No trailing spaces here — matching is done with regex that handles both
# mid-line (followed by space) and end-of-line (followed by newline/EOL) cases.
AICTP_SWAPS = [
    # "that" variants (longest first)
    ("And now it came to pass that", "And now"),
    ("Now, it came to pass that", "Now,"),
    ("Now it came to pass that", "Now"),
    ("Behold, it came to pass that", "Then behold,"),
    ("Wherefore, it came to pass that", "And so"),
    ("Wherefore it came to pass that", "And so"),
    ("Therefore it came to pass that", "Therefore"),
    ("But it came to pass that", "But then"),
    ("For it came to pass that", "For then"),
    ("And it came to pass that", "And then"),
    ("and it came to pass that", "and then"),
    ("thus it came to pass that", "thus"),
    ("before it came to pass that", "before"),
    ("behold it came to pass that", "then behold"),
    # Bare / comma variants (no "that")
    ("And now it came to pass,", "And now,"),
    ("And now it came to pass", "And now"),
    ("But it came to pass,", "But then,"),
    ("But it came to pass", "But then"),
    ("Now it came to pass", "Now"),
    ("For it came to pass", "For then"),
    ("thus it came to pass,", "thus,"),
    ("Behold, it came to pass", "Then behold,"),
    ("behold it came to pass", "then behold"),
    ("Therefore it came to pass", "Therefore"),
    ("before it came to pass", "before"),
    ("And it came to pass,", "And then,"),
    ("And it came to pass", "And then"),
    ("and it came to pass", "and then"),
    # Bare mid-sentence (no prefix)
    ("it came to pass that", "then"),
    ("it came to pass,", "then,"),
    ("it came to pass", "then"),

    # ── Future tense: "it shall come to pass" ──
    # "that" variants (longest first)
    ("And now it shall come to pass that", "And now"),
    ("Wherefore it shall come to pass that", "And so"),
    ("Therefore it shall come to pass that", "Therefore"),
    ("But behold, it shall come to pass that", "But behold,"),
    ("But it shall come to pass that", "But then"),
    ("For it shall come to pass that", "For then"),
    ("And it shall come to pass that", "And then"),
    ("and it shall come to pass that", "and then"),
    ("And behold it shall come to pass that", "And behold,"),
    ("And again it shall come to pass that", "And again"),
    ("Yea, and it shall come to pass that", "Yea, and"),
    # "in that day" variants
    ("And it shall come to pass in that day,", "And in that day,"),
    ("And it shall come to pass in that day", "And in that day"),
    ("and it shall come to pass in that day", "and in that day"),
    # Bare / comma variants (no "that")
    ("And it shall come to pass,", "And then,"),
    ("And it shall come to pass", "And then"),
    ("and it shall come to pass", "and then"),
    ("For it shall come to pass", "For then"),
    ("But behold, it shall come to pass", "But behold,"),
    ("Wherefore it shall come to pass", "And so"),
    ("Therefore it shall come to pass", "Therefore"),
    # Bare mid-sentence
    ("it shall come to pass that", "then"),
    ("it shall come to pass,", "then,"),
    ("it shall come to pass", "then"),
]

COMPOUND_SWAPS = [
    ("go to", "go"),  # archaic interjection (only when followed by , or ;)
    ("none other object save it be", "no other purpose except"),
    ("inasmuch as", "to the degree that"), ("Inasmuch as", "To the degree that"),
    ("things of naught", "worthless things"), ("thing of naught", "worthless thing"),
    ("set at naught", "treated with contempt"), ("setteth at naught", "treats with contempt"),
    # ── Participle fixes: have/has/had + archaic past → correct past participle ──
    ("hast beheld", "have seen"), ("hath beheld", "has seen"),
    ("had beheld", "had seen"), ("have beheld", "have seen"),
    ("has beheld", "has seen"),  # post-hath swap
    ("never have beheld", "never have seen"), ("never had beheld", "never had seen"),
    ("hast spake", "have spoken"), ("hath spake", "has spoken"),
    ("had spake", "had spoken"), ("have spake", "have spoken"),
    ("hast spoken", "have spoken"),  # hast→have participle fix
    # ── yea, even → indeed, even (emphatic, not affirmative) ──
    ("yea, even", "indeed, even"), ("Yea, even", "Indeed, even"),
    ("yea even", "indeed even"), ("Yea even", "Indeed even"),
    # ── lest that → for fear that (avoid double 'that') ──
    ("lest that", "for fear that"),
    # ── abomination collision avoidance ──
    # "wickedness and abominations" → avoid "wickedness and wicked practices"
    ("wickedness and abominations", "wickedness and evil deeds"),
    ("wickedness and abomination", "wickedness and evil deeds"),
    ("wickedness and their abominations", "wickedness and their evil deeds"),
    ("wickedness and his abominations", "wickedness and his evil deeds"),
    # "iniquity and abominations" → same issue (iniquity ≈ wickedness)
    ("iniquity and abominations", "iniquity and evil deeds"),
    ("iniquities and abominations", "iniquities and evil deeds"),
    ("iniquity and abomination", "iniquity and evil deeds"),
    # "wicked abominations" → collapse redundancy
    ("wicked abominations", "wicked practices"),
    ("wicked abomination", "wicked practice"),
    # "mother of abominations" → biblical title (Rev 17), keep as-is
    ("mother of abominations", "mother of abominations"),
    ("hither and thither", "this way and that"),
    ("an account", "a record"), ("in fine", "in other words"), ("lust after", "desire"),
    ("save two churches only", "only two churches"), ("save a few only", "only a few"),
    ("save it were", "except"), ("save it be", "except"), ("save that", "except that"),
    ("Thou mightest", "You might"), ("thou mightest", "you might"),
    ("Thou knowest", "You know"), ("thou knowest", "you know"),
    ("Thou shalt", "You shall"), ("thou shalt", "you shall"),
    ("Thou hast", "You have"), ("thou hast", "you have"),
    ("Thou wilt", "You will"), ("thou wilt", "you will"),
    ("Thou dost", "You do"), ("thou dost", "you do"),
    ("Thou art", "You are"), ("thou art", "you are"),
    ("wilt thou", "will you"), ("Wilt thou", "Will you"),
    ("art thou", "are you"), ("Art thou", "Are you"),
    # ── Inverted -est thou questions → "Do you [verb]" ──
    ("Believest thou", "Do you believe"), ("believest thou", "do you believe"),
    ("Knowest thou", "Do you know"), ("knowest thou", "do you know"),
    ("Deniest thou", "Do you deny"), ("deniest thou", "do you deny"),
    ("Seest thou", "Do you see"), ("seest thou", "do you see"),
    ("Sawest thou", "Did you see"), ("sawest thou", "did you see"),
    ("Rememberest thou", "Do you remember"), ("rememberest thou", "do you remember"),
    ("beholdest thou", "do you behold"), ("beheldest thou", "did you behold"),
    ("desirest thou", "do you desire"),
    ("sayest thou", "do you say"),
    ("prayest thou", "do you pray"),
    ("persecutest thou", "do you persecute"),
    ("commandest thou", "do you command"),
    ("comest thou", "do you come"),
    # ── Non-inverted thou + -est (common patterns not yet caught) ──
    ("thou seest", "you see"), ("Thou seest", "You see"),
    ("thou mayest", "you may"), ("Thou mayest", "You may"),
    ("thou beholdest", "you behold"), ("Thou beholdest", "You behold"),
    ("thou desirest", "you desire"), ("Thou desirest", "You desire"),
    ("thou believest", "you believe"), ("Thou believest", "You believe"),
    ("thou sayest", "you say"), ("Thou sayest", "You say"),
    ("thou prayest", "you pray"), ("thou goest", "you go"),
    ("thou livest", "you live"), ("thou workest", "you work"),
    ("thou heardest", "you heard"), ("thou speakest", "you speak"),
    ("thou beheldest", "you beheld"),
    ("thou comfortedst", "you comforted"), ("thou receivedst", "you received"),
    # ── Collision guards ──
    ("from thence", "from there"),
    ("from whence", "from where"),
    # ── "succoring" before "succor" simple swap ──
    ("succoring", "helping"), ("Succoring", "Helping"),
    ("succored", "helped"), ("Succored", "Helped"),
    ("did murmur", "complained"), ("did exhort", "urged"),
    # confound — "silenced" for debate sense; base form gets "confuse" for language sense
    ("did confound", "silenced"),
    ("confound the language", "confuse the language"),
    ("not confound us", "not confuse us"),
    ("did engraven", "engraved"),
    ("should engraven", "should engrave"), ("might engraven", "might engrave"),
    ("could engraven", "could engrave"), ("would engraven", "would engrave"),
    ("shall engraven", "shall engrave"), ("shalt engraven", "shall engrave"),
    ("will engraven", "will engrave"), ("wilt engraven", "will engrave"),
    ("may engraven", "may engrave"), ("can engraven", "can engrave"),
    ("mayest engraven", "may engrave"), ("canst engraven", "can engrave"),
    ("to engraven", "to engrave"),
    ("did slay", "killed"), ("did smite", "struck"),
    # Did + compound verb (shared auxiliary: "did X and Y exceedingly")
    ("did quake and tremble exceedingly", "quaked and trembled greatly"),
    ("did fear and tremble exceedingly", "feared and trembled greatly"),
    ("did multiply and wax exceedingly", "multiplied and grew very"),
    ("did multiply and prosper exceedingly", "multiplied and prospered greatly"),
    # Doth + adverb + verb (pre-collapse to avoid "does greatly rejoice")
    ("doth exceedingly rejoice", "rejoices greatly"),
    ("doth immediately bless", "immediately blesses"),
    ("doth speedily drag", "speedily drags"),
    ("doth rightly belong", "rightly belongs"),
    # Bowels — figurative (seat of emotion / mercy)
    ("bowels of mercy", "depths of mercy"),
    ("bowels are filled with compassion", "heart is filled with compassion"),
    ("bowels are filled with mercy", "heart is filled with mercy"),
    ("bowels may be filled with mercy", "heart may be filled with mercy"),
    ("offspring of thy bowels", "offspring of your body"),
    ("bowels of my mother", "womb of my mother"),
    # Loins — figurative (lineage) vs literal (waist)
    ("fruit of my loins", "fruit of my lineage"),
    ("fruit of thy loins", "fruit of your lineage"),
    ("fruit of his loins", "fruit of his lineage"),
    ("fruit of the loins", "fruit of the lineage"),
    ("seed of thy loins", "seed of your lineage"),
    ("spokesman of thy loins", "spokesman of your lineage"),
    # ── Pronoun collision: thee/thou adjacency → "you, you" (insert comma) ──
    ("unto thee ye", "to you, you"),
    ("from thee thou", "from you, you"),
    ("thee thou", "you, you"),  # catch-all for other adjacencies
    # ── Isaiah archaic phrases ──
    ("forasmuch as", "because"), ("Forasmuch as", "Because"),
    ("hardly bestead", "hard-pressed"),
    ("teil tree", "terebinth"),
    ("mean man", "common man"),
    ("narrowly look upon", "look closely at"),
    ("doleful creatures", "mournful creatures"),
    ("cockatrice's", "viper's"), ("Cockatrice's", "Viper's"),  # before simple cockatrice swap
    # ── Isaiah false friends & opaque phrases (batch 2) ──
    ("ragged rocks", "jagged rocks"),
    ("smite with a scab", "smite with sores"),
    ("a rent", "a torn rag"),
    ("stout heart", "proud heart"),
    ("stout against", "harsh against"),
    ("cunning artificer", "skilled craftsman"),
    ("round tires like the moon", "crescent ornaments"),
    ("pleasant pictures", "beautiful craft"),
    ("wanton eyes", "flirtatious eyes"),
    ("walking and mincing as they go", "walking and taking dainty steps"),
    ("peep and mutter", "chirp and mutter"),
    ("crisping-pins", "purses"), ("Crisping-pins", "Purses"),
    ("dry shod", "dry-footed"),
    ("girdle of his reins", "belt around his waist"),  # reins = loins/inner being
    ("girdle of their loins", "belt of their loins"),
    ("girdle of his loins", "belt of his loins"),
    ("about my loins", "about my waist"),
    ("about his loins", "about his waist"),
    ("about their loins", "about their waist"),
    ("about her loins", "about her waist"),
    ("of his loins", "of his waist"),
    ("of their loins", "of their waist"),
    # ── gird/girded: context-dependent verb ──
    ("gird yourselves", "prepare yourselves"), ("Gird yourselves", "Prepare yourselves"),
    ("girding of", "wrapping of"),
    ("gird on", "strap on"),
]

SIMPLE_SWAPS = [
    ("unto", "to"), ("Unto", "To"),
    ("wherefore", "so"), ("Wherefore", "So"),
    ("brethren", "brothers"), ("Brethren", "Brothers"),
    ("thereof", "of it"), ("Thereof", "Of it"),
    ("whereby", "by which"), ("Whereby", "By which"),
    ("wherewith", "with which"), ("Wherewith", "With which"),
    ("whither", "where"), ("Whither", "Where"),
    ("whence", "where"), ("Whence", "Where"),
    ("hither", "here"), ("Hither", "Here"),
    ("thither", "there"), ("Thither", "There"),
    ("thine", "your"), ("Thine", "Your"),
    ("thee", "you"), ("Thee", "You"),
    ("thou", "you"), ("Thou", "You"),
    ("thy", "your"), ("Thy", "Your"),
    ("ye", "you"), ("Ye", "You"),
    ("mine", "my"), ("Mine", "My"),
    ("beheld", "saw"), ("spake", "spoke"),
    ("hath", "has"), ("Hath", "Has"),
    ("exceedingly", "very"), ("Exceedingly", "Very"),
    ("rejoice exceedingly", "rejoice greatly"), ("rejoiced exceedingly", "rejoiced greatly"),
    ("prosper exceedingly", "prosper greatly"), ("prospered exceedingly", "prospered greatly"),
    ("astonished exceedingly", "astonished greatly"),
    ("labor exceedingly", "labor greatly"), ("labored exceedingly", "labored greatly"),
    ("fear exceedingly", "fear greatly"), ("feared exceedingly", "feared greatly"),
    ("grow exceedingly", "grow greatly"),
    ("tremble exceedingly", "tremble greatly"), ("trembled exceedingly", "trembled greatly"),
    ("mourn exceedingly", "mourn greatly"),
    ("wax exceedingly", "wax greatly"),
    ("shook exceedingly", "shook greatly"),
    ("multiply exceedingly", "multiply greatly"), ("multiplied exceedingly", "multiplied greatly"),
    ("weep exceedingly", "weep greatly"),
    ("thrive exceedingly", "thrive greatly"),
    ("shine exceedingly", "shine greatly"),
    ("stumble exceedingly", "stumble greatly"),
    ("flourish exceedingly", "flourish greatly"),
    ("fight exceedingly", "fight greatly"),
    ("murmur exceedingly", "murmur greatly"),
    ("suffered exceedingly", "suffered greatly"),
    ("destroyed exceedingly", "destroyed greatly"),
    ("frightened exceedingly", "frightened greatly"),
    ("affrighted exceedingly", "affrighted greatly"),
    ("exercising exceedingly", "exercising greatly"),
    ("worn exceedingly", "worn greatly"),
    ("swollen exceedingly", "swollen greatly"),
    ("seen exceedingly", "seen greatly"),
    ("humble themselves exceedingly", "humble themselves greatly"),
    ("fall exceedingly", "fall greatly"),
    ("rend the air exceedingly", "rend the air greatly"),
    ("pleased exceedingly", "pleased greatly"), ("please exceedingly", "please greatly"),
    ("Nephi exceedingly", "Nephi greatly"), ("Moroni exceedingly", "Moroni greatly"),
    ("Lehi exceedingly", "Lehi greatly"), ("Kishkumen exceedingly", "Kishkumen greatly"),
    ("Lamanites exceedingly", "Lamanites greatly"), ("Lord exceedingly", "Lord greatly"),
    ("exceeding", "great"), ("Exceeding", "Great"),
    ("insomuch", "so much so"), ("Insomuch", "So much so"),
    ("hearken", "listen"), ("Hearken", "Listen"),
    ("hearkened", "listened"), ("Hearkened", "Listened"),
    ("engraven", "engraved"), ("Engraven", "Engraved"),
    ("murmurings", "complaints"), ("Murmurings", "Complaints"),
    ("murmured", "complained"), ("Murmured", "Complained"),
    ("murmur", "complain"), ("Murmur", "Complain"),
    ("slain", "killed"), ("Slain", "Killed"),
    ("afflictions", "hardships"), ("Afflictions", "Hardships"),
    ("hast", "have"), ("Hast", "Have"),
    ("fulness", "fullness"), ("Fulness", "Fullness"),
    ("slay", "kill"), ("Slay", "Kill"),
    ("shalt", "shall"), ("Shalt", "Shall"),
    ("canst", "can"), ("Canst", "Can"),
    ("didst", "did"), ("Didst", "Did"),
    ("shouldst", "should"), ("Shouldst", "Should"),
    ("wouldst", "would"), ("Wouldst", "Would"),
    ("wast", "were"), ("Wast", "Were"),
    ("hadst", "had"), ("Hadst", "Had"),
    ("saidst", "said"), ("Saidst", "Said"),
    ("abominations", "wicked practices"), ("Abominations", "Wicked practices"),
    ("abomination", "wicked practice"), ("Abomination", "Wicked practice"),
    ("abridgment", "summary"), ("Abridgment", "Summary"),
    ("abridged", "summarized"), ("Abridged", "Summarized"),
    ("stiffneckedness", "stubbornness"), ("Stiffneckedness", "Stubbornness"),
    ("commencement", "beginning"), ("Commencement", "Beginning"),
    ("confounded", "confused"), ("Confounded", "Confused"),
    ("constrained", "compelled"), ("Constrained", "Compelled"),
    ("nevertheless", "but"), ("Nevertheless", "But"),
    ("concourses", "crowds"), ("Concourses", "Crowds"),
    ("account", "record"), ("Account", "Record"),
    ("naught", "nothing"), ("Naught", "Nothing"),
    ("surety", "certainty"), ("Surety", "Certainty"),
    ("firmament", "sky"), ("Firmament", "Sky"),
    ("asunder", "apart"), ("Asunder", "Apart"),
    ("apparel", "clothing"), ("Apparel", "Clothing"),
    ("goodly", "good"), ("Goodly", "Good"),
    ("luster", "brightness"), ("Luster", "Brightness"),
    ("methought", "I thought"), ("Methought", "I thought"),
    ("midst", "middle"), ("Midst", "Middle"),
    ("shrunk", "shrank"), ("Shrunk", "Shrank"),
    ("smote", "struck"), ("Smote", "Struck"),
    ("smitten", "struck"), ("Smitten", "Struck"),
    ("smite", "strike"), ("Smite", "Strike"),
    ("tarried", "stayed"), ("Tarried", "Stayed"),
    ("tarry", "stay"), ("Tarry", "Stay"),
    ("wroth", "angry"), ("Wroth", "Angry"),
    ("durst", "dare"), ("Durst", "Dare"),
    ("bade", "told"), ("Bade", "Told"),
    ("doth", "does"), ("Doth", "Does"),
    ("whit", "bit"), ("Whit", "Bit"),
    ("wo", "woe"), ("Wo", "Woe"),
    ("lest", "for fear that"), ("Lest", "For fear that"),
    ("yea", "yes"), ("Yea", "Indeed"),
    ("meet", "fitting"), ("Meet", "Fitting"),
    ("aught", "anything"), ("Aught", "Anything"),
    ("nay", "no"), ("Nay", "No"),
    ("privily", "secretly"), ("Privily", "Secretly"),
    ("wist", "knew"), ("Wist", "Knew"),
    ("notwithstanding", "despite"), ("Notwithstanding", "Despite"),  # overridden context-sensitively in apply_swaps()
    ("sufficeth", "is enough for"), ("constraineth", "compels"),
    ("commandeth", "commands"), ("speaketh", "speaks"),
    ("prepareth", "prepares"), ("standeth", "stands"),
    ("knoweth", "knows"), ("leadeth", "leads"),
    ("ceaseth", "ceases"), ("seeketh", "seeks"),
    ("slayeth", "kills"), ("liveth", "lives"),
    ("giveth", "gives"), ("goeth", "goes"), ("mattereth", "matters"),
    # ── Isaiah archaic vocabulary ──
    ("twain", "two"), ("Twain", "Two"),
    ("amongst", "among"), ("Amongst", "Among"),
    ("betwixt", "between"), ("Betwixt", "Between"),
    ("howbeit", "however"), ("Howbeit", "However"),
    ("cockatrice", "viper"), ("Cockatrice", "Viper"),
    ("satyrs", "wild goats"), ("Satyrs", "Wild goats"),
    ("besom", "broom"), ("Besom", "Broom"),
    ("disannul", "undo"), ("Disannul", "Undo"),
    ("viols", "lyres"), ("Viols", "Lyres"),
    ("bittern", "hedgehog"), ("Bittern", "Hedgehog"),
    ("ensign", "banner"), ("Ensign", "Banner"),
    ("feller", "woodcutter"), ("Feller", "Woodcutter"),
    ("gin", "trap"), ("Gin", "Trap"),
    ("hiss", "whistle"), ("Hiss", "Whistle"),
    ("vex", "trouble"), ("Vex", "Trouble"),
    ("vexed", "troubled"), ("Vexed", "Troubled"),
    ("vexation", "distress"), ("Vexation", "Distress"),
    # ── Isaiah false friends & dead words (batch 2) ──
    ("bravery", "finery"), ("Bravery", "Finery"),  # KJV "bravery" = splendor, NOT courage
    ("carriages", "baggage"), ("Carriages", "Baggage"),  # NOT vehicles
    ("girdle", "belt"), ("Girdle", "Belt"),
    ("stoutness", "arrogance"), ("Stoutness", "Arrogance"),
    ("replenished", "filled"), ("Replenished", "Filled"),
    ("cauls", "hairnets"), ("Cauls", "Hairnets"),
    ("mufflers", "veils"), ("Mufflers", "Veils"),
    ("wimples", "shawls"), ("Wimples", "Shawls"),
    ("stomacher", "fine robe"), ("Stomacher", "Fine robe"),
    ("tabret", "tambourine"), ("Tabret", "Tambourine"),
    ("latchet", "strap"), ("Latchet", "Strap"),
    ("mattock", "hoe"), ("Mattock", "Hoe"),
    ("silverlings", "silver coins"), ("Silverlings", "Silver coins"),
    ("threescore", "sixty"), ("Threescore", "Sixty"),
    ("digged", "dug"), ("Digged", "Dug"),
    ("soothsayers", "fortune-tellers"), ("Soothsayers", "Fortune-tellers"),
    ("fatlings", "fattened calves"), ("Fatlings", "Fattened calves"),
    ("fatling", "fattened calf"), ("Fatling", "Fattened calf"),
    ("arrogancy", "arrogance"), ("Arrogancy", "Arrogance"),
    ("comely", "lovely"), ("Comely", "Lovely"),
    ("covert", "shelter"), ("Covert", "Shelter"),
    ("therein", "in it"), ("Therein", "In it"),
    ("viol", "lyre"), ("Viol", "Lyre"),  # singular (viols already handled)
    ("peeped", "chirped"), ("Peeped", "Chirped"),
    ("Lo", "See"), ("lo", "see"),
    # ── Full BofM archaic vocabulary ──
    ("nigh", "near"), ("Nigh", "Near"),
    ("thence", "from there"), ("Thence", "From there"),
    ("hence", "from here"), ("Hence", "From here"),
    ("waxed", "grew"), ("Waxed", "Grew"),
    ("waxen", "grown"), ("Waxen", "Grown"),
    ("succor", "help"), ("Succor", "Help"),
    ("raiment", "clothing"), ("Raiment", "Clothing"),
    ("straightway", "immediately"), ("Straightway", "Immediately"),
    ("hereafter", "after this"), ("Hereafter", "After this"),
    ("travail", "toil"), ("Travail", "Toil"),
    ("sojourn", "stay"), ("Sojourn", "Stay"),
    ("sojourned", "stayed"), ("Sojourned", "Stayed"),
    ("dearth", "famine"), ("Dearth", "Famine"),
    ("fain", "gladly"), ("Fain", "Gladly"),
    ("begat", "fathered"), ("Begat", "Fathered"),
    ("beguile", "deceive"), ("Beguile", "Deceive"),
    ("beguiled", "deceived"), ("Beguiled", "Deceived"),
    ("thereon", "on it"), ("Thereon", "On it"),
    ("therewith", "with it"), ("Therewith", "With it"),
    ("thereto", "to it"), ("Thereto", "To it"),
    ("wherein", "in which"), ("Wherein", "In which"),
    ("whereon", "on which"), ("Whereon", "On which"),
    ("whereat", "at which"), ("Whereat", "At which"),
    ("girded", "fastened"), ("Girded", "Fastened"),
    ("commenced", "began"), ("Commenced", "Began"),
    ("remembrance", "memory"), ("Remembrance", "Memory"),
    ("pestilence", "plague"), ("Pestilence", "Plague"),
    ("sundry", "various"), ("Sundry", "Various"),
    ("manifold", "many"), ("Manifold", "Many"),
    ("withal", "as well"), ("Withal", "As well"),
    ("anon", "soon"), ("Anon", "Soon"),
    ("ere", "before"), ("Ere", "Before"),
]

KNOWN_ETH = {
    'cometh': 'comes', 'maketh': 'makes', 'taketh': 'takes',
    'giveth': 'gives', 'hideth': 'hides', 'loveth': 'loves',
    'moveth': 'moves', 'saveth': 'saves', 'waketh': 'wakes',
    'awaketh': 'awakes', 'ariseth': 'arises', 'consumeth': 'consumes',
    'desireth': 'desires', 'deviseth': 'devises', 'despiseth': 'despises',
    'endureth': 'endures', 'executeth': 'executes',
    'grieveth': 'grieves', 'hateth': 'hates', 'hopeth': 'hopes',
    'humbleth': 'humbles', 'inviteth': 'invites', 'judgeth': 'judges',
    'persuadeth': 'persuades', 'pleaseth': 'pleases', 'praiseth': 'praises',
    'prepareth': 'prepares', 'preserveth': 'preserves', 'proveth': 'proves',
    'provideth': 'provides', 'provoketh': 'provokes', 'raiseth': 'raises',
    'receiveth': 'receives', 'refuseth': 'refuses', 'rejoiceth': 'rejoices',
    'removeth': 'removes', 'reproveth': 'reproves', 'requireth': 'requires',
    'restoreth': 'restores', 'ruleth': 'rules', 'serveth': 'serves',
    'shaketh': 'shakes', 'smiteth': 'smites', 'striketh': 'strikes',
    'supposeth': 'supposes', 'trembleth': 'trembles', 'troubleth': 'troubles',
    'wasteth': 'wastes', 'writeth': 'writes', 'behooveth': 'behooves',
    'curseth': 'curses', 'doeth': 'does', 'seeth': 'sees', 'lieth': 'lies',
    'dyeth': 'dies', 'fleeth': 'flees',
    'crieth': 'cries', 'denieth': 'denies', 'carrieth': 'carries',
    'satisfieth': 'satisfies', 'justifieth': 'justifies',
    'magnifieth': 'magnifies', 'testifieth': 'testifies',
    'glorifieth': 'glorifies', 'multiplieth': 'multiplies',
    'prophesieth': 'prophesies', 'signifieth': 'signifies',
    'applieth': 'applies', 'emptieth': 'empties', 'envieth': 'envies',
    'speaketh': 'speaks', 'knoweth': 'knows', 'leadeth': 'leads',
    'commandeth': 'commands', 'standeth': 'stands', 'ceaseth': 'ceases',
    'seeketh': 'seeks', 'slayeth': 'kills', 'goeth': 'goes',
    'sufficeth': 'is enough for', 'constraineth': 'compels', 'mattereth': 'matters',
    'teacheth': 'teaches', 'delighteth': 'delights', 'passeth': 'passes',
    'showeth': 'shows', 'pondereth': 'ponders', 'layeth': 'lays',
    'fighteth': 'fights', 'dreameth': 'dreams', 'stirreth': 'stirs',
    'putteth': 'puts', 'suffereth': 'suffers', 'remembereth': 'remembers',
    'abhorreth': 'abhors', 'ascendeth': 'ascends', 'asketh': 'asks',
    'bindeth': 'binds', 'boweth': 'bows', 'bringeth': 'brings',
    'burneth': 'burns', 'cheateth': 'cheats', 'comforteth': 'comforts',
    'contendeth': 'contends', 'covenanteth': 'covenants',
    'delivereth': 'delivers', 'devoureth': 'devours',
    'drinketh': 'drinks', 'dwelleth': 'dwells', 'eateth': 'eats',
    'employeth': 'employs', 'exclaimeth': 'exclaims',
    'feareth': 'fears', 'fainteth': 'faints', 'flattereth': 'flatters',
    'gathereth': 'gathers', 'groaneth': 'groans', 'hasteneth': 'hastens',
    'hearkeneth': 'hearkens', 'heweth': 'hews', 'hindereth': 'hinders',
    'killeth': 'kills', 'knocketh': 'knocks', 'manifesteth': 'manifests',
    'meaneth': 'means', 'mixeth': 'mixes', 'mustereth': 'musters',
    'obeyeth': 'obeys', 'offereth': 'offers', 'perisheth': 'perishes',
    'pleadeth': 'pleads', 'profiteth': 'profits', 'prospereth': 'prospers',
    'sendeth': 'sends', 'seemeth': 'seems', 'sorroweth': 'sorrows',
    'stoppeth': 'stops', 'telleth': 'tells', 'thirsteth': 'thirsts',
    'transformeth': 'transforms', 'transgresseth': 'transgresses',
    'turneth': 'turns', 'walketh': 'walks', 'whispereth': 'whispers',
    'witnesseth': 'witnesses', 'worketh': 'works', 'rejecteth': 'rejects',
    'abideth': 'abides', 'believeth': 'believes', 'blesseth': 'blesses',
    'buildeth': 'builds', 'calleth': 'calls', 'casteth': 'casts',
    'causeth': 'causes', 'chooseth': 'chooses', 'covereth': 'covers',
    'declareth': 'declares', 'departeth': 'departs', 'descendeth': 'descends',
    'destroyeth': 'destroys', 'directeth': 'directs', 'draweth': 'draws',
    'driveth': 'drives', 'entereth': 'enters', 'existeth': 'exists',
    'falleth': 'falls', 'feedeth': 'feeds', 'filleth': 'fills',
    'findeth': 'finds', 'followeth': 'follows', 'forgiveth': 'forgives',
    'fulfilleth': 'fulfills', 'groweth': 'grows', 'guideth': 'guides',
    'hangeth': 'hangs', 'hardeneth': 'hardens', 'healeth': 'heals',
    'heareth': 'hears', 'holdeth': 'holds', 'keepeth': 'keeps',
    'lifteth': 'lifts', 'looketh': 'looks', 'loseth': 'loses',
    'melteth': 'melts', 'numbereth': 'numbers', 'openeth': 'opens',
    'overcometh': 'overcomes', 'planteth': 'plants', 'poureth': 'pours',
    'prayeth': 'prays', 'proceedeth': 'proceeds', 'promiseth': 'promises',
    'punisheth': 'punishes', 'readeth': 'reads', 'reigneth': 'reigns',
    'remaineth': 'remains', 'repenteth': 'repents', 'returneth': 'returns',
    'revealeth': 'reveals', 'runneth': 'runs', 'saith': 'says',
    'scattereth': 'scatters', 'searcheth': 'searches', 'sealeth': 'seals',
    'setteth': 'sets', 'shineth': 'shines', 'sitteth': 'sits',
    'sleepeth': 'sleeps', 'soweth': 'sows', 'spreadeth': 'spreads',
    'sweareth': 'swears', 'thinketh': 'thinks', 'toucheth': 'touches',
    'trusteth': 'trusts', 'understandeth': 'understands', 'uttereth': 'utters',
    'waiteth': 'waits', 'watcheth': 'watches', 'yieldeth': 'yields',
    'nourisheth': 'nourishes', 'worshippeth': 'worships',
    'appeareth': 'appears', 'burdeneth': 'burdens', 'condemneth': 'condemns',
    'becometh': 'becomes', 'counseleth': 'counsels', 'beginneth': 'begins',
    'cleaveth': 'cleaves', 'liveth': 'lives',
    'belongeth': 'belongs', 'listeth': 'lists', 'dieth': 'dies',
    'atoneth': 'atones', 'rebelleth': 'rebels', 'availeth': 'avails',
    'borroweth': 'borrows', 'wondereth': 'wonders', 'bloweth': 'blows',
    'pretendeth': 'pretends', 'publisheth': 'publishes', 'breaketh': 'breaks',
    'redeemeth': 'redeems', 'trieth': 'tries', 'granteth': 'grants',
    'teareth': 'tears', 'trampleth': 'tramples', 'enacteth': 'enacts',
    'mingleth': 'mingles', 'endeth': 'ends', 'heapeth': 'heaps',
    'stinketh': 'stinks', 'exerciseth': 'exercises',
    'comprehendeth': 'comprehends', 'allotteth': 'allots',
    'decreeth': 'decrees', 'perverteth': 'perverts', 'imparteth': 'imparts',
    'swelleth': 'swells', 'sprouteth': 'sprouts', 'scorcheth': 'scorches',
    'murdereth': 'murders', 'overpowereth': 'overpowers',
    'rewardeth': 'rewards', 'claimeth': 'claims', 'inflicteth': 'inflicts',
    'fadeth': 'fades', 'getteth': 'gets', 'awaiteth': 'awaits',
    'laugheth': 'laughs', 'beareth': 'bears', 'committeth': 'commits',
    'treadeth': 'treads', 'spareth': 'spares', 'spurneth': 'spurns',
    'avengeth': 'avenges', 'changeth': 'changes',
    'divideth': 'divides', 'sweepeth': 'sweeps',
    'enticeth': 'entices', 'advocateth': 'advocates',
    'faileth': 'fails', 'acknowledgeth': 'acknowledges',
    'sheddeth': 'sheds', 'blindeth': 'blinds',
    'tortureth': 'tortures', 'yoketh': 'yokes',
    'containeth': 'contains', 'cutteth': 'cuts',
    'esteemeth': 'esteems',
}

NOT_ETH_VERBS = {'teeth', 'thirtieth', 'twentieth', 'fortieth', 'fiftieth',
    'sixtieth', 'seventieth', 'eightieth', 'ninetieth', 'hundredth',
    'seth', 'beth', 'heth', 'nazareth', 'shibboleth', 'japheth', 'Kenneth',
    'beneath', 'breadth', 'hundredeth'}

IRREGULAR_PAST = {
    'speak': 'spoke', 'give': 'gave', 'go': 'went', 'take': 'took',
    'make': 'made', 'come': 'came', 'know': 'knew', 'see': 'saw',
    'find': 'found', 'write': 'wrote', 'read': 'read', 'tell': 'told',
    'think': 'thought', 'bring': 'brought', 'build': 'built',
    'burn': 'burned', 'cast': 'cast', 'drive': 'drove', 'eat': 'ate',
    'fall': 'fell', 'fight': 'fought', 'flee': 'fled', 'fly': 'flew',
    'gather': 'gathered', 'grow': 'grew', 'hear': 'heard',
    'keep': 'kept', 'lead': 'led', 'leave': 'left', 'lay': 'laid',
    'lose': 'lost', 'meet': 'met', 'pay': 'paid', 'put': 'put',
    'raise': 'raised', 'rise': 'rose', 'run': 'ran', 'say': 'said',
    'seek': 'sought', 'send': 'sent', 'set': 'set', 'shake': 'shook',
    'show': 'showed', 'sit': 'sat', 'stand': 'stood', 'strike': 'struck',
    'swear': 'swore', 'teach': 'taught', 'throw': 'threw',
    'understand': 'understood', 'wax': 'waxed', 'begin': 'began',
    'bind': 'bound', 'break': 'broke', 'draw': 'drew', 'drink': 'drank',
    'dwell': 'dwelt', 'feed': 'fed', 'forsake': 'forsook',
    'hold': 'held', 'hide': 'hid', 'hurt': 'hurt', 'kneel': 'knelt',
    'liken': 'likened', 'look': 'looked', 'cry': 'cried',
    'mourn': 'mourned', 'nourish': 'nourished', 'prosper': 'prospered',
    'rejoice': 'rejoiced', 'suffer': 'suffered', 'walk': 'walked',
    'work': 'worked', 'worship': 'worshipped', 'preach': 'preached',
    'travel': 'traveled', 'labor': 'labored', 'number': 'numbered',
    'pour': 'poured', 'press': 'pressed', 'separate': 'separated',
    'spread': 'spread', 'stir': 'stirred', 'stretch': 'stretched',
    'turn': 'turned', 'visit': 'visited', 'cause': 'caused',
    'cease': 'ceased', 'deliver': 'delivered', 'desire': 'desired',
    'depart': 'departed', 'discover': 'discovered', 'exercise': 'exercised',
    'harden': 'hardened', 'harrow': 'harrowed', 'judge': 'judged',
    'minister': 'ministered', 'obtain': 'obtained', 'ordain': 'ordained',
    'pitch': 'pitched', 'prepare': 'prepared', 'preserve': 'preserved',
    'prevail': 'prevailed', 'receive': 'received', 'reign': 'reigned',
    'repent': 'repented', 'return': 'returned', 'scatter': 'scattered',
    'strive': 'strove', 'suppose': 'supposed', 'translate': 'translated',
    'tremble': 'trembled', 'humble': 'humbled', 'contend': 'contended',
    'fortify': 'fortified', 'march': 'marched', 'overpower': 'overpowered',
    'pursue': 'pursued', 'repair': 'repaired', 'retire': 'retired',
    'establish': 'established', 'appoint': 'appointed', 'commence': 'commenced',
    'inhabit': 'inhabited', 'possess': 'possessed', 'multiply': 'multiplied',
    'have': 'had', 'beat': 'beat', 'cut': 'cut', 'overthrow': 'overthrew',
    'cleave': 'cleft', 'sow': 'sowed', 'bestow': 'bestowed',
    'overshadow': 'overshadowed', 'sorrow': 'sorrowed',
    'buy': 'bought', 'joy': 'rejoiced',
}

# ============================================================================
# PROCESSING — identical to assemble_all.py
# ============================================================================

def parse_verses(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    verses = []
    for block in text.strip().split('\n\n'):
        lines = block.strip().split('\n')
        if not lines: continue
        ref = lines[0].strip()
        if not re.match(r'^\d+:\d+$', ref): continue
        parts = ref.split(':')
        verses.append({'ref': ref, 'chapter': int(parts[0]), 'verse': int(parts[1]),
                       'lines': [l for l in lines[1:] if l.strip()]})
    return verses

def build_swap_list():
    s = list(AICTP_SWAPS) + list(COMPOUND_SWAPS) + list(SIMPLE_SWAPS)
    s.sort(key=lambda x: len(x[0]), reverse=True)
    return s

# ============================================================================
# SINGLE-PASS SWAP ENGINE — replaces the old O(text × swaps) loop
# ============================================================================
# Pre-compile a single regex alternation from all "general" swaps (those with
# no special matching logic).  Special-case words (meet, mine, save, account,
# go to, notwithstanding, AICTP) are still handled individually.
#
# The compiled regex is built once at module load and reused for every verse.
# ============================================================================

SPECIAL_CASE_ARCHAICS = {
    'meet', 'Meet', 'mine', 'Mine', 'account', 'Account',
    'notwithstanding', 'Notwithstanding',
}

def _build_general_swap_engine(swap_list):
    """Build a compiled regex + lookup dict for all non-special swaps.
    Returns (compiled_regex, lookup_dict) where lookup_dict maps
    archaic string → modern string."""
    lookup = {}
    patterns = []
    seen = set()
    for archaic, modern in swap_list:
        if 'it came to pass' in archaic or 'it shall come to pass' in archaic:
            continue  # AICTP handled separately
        if archaic in SPECIAL_CASE_ARCHAICS:
            continue  # handled individually
        if archaic == "go to" and modern == "go":
            continue  # special punctuation lookahead
        if archaic == "save" and modern == "unless":
            continue  # special negative lookbehind
        if archaic in seen:
            continue  # deduplicate (longest-first already in swap_list)
        seen.add(archaic)
        lookup[archaic] = modern
        patterns.append(re.escape(archaic))
    # Sort patterns longest-first so the alternation prefers longer matches
    patterns.sort(key=len, reverse=True)
    # Build one big regex: \b(?:pattern1|pattern2|...)\b
    big_pattern = r'\b(?:' + '|'.join(patterns) + r')\b'
    compiled = re.compile(big_pattern)
    return compiled, lookup

# Module-level cache (built lazily on first call)
_SWAP_ENGINE = None

def _get_swap_engine(swap_list):
    global _SWAP_ENGINE
    if _SWAP_ENGINE is None:
        _SWAP_ENGINE = _build_general_swap_engine(swap_list)
    return _SWAP_ENGINE

def apply_swaps(text, swap_list):
    placeholders = []
    result = text

    # ---- PRE-PASS: DO/DOES/DOTH + VERB → present tense collapse ----
    # "doth tremble" → "trembles", "does carry" → "carries"
    # "do know" → "know", "do rejoice" → "rejoice"
    # Non-verbs: leave the aux alone (e.g. "doth not" stays for later doth→does swap)
    DO_SKIP = {
        # pronouns / determiners
        'not', 'ye', 'you', 'all', 'this', 'that', 'these', 'those',
        'the', 'it', 'they', 'we', 'he', 'she', 'i', 'me', 'him',
        'them', 'us', 'her', 'his', 'my', 'our', 'your', 'their', 'its',
        'a', 'an', 'some', 'any', 'such', 'nothing', 'something',
        'none', 'no', 'every', 'one', 'mine', 'whatsoever', 'anything',
        # prepositions / conjunctions
        'so', 'as', 'in', 'to', 'unto', 'with', 'for', 'after',
        'among', 'concerning', 'if', 'now', 'then',
        # adverbs (appear between aux and real verb: "doth exceedingly rejoice")
        'well', 'much', 'more', 'many', 'also', 'even', 'thus',
        'likewise', 'always', 'greatly', 'exceedingly', 'immediately',
        'speedily', 'rightly', 'justly', 'still', 'already',
        # nouns / adjectives that follow "do" but aren't verbs
        'good', 'evil', 'iniquity', 'wickedly', 'great',
        'according', 'because', 'here', 'there', 'like',
        'men', 'wrong', 'alms', 'miracles', 'justice', 'mercy',
        'salvation', 'battle', 'business', 'service',
        # title nouns (appear between aux and real verb: "did king Benjamin teach")
        'king', 'captain', 'chief', 'judge', 'prophet', 'queen',
        # proper nouns (appear as subject after inverted aux: "did Alma teach")
        'abinadi', 'alma', 'ammon', 'antipus', 'gideon', 'helaman',
        'laman', 'lamoni', 'lehi', 'limhi', 'moroni', 'mosiah',
        'nephi', 'noah', 'satan', 'sherem', 'zeniff',
        # other words that follow "did/do" but aren't verbs
        'again',
    }

    def _third_person_s(verb):
        """Base verb → 3rd-person singular: tremble→trembles, carry→carries"""
        if verb.endswith(('s', 'sh', 'x', 'z', 'ch')):
            return verb + 'es'
        if verb.endswith('y') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return verb[:-1] + 'ies'
        return verb + 's'

    def _do_verb_replace(m):
        full = m.group(0)
        aux = m.group(1)     # do / does / doth / Do / Does / Doth
        verb = m.group(2)    # the base verb
        if verb.lower() in DO_SKIP:
            return full       # not a verb — leave untouched for later swap passes
        # doth/does + verb → 3rd person singular
        if aux.lower() in ('doth', 'does'):
            modern = _third_person_s(verb)
        else:
            # do + verb → just drop "do", keep verb as-is (1st/2nd/plural)
            modern = verb
        # Capitalize if aux was capitalized at start of sentence
        if aux[0].isupper() and not modern[0].isupper():
            modern = modern[0].upper() + modern[1:]
        idx = len(placeholders); sent = f"\x00O{idx}\x00"
        placeholders.append((sent, full, modern)); return sent

    result = re.sub(r'\b(do|does|doth|Do|Does|Doth) (\w+)\b', _do_verb_replace, result)

    # ---- AICTP swaps: literal string match (no word boundary) ----
    for archaic, modern in swap_list:
        if 'it came to pass' not in archaic and 'it shall come to pass' not in archaic:
            continue
        if archaic in result:
            sentinel = f"\x00A{len(placeholders)}\x00"
            result = result.replace(archaic, sentinel)
            placeholders.append((sentinel, archaic, modern))

    # ---- Special-case swaps (custom regex logic) ----
    # Build a quick lookup from swap_list for special words
    _special_lookup = {}
    for archaic, modern in swap_list:
        if archaic in SPECIAL_CASE_ARCHAICS or (archaic == "go to" and modern == "go") or (archaic == "save" and modern == "unless"):
            _special_lookup[archaic] = modern

    for archaic, modern in _special_lookup.items():
        sentinel = f"\x00S{len(placeholders)}\x00"
        if archaic.lower() == "meet":
            for prefix in [r'(?<=\bis )', r'(?<=\bwas )', r'(?<=\bbe )']:
                result = re.sub(prefix + re.escape(archaic) + r'\b', sentinel, result)
            placeholders.append((sentinel, archaic, modern)); continue
        if archaic in ("mine", "Mine"):
            result = re.sub(r'(?<!\ba )(?<!\bthe )\b' + re.escape(archaic) + r'\b', sentinel, result)
            placeholders.append((sentinel, archaic, modern)); continue
        if archaic == "save" and modern == "unless":
            result = re.sub(r'(?<!\bto )(?<!\bdid )(?<!\bwill )(?<!\bshall )(?<!\bcould )(?<!\bwould )(?<!\bmight )(?<!\bmay )(?<!\bcan )\bsave\b(?! us| them| him| her| his| the | those| all| my| your| our| a | it$)', sentinel, result)
            placeholders.append((sentinel, archaic, modern)); continue
        if archaic in ("account", "Account"):
            result = re.sub(r'\b' + re.escape(archaic) + r'\b(?! of\b| for\b)', sentinel, result)
            placeholders.append((sentinel, archaic, modern)); continue
        if archaic == "go to" and modern == "go":
            result = re.sub(r'\bgo to(?=[,;])', sentinel, result)
            placeholders.append((sentinel, archaic, modern)); continue
        # notwithstanding: context-sensitive
        if archaic.lower() == 'notwithstanding':
            cap = archaic[0].isupper()
            def _notw_replace(m, _cap=cap, _archaic=archaic):
                after = result[m.end():m.end()+20].lstrip()
                first_word = re.match(r'[a-zA-Z]+', after)
                fw = first_word.group(0).lower() if first_word else ''
                if fw in ('the','their','all','our','my','his','her','its','a','an',
                          'these','this','that','those','such','every','much','many'):
                    mod = 'Despite' if _cap else 'despite'
                elif fw in ('they','we','he','she','i','it','so','there','being'):
                    mod = 'Even though' if _cap else 'even though'
                else:
                    mod = 'Nevertheless' if _cap else 'nevertheless'
                idx = len(placeholders); sent = f"\x00N{idx}\x00"
                placeholders.append((sent, _archaic, mod)); return sent
            result = re.sub(r'\b' + re.escape(archaic) + r'\b', _notw_replace, result)
            continue

    # ---- SINGLE-PASS general swaps (the big performance win) ----
    compiled_re, lookup = _get_swap_engine(swap_list)

    def _general_replace(m):
        matched = m.group(0)
        # Skip if inside a sentinel (already replaced by earlier pass)
        if '\x00' in result[max(0, m.start()-2):m.start()]:
            return matched
        modern = lookup.get(matched)
        if modern is None:
            return matched  # shouldn't happen, but safety
        idx = len(placeholders); sent = f"\x00G{idx}\x00"
        placeholders.append((sent, matched, modern))
        return sent

    result = compiled_re.sub(_general_replace, result)

    # ---- -eth verb fallback (catch any remaining -eth words) ----
    def eth_replace(m):
        word = m.group(0)
        if word.lower() in NOT_ETH_VERBS:
            return word
        if word in KNOWN_ETH: mf = KNOWN_ETH[word]
        else:
            stem = word[:-3]
            if stem.endswith('i'): mf = stem[:-1] + 'ies'
            elif stem.endswith(('s','sh','x','z','ch')): mf = stem + 'es'
            elif stem.endswith(('rr','tt','pp','dd','gg','nn')): mf = stem[:-1] + 's'
            elif stem.endswith('ll'): mf = stem + 's'
            elif len(stem) <= 2: mf = stem + 'es'
            else: mf = stem + 's'
            print(f"  WARNING: Unknown -eth '{word}' → '{mf}'", file=sys.stderr)
        idx = len(placeholders); sent = f"\x00E{idx}\x00"
        placeholders.append((sent, word, mf)); return sent
    result = re.sub(r'\b[a-z]+eth\b', lambda m: eth_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    # ---- "did" + verb → past tense ----
    DID_SKIP = {'my', 'his', 'her', 'their', 'our', 'your', 'its', 'the', 'a', 'an',
                'not', 'also', 'all', 'both', 'even', 'never', 'once', 'then', 'thus',
                'i', 'it', 'they', 'she', 'he', 'we', 'so', 'as', 'again', 'frankly',
                'still', 'do', 'molten', 'this', 'that', 'these', 'those',
                'now', 'throughout', 'there', 'here', 'much', 'more',
                # title nouns (subject between aux and verb: "did king Benjamin teach")
                'king', 'captain', 'chief', 'judge', 'prophet', 'queen',
                # proper nouns (inverted subject: "did Alma teach")
                'abinadi', 'alma', 'ammon', 'antipus', 'gideon', 'helaman',
                'laman', 'lamoni', 'lehi', 'limhi', 'moroni', 'mosiah',
                'nephi', 'noah', 'satan', 'sherem', 'zeniff'}

    def did_verb_replace(m):
        full, verb = m.group(0), m.group(1)
        if verb.lower() in DID_SKIP:
            return full  # not a verb, leave as-is
        if verb in IRREGULAR_PAST: past = IRREGULAR_PAST[verb]
        elif verb.endswith('e'): past = verb + 'd'
        elif verb.endswith('y') and len(verb)>1 and verb[-2] not in 'aeiou': past = verb[:-1] + 'ied'
        else: past = verb + 'ed'
        idx = len(placeholders); sent = f"\x00D{idx}\x00"
        placeholders.append((sent, full, past)); return sent
    result = re.sub(r'\bdid (\w+)\b', lambda m: did_verb_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    # ---- "thou" + -est fallback (catch any not already in compound swaps) ----
    def thou_est_replace(m):
        full, ve = m.group(0), m.group(1)
        base = ve[:-3] if ve.endswith('est') else (ve[:-2] if ve.endswith('st') else None)
        if not base: return full
        idx = len(placeholders); sent = f"\x00T{idx}\x00"
        placeholders.append((sent, full, ("You " if full[0]=='T' else "you ") + base)); return sent
    result = re.sub(r'\b[Tt]hou (\w+est)\b', lambda m: thou_est_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    # ---- Final expansion: sentinels → HTML <span> markup ----
    for sentinel, archaic, modern in placeholders:
        arc_low = archaic.lower()
        is_quiet = (arc_low in QUIET_ARCHAICS
                    or any(q in arc_low for q in QUIET_ARCHAICS if len(q) > 3))
        quiet = ' swap-quiet' if is_quiet else ''
        result = result.replace(sentinel, f'<span class="swap{quiet}" data-orig="{archaic}" data-mod="{modern}">{archaic}</span>')
    return result

def fix_participles(text):
    """Fix past tense → past participle after have/has/had/be auxiliaries,
    and past tense → base form after modals and 'to' infinitive.

    Uses a single-pass approach: find all data-mod attributes, check the
    preceding context for auxiliaries/modals, and correct as needed."""
    PARTICIPLE_MAP = {
        'saw': 'seen', 'spoke': 'spoken', 'broke': 'broken',
        'gave': 'given', 'took': 'taken', 'wrote': 'written',
        'drove': 'driven', 'chose': 'chosen', 'rose': 'risen',
        'fell': 'fallen', 'grew': 'grown', 'knew': 'known',
        'threw': 'thrown', 'drew': 'drawn', 'swore': 'sworn',
        'tore': 'torn', 'wore': 'worn', 'froze': 'frozen',
        'stole': 'stolen', 'shrank': 'shrunk', 'drank': 'drunk',
        'began': 'begun', 'sang': 'sung', 'ran': 'run',
        'went': 'gone',
    }
    MODAL_BASE_MAP = {
        'engraved': 'engrave',
        'saw': 'see', 'spoke': 'speak', 'broke': 'break',
        'gave': 'give', 'took': 'take', 'wrote': 'write',
        'drove': 'drive', 'chose': 'choose', 'rose': 'rise',
        'fell': 'fall', 'grew': 'grow', 'knew': 'know',
        'threw': 'throw', 'drew': 'draw', 'swore': 'swear',
        'tore': 'tear', 'wore': 'wear', 'froze': 'freeze',
        'stole': 'steal', 'shrank': 'shrink', 'drank': 'drink',
        'began': 'begin', 'sang': 'sing', 'ran': 'run',
        'went': 'go', 'struck': 'strike', 'killed': 'kill',
        'fastened': 'fasten', 'listened': 'listen',
        'complained': 'complain', 'stayed': 'stay',
        'confused': 'confuse', 'compelled': 'compel',
        'deceived': 'deceive', 'filled': 'fill',
    }
    AUX_SET = {'had', 'have', 'has', 'was', 'were', 'be', 'been', 'being', 'is', 'are'}
    MODAL_SET = {'should', 'would', 'could', 'may', 'might', 'shall', 'will', 'can', 'must'}
    # All words that might need correction in data-mod
    ALL_TARGETS = set(PARTICIPLE_MAP.keys()) | set(MODAL_BASE_MAP.keys())

    def _fix_mod(m):
        mod_val = m.group(1)
        if mod_val not in ALL_TARGETS:
            return m.group(0)
        # Look back ~120 chars for context (covers preceding spans + text)
        start = max(0, m.start() - 120)
        context = text[start:m.start()]

        # Strip HTML tags to get plain text context for clause-boundary detection
        plain_context = re.sub(r'<[^>]+>', ' ', context)

        # For modal detection, only look within the current clause.
        # Split on clause boundaries (comma, semicolon, colon, period, question mark)
        # and use only the last clause fragment.
        clause_context = re.split(r'[,;:.?!]', plain_context)[-1]

        # Check for auxiliary (have/has/had/was/were/be...) immediately preceding the verb
        # Only match if the aux is within a few words of the swap (not a distant copula)
        # Use the last ~40 chars of plain context stripped of HTML
        near_context = re.sub(r'<[^>]*>?', '', context[-60:]).strip()
        near_words = near_context.split()
        # Check last 3 words before the swap for an auxiliary
        has_aux = bool(set(w.lower() for w in near_words[-3:]) & AUX_SET)
        # Check for modal only in same clause (prevents cross-clause false positives)
        has_modal = bool(re.search(r'\b(' + '|'.join(MODAL_SET) + r')\b', clause_context))
        # Also check for modal/aux inside preceding data-mod attributes (same clause)
        for dm in re.finditer(r'data-mod="([^"]*)"', context):
            dm_text = dm.group(1)
            if re.search(r'\b(' + '|'.join(AUX_SET) + r')$', dm_text):
                has_aux = True
        # Only count data-mod modals if they're in the same clause fragment
        clause_context_raw = context[context.rfind('>') if '>' in context else 0:]
        for dm in re.finditer(r'data-mod="([^"]*)"', clause_context_raw):
            dm_text = dm.group(1)
            if re.search(r'\b(' + '|'.join(MODAL_SET) + r')$', dm_text):
                has_modal = True
        # Check for "to" infinitive
        has_to = bool(re.search(r'\bto\s*$', plain_context))
        # When both modal AND be-auxiliary are present (e.g. "should be engraved"),
        # it's passive voice — keep past participle, don't reduce to base form.
        # IMPORTANT: both modal and be must be NEAR the verb (within 5 words),
        # not just anywhere in the clause. "shall read are they which Isaiah spake"
        # has 'shall' and 'are' in the same clause but neither modifies 'spake'.
        BE_WORDS = {'be', 'been', 'being', 'is', 'are', 'was', 'were'}
        near_words_lower = [w.lower() for w in near_words[-5:]]
        has_near_modal = bool(set(near_words_lower) & MODAL_SET)
        has_near_be = bool(set(near_words_lower) & BE_WORDS)
        has_be = bool(re.search(r'\b(' + '|'.join(BE_WORDS) + r')\b', clause_context))
        if has_near_modal and has_near_be and mod_val in PARTICIPLE_MAP:
            # Passive: "should be engraved" — keep participle
            return 'data-mod="' + PARTICIPLE_MAP[mod_val] + '"'
        if has_near_modal and has_near_be:
            # Passive but no irregular participle — keep as-is (regular -ed is fine)
            return m.group(0)
        if has_near_modal and mod_val in MODAL_BASE_MAP:
            return 'data-mod="' + MODAL_BASE_MAP[mod_val] + '"'
        if has_to and mod_val in MODAL_BASE_MAP:
            return 'data-mod="' + MODAL_BASE_MAP[mod_val] + '"'
        if has_aux and mod_val in PARTICIPLE_MAP:
            return 'data-mod="' + PARTICIPLE_MAP[mod_val] + '"'
        return m.group(0)

    text = re.sub(r'data-mod="([^"]*)"', _fix_mod, text)
    return text

def fix_articles(text):
    """Fix 'an' → 'a' before consonant sounds introduced by swaps (e.g. 'an very')."""
    # Match: an <span class="swap..."...data-mod="[consonant-starting]"...>
    # Note: class may be "swap" or "swap swap-quiet", so match with [^>]* after "swap
    def _fix_an(m):
        return 'a' + m.group(0)[2:]  # replace 'an' with 'a'
    text = re.sub(r'\ban\s+(<span class="swap[^"]*"[^>]*data-mod="[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ])', _fix_an, text)
    # Also fix 'a' → 'an' before vowel-starting swap output
    def _fix_a(m):
        return 'an' + m.group(0)[1:]  # replace 'a' with 'an'
    text = re.sub(r'\ba\s+(<span class="swap[^"]*"[^>]*data-mod="[aeiouAEIOU])', _fix_a, text)
    return text

def wrap_punctuation(text):
    text = text.replace('--', '\u2014')
    parts = re.split(r'(<[^>]+>)', text)
    result = []
    for part in parts:
        if part.startswith('<'): result.append(part)
        else:
            # Em-dashes get a separate class so they can insert space when hidden
            part = part.replace('\u2014', '<span class="punct punct-dash">\u2014</span>')
            for ch in [',',';',':','.','!','?','(',')','\'','\u2018','\u2019']:
                part = part.replace(ch, f'<span class="punct">{ch}</span>')
            part = re.sub(r'(?<=\s)-(?=\s)', '<span class="punct">-</span>', part)
            result.append(part)
    return ''.join(result)

def process_line(line, swap_list):
    return wrap_punctuation(fix_articles(fix_participles(apply_swaps(line, swap_list))))

# ============================================================================
# V0 PARAGRAPH TEXT — original verse paragraphs for base-layer display
# ============================================================================

V0_DIR = Path(__file__).resolve().parent / 'data' / 'text-files' / 'v0-bofm-original'

# Map book IDs (lowercase, as used in booklist.txt) → v0 filenames
V0_FILE_MAP = {
    '1nephi': '1_Nephi.txt', '2nephi': '2_Nephi.txt',
    '3nephi': '3_Nephi.txt', '4nephi': '4_Nephi.txt',
    'jacob': 'Jacob.txt', 'enos': 'Enos.txt', 'jarom': 'Jarom.txt',
    'omni': 'Omni.txt', 'words-of-mormon': 'Words_of_Mormon.txt',
    'mosiah': 'Mosiah.txt', 'alma': 'Alma.txt', 'helaman': 'Helaman.txt',
    'mormon': 'Mormon.txt', 'ether': 'Ether.txt', 'moroni': 'Moroni.txt',
}

_v0_cache = {}

def load_v0_paragraphs(book_name):
    """Load v0 original text, return dict of {chapter:verse_num: paragraph_text}."""
    if book_name in _v0_cache:
        return _v0_cache[book_name]
    fname = V0_FILE_MAP.get(book_name)
    if not fname:
        _v0_cache[book_name] = {}
        return {}
    fpath = V0_DIR / fname
    if not fpath.exists():
        _v0_cache[book_name] = {}
        return {}
    result = {}
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    for block in text.strip().split('\n\n'):
        lines = block.strip().split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        # v0 format: "1 Nephi 1:1" — extract chapter:verse
        m = re.match(r'.+\s+(\d+):(\d+)$', header)
        if not m:
            continue
        ch, vs = int(m.group(1)), int(m.group(2))
        # Join remaining lines as paragraph text (some long verses wrap in the file)
        para_text = ' '.join(l.strip() for l in lines[1:] if l.strip())
        result[(ch, vs)] = para_text
    _v0_cache[book_name] = result
    return result

# ============================================================================
# INTERTEXT DATA — Hardy biblical references loaded at build time
# ============================================================================

# Short abbreviations for bible books (displayed inline after verses)
BIBLE_ABBREV = {
    'Genesis': 'Gen', 'Exodus': 'Exo', 'Leviticus': 'Lev', 'Numbers': 'Num',
    'Deuteronomy': 'Deu', 'Joshua': 'Jos', 'Judges': 'Jdg', 'Ruth': 'Rth',
    '1 Samuel': '1Sa', '2 Samuel': '2Sa', '1 Kings': '1Ki', '2 Kings': '2Ki',
    '1 Chronicles': '1Ch', '2 Chronicles': '2Ch', 'Ezra': 'Ezr', 'Nehemiah': 'Neh',
    'Esther': 'Est', 'Job': 'Job', 'Psalms': 'Psa', 'Proverbs': 'Pro',
    'Ecclesiastes': 'Ecc', 'Song of Solomon': 'SoS', 'Isaiah': 'Isa',
    'Jeremiah': 'Jer', 'Lamentations': 'Lam', 'Ezekiel': 'Eze', 'Daniel': 'Dan',
    'Hosea': 'Hos', 'Joel': 'Joe', 'Amos': 'Amo', 'Obadiah': 'Oba',
    'Jonah': 'Jon', 'Micah': 'Mic', 'Nahum': 'Nah', 'Habakkuk': 'Hab',
    'Zephaniah': 'Zep', 'Haggai': 'Hag', 'Zechariah': 'Zec', 'Malachi': 'Mal',
    'Matthew': 'Mat', 'Mark': 'Mrk', 'Luke': 'Luk', 'John': 'Jhn',
    'Acts': 'Act', 'Romans': 'Rom', '1 Corinthians': '1Co', '2 Corinthians': '2Co',
    'Galatians': 'Gal', 'Ephesians': 'Eph', 'Philippians': 'Php',
    'Colossians': 'Col', '1 Thessalonians': '1Th', '2 Thessalonians': '2Th',
    '1 Timothy': '1Ti', '2 Timothy': '2Ti', 'Titus': 'Tit', 'Philemon': 'Phm',
    'Hebrews': 'Heb', 'James': 'Jas', '1 Peter': '1Pe', '2 Peter': '2Pe',
    '1 John': '1Jn', '2 John': '2Jn', '3 John': '3Jn', 'Jude': 'Jud',
    'Revelation': 'Rev',
}
# Sort longest-first so "1 Corinthians" matches before "1 Co..." etc.
_SORTED_BIBLE = sorted(BIBLE_ABBREV.keys(), key=len, reverse=True)

def shorten_bible_ref(ref):
    """Shorten 'Isaiah 40.3' → 'Isa 40.3', 'Matthew 3.3+' → 'Mat 3.3+'."""
    for full in _SORTED_BIBLE:
        if ref.startswith(full):
            return BIBLE_ABBREV[full] + ref[len(full):]
    return ref

_INTERTEXT_INDEX = None  # populated by load_intertext()
_PHRASE_INDEX = None      # populated by load_intertext()
_KJV_DIFF_INDEX = None   # populated by load_intertext()
_PERICOPE_INDEX = None    # populated by load_intertext()
_GLOSS_INDEX = {}         # populated by load_intertext() — contextual glosses for Isaiah/Malachi

def load_intertext():
    """Load the enriched Hardy intertext index, phrase index, KJV diff, and glosses."""
    global _INTERTEXT_INDEX, _PHRASE_INDEX, _KJV_DIFF_INDEX, _PERICOPE_INDEX, _GLOSS_INDEX
    base = os.path.dirname(os.path.abspath(__file__))
    intertext_path = os.path.join(base, 'data', 'hardy_intertext.json')
    phrase_path = os.path.join(base, 'data', 'hardy_phrase_index.json')
    diff_path = os.path.join(base, 'data', 'kjv_diff_index.json')
    if os.path.exists(intertext_path):
        with open(intertext_path) as f:
            _INTERTEXT_INDEX = json.load(f)
        total = sum(len(vs) for ch in _INTERTEXT_INDEX.values() for vs in ch.values())
        print(f"Loaded intertext index: {len(_INTERTEXT_INDEX)} books, {total} verse slots")
    else:
        print(f"  No intertext data at {intertext_path}, skipping intertext injection")
        _INTERTEXT_INDEX = {}
    if os.path.exists(phrase_path):
        with open(phrase_path) as f:
            _PHRASE_INDEX = json.load(f)
        total = sum(1 for ch in _PHRASE_INDEX.values() for vs in ch.values() for _ in vs.values())
        print(f"Loaded phrase index: {total} verse entries for phrase-level quotation coloring")
    else:
        print(f"  No phrase index at {phrase_path}, quotations will use full-verse coloring")
        _PHRASE_INDEX = {}
    if os.path.exists(diff_path):
        with open(diff_path) as f:
            _KJV_DIFF_INDEX = json.load(f)
        total = sum(1 for ch in _KJV_DIFF_INDEX.values() for vs in ch.values() for _ in vs.values())
        print(f"Loaded KJV diff index: {total} verse entries for parallel passage visualization")
    else:
        print(f"  No KJV diff index at {diff_path}, skipping diff layer")
        _KJV_DIFF_INDEX = {}
    pericope_path = os.path.join(base, 'data', 'pericope_index.json')
    if os.path.exists(pericope_path):
        with open(pericope_path) as f:
            _PERICOPE_INDEX = json.load(f)
        total = sum(len(entries) for ch in _PERICOPE_INDEX.values() for entries in ch.values())
        print(f"Loaded pericope index: {total} section headers for Sections layer")
    else:
        print(f"  No pericope index at {pericope_path}, skipping Sections layer")
        _PERICOPE_INDEX = {}
    load_parallel_index(base)
    load_parry_index(base)
    load_contextual_glosses(base)

_PARALLEL_INDEX = {}

def load_parallel_index(base):
    global _PARALLEL_INDEX
    path = os.path.join(base, 'data', 'parallel_index.json')
    if os.path.exists(path):
        with open(path) as f:
            _PARALLEL_INDEX = json.load(f)
        total = sum(len(e) for ch in _PARALLEL_INDEX.values() for e in ch.values())
        print(f"Loaded parallel index: {total} structures for Hebrew Poetry layer")
    else:
        print(f"  No parallel index at {path}, skipping Hebrew Poetry layer")
        _PARALLEL_INDEX = {}

def get_parallel_structures(book_id, chapter):
    """Return list of parallel structures for this chapter, or empty list."""
    return _PARALLEL_INDEX.get(book_id, {}).get(str(chapter), [])

# ── Parry parallelism overlay data ──
_PARRY_INDEX = {}

def load_parry_index(base):
    global _PARRY_INDEX
    path = os.path.join(base, 'data', 'parry_index.json')
    if os.path.exists(path):
        with open(path) as f:
            _PARRY_INDEX = json.load(f)
        total = sum(len(e) for ch in _PARRY_INDEX.values() for e in ch.values())
        print(f"Loaded Parry index: {total} verses for Poetic layer")
    else:
        print(f"  No Parry index at {path}, skipping Parry overlay")
        _PARRY_INDEX = {}

def get_parry_verses(book_id, chapter):
    """Return dict of verse_num → {lines, types} for this chapter from Parry index v2."""
    ch_data = _PARRY_INDEX.get(book_id, {}).get(str(chapter), [])
    result = {}
    for entry in ch_data:
        result[entry['v']] = entry
    return result


def load_contextual_glosses(base):
    """Load contextual glosses for Isaiah/Malachi sections.

    The JSON has flat keys like "2nephi:12:1" mapping to arrays of
    {phrase, note, category} objects.  We restructure into nested
    book → chapter → verse → [glosses] for O(1) lookup.
    """
    global _GLOSS_INDEX
    path = os.path.join(base, 'data', 'contextual_glosses.json')
    if not os.path.exists(path):
        print(f"  No contextual glosses at {path}, skipping gloss layer")
        _GLOSS_INDEX = {}
        return
    with open(path) as f:
        raw = json.load(f)
    _GLOSS_INDEX = {}
    total = 0
    for key, entries in raw.items():
        if key == '_meta' or not entries:
            continue
        parts = key.split(':')
        if len(parts) != 3:
            continue
        book, ch, v = parts
        _GLOSS_INDEX.setdefault(book, {}).setdefault(ch, {})[v] = entries
        total += len(entries)
    print(f"Loaded contextual glosses: {total} glosses for Isaiah/Malachi annotation")


def get_glosses(book_id, chapter, verse):
    """Return list of gloss entries for this verse, or empty list."""
    if not _GLOSS_INDEX:
        return []
    return _GLOSS_INDEX.get(book_id, {}).get(str(chapter), {}).get(str(verse), [])


def apply_gloss_highlights(line_text, gloss_entries):
    """Wrap glossed phrases in <span class="gloss" data-note="..." data-cat="...">.

    Matches phrase text case-insensitively against the line (which may
    contain HTML tags from swap processing).  Works on the visible-text
    layer, skipping over tags.
    """
    if not gloss_entries:
        return line_text

    # Build a plain-text map (char positions in the HTML → visible text)
    # so we can match phrases against visible text and map back to HTML positions
    plain_chars = []  # list of (html_pos, char)
    i = 0
    while i < len(line_text):
        if line_text[i] == '<':
            end = line_text.find('>', i)
            if end == -1:
                break
            i = end + 1
        else:
            plain_chars.append((i, line_text[i]))
            i += 1

    plain_text = ''.join(c for _, c in plain_chars)
    plain_lower = plain_text.lower()

    # Find all gloss matches as intervals in plain-text space
    intervals = []
    for entry in gloss_entries:
        phrase = entry.get('phrase', '')
        if not phrase:
            continue
        note = entry.get('note', '').replace('"', '&quot;')
        cat = entry.get('category', '')
        idx = plain_lower.find(phrase.lower())
        if idx != -1:
            intervals.append((idx, idx + len(phrase), note, cat))

    if not intervals:
        return line_text

    # Sort by start; resolve overlaps (keep longest)
    intervals.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    merged = []
    for s, e, note, cat in intervals:
        if merged and s < merged[-1][1]:
            if e - s > merged[-1][1] - merged[-1][0]:
                merged[-1] = (s, e, note, cat)
        else:
            merged.append((s, e, note, cat))

    # Map plain-text positions back to HTML positions
    result = []
    html_pos = 0
    plain_idx = 0

    for s, e, note, cat in merged:
        # Advance to start of this interval
        while plain_idx < s:
            html_p = plain_chars[plain_idx][0]
            # Include any HTML tags between current html_pos and this char
            while html_pos < html_p:
                result.append(line_text[html_pos])
                html_pos += 1
            result.append(line_text[html_pos])
            html_pos += 1
            plain_idx += 1

        # Collect the HTML fragment for this gloss range
        frag_parts = []
        while plain_idx < e:
            html_p = plain_chars[plain_idx][0]
            while html_pos < html_p:
                frag_parts.append(line_text[html_pos])
                html_pos += 1
            frag_parts.append(line_text[html_pos])
            html_pos += 1
            plain_idx += 1
        fragment = ''.join(frag_parts)

        # Wrap visible text in gloss span, respecting existing tag boundaries.
        # Continuation fragments (after the first open) get gloss-cont class
        # so CSS can suppress duplicate ✦ markers.
        gloss_open_first = f'<span class="gloss" data-note="{note}" data-cat="{cat}">'
        gloss_open_cont  = f'<span class="gloss gloss-cont" data-note="{note}" data-cat="{cat}">'
        in_gloss = False
        gloss_opened_count = 0
        fi = 0
        while fi < len(fragment):
            if fragment[fi] == '<':
                end_tag = fragment.find('>', fi)
                if end_tag == -1:
                    break
                tag = fragment[fi:end_tag + 1]
                if in_gloss:
                    result.append('</span>')
                    in_gloss = False
                result.append(tag)
                fi = end_tag + 1
            else:
                if not in_gloss:
                    gloss_opened_count += 1
                    result.append(gloss_open_first if gloss_opened_count == 1 else gloss_open_cont)
                    in_gloss = True
                result.append(fragment[fi])
                fi += 1
        if in_gloss:
            result.append('</span>')

    # Emit remainder
    while html_pos < len(line_text):
        result.append(line_text[html_pos])
        html_pos += 1

    return ''.join(result)


def _extract_visible_text(html):
    """Strip HTML tags to get visible text only."""
    result = []
    i = 0
    while i < len(html):
        if html[i] == '<':
            end = html.find('>', i)
            if end == -1:
                break
            i = end + 1
        else:
            result.append(html[i])
            i += 1
    return ''.join(result)


def apply_gloss_highlights_multiline(lines, gloss_entries):
    """Apply glosses across multiple lines, handling phrases that span line breaks.

    For phrases found within a single line, delegates to apply_gloss_highlights.
    For phrases that span multiple lines, splits the phrase at line boundaries
    and applies sub-phrase glosses to each line.
    """
    if not gloss_entries or not lines:
        return lines

    # Extract plain text for each line
    line_plains = [_extract_visible_text(line) for line in lines]

    # Separate single-line vs multi-line gloss entries
    single_entries = []
    multi_entries = []
    for entry in gloss_entries:
        phrase = entry.get('phrase', '')
        if not phrase:
            continue
        phrase_lower = phrase.lower()
        if any(phrase_lower in lp.lower() for lp in line_plains):
            single_entries.append(entry)
        else:
            multi_entries.append(entry)

    # Apply single-line glosses normally
    result = [apply_gloss_highlights(line, single_entries) for line in lines]

    if not multi_entries:
        return result

    # Build concatenated plain text with line-boundary offsets
    # Join with space (matching visual separation between sense lines)
    line_offsets = []  # (start, end) in the concatenated string
    pos = 0
    for lp in line_plains:
        line_offsets.append((pos, pos + len(lp)))
        pos += len(lp) + 1  # +1 for the joining space

    full_plain = ' '.join(line_plains)
    full_lower = full_plain.lower()

    for entry in multi_entries:
        phrase = entry.get('phrase', '')
        note = entry.get('note', '')
        cat = entry.get('category', '')
        phrase_lower = phrase.lower()

        idx = full_lower.find(phrase_lower)
        if idx == -1:
            continue
        phrase_end = idx + len(phrase)

        # Determine which lines the phrase spans
        for li, (ls, le) in enumerate(line_offsets):
            overlap_start = max(idx, ls)
            overlap_end = min(phrase_end, le)

            if overlap_start < overlap_end:
                sub_phrase = line_plains[li][overlap_start - ls : overlap_end - ls]
                if sub_phrase.strip():
                    sub_entry = {
                        'phrase': sub_phrase,
                        'note': note,
                        'category': cat,
                    }
                    result[li] = apply_gloss_highlights(result[li], [sub_entry])

    return result


def get_pericope(book_id, chapter, verse):
    """Return a pericope section title if this verse starts a new section, or None."""
    if not _PERICOPE_INDEX:
        return None
    entries = _PERICOPE_INDEX.get(book_id, {}).get(str(chapter), [])
    for entry in entries:
        if entry['verse'] == verse:
            return entry['title']
    return None

def format_pericope_header(title):
    """Format a pericope title into a two-tier HTML header.

    Splits on colon to create a main title and subtitle line.
    Extracts parenthetical scripture references (Isaiah X:Y, Malachi X:Y)
    into a separate styled span.

    Examples:
      "The Song of the Vineyard: God's People Fail to Bear Fruit (Isaiah 5:1–7)"
      → main: "The Song of the Vineyard"
      → sub:  "God's People Fail to Bear Fruit"  ref: "Isaiah 5:1–7"

      "Nephi Explains Isaiah's Difficult Prophecies"
      → main: "Nephi Explains Isaiah's Difficult Prophecies"  (no subtitle)
    """
    import re

    # Extract parenthetical scripture reference if present (Isaiah, Malachi, etc.)
    # Also extract verse-range references like (vv. 1–8) or (v. 3)
    ref_match = re.search(r'\s*\(([^)]*(?:Isaiah|Malachi|Genesis|Exodus|Psalm|Isa|Mal|Gen|Exo|Psa|Mic|Deut|Lev)[^)]*)\)\s*$', title)
    ref_html = ''
    if ref_match:
        ref_text = ref_match.group(1)
        ref_html = f'<span class="pericope-ref">{ref_text}</span>'
        title = title[:ref_match.start()]

    # Extract verse-range references like (vv. 1–8) or (v. 3)
    vv_match = re.search(r'\s*\((vv?\.\s*\d+(?:\s*\u2013\s*\d+)?)\)\s*$', title)
    vv_html = ''
    if vv_match:
        vv_text = vv_match.group(1)
        vv_html = f'<span class="pericope-vv">{vv_text}</span>'
        title = title[:vv_match.start()]

    # Split on colon for two-tier display (but not if colon is inside quotes)
    if ': ' in title and "'" not in title.split(': ')[0][-5:]:
        parts = title.split(': ', 1)
        main_title = parts[0].strip()
        subtitle = parts[1].strip()
        inner = f'<span class="pericope-main">{main_title}</span>'
        inner += f'<span class="pericope-sub">{subtitle}</span>'
        if ref_html:
            inner += ref_html
        if vv_html:
            inner += vv_html
        return f'<div class="pericope-header pericope-two-tier">{inner}</div>'
    else:
        # Single-tier: no colon split
        inner = f'<span class="pericope-main">{title}</span>'
        if ref_html:
            inner += ref_html
            if vv_html:
                inner += vv_html
            # Use pericope-with-ref class so ref gets its own line via flex
            return f'<div class="pericope-header pericope-with-ref">{inner}</div>'
        if vv_html:
            inner += vv_html
        return f'<div class="pericope-header">{inner}</div>'

def get_intertext(book_id, chapter, verse):
    """Return list of intertext entries for a given verse, or empty list."""
    if not _INTERTEXT_INDEX:
        return []
    return _INTERTEXT_INDEX.get(book_id, {}).get(str(chapter), {}).get(str(verse), [])

def get_kjv_diff(book_id, chapter, verse):
    """Return KJV diff data for a parallel verse, or None."""
    if not _KJV_DIFF_INDEX:
        return None
    return _KJV_DIFF_INDEX.get(book_id, {}).get(str(chapter), {}).get(str(verse), None)

def render_kjv_diff(diff_data):
    """Render a KJV diff entry as HTML with strikethrough/bold markup.

    Returns an HTML string where:
    - 'delete' words get <del class="kjv-del">
    - 'insert' words get <b class="kjv-ins">
    - 'equal' words are plain text
    Also includes the KJV source reference.
    """
    parts = []
    for segment in diff_data['diff']:
        text = segment['text']
        stype = segment['type']
        if stype == 'delete':
            parts.append(f'<del class="kjv-del">{text}</del>')
        elif stype == 'insert':
            parts.append(f'<b class="kjv-ins">{text}</b>')
        else:
            parts.append(text)
    html = ' '.join(parts)
    # Clean up spacing around punctuation that diff may have split awkwardly
    html = re.sub(r'\s+([.,;:!?])', r'\1', html)
    # Per-verse ref removed — pericope section headers provide the Isaiah/Malachi context
    return f'<span class="kjv-diff-text">{html}</span>'

def get_phrase_matches(book_id, chapter, verse):
    """Return phrase match data for a quotation verse, or None."""
    if not _PHRASE_INDEX:
        return None
    return _PHRASE_INDEX.get(book_id, {}).get(str(chapter), {}).get(str(verse), None)

def _build_text_map(html):
    """Build a mapping between text-only positions and HTML positions.

    Returns (plain_text, text_to_html_map) where text_to_html_map[i] gives
    the HTML position corresponding to plain_text[i]. This allows us to find
    phrases in plain text and map match positions back to the original HTML.
    """
    plain_chars = []
    text_to_html = []
    i = 0
    in_tag = False
    while i < len(html):
        if html[i] == '<':
            in_tag = True
            i += 1
        elif html[i] == '>' and in_tag:
            in_tag = False
            i += 1
        elif in_tag:
            i += 1
        else:
            plain_chars.append(html[i])
            text_to_html.append(i)
            i += 1
    # Sentinel for end-of-string mapping
    text_to_html.append(len(html))
    return ''.join(plain_chars), text_to_html


def apply_phrase_highlights(line_text, phrases, css_class):
    """Wrap matched phrases within a line with <span class="css_class">.

    Uses case-insensitive matching to find phrase text within the line,
    then wraps matched portions. Searches only in visible text (not inside
    HTML tags or attributes) to avoid corrupting existing markup.
    Also matches partial phrases: if a multi-word phrase spans across line
    breaks, we check whether any 3+ word suffix or prefix falls on this line.
    Returns the line with spans inserted.
    """
    if not phrases:
        return line_text

    # Build text-only version for safe phrase matching
    plain_text, text_to_html = _build_text_map(line_text)
    plain_lower = plain_text.lower()

    # Find all phrase occurrences in plain text (case-insensitive)
    text_intervals = []  # intervals in plain_text coordinates
    for phrase in phrases:
        phrase_lower = phrase.lower()
        # Try full phrase first
        start = 0
        found_full = False
        while True:
            idx = plain_lower.find(phrase_lower, start)
            if idx == -1:
                break
            text_intervals.append((idx, idx + len(phrase_lower)))
            start = idx + 1
            found_full = True

        # If full phrase not found, try sub-phrases (for cross-line spanning)
        if not found_full:
            words = phrase_lower.split()
            if len(words) >= 5:
                for n in range(len(words) - 1, 3, -1):
                    prefix = ' '.join(words[:n])
                    idx = plain_lower.find(prefix)
                    if idx != -1:
                        text_intervals.append((idx, idx + len(prefix)))
                        break
                    suffix = ' '.join(words[len(words)-n:])
                    idx = plain_lower.find(suffix)
                    if idx != -1:
                        text_intervals.append((idx, idx + len(suffix)))
                        break

    if not text_intervals:
        return line_text

    # Merge overlapping intervals (in text coordinates)
    text_intervals.sort()
    merged = [text_intervals[0]]
    for s, e in text_intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    # Map text intervals back to HTML positions
    html_intervals = []
    for ts, te in merged:
        hs = text_to_html[ts]
        he = text_to_html[te]
        html_intervals.append((hs, he))

    # Build result with spans around matched portions in original HTML.
    # We must respect existing span boundaries: if our highlight range starts
    # or ends inside an existing <span>, we wrap only the visible-text portions
    # by closing/reopening the highlight span at each tag boundary.
    def _wrap_respecting_tags(html_fragment, cls):
        """Wrap visible text in <span class=cls>, closing and reopening
        around any existing HTML tags so nesting stays valid.
        Continuation fragments (after the first) get an extra 'gloss-cont'
        class so CSS can suppress duplicate markers."""
        parts = []
        inside_highlight = False
        opened_count = 0      # how many times we've opened a highlight span
        i = 0
        while i < len(html_fragment):
            if html_fragment[i] == '<':
                # We hit a tag — close highlight before tag, emit tag
                end_tag = html_fragment.find('>', i)
                if end_tag == -1:
                    break
                tag = html_fragment[i:end_tag + 1]
                if inside_highlight:
                    parts.append('</span>')
                    inside_highlight = False
                parts.append(tag)
                i = end_tag + 1
            else:
                # Visible text — make sure we're inside highlight
                if not inside_highlight:
                    opened_count += 1
                    if opened_count > 1 and 'gloss' in cls:
                        parts.append(f'<span class="{cls} gloss-cont">')
                    else:
                        parts.append(f'<span class="{cls}">')
                    inside_highlight = True
                parts.append(html_fragment[i])
                i += 1
        if inside_highlight:
            parts.append('</span>')
        return ''.join(parts)

    result = []
    pos = 0
    for hs, he in html_intervals:
        if pos < hs:
            result.append(line_text[pos:hs])
        result.append(_wrap_respecting_tags(line_text[hs:he], css_class))
        pos = he
    if pos < len(line_text):
        result.append(line_text[pos:])
    return ''.join(result)

# ============================================================================
# HTML GENERATION — outputs standalone book fragments
# ============================================================================

def find_deep_structure_verses(parry_verse_map):
    """Identify verses belonging to structures that go deeper than E.

    Groups labeled verses into structures (separated by gaps of unlabeled verses
    or label resets back to A). If any structure contains an uppercase label
    beyond E (i.e. F-K), ALL verses in that structure are marked as "deep"
    and their uppercase labels should be hidden entirely.

    Returns a set of verse numbers whose uppercase labels should be suppressed.
    """
    MAX_LABEL = 4  # E = ord('E') - ord('A')

    if not parry_verse_map:
        return set()

    # Collect (verse_num, max_uppercase_letter_pos) for labeled verses
    labeled_verses = []
    for vnum in sorted(parry_verse_map.keys()):
        entry = parry_verse_map[vnum]
        uppercase_labels = []
        for line in entry.get('lines', []):
            lbl = line.get('label', '')
            if lbl and lbl[0].isupper():
                pos = ord(lbl.rstrip("'")[0]) - ord('A')
                uppercase_labels.append(pos)
        if uppercase_labels:
            labeled_verses.append((vnum, max(uppercase_labels)))

    if not labeled_verses:
        return set()

    # Group into structures: a new structure starts when we see A (pos=0)
    # after a gap or after seeing the sequence descend back to A.
    structures = []  # list of [(vnum, max_pos), ...]
    current_group = [labeled_verses[0]]

    for i in range(1, len(labeled_verses)):
        vnum, max_pos = labeled_verses[i]
        prev_vnum, prev_max = labeled_verses[i - 1]

        # Heuristic: new structure if label resets to A after gap of 2+ unlabeled verses
        # or if we see A again after the structure has already descended back to A
        gap = vnum - prev_vnum
        has_A = max_pos == 0

        # Check if current group already contains the full mirror (went up and came back)
        group_positions = [p for _, p in current_group]
        peaked = len(group_positions) > 2 and group_positions[-1] <= 1

        if has_A and (gap > 2 or peaked):
            structures.append(current_group)
            current_group = [(vnum, max_pos)]
        else:
            current_group.append((vnum, max_pos))

    structures.append(current_group)

    # Mark all verses in deep structures
    deep_verses = set()
    for group in structures:
        max_depth = max(p for _, p in group)
        if max_depth > MAX_LABEL:
            for vnum, _ in group:
                deep_verses.add(vnum)

    return deep_verses


def _fix_double_that(lines):
    """Fix AICTP double-that: when 'it came to pass that [X], / that [Y]',
    the AICTP swap consumes the first 'that' but leaves the second orphaned.
    Pre-process: if line[i] contains 'it came to pass that' and ends with comma,
    and line[i+1] starts with 'that ', remove that second 'that' so the swap
    produces clean grammar ('And then [X], [Y]' instead of 'And then [X], that [Y]')."""
    result = list(lines)
    for i in range(len(result) - 1):
        if 'it came to pass that' in result[i].lower() and result[i].rstrip().endswith(','):
            nxt = result[i + 1]
            if nxt.startswith('that ') or nxt.startswith('That '):
                # Remove the leading "that " — capitalize next word if "That" was capitalized
                rest = nxt[5:]  # skip "that "
                result[i + 1] = rest
    return result


def gen_verse(verse, swap_list, book_id=None, parallel_map=None, parry_lines=None, deep_structure_verses=None):
    ref = verse['ref']
    fixed_lines = _fix_double_that(verse['lines'])
    processed = [process_line(l, swap_list) for l in fixed_lines]

    # Check for intertext references on this verse
    entries = get_intertext(book_id, verse['chapter'], verse['verse']) if book_id else []

    # Compute phrase/allusion data once — used across all three text layers
    quote_phrases = []
    allusion_phrases = []
    sources = ''
    if entries:
        has_quotation = any(e['type'] == 'quotation' for e in entries)
        sources = '; '.join(shorten_bible_ref(e['bible_ref']) for e in entries)

        # Look up phrase-level matches (now includes both quotations and allusions)
        phrase_data = get_phrase_matches(book_id, verse['chapter'], verse['verse'])
        matches = phrase_data.get('matches', []) if phrase_data else []

        # Separate matches by type
        quote_phrases = [m['text'] for m in matches if m.get('type') == 'quotation']
        allusion_phrases = [m['text'] for m in matches if m.get('type') == 'allusion']
        has_any_phrases = bool(quote_phrases or allusion_phrases)

        # Apply highlighting to sense-lines
        wrapped = []
        for i, line in enumerate(processed):
            highlighted = line
            if quote_phrases:
                highlighted = apply_phrase_highlights(highlighted, quote_phrases, 'quote-bible')
            if allusion_phrases:
                highlighted = apply_phrase_highlights(highlighted, allusion_phrases, 'quote-allusion')
            # Add data-source only on the last line
            if i == len(processed) - 1:
                wrapped.append(f'<span data-source="{sources}">{highlighted}</span>')
            else:
                wrapped.append(highlighted)
        processed = wrapped

    # Check for contextual glosses (Isaiah/Malachi inline annotations)
    gloss_entries = get_glosses(book_id, verse['chapter'], verse['verse']) if book_id else []
    if gloss_entries:
        processed = apply_gloss_highlights_multiline(processed, gloss_entries)

    # Check for KJV diff data (parallel passage visualization)
    diff_data = get_kjv_diff(book_id, verse['chapter'], verse['verse']) if book_id else None
    has_diff = diff_data is not None  # Mark ALL verses with KJV parallel data, even identical ones

    # ── Paragraph layer (v0 text) ──
    v0 = load_v0_paragraphs(book_id) if book_id else {}
    para_text = v0.get((verse['chapter'], verse['verse']), '')
    para_html = ''
    if para_text:
        # Fix double-that in paragraph text too
        para_text = re.sub(
            r'(it came to pass that\b[^,]+,)\s+that ',
            r'\1 ',
            para_text,
            flags=re.IGNORECASE
        )
        para_html = process_line(para_text, swap_list)
        # Apply allusion/quotation highlighting to paragraph layer too
        if quote_phrases:
            para_html = apply_phrase_highlights(para_html, quote_phrases, 'quote-bible')
        if allusion_phrases:
            para_html = apply_phrase_highlights(para_html, allusion_phrases, 'quote-allusion')
        # Apply contextual glosses to paragraph layer
        if gloss_entries:
            para_html = apply_gloss_highlights(para_html, gloss_entries)
        if sources:
            para_html = f'<span data-source="{sources}">{para_html}</span>'

    # Helper to build parallel attributes for a line
    def _par_attrs(line_idx):
        if not parallel_map:
            return ''
        key = (verse['verse'], line_idx)
        if key in parallel_map:
            gid, lvl = parallel_map[key]
            return f' data-parallel-group="{gid}" data-parallel-level="{lvl}"'
        return ''

    div_class = 'verse has-kjv-diff' if has_diff else 'verse'
    parts = [f'<div class="{div_class}"><span class="verse-num">{ref}</span>']

    # Paragraph span (base layer — visible by default)
    if para_html:
        parts.append(f'  <span class="line-para">{para_html}</span>')

    # Sense-line spans (hidden by default, shown when "Lines" is active)
    for idx, line in enumerate(processed):
        pa = _par_attrs(idx)
        cls = 'line verse-normal' if has_diff else 'line'
        parts.append(f'  <span class="{cls}"{pa}>{line}</span>')

    # KJV diff annotation (appears after sense-lines when diff layer is on)
    if has_diff:
        diff_html = render_kjv_diff(diff_data)
        parts.append(f'  <span class="line verse-diff">{diff_html}</span>')

    # Poetic / Hebrew Poetry layer (third text mode — hidden by default)
    # parry_lines is a v2 entry: {"v": N, "lines": [{label, text}], "types": [...]}
    #
    # Indent rules:
    #   If this verse belongs to a deep structure (one that goes beyond E),
    #   ALL uppercase labels in that structure are hidden. Only lowercase
    #   sub-structures (a-b, a-b-c) are shown within deep structures.
    #
    #   For non-deep structures:
    #   Uppercase A-E: indent = letter position (A=0, B=1, C=2, D=3, E=4)
    #   Lowercase a-z: indent = last_uppercase_indent + letter_pos + 1
    #   Unlabeled continuation lines: indent 0
    MAX_INDENT = 4  # E
    verse_num = verse.get('verse', 0)
    in_deep_structure = deep_structure_verses and verse_num in deep_structure_verses
    if parry_lines:
        plines = parry_lines.get('lines', [])
        ptypes = parry_lines.get('types', [])
        # Fix double-that in Parry lines
        parry_raw_texts = [pl.get('text', '') for pl in plines]
        parry_raw_texts = _fix_double_that(parry_raw_texts)
        # Also fix single-line Parry entries where the whole verse is one string
        parry_raw_texts = [
            re.sub(r'(it came to pass that\b[^,]+,)\s+that ', r'\1 ', t, flags=re.IGNORECASE)
            for t in parry_raw_texts
        ]
        last_upper_indent = 0
        parry_metadata = []   # (label_html, indent) per Parry line
        parry_texts = []      # processed HTML text per Parry line
        for pl_idx, pl in enumerate(plines):
            raw_label = pl.get('label', '')
            text = parry_raw_texts[pl_idx]

            if raw_label:
                base_char = raw_label.rstrip("'")[0] if raw_label.rstrip("'") else ''
                letter_pos = ord(base_char.upper()) - ord('A') if base_char.isalpha() else 0

                if base_char.isupper() and in_deep_structure:
                    # Verse belongs to a deep structure — hide ALL uppercase labels
                    label_html = '<span class="parry-label-spacer"></span>'
                    indent = 0
                elif base_char.isupper() and letter_pos > MAX_INDENT:
                    # Standalone deep label outside detected structure — hide
                    label_html = '<span class="parry-label-spacer"></span>'
                    indent = 0
                    last_upper_indent = MAX_INDENT
                elif base_char.isupper():
                    indent = letter_pos
                    last_upper_indent = indent
                    label_html = f'<span class="parry-label">{raw_label}</span>'
                else:
                    # Lowercase sub-structure: always shown
                    indent = min(last_upper_indent + letter_pos + 1, MAX_INDENT)
                    label_html = f'<span class="parry-label">{raw_label}</span>'
            else:
                label_html = '<span class="parry-label-spacer"></span>'
                indent = 0

            # Apply swap processing so the Aid layer works in Poetic mode
            processed_text = process_line(text, swap_list)
            # Apply allusion/quotation highlighting to Poetic layer too
            if quote_phrases:
                processed_text = apply_phrase_highlights(processed_text, quote_phrases, 'quote-bible')
            if allusion_phrases:
                processed_text = apply_phrase_highlights(processed_text, allusion_phrases, 'quote-allusion')
            parry_metadata.append((label_html, indent))
            parry_texts.append(processed_text)

        # Apply contextual glosses across all Parry lines at once
        # (handles phrases that span multiple lines)
        if gloss_entries:
            parry_texts = apply_gloss_highlights_multiline(parry_texts, gloss_entries)

        # Wrap each Parry line in its span
        for pl_idx, (processed_text, (label_html, indent)) in enumerate(zip(parry_texts, parry_metadata)):
            # Add data-source on the last Parry line for reference tooltip
            if sources and pl_idx == len(plines) - 1:
                processed_text = f'<span data-source="{sources}">{processed_text}</span>'
            parts.append(f'  <span class="line-parry parry-indent-{indent}">{label_html}{processed_text}</span>')
        # Type annotations (chiasmus, simple alternate, etc.) are no longer
        # rendered visibly — they are metadata only, not displayed to the reader.
    else:
        # Fallback: show paragraph text when no Parry data exists
        if para_html:
            parts.append(f'  <span class="line-parry">{para_html}</span>')

    parts.append('</div>')
    return '\n'.join(parts)

def build_parallel_map(bid, ch_num, ch_verses):
    """Build a map: (verse_num, line_index) -> (group_id, level) for parallel highlighting.

    Matches Parry's text fragments against the raw source lines using word-based scoring.
    Returns dict like {(3, 2): ('p1', 'A'), (3, 3): ('p1', 'B'), ...}

    Quality filters:
    - Skip structures with >10 Parry lines (too sprawling for our sense-line granularity)
    - Skip structures using levels deeper than C (D, E, F... too fine-grained)
    - Stop-words excluded from match scoring (common function words don't count)
    - Structures where <60% of lines match are dropped entirely (too noisy)
    - When multiple Parry lines match the same sense-line, uses the shallowest (A>B>C) level
    - Orphan labels (single label in a verse) are pruned
    - After pruning, skip if matched lines don't show both halves of the pattern (need A and B minimum)
    - First label in reading order must be A (not B, C, or prime variants)
    - No gap of >3 unlabeled lines between adjacent matches within a verse
    """
    structures = get_parallel_structures(bid, ch_num)
    if not structures:
        return {}

    MAX_LINES = 10       # structures larger than this are too sprawling
    MAX_DEPTH = 'C'      # don't display levels deeper than C (D, E, F are too fine-grained)
    MAX_GAP = 3          # max unlabeled lines between adjacent matches in same verse

    # Function words excluded from match scoring — too common to be distinctive
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'of', 'in', 'to', 'for',
        'is', 'it', 'that', 'which', 'with', 'he', 'his', 'him', 'she',
        'her', 'they', 'them', 'their', 'we', 'our', 'us', 'i', 'my',
        'me', 'ye', 'you', 'your', 'unto', 'by', 'as', 'on', 'at',
        'from', 'be', 'was', 'were', 'are', 'been', 'had', 'have', 'has',
        'did', 'do', 'not', 'no', 'this', 'these', 'those',
    }

    # Build a lookup: verse_num -> [(line_index, raw_text), ...]
    verse_lines = {}
    for v in ch_verses:
        vn = v['verse']
        verse_lines[vn] = [(i, line.strip().lower()) for i, line in enumerate(v['lines'])]

    result = {}
    for si, struct in enumerate(structures):
        # Pre-filter: skip structures that are too large or too deep
        if len(struct['lines']) > MAX_LINES:
            continue
        # Check max depth used in structure
        deepest = max((line['level'].rstrip("'") for line in struct['lines']), default='A')
        if deepest > MAX_DEPTH:
            continue

        group_id = f'p{ch_num}-{si}'
        # Track which sense-lines have been consumed within each verse for this structure,
        # so repeated text (e.g., "and he suffereth it" x3) matches sequentially
        consumed_per_verse = {}  # verse_num -> set of line indices already taken

        # First pass: match all lines and collect candidates
        struct_matches = {}  # key -> (group_id, level)
        total_lines = len(struct['lines'])
        matched_count = 0

        for pline in struct['lines']:
            verse_num = pline['verse']
            level = pline['level']
            frag = pline['text_fragment'].strip().lower()
            # Remove Parry markup artifacts
            frag = re.sub(r'^[a-k]\t', '', frag)

            if verse_num not in verse_lines:
                continue

            consumed = consumed_per_verse.setdefault(verse_num, set())

            # Extract first N significant words from fragment for matching
            # Filter out stop-words — they're too common to be useful for matching
            all_frag_words = re.findall(r'[a-z]+', frag)
            frag_content_words = [w for w in all_frag_words if w not in STOP_WORDS][:6]
            frag_first_word = all_frag_words[0] if all_frag_words else ''
            if not frag_content_words:
                continue

            # Find the best matching line NOT YET consumed
            best_match = -1
            best_score = 0

            for li, raw in verse_lines[verse_num]:
                if li in consumed:
                    continue  # Skip already-matched lines
                raw_words = re.findall(r'[a-z]+', raw)
                if not raw_words:
                    continue
                # Count how many content words from fragment appear in this line
                score = sum(1 for w in frag_content_words if w in raw_words)
                # Bonus for matching the first word (even if it's a stop-word)
                if frag_first_word and frag_first_word == raw_words[0]:
                    score += 2
                if score > best_score:
                    best_score = score
                    best_match = li

            # Require a strong match: at least 3 content-word hits, or 50% of content words
            if best_match >= 0 and best_score >= max(3, len(frag_content_words) * 0.5):
                consumed.add(best_match)
                matched_count += 1
                key = (verse_num, best_match)
                # When multiple Parry lines hit the same sense-line, keep the shallowest level
                if key in struct_matches:
                    existing_level = struct_matches[key][1]
                    # Shallowest = closest to 'A' (strip prime for comparison)
                    if level.rstrip("'") < existing_level.rstrip("'"):
                        struct_matches[key] = (group_id, level)
                else:
                    struct_matches[key] = (group_id, level)

        # Quality gate: drop structures where less than 60% of lines matched
        if total_lines > 0 and matched_count / total_lines < 0.6:
            continue

        # Contiguity gate: matched lines should form a coherent block, not scattered orphans.
        # For structures with matches across multiple verses, require at least 2 matched lines
        # in any verse that has matches (drop verses with only 1 orphan label).
        if len(struct_matches) >= 3:
            from collections import Counter
            verse_match_counts = Counter(k[0] for k in struct_matches)
            # Remove orphan matches (single label in a verse with no neighbors)
            orphan_keys = [k for k in struct_matches if verse_match_counts[k[0]] < 2]
            for k in orphan_keys:
                del struct_matches[k]

        # After pruning orphans, need at least 2 lines to be useful
        if len(struct_matches) < 2:
            continue

        # Pattern completeness: must have at least A and B levels to show a real parallel
        remaining_levels = set(v[1].rstrip("'") for v in struct_matches.values())
        if 'A' not in remaining_levels or 'B' not in remaining_levels:
            continue

        # Gap check: the remaining levels should be consecutive (A,B or A,B,C — no A,C skipping B)
        sorted_levels = sorted(remaining_levels)
        has_gaps = False
        for i in range(1, len(sorted_levels)):
            if ord(sorted_levels[i]) - ord(sorted_levels[i-1]) > 1:
                has_gaps = True
                break
        if has_gaps:
            continue

        # Reading-order check: first label must be A (not B, C, or prime variants).
        # Without this, readers see a "b" or "c'" label with no preceding "a" — confusing.
        sorted_keys = sorted(struct_matches.keys())
        first_level = struct_matches[sorted_keys[0]][1]
        if first_level.rstrip("'") != 'A':
            continue

        # Gap-within-verse check: adjacent matched lines shouldn't be >MAX_GAP lines apart.
        # Large gaps make the parallel structure visually unclear.
        from collections import defaultdict
        verse_indices = defaultdict(list)
        for (vn, li) in sorted_keys:
            verse_indices[vn].append(li)
        gap_ok = True
        for vn, indices in verse_indices.items():
            indices.sort()
            for i in range(1, len(indices)):
                if indices[i] - indices[i-1] > MAX_GAP + 1:  # +1 because gap of 3 means 3 lines between
                    gap_ok = False
                    break
            if not gap_ok:
                break
        if not gap_ok:
            continue

        # Level-adjacency check: within each verse, consecutive matched lines should
        # have labels within 1 level of each other (A→B ok, A→C confusing).
        # This catches cases like A, C, B, C where sense-line merging garbles the order.
        level_order_ok = True
        for vn, indices in verse_indices.items():
            verse_keys_sorted = sorted((li, struct_matches[(vn, li)][1]) for li in indices)
            for i in range(1, len(verse_keys_sorted)):
                prev_base = ord(verse_keys_sorted[i-1][1].rstrip("'"))
                curr_base = ord(verse_keys_sorted[i][1].rstrip("'"))
                if abs(curr_base - prev_base) > 1:
                    level_order_ok = False
                    break
            if not level_order_ok:
                break
        if not level_order_ok:
            continue

        # Merge into result — all-or-nothing to avoid orphaned labels.
        # If ANY key in this structure conflicts with an existing assignment,
        # skip the entire structure rather than leaving partial/orphaned entries.
        conflicts = [k for k in struct_matches if k in result]
        if not conflicts:
            result.update(struct_matches)
        else:
            # Check if the non-conflicting subset still has A and B
            remaining = {k: v for k, v in struct_matches.items() if k not in result}
            rem_levels = set(v[1].rstrip("'") for v in remaining.values())
            if 'A' in rem_levels and 'B' in rem_levels and len(remaining) >= 2:
                # Verify first-label and level-adjacency for the subset
                rem_sorted = sorted(remaining.keys())
                if remaining[rem_sorted[0]][1].rstrip("'") == 'A':
                    result.update(remaining)
            # Otherwise: skip entirely — the overlapping structure won

    return result


def gen_chapter(bid, ch_num, ch_verses, total_chapters, swap_list):
    p = [f'<div id="ch-{bid}-{ch_num}" class="chapter-content" style="display:none;">']
    p.append(f'<div class="chapter-title">Chapter {ch_num}</div>')
    # Prev/Next nav at TOP
    p.append('<div class="chapter-nav">')
    if ch_num > 1:
        p.append(f'  <a href="#" onclick="showChapter(\'{bid}\', {ch_num-1}); return false;" class="chapter-nav-link">&larr; Ch {ch_num-1}</a>')
    else:
        p.append('  <span class="chapter-nav-disabled">&larr; Intro</span>')
    if ch_num < total_chapters:
        p.append(f'  <a href="#" onclick="showChapter(\'{bid}\', {ch_num+1}); return false;" class="chapter-nav-link">Ch {ch_num+1} &rarr;</a>')
    else:
        p.append('  <span class="chapter-nav-disabled">End</span>')
    p.append('</div>')

    # Build parallel structure map for this chapter
    par_map = build_parallel_map(bid, ch_num, ch_verses)

    # Build Parry per-verse map from v2 index (verse_num → entry with lines + types)
    parry_verse_map = get_parry_verses(bid, ch_num)
    deep_verset = find_deep_structure_verses(parry_verse_map)

    for v in ch_verses:
        # Check for pericope section header before this verse
        pericope_title = get_pericope(bid, v['chapter'], v['verse'])
        if pericope_title:
            p.append(format_pericope_header(pericope_title))
        p.append(gen_verse(v, swap_list, book_id=bid, parallel_map=par_map,
                           parry_lines=parry_verse_map.get(v['verse']),
                           deep_structure_verses=deep_verset))
        p.append('')
    p.append('</div>')
    return '\n'.join(p)

def build_book(bid, source_file, swap_list):
    """Build a single book HTML fragment from a sense-line source file."""
    print(f"\nProcessing {bid} from {source_file}...")
    verses = parse_verses(source_file)
    chapters = {}
    for v in verses:
        chapters.setdefault(v['chapter'], []).append(v)
    total = max(chapters.keys())
    print(f"  {len(verses)} verses, {total} chapters")

    # Generate book content div
    p = [f'<div id="book-{bid}" class="book-content">']
    for ch in range(1, total + 1):
        if ch in chapters:
            p.append(gen_chapter(bid, ch, chapters[ch], total, swap_list))
            p.append('')
    p.append(f'</div>')

    content = '\n'.join(p)

    # Stats
    sc = content.count('<span class="swap"')
    nest = len(re.findall(r'<span class="swap"[^>]*>[^<]*<span class="swap"', content))
    print(f"  Swaps: {sc}, Nested: {nest}")
    if nest > 0:
        print(f"  *** WARNING: {nest} NESTED SWAPS DETECTED ***", file=sys.stderr)

    return content, len(verses), total, sc, nest

# ============================================================================
# MAIN
# ============================================================================

def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(1)

    # Determine output directory
    out_dir = 'books'
    if '--out' in args:
        idx = args.index('--out')
        out_dir = args[idx + 1]
        args = args[:idx] + args[idx+2:]

    os.makedirs(out_dir, exist_ok=True)
    swap_list = build_swap_list()
    load_intertext()

    if args[0] == '--all':
        # Read booklist.txt for all book/file pairs
        listfile = args[1] if len(args) > 1 else 'booklist.txt'
        if not os.path.exists(listfile):
            print(f"ERROR: {listfile} not found. Create it with lines like:")
            print(f"  2nephi 02-2_nephi-stan-v1.txt")
            print(f"  jacob 03-jacob-2020-sb.txt")
            sys.exit(1)
        books = []
        with open(listfile) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split(None, 1)
                if len(parts) == 2:
                    books.append((parts[0], parts[1]))
        print(f"Building {len(books)} books from {listfile}...")
    else:
        # Single book mode: build_book.py BOOK_ID source.txt
        if len(args) < 2:
            print("Usage: python3 build_book.py BOOK_ID source.txt [--out books/]")
            sys.exit(1)
        books = [(args[0], args[1])]

    total_verses = 0
    total_swaps = 0
    results = []

    for bid, source_file in books:
        content, verses, chapters, swaps, nested = build_book(bid, source_file, swap_list)
        outpath = os.path.join(out_dir, f'{bid}.html')
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(content + '\n')
        print(f"  → {outpath} ({os.path.getsize(outpath):,} bytes)")
        total_verses += verses
        total_swaps += swaps
        results.append((bid, verses, chapters, swaps, nested))

    # Summary
    print(f"\n{'='*50}")
    print(f"{'BOOK':<20} {'VERSES':>7} {'CHAPTERS':>9} {'SWAPS':>7} {'NESTED':>7}")
    print(f"{'-'*50}")
    for bid, verses, chapters, swaps, nested in results:
        flag = ' ***' if nested > 0 else ''
        print(f"{bid:<20} {verses:>7} {chapters:>9} {swaps:>7} {nested:>7}{flag}")
    print(f"{'-'*50}")
    print(f"{'TOTAL':<20} {total_verses:>7} {'':>9} {total_swaps:>7}")
    print(f"\nOutput directory: {out_dir}/")

if __name__ == '__main__':
    main()
