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
    # ── wicked + abomination collision ──
    ("wicked abominations", "wicked practices"),
    ("wicked abomination", "wicked practice"),
    ("hither and thither", "this way and that"),
    ("an account", "a record"), ("in fine", "in other words"), ("lust after", "desire"),
    ("save two churches only", "only two churches"), ("save a few only", "only a few"),
    ("save it were", "except"), ("save it be", "unless"), ("save that", "except that"),
    ("Thou mightest", "You might"), ("thou mightest", "you might"),
    ("Thou knowest", "You know"), ("thou knowest", "you know"),
    ("Thou shalt", "You shall"), ("thou shalt", "you shall"),
    ("Thou hast", "You have"), ("thou hast", "you have"),
    ("Thou wilt", "You will"), ("thou wilt", "you will"),
    ("Thou dost", "You do"), ("thou dost", "you do"),
    ("Thou art", "You are"), ("thou art", "you are"),
    ("wilt thou", "will you"), ("Wilt thou", "Will you"),
    ("art thou", "are you"), ("Art thou", "Are you"),
    ("did murmur", "complained"), ("did exhort", "urged"),
    # confound — "silenced" for debate sense; base form gets "confuse" for language sense
    ("did confound", "silenced"),
    ("confound the language", "confuse the language"),
    ("not confound us", "not confuse us"),
    ("did engraven", "engraved"),
    ("did slay", "killed"), ("did smite", "struck"),
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
    # ── Pronoun collision: "unto thee ye" → "to you, you" (insert comma) ──
    ("unto thee ye", "to you, you"),
    ("about my loins", "about my waist"),
    ("about his loins", "about his waist"),
    ("about their loins", "about their waist"),
    ("about her loins", "about her waist"),
    ("of his loins", "of his waist"),
    ("of their loins", "of their waist"),
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
    'seth', 'beth', 'nazareth', 'shibboleth', 'japheth', 'Kenneth',
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

    for i, (archaic, modern) in enumerate(swap_list):
        sentinel = f"\x00{i}\x00"
        # AICTP patterns: literal match, not word-boundary
        # Match the formula followed by space or end-of-line, preserve spacing
        if 'it came to pass' in archaic:
            if archaic in result:
                result = result.replace(archaic, sentinel)
                placeholders.append((sentinel, archaic, modern))
            continue
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
            # Only match the archaic interjection form: "go to," or "go to;"
            result = re.sub(r'\bgo to(?=[,;])', sentinel, result)
            placeholders.append((sentinel, archaic, modern)); continue
        # notwithstanding: context-sensitive — "despite" before NP, "even though" before clause
        if archaic.lower() == 'notwithstanding':
            cap = archaic[0].isupper()
            def _notw_replace(m):
                after = result[m.end():m.end()+20].lstrip()
                first_word = re.match(r'[a-zA-Z]+', after)
                fw = first_word.group(0).lower() if first_word else ''
                # Before noun phrases → "despite"
                if fw in ('the','their','all','our','my','his','her','its','a','an',
                          'these','this','that','those','such','every','much','many'):
                    mod = 'Despite' if cap else 'despite'
                # Before clause (pronoun + verb) → "even though"
                elif fw in ('they','we','he','she','i','it','so','there','being'):
                    mod = 'Even though' if cap else 'even though'
                # Standalone / end of phrase → "nevertheless"
                else:
                    mod = 'Nevertheless' if cap else 'nevertheless'
                idx = len(placeholders); sent = f"\x00{len(placeholders)+1000}\x00"
                placeholders.append((sent, archaic, mod)); return sent
            result = re.sub(r'\b' + re.escape(archaic) + r'\b', _notw_replace, result)
            continue
        result = re.sub(r'\b' + re.escape(archaic) + r'\b', sentinel, result)
        placeholders.append((sentinel, archaic, modern))

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

    # Words that follow "did" but are NOT verbs — skip these
    DID_SKIP = {'my', 'his', 'her', 'their', 'our', 'your', 'its', 'the', 'a', 'an',
                'not', 'also', 'all', 'both', 'even', 'never', 'once', 'then', 'thus',
                'i', 'it', 'they', 'she', 'he', 'we', 'so', 'as', 'again', 'frankly',
                'still', 'do', 'molten', 'this', 'that', 'these', 'those',
                'now', 'throughout', 'there', 'here', 'much', 'more'}

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

    def thou_est_replace(m):
        full, ve = m.group(0), m.group(1)
        base = ve[:-3] if ve.endswith('est') else (ve[:-2] if ve.endswith('st') else None)
        if not base: return full
        idx = len(placeholders); sent = f"\x00T{idx}\x00"
        placeholders.append((sent, full, ("You " if full[0]=='T' else "you ") + base)); return sent
    result = re.sub(r'\b[Tt]hou (\w+est)\b', lambda m: thou_est_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    for sentinel, archaic, modern in placeholders:
        result = result.replace(sentinel, f'<span class="swap" data-orig="{archaic}" data-mod="{modern}">{archaic}</span>')
    return result

def fix_participles(text):
    """Fix past tense → past participle after have/has/had auxiliaries."""
    PARTICIPLE_MAP = [
        ('saw', 'seen'), ('spoke', 'spoken'), ('broke', 'broken'),
        ('gave', 'given'), ('took', 'taken'), ('wrote', 'written'),
        ('drove', 'driven'), ('chose', 'chosen'), ('rose', 'risen'),
        ('fell', 'fallen'), ('grew', 'grown'), ('knew', 'known'),
        ('threw', 'thrown'), ('drew', 'drawn'), ('swore', 'sworn'),
        ('tore', 'torn'), ('wore', 'worn'), ('froze', 'frozen'),
        ('stole', 'stolen'), ('shrank', 'shrunk'), ('drank', 'drunk'),
        ('began', 'begun'), ('sang', 'sung'), ('ran', 'run'),
        ('went', 'gone'),
    ]
    for wrong, right in PARTICIPLE_MAP:
        # Match have/has/had within a clause window (no ; or . between)
        # Window of 50 chars to catch adverbs like "never", "also", "not yet"
        for aux in ('had', 'have', 'has'):
            text = re.sub(
                r'(\b' + aux + r'\b[^;.]{0,50}?)data-mod="' + re.escape(wrong) + '"',
                r'\1data-mod="' + right + '"', text)
    return text

def fix_articles(text):
    """Fix 'an' → 'a' before consonant sounds introduced by swaps (e.g. 'an very')."""
    # Match: an <span...data-mod="[consonant-starting]"...>
    def _fix_an(m):
        return 'a' + m.group(0)[2:]  # replace 'an' with 'a'
    text = re.sub(r'\ban\s+(<span class="swap"[^>]*data-mod="[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ])', _fix_an, text)
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

V0_DIR = Path(__file__).resolve().parent / 'text-files' / 'v0-bofm-original'

# Map book display names → v0 filenames
V0_FILE_MAP = {
    '1 Nephi': '1_Nephi.txt', '2 Nephi': '2_Nephi.txt',
    '3 Nephi': '3_Nephi.txt', '4 Nephi': '4_Nephi.txt',
    'Jacob': 'Jacob.txt', 'Enos': 'Enos.txt', 'Jarom': 'Jarom.txt',
    'Omni': 'Omni.txt', 'Words of Mormon': 'Words_of_Mormon.txt',
    'Mosiah': 'Mosiah.txt', 'Alma': 'Alma.txt', 'Helaman': 'Helaman.txt',
    'Mormon': 'Mormon.txt', 'Ether': 'Ether.txt', 'Moroni': 'Moroni.txt',
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
_GEO_INDEX = None         # populated by load_intertext()
_PERICOPE_INDEX = None    # populated by load_intertext()

def load_intertext():
    """Load the enriched Hardy intertext index, phrase index, KJV diff, and geo index."""
    global _INTERTEXT_INDEX, _PHRASE_INDEX, _KJV_DIFF_INDEX, _GEO_INDEX, _PERICOPE_INDEX
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
    geo_path = os.path.join(base, 'data', 'geo_index.json')
    if os.path.exists(geo_path):
        with open(geo_path) as f:
            _GEO_INDEX = json.load(f)
        total = sum(len(vs) for ch in _GEO_INDEX.values() for vs in ch.values() for vs in vs.values())
        print(f"Loaded geo index: {total} verse-category entries for geography layer")
    else:
        print(f"  No geo index at {geo_path}, skipping geography layer")
        _GEO_INDEX = {}
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

    # Extract parenthetical scripture reference if present
    ref_match = re.search(r'\s*\(([^)]*(?:Isaiah|Malachi|Genesis|Exodus|Psalm)[^)]*)\)\s*$', title)
    ref_html = ''
    if ref_match:
        ref_text = ref_match.group(1)
        ref_html = f'<span class="pericope-ref">{ref_text}</span>'
        title = title[:ref_match.start()]

    # Split on colon for two-tier display (but not if colon is inside quotes)
    if ': ' in title and "'" not in title.split(': ')[0][-5:]:
        parts = title.split(': ', 1)
        main_title = parts[0].strip()
        subtitle = parts[1].strip()
        inner = f'<span class="pericope-main">{main_title}</span>'
        inner += f'<span class="pericope-sub">{subtitle}</span>'
        if ref_html:
            inner += ref_html
        return f'<div class="pericope-header pericope-two-tier">{inner}</div>'
    else:
        # Single-tier: no colon split
        inner = f'<span class="pericope-main">{title}</span>'
        if ref_html:
            inner += ref_html
            # Use pericope-with-ref class so ref gets its own line via flex
            return f'<div class="pericope-header pericope-with-ref">{inner}</div>'
        return f'<div class="pericope-header">{inner}</div>'

def get_intertext(book_id, chapter, verse):
    """Return list of intertext entries for a given verse, or empty list."""
    if not _INTERTEXT_INDEX:
        return []
    return _INTERTEXT_INDEX.get(book_id, {}).get(str(chapter), {}).get(str(verse), [])

def get_geo_entries(book_id, chapter, verse):
    """Return list of geography entries for a given verse, or empty list."""
    if not _GEO_INDEX:
        return []
    return _GEO_INDEX.get(book_id, {}).get(str(chapter), {}).get(str(verse), [])

def _is_geo_fragment(frag, category):
    """Check if a fragment contains geographically meaningful content.

    Short fragments from ellipsis splitting often capture just names
    (e.g. 'king Lamoni', 'Ammon') or bare directional phrases
    (e.g. 'on the west') rather than actual geographic data.
    """
    # Generic fragments that are just compass directions, not real geo data
    GENERIC_BLOCKLIST = {
        'on the west', 'on the east', 'on the north', 'on the south',
        'on the east and on the west', 'on the north and on the south',
        'the lamanites', 'ammon', 'no wait', 'he being determined',
        'a considerable number', 'those who were in favor of kings',
    }
    frag_lower = frag.lower().strip()
    if frag_lower in GENERIC_BLOCKLIST:
        return False

    GEO_KEYWORDS = {
        'sea', 'river', 'land', 'wilderness', 'mountain', 'hill', 'valley',
        'north', 'south', 'east', 'west', 'border', 'borders', 'bordering',
        'city', 'village', 'narrow', 'strip', 'desolation', 'bountiful',
        'journey', 'distance', 'day', 'days', 'mile',
        'water', 'waters', 'flood', 'deep', 'shore', 'seashore',
        'forest', 'tree', 'trees', 'timber', 'grain', 'fruit',
        'horse', 'horses', 'chariot', 'chariots', 'flock', 'flocks',
        'cattle', 'goat', 'elephant', 'serpent', 'bee', 'beast',
        'heat', 'cold', 'rain', 'drought', 'snow', 'storm',
        'tent', 'tents', 'dwell', 'possess', 'inheritance', 'inhabit',
        'place', 'plain', 'plains', 'tower', 'wall', 'gate',
    }
    # Long fragments (25+ chars) are likely meaningful enough
    if len(frag) >= 25:
        return True
    # Medium fragments (15-24 chars) need a geo keyword
    if len(frag) >= 15:
        words = set(re.sub(r'[^\w\s]', '', frag_lower).split())
        return bool(words & GEO_KEYWORDS)
    # Short fragments (<15 chars) must have a geo keyword AND a proper noun or
    # specific place name to be worth highlighting — otherwise too generic
    words = set(re.sub(r'[^\w\s]', '', frag_lower).split())
    if not (words & GEO_KEYWORDS):
        return False
    # "land of Nephi" (13 chars) is good; "on the west" (11 chars) is not
    # Require "land of", "city of", "sea", "river", "wilderness", "narrow" for short frags
    SPECIFIC_SHORT = {'land', 'city', 'sea', 'river', 'wilderness', 'narrow', 'valley', 'hill', 'mountain', 'seashore', 'forest'}
    return bool(words & SPECIFIC_SHORT)

def apply_geo_highlights(line_text, geo_entries):
    """Wrap geographic extract phrases within a line with <span class="geo-ref">.

    Each geo entry has an 'extract' field with the text to match, and a 'category'.
    We do case-insensitive substring matching and wrap with a span that includes
    the category as a data attribute.
    """
    if not geo_entries:
        return line_text

    intervals = []
    line_lower = line_text.lower()
    for entry in geo_entries:
        extract = entry.get('extract', '')
        if not extract or len(extract) < 5:
            continue
        cat = entry.get('category', '')
        # Split on ellipsis to get matchable fragments
        fragments = [f.strip() for f in extract.replace('…', '...').split('...') if f.strip() and len(f.strip()) >= 5]
        if not fragments:
            fragments = [extract]
        for frag in fragments:
            # Skip fragments that are just names/context, not geographic content
            if not _is_geo_fragment(frag, cat):
                continue
            frag_lower = frag.lower()
            idx = line_lower.find(frag_lower)
            if idx != -1:
                intervals.append((idx, idx + len(frag), cat))

    if not intervals:
        return line_text

    # Sort by start position; handle overlaps by taking longest
    intervals.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    merged = []
    for s, e, cat in intervals:
        if merged and s < merged[-1][1]:
            # Overlapping — keep the longer one
            if e - s > merged[-1][1] - merged[-1][0]:
                merged[-1] = (s, e, cat)
        else:
            merged.append((s, e, cat))

    result = []
    pos = 0
    for s, e, cat in merged:
        if pos < s:
            result.append(line_text[pos:s])
        result.append(f'<span class="geo-ref" data-geo-cat="{cat}">{line_text[s:e]}</span>')
        pos = e
    if pos < len(line_text):
        result.append(line_text[pos:])
    return ''.join(result)

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

def apply_phrase_highlights(line_text, phrases, css_class):
    """Wrap matched phrases within a line with <span class="css_class">.

    Uses case-insensitive matching to find phrase text within the line,
    then wraps matched portions. Non-matched portions are left unwrapped.
    Also matches partial phrases: if a multi-word phrase spans across line
    breaks, we check whether any 3+ word suffix or prefix falls on this line.
    Returns the line with spans inserted.
    """
    if not phrases:
        return line_text

    # Find all phrase occurrences in this line (case-insensitive)
    intervals = []
    line_lower = line_text.lower()
    for phrase in phrases:
        phrase_lower = phrase.lower()
        # Try full phrase first
        start = 0
        found_full = False
        while True:
            idx = line_lower.find(phrase_lower, start)
            if idx == -1:
                break
            intervals.append((idx, idx + len(phrase)))
            start = idx + 1
            found_full = True

        # If full phrase not found, try sub-phrases (for cross-line spanning)
        if not found_full:
            words = phrase_lower.split()
            if len(words) >= 5:
                # Try prefixes and suffixes of 4+ words (avoid short noisy fragments)
                for n in range(len(words) - 1, 3, -1):
                    # Try prefix (end of phrase on this line)
                    prefix = ' '.join(words[:n])
                    idx = line_lower.find(prefix)
                    if idx != -1:
                        intervals.append((idx, idx + len(prefix)))
                        break
                    # Try suffix (start of phrase on this line)
                    suffix = ' '.join(words[len(words)-n:])
                    idx = line_lower.find(suffix)
                    if idx != -1:
                        intervals.append((idx, idx + len(suffix)))
                        break

    if not intervals:
        return line_text

    # Merge overlapping intervals
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    # Build result with spans around matched portions
    result = []
    pos = 0
    for s, e in merged:
        if pos < s:
            result.append(line_text[pos:s])
        result.append(f'<span class="{css_class}">{line_text[s:e]}</span>')
        pos = e
    if pos < len(line_text):
        result.append(line_text[pos:])
    return ''.join(result)

# ============================================================================
# HTML GENERATION — outputs standalone book fragments
# ============================================================================

def gen_verse(verse, swap_list, book_id=None, parallel_map=None):
    ref = verse['ref']
    processed = [process_line(l, swap_list) for l in verse['lines']]

    # Check for intertext references on this verse
    entries = get_intertext(book_id, verse['chapter'], verse['verse']) if book_id else []

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

    # Check for geography entries on this verse
    geo_entries = get_geo_entries(book_id, verse['chapter'], verse['verse']) if book_id else []
    if geo_entries:
        # Build category annotation — show the most specific category
        # Priority order: more specific > less specific
        GEO_CAT_PRIORITY = {
            'terrain': 1, 'water': 2, 'settlement': 3, 'distance': 4,
            'flora': 5, 'fauna': 6, 'climate': 7, 'materials': 8,
            'demographics': 9, 'old world': 10, 'direction': 11, 'misc': 12,
        }
        geo_cats = list(dict.fromkeys(e.get('category', '') for e in geo_entries))
        geo_cats.sort(key=lambda c: GEO_CAT_PRIORITY.get(c, 99))
        geo_label = geo_cats[0] if geo_cats else ''
        geo_wrapped = []
        last_geo_line = -1
        for i, line in enumerate(processed):
            highlighted = apply_geo_highlights(line, geo_entries)
            geo_wrapped.append(highlighted)
            if 'geo-ref' in highlighted:
                last_geo_line = i
        # Only add category label if at least one fragment was actually highlighted
        if last_geo_line >= 0:
            geo_wrapped[last_geo_line] = f'<span data-geo="{geo_label}">{geo_wrapped[last_geo_line]}</span>'
        processed = geo_wrapped

    # Check for KJV diff data (parallel passage visualization)
    diff_data = get_kjv_diff(book_id, verse['chapter'], verse['verse']) if book_id else None
    has_diff = diff_data is not None  # Mark ALL verses with KJV parallel data, even identical ones

    # ── Paragraph layer (v0 text) ──
    v0 = load_v0_paragraphs(book_id) if book_id else {}
    para_text = v0.get((verse['chapter'], verse['verse']), '')
    para_html = ''
    if para_text:
        para_html = process_line(para_text, swap_list)

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

    for v in ch_verses:
        # Check for pericope section header before this verse
        pericope_title = get_pericope(bid, v['chapter'], v['verse'])
        if pericope_title:
            p.append(format_pericope_header(pericope_title))
        p.append(gen_verse(v, swap_list, book_id=bid, parallel_map=par_map))
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
