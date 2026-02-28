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

import re, sys, os

# ============================================================================
# SWAP LEXICON — Single source of truth for all archaic word modernization
# ============================================================================

COMPOUND_SWAPS = [
    ("none other object save it be", "no other purpose except"),
    ("inasmuch as", "to the degree that"), ("Inasmuch as", "To the degree that"),
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
    ("did confound", "silenced"), ("did engraven", "engraved"),
    ("did slay", "killed"), ("did smite", "struck"),
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
    ("confounded", "put to shame"), ("Confounded", "Put to shame"),
    ("constrained", "compelled"), ("Constrained", "Compelled"),
    ("nevertheless", "but"), ("Nevertheless", "But"),
    ("concourses", "crowds"), ("Concourses", "Crowds"),
    ("account", "record"), ("Account", "Record"),
    ("naught", "nothing"), ("Naught", "Nothing"),
    ("surety", "certainty"), ("Surety", "Certainty"),
    ("firmament", "sky"), ("Firmament", "Sky"),
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
    ("durst", "dared"), ("Durst", "Dared"),
    ("bade", "told"), ("Bade", "Told"),
    ("doth", "does"), ("Doth", "Does"),
    ("whit", "bit"), ("Whit", "Bit"),
    ("wo", "woe"), ("Wo", "Woe"),
    ("lest", "for fear that"), ("Lest", "For fear that"),
    ("yea", "yes"), ("Yea", "Indeed"),
    ("meet", "fitting"), ("Meet", "Fitting"),
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
    s = list(COMPOUND_SWAPS) + list(SIMPLE_SWAPS)
    s.sort(key=lambda x: len(x[0]), reverse=True)
    return s

def apply_swaps(text, swap_list):
    placeholders = []
    result = text
    for i, (archaic, modern) in enumerate(swap_list):
        sentinel = f"\x00{i}\x00"
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
        idx = len(placeholders); sent = f"\x00{idx}\x00"
        placeholders.append((sent, word, mf)); return sent
    result = re.sub(r'\b[a-z]+eth\b', lambda m: eth_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    # Words that follow "did" but are NOT verbs — skip these
    DID_SKIP = {'my', 'his', 'her', 'their', 'our', 'your', 'its', 'the', 'a', 'an',
                'not', 'also', 'all', 'both', 'even', 'never', 'once', 'then', 'thus',
                'it', 'they', 'she', 'he', 'we', 'so', 'as', 'again', 'frankly',
                'still', 'do', 'molten', 'this', 'that', 'these', 'those'}

    def did_verb_replace(m):
        full, verb = m.group(0), m.group(1)
        if verb.lower() in DID_SKIP:
            return full  # not a verb, leave as-is
        if verb in IRREGULAR_PAST: past = IRREGULAR_PAST[verb]
        elif verb.endswith('e'): past = verb + 'd'
        elif verb.endswith('y') and len(verb)>1 and verb[-2] not in 'aeiou': past = verb[:-1] + 'ied'
        else: past = verb + 'ed'
        idx = len(placeholders); sent = f"\x00{idx}\x00"
        placeholders.append((sent, full, past)); return sent
    result = re.sub(r'\bdid (\w+)\b', lambda m: did_verb_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    def thou_est_replace(m):
        full, ve = m.group(0), m.group(1)
        base = ve[:-3] if ve.endswith('est') else (ve[:-2] if ve.endswith('st') else None)
        if not base: return full
        idx = len(placeholders); sent = f"\x00{idx}\x00"
        placeholders.append((sent, full, ("You " if full[0]=='T' else "you ") + base)); return sent
    result = re.sub(r'\b[Tt]hou (\w+est)\b', lambda m: thou_est_replace(m) if '\x00' not in m.group(0) else m.group(0), result)

    for sentinel, archaic, modern in placeholders:
        result = result.replace(sentinel, f'<span class="swap" data-orig="{archaic}" data-mod="{modern}">{archaic}</span>')
    return result

def fix_participles(text):
    for wrong, right in [('saw','seen'),('spoke','spoken'),('broke','broken')]:
        text = re.sub(r'(\bhad\b.{0,60}?)data-mod="'+re.escape(wrong)+'"', r'\1data-mod="'+right+'"', text)
        text = re.sub(r'(\bhave\b.{0,60}?)data-mod="'+re.escape(wrong)+'"', r'\1data-mod="'+right+'"', text)
    return text

def wrap_punctuation(text):
    text = text.replace('--', '\u2014')
    parts = re.split(r'(<[^>]+>)', text)
    result = []
    for part in parts:
        if part.startswith('<'): result.append(part)
        else:
            for ch in [',',';',':','.','!','?','\u2014','(',')','\'','\u2018','\u2019']:
                part = part.replace(ch, f'<span class="punct">{ch}</span>')
            part = re.sub(r'(?<=\s)-(?=\s)', '<span class="punct">-</span>', part)
            result.append(part)
    return ''.join(result)

def process_line(line, swap_list):
    return wrap_punctuation(fix_participles(apply_swaps(line, swap_list)))

# ============================================================================
# HTML GENERATION — outputs standalone book fragments
# ============================================================================

def gen_verse(verse, swap_list):
    ref = verse['ref']
    processed = [process_line(l, swap_list) for l in verse['lines']]
    parts = [f'<div class="verse"><span class="verse-num">{ref}</span>']
    for line in processed:
        parts.append(f'  <span class="line">{line}</span>')
    parts.append('</div>')
    return '\n'.join(parts)

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
    for v in ch_verses:
        p.append(gen_verse(v, swap_list))
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
