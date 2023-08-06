# -*- coding: utf-8 -*-
"""
Set of stopwords. Each set if stored in a specific registry, 'stopwords'
"""
from cubicweb.appobject import AppObject


class StopWords(AppObject):
    __registry__ = 'stopwords'
    __abstract__ = True
    stopwords = set() # Defined in concrete subclasses

class FrenchStopWords(StopWords):
    __regid__ = 'french'
    stopwords = set([
        'au','aux','avec','ce','ces','dans','de','des','du','elle','en',
        'et','eux','il','je','la','le','les', 'leur','lui','ma','mais','me',
        'meme','mes','moi','mon','ne','nos','notre','nous','on','ou',
        'par','pas','pour','qu','que','qui','sa','se','ses','son','sur',
        'ta','te','tes','toi','ton','tu','un','une','vos','votre','vous'])

class FrenchStopWordsLong(StopWords):
    __regid__ = 'french-long'
    stopwords = set([
        'alors','au','aucuns','aussi','autre','avant','avec','avoir','bon',
        'car','ce','cela','ces','ceux','chaque','ci','comme','comment','dans',
        'des','du','dedans','dehors','depuis','deux','devrait','doit','donc',
        'dos','droite','début','elle','elles','en','encore','essai','est','et',
        'eu','fait','faites','fois','font','force','haut','hors','ici','il',
        'ils','je','juste','la','le','les','leur','là','ma','maintenant','mais',
        'mes','mine','moins','mon','mot','meme','ni','nommés','notre','nous',
        'nouveaux','ou','où','par','parce','parole','pas','personnes','peut',
        'peu','pièce','plupart','pour','pourquoi','quand','que','quel','quelle',
        'quelles','quels', 'qui','sa','sans','ses','seulement','si','sien','son',
        'sont','sous','soyez','sujet','sur', 'ta','tandis','tellement','tels',
        'tes','ton','tous','tout','trop','très','tu','valeur', 'voie','voient',
        'vont','votre','vous','vu','ça','étaient','état','étions','été','être' ])

class EnglishStopWords(StopWords):
    __regid__ = 'english'
    stopwords = set([
        "a", "an", "and", "any", "as", "at", "but", "by", "for", "if", "in",
        "not", "of", "off", "on","or","so", "the", "to"])

class EnglishStopWordsLong(StopWords):
    __regid__ = 'english-long'
    stopwords = set([
        "a", "about", "above", "across", "after", "afterwards", "again", "against",
        "all", "almost", "alone", "along", "already", "also", "although", "always",
        "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
        "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
        "around", "as", "at", "back", "be", "became", "because", "become",
        "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
        "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom",
        "but", "by", "call", "can", "cannot", "cant", "co", "computer", "con",
        "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down",
        "due", "during", "each", "eg", "eight", "either", "eleven", "else",
        "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
        "everything", "everywhere", "except", "few", "fifteen", "fify", "fill",
        "find", "fire", "first", "five", "for", "former", "formerly", "forty",
        "found", "four", "from", "front", "full", "further", "get", "give", "go",
        "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
        "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
        "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
        "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
        "latterly", "least", "less", "ltd", "made", "many", "may", "me",
        "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
        "move", "much", "must", "my", "myself", "name", "namely", "neither", "never",
        "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor",
        "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once",
        "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours",
        "ourselves", "out", "over", "own", "part", "per", "perhaps", "please",
        "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems",
        "serious", "several", "she", "should", "show", "side", "since", "sincere",
        "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime",
        "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than",
        "that", "the", "their", "them", "themselves", "then", "thence", "there",
        "thereafter", "thereby", "therefore", "therein", "thereupon", "these",
        "they", "thick", "thin", "third", "this", "those", "though", "three",
        "through", "throughout", "thru", "thus", "to", "together", "too", "top",
        "toward", "towards", "twelve", "twenty", "two", "un", "under", "until",
        "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what",
        "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas",
        "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while",
        "whither", "who", "whoever", "whole", "whom", "whose", "why", "will",
        "with", "within", "without", "would", "yet", "you", "your", "yours",
        "yourself", "yourselves"])

class EnglishStopWordsMySql(StopWords):
    __regid__ = 'english-mysql'
    stopwords = set([
        'a', 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after',
        'afterwards', 'again', 'against', 'ain’t', 'all', 'allow', 'allows', 'almost', 'alone',
        'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and',
        'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere',
        'apart', 'appear', 'appreciate', 'appropriate', 'are', 'aren’t', 'around', 'as', 'aside',
        'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'be', 'became',
        'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind',
        'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond',
        'both', 'brief', 'but', 'by', 'c’mon', 'c’s', 'came', 'can', 'can’t', 'cannot', 'cant',
        'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come',
        'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing',
        'contains', 'corresponding', 'could', 'couldn’t', 'course', 'currently', 'definitely',
        'described', 'despite', 'did', 'didn’t', 'different', 'do', 'does', 'doesn’t', 'doing',
        'don’t', 'done', 'down', 'downwards', 'during', 'each', 'edu', 'eg', 'eight', 'either',
        'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever',
        'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example',
        'except', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for',
        'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'get', 'gets',
        'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings',
        'had', 'hadn’t', 'happens', 'hardly', 'has', 'hasn’t', 'have', 'haven’t', 'having', 'he',
        'he’s', 'hello', 'help', 'hence', 'her', 'here', 'here’s', 'hereafter', 'hereby', 'herein',
        'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how',
        'howbeit', 'however', 'i’d', 'i’ll', 'i’m', 'i’ve', "i'd", "i'll", "i'm", "i've", 'ie', 'if',
        'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates',
        'inner', 'insofar', 'instead', 'into', 'inward', 'is', 'isn’t', 'it', 'it’d', 'it’ll', 'it’s',
        'its', 'itself', 'just', 'keep', 'keeps', 'kept', 'know', 'knows', 'known', 'last', 'lately',
        'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'let’s', 'like', 'liked',
        'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'mainly', 'many', 'may', 'maybe', 'me',
        'mean', 'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must',
        'my', 'myself', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', 'needs',
        'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'no', 'nobody', 'non', 'none',
        'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'obviously', 'of',
        'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto',
        'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside',
        'over', 'overall', 'own', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please',
        'plus', 'possible', 'presumably', 'probably', 'provides', 'que', 'quite', 'qv', 'rather', 'rd',
        're', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 'relatively', 'respectively',
        'right', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing',
        'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious',
        'seriously', 'seven', 'several', 'shall', 'she', 'should', 'shouldn’t', 'since', 'six', 'so',
        'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat',
        'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such',
        'sup', 'sure', 't’s', 'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks',
        'thanx', 'that', 'that’s', "that's", 'thats', 'the', 'their', 'theirs', 'them', 'themselves',
        'then', 'thence', 'there', 'there’s', 'thereafter', 'thereby', 'therefore', 'therein', 'theres',
        'thereupon', 'these', 'they', 'they’d', 'they’ll', 'they’re', 'they’ve', 'think', 'third', 'this',
        'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus',
        'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying',
        'twice', 'two', 'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up',
        'upon', 'us', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'value', 'various', 'very',
        'via', 'viz', 'vs', 'want', 'wants', 'was', 'wasn’t', 'way', 'we', 'we’d', 'we’ll', 'we’re',
        'we’ve', 'welcome', 'well', 'went', 'were', 'weren’t', 'what', 'what’s', 'whatever', 'when',
        'whence', 'whenever', 'where', 'where’s', 'whereafter', 'whereas', 'whereby', 'wherein',
        'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'who’s', 'whoever',
        'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without',
        'won’t', 'wonder', 'would', 'would', 'wouldn’t', 'yes', 'yet', 'you', 'you’d', 'you’ll',
        'you’re', 'you’ve', 'your', 'yours', 'yourself', 'yourselves', 'zero'])

class EnglishStopWordsRegularVerb(StopWords):
    __regid__ = 'english-regular-verb'
    stopwords = set([
        'accept', 'add', 'admire', 'admit', 'advise', 'afford', 'agree', 'alert', 'allow',
        'amuse', 'analyse', 'announce', 'annoy', 'answer', 'apologise', 'appear', 'applaud',
        'appreciate', 'approve', 'argue', 'arrange', 'arrest', 'arrive', 'ask', 'attach', 'attack',
        'attempt', 'attend', 'attract', 'avoid', 'back', 'bake', 'balance', 'ban', 'bang',
        'bare', 'bat', 'bathe', 'battle', 'beam', 'beg', 'behave', 'belong', 'bleach', 'bless',
        'blind', 'blink', 'blot', 'blush', 'boast', 'boil', 'bolt', 'bomb', 'book', 'bore',
        'borrow', 'bounce', 'bow', 'box', 'brake', 'branch', 'breathe', 'bruise', 'brush',
        'bubble', 'bump', 'burn', 'bury', 'buzz', 'calculate', 'call', 'camp', 'care', 'carry',
        'carve', 'cause', 'challenge', 'change', 'charge', 'chase', 'cheat', 'check', 'cheer',
        'chew', 'choke', 'chop', 'claim', 'clap', 'clean', 'clear', 'clip', 'close', 'coach',
        'coil', 'collect', 'colour', 'comb', 'command', 'communicate', 'compare', 'compete',
        'complain', 'complete', 'concentrate', 'concern', 'confess', 'confuse', 'connect',
        'consider', 'consist', 'contain', 'continue', 'copy', 'correct', 'cough', 'count',
        'cover', 'crack', 'crash', 'crawl', 'cross', 'crush', 'cry', 'cure', 'curl', 'curve',
        'cycle', 'dam', 'damage', 'dance', 'dare', 'decay', 'deceive', 'decide', 'decorate',
        'delay', 'delight', 'deliver', 'depend', 'describe', 'desert', 'deserve', 'destroy',
        'detect', 'develop', 'disagree', 'disappear', 'disapprove', 'disarm', 'discover', 'dislike',
        'divide', 'double', 'doubt', 'drag', 'drain', 'dream', 'dress', 'drip', 'drop', 'drown',
        'drum', 'dry', 'dust', 'earn', 'educate', 'embarrass', 'employ', 'empty', 'encourage',
        'end', 'enjoy', 'enter', 'entertain', 'escape', 'examine', 'excite', 'excuse', 'exercise',
        'exist', 'expand', 'expect', 'explain', 'explode', 'extend',  ' face', 'fade', 'fail',
        'fancy', 'fasten', 'fax', 'fear', 'fence', 'fetch', 'file', 'fill', 'film', 'fire', 'fit',
        'fix', 'flap', 'flash', 'float', 'flood', 'flow', 'flower', 'fold', 'follow', 'fool',
        'force', 'form', 'found', 'frame', 'frighten', 'fry', 'gather', 'gaze', 'glow', 'glue',
        'grab', 'grate', 'grease', 'greet', 'grin', 'grip', 'groan', 'guarantee', 'guard', 'guess',
        'guide', 'hammer', 'hand', 'handle', 'hang', 'happen', 'harass', 'harm', 'hate', 'haunt',
        'head', 'heal', 'heap', 'heat', 'help', 'hook', 'hop', 'hope', 'hover', 'hug', 'hum',
        'hunt', 'hurry', 'identify', 'ignore', 'imagine', 'impress', 'improve', 'include', 'increase',
        'influence', 'inform', 'inject', 'injure', 'instruct', 'intend', 'interest', 'interfere',
        'interrupt', 'introduce', 'invent', 'invite', 'irritate', 'itch', 'jail', 'jam', 'jog',
        'join', 'joke', 'judge', 'juggle', 'jump', 'kick', 'kill', 'kiss', 'kneel', 'knit', 'knock',
        'knot', 'label', 'land', 'last', 'laugh', 'launch', 'learn', 'level', 'license', 'lick',
        'lie', 'lighten', 'like', 'list', 'listen', 'live', 'load', 'lock', 'long', 'look', 'love',
        'man', 'manage', 'march', 'mark', 'marry', 'match', 'mate', 'matter', 'measure', 'meddle',
        'melt', 'memorise', 'mend', 'mess up', 'milk', 'mine', 'miss', 'mix', 'moan', 'moor',
        'mourn', 'move', 'muddle', 'mug', 'multiply', 'murder', 'nail', 'name', 'need', 'nest',
        'nod', 'note', 'notice', 'number', 'obey', 'object', 'observe', 'obtain', 'occur', 'offend',
        'offer', 'open', 'order', 'overflow', 'owe', 'own', 'pack', 'paddle', 'paint', 'park',
        'part', 'pass', 'paste', 'pat', 'pause', 'peck', 'pedal', 'peel', 'peep', 'perform', 'permit',
        'phone', 'pick', 'pinch', 'pine', 'place', 'plan', 'plant', 'play', 'please', 'plug',
        'point', 'poke', 'polish', 'pop', 'possess', 'post', 'pour', 'practise', 'pray', 'preach',
        'precede', 'prefer', 'prepare', 'present', 'preserve', 'press', 'pretend', 'prevent',
        'prick', 'print', 'produce', 'program', 'promise', 'protect', 'provide', 'pull', 'pump',
        'punch', 'puncture', 'punish', 'push', 'question', 'queue', 'race', 'radiate', 'rain', 'raise',
        'reach', 'realise', 'receive', 'recognise', 'record', 'reduce', 'reflect', 'refuse',
        'regret', 'reign', 'reject', 'rejoice', 'relax', 'release', 'rely', 'remain', 'remember',
        'remind', 'remove', 'repair', 'repeat', 'replace', 'reply', 'report', 'reproduce', 'request',
        'rescue', 'retire', 'return', 'rhyme', 'rinse', 'risk', 'rob', 'rock', 'roll', 'rot', 'rub',
        'ruin', 'rule', 'rush', 'sack', 'sail', 'satisfy', 'save', 'saw', 'scare', 'scatter',
        'scold', 'scorch', 'scrape', 'scratch', 'scream', 'screw', 'scribble', 'scrub', 'seal',
        'search', 'separate', 'serve', 'settle', 'shade', 'share', 'shave', 'shelter', 'shiver',
        'shock', 'shop', 'shrug', 'sigh', 'sign', 'signal', 'sin', 'sip', 'ski', 'skip', 'slap',
        'slip', 'slow', 'smash', 'smell', 'smile', 'smoke', 'snatch', 'sneeze', 'sniff', 'snore',
        'snow', 'soak', 'soothe', 'sound', 'spare', 'spark', 'sparkle', 'spell', 'spill', 'spoil',
        'spot', 'spray', 'sprout', 'squash', 'squeak', 'squeal', 'squeeze', 'stain', 'stamp', 'stare',
        'start', 'stay', 'steer', 'step', 'stir', 'stitch', 'stop', 'store', 'strap', 'strengthen',
        'stretch', 'strip', 'stroke', 'stuff', 'subtract', 'succeed', 'suck', 'suffer', 'suggest',
        'suit', 'supply', 'support', 'suppose', 'surprise', 'surround', 'suspect', 'suspend', 'switch',
        'talk', 'tame', 'tap', 'taste', 'tease', 'telephone', 'tempt', 'terrify', 'test', 'thank',
        'thaw', 'tick', 'tickle', 'tie', 'time', 'tip', 'tire', 'touch', 'tour', 'tow', 'trace',
        'trade', 'train', 'transport', 'trap', 'travel', 'treat', 'tremble', 'trick', 'trip', 'trot',
        'trouble', 'trust', 'try', 'tug', 'tumble', 'turn', 'twist', 'type', 'undress', 'unfasten',
        'unite', 'unlock', 'unpack', 'untidy', 'use', 'vanish', 'visit', 'wail', 'wait', 'walk', 'wander',
        'want', 'warm', 'warn', 'wash', 'waste', 'watch', 'water', 'wave', 'weigh', 'welcome', 'whine',
        'whip', 'whirl', 'whisper', 'whistle', 'wink', 'wipe', 'wish', 'wobble', 'wonder', 'work',
        'worry', 'wrap', 'wreck', 'wrestle', 'wriggle', 'x-ray', 'yawn', 'yell', 'zip', 'zoom'])

class EnglishStopWordsIrregularVerb(StopWords):
    __regid__ = 'english-irregular-verb'
    stopwords = set([
        'arise ', 'arose ', 'arisen', 'awake', 'awakened', 'awoke', 'awakened', 'awoken', 'backslide',
        'backslid', 'backslidden', 'backslid', 'be', 'was, were', 'been', 'bear', 'bore', 'born',
        'borne', 'beat', 'beat', 'beaten', 'beat', 'become', 'became', 'become', 'begin', 'began',
        'begun', 'bend', 'bent', 'bent', 'bet', 'bet', 'betted', 'bet', 'betted', 'bid', 'bid', 'bade',
        'bidden', 'bid', 'bid', 'bid', 'bind', 'bound', 'bound', 'bite', 'bit', 'bitten', 'bleed',
        'bled', 'bled', 'blow', 'blew', 'blown', 'break', 'broke', 'broken', 'breed', 'bred', 'bred',
        'bring', 'brought', 'brought', 'broadcast', 'broadcast', 'broadcasted', 'broadcast', 'broadcasted',
        'build', 'built', 'built', 'burn', 'burned', 'burnt', 'burned', 'burnt', 'burst', 'burst',
        'burst', 'bust', 'busted', 'bust', 'busted', 'bust', 'buy', 'bought', 'bought', 'cast', 'cast',
        'cast', 'catch', 'caught', 'caught', 'choose', 'chose', 'chosen', 'cling', 'clung', 'clung',
        'clothe', 'clothed', 'clad', 'clothed', 'clad', 'come', 'came', 'come', 'cost', 'cost', 'cost',
        'creep', 'crept', 'crept', 'cut', 'cut', 'cut', 'daydream', 'daydreamed', 'daydreamt',
        'daydreamed', 'daydreamt', 'deal', 'dealt', 'dealt', 'dig', 'dug', 'dug', 'disprove', 'disproved',
        'disproved', 'disproven', 'dive', 'dove', 'dived', 'dived', 'dive', 'dived', 'dove', 'dived',
        'do', 'did', 'done', 'draw', 'drew', 'drawn', 'dream', 'dreamed', 'dreamt', 'dreamed',
        'dreamt', 'drink', 'drank', 'drunk', 'drive', 'drove', 'driven', 'dwell', 'dwelt', 'dwelled',
        'dwelt', 'dwelled', 'eat', 'ate', 'eaten', 'fall', 'fell', 'fallen', 'feed', 'fed', 'fed',
        'feel', 'felt', 'felt', 'fight', 'fought', 'fought', 'find', 'found', 'found', 'fit', 'fitted',
        'fit', 'fitted', 'fit', 'fit', 'fit', 'fitted', 'fit', 'fitted', 'flee', 'fled', 'fled',
        'fling', 'flung', 'flung', 'fly', 'flew', 'flown', 'forbid', 'forbade', 'forbidden', 'forecast',
        'forecast', 'forecast', 'forego', 'forewent', 'foregone', 'foresee', 'foresaw', 'foreseen',
        'foretell', 'foretold', 'foretold', 'forget', 'forgot', 'forgotten', 'forgot', 'forgive',
        'forgave', 'forgiven', 'forsake', 'forsook', 'forsaken', 'freeze', 'froze', 'frozen', 'get',
        'got', 'gotten', 'got', 'give', 'gave', 'given', 'go', 'went', 'gone', 'grind', 'ground',
        'ground', 'grow', 'grew', 'grown', 'hang', 'hung', 'hung', 'have', 'had', 'had', 'hear',
        'heard', 'heard', 'hew', 'hewed', 'hewn', 'hewed', 'hide', 'hid', 'hidden', 'hit', 'hit',
        'hit', 'hold', 'held', 'held', 'hurt', 'hurt', 'hurt', 'keep', 'kept', 'kept', 'kneel', 'knelt',
        'kneeled', 'knelt', 'kneeled', 'knit', 'knitted', 'knit', 'knitted', 'knit', 'know', 'knew',
        'known', 'lay', 'laid', 'laid', 'lead', 'led', 'led', 'lean', 'leaned', 'leant', 'leaned',
        'leant', 'leap', 'leaped', 'leapt', 'leaped', 'leapt', 'learn', 'learned', 'learnt', 'learned',
        'learnt', 'leave', 'left', 'left', 'lend', 'lent', 'lent', 'let', 'let', 'let', 'lie', 'lay',
        'lain', 'lie', 'lied', 'lied', 'light', 'lit', 'lighted', 'lit', 'lighted', 'lose', 'lost', 'lost',
        'make', 'made', 'made', 'mean', 'meant', 'meant', 'meet', 'met', 'met', 'misunderstand',
        'misunderstood', 'misunderstood', 'mow', 'mowed', 'mowed', 'mown', 'partake', 'partook',
        'partaken', 'pay', 'paid', 'paid', 'plead', 'pleaded', 'pled', 'pleaded', 'pled', 'proofread',
        'proofread', 'proofread', 'prove', 'proved', 'proven', 'proved', 'put', 'put', 'put',
        'quick-freeze', 'quick-froze', 'quick-frozen', 'quit', 'quit', 'quitted', 'quit', 'quitted',
        'read', 'read', ' read', 'rid', 'rid', 'rid', 'ride', 'rode', 'ridden', 'ring', 'rang', 'rung',
        'rise', 'rose', 'risen', 'run', 'ran', 'run', 'saw', 'sawed', 'sawed', 'sawn', 'say', 'said',
        'said', 'see', 'saw', 'seen', 'seek', 'sought', 'sought', 'sell', 'sold', 'sold', 'send', 'sent',
        'sent', 'set', 'set', 'set', 'sew', 'sewed', 'sewn', 'sewed', 'shake', 'shook', 'shaken', 'shave',
        'shaved', 'shaved', 'shaven', 'shear', 'sheared', 'sheared', 'shorn', 'shed', 'shed', 'shed',
        'shine', 'shined', 'shone', 'shined', 'shone', 'shoot', 'shot', 'shot', 'show', 'showed', 'shown',
        'showed', 'shrink', 'shrank', 'shrunk', 'shrunk', 'shut', 'shut', 'shut', 'sing', 'sang', 'sung',
        'sink', 'sank', 'sunk', 'sunk', 'sit', 'sat', 'sat', 'slay', 'slew', 'slayed', 'slain', 'slayed',
        'slay', 'slayed', 'slayed', 'sleep', 'slept', 'slept', 'slide', 'slid', 'slid', 'sling', 'slung',
        'slung', 'slink', 'slinked', 'slunk', 'slinked', 'slunk', 'slit', 'slit', 'slit', 'smell',
        'smelled', 'smelt', 'smelled', 'smelt', 'sneak', 'sneaked', 'snuck', 'sneaked', 'snuck', 'sow',
        'sowed', 'sown', 'sowed', 'speak', 'spoke', 'spoken', 'speed', 'sped', 'speeded', 'sped', 'speeded',
        'spell', 'spelled', 'spelt', 'spelled', 'spelt', 'spend', 'spent', 'spent', 'spill', 'spilled',
        'spilt', 'spilled', 'spilt', 'spin', 'spun', 'spun', 'spit', 'spit', 'spat', 'spit', 'spat',
        'split', 'split', 'split', 'spoil', 'spoiled', 'spoilt', 'spoiled', 'spoilt', 'spread', 'spread',
        'spread', 'spring', 'sprang', 'sprung', 'sprung', 'stand ', 'stood', 'stood', 'steal', 'stole',
        'stolen', 'stick', 'stuck', 'stuck', 'sting', 'stung', 'stung', 'stink', 'stunk', 'stank', 'stunk',
        'strew', 'strewed', 'strewn', 'strewed', 'stride', 'strode', 'stridden', 'strike', 'struck',
        'stricken', 'strike', 'struck', 'struck', 'stricken', 'string', 'strung', 'strung', 'strive',
        'strove', 'strived', 'striven', 'strived', 'sublet', 'sublet', 'sublet', 'sunburn', 'sunburned',
        'sunburnt', 'sunburned', 'sunburnt', 'swear', 'swore', 'sworn', 'sweat', 'sweat', 'sweated',
        'sweat', 'sweated', 'sweep', 'swept', 'swept', 'swell', 'swelled', 'swollen', 'swelled', 'swim',
        'swam', 'swum', 'swing', 'swung', 'swung', 'take', 'took', 'taken', 'teach', 'taught', 'taught',
        'tear', 'tore', 'torn', 'telecast', 'telecast', 'telecast', 'tell', 'told', 'told', 'test-drive',
        'test-drove', 'test-driven', 'test-fly', 'test-flew', 'test-flown', 'think', 'thought', 'thought',
        'throw', 'threw', 'thrown', 'thrust', 'thrust', 'thrust', 'tread', 'trod', 'trodden', 'trod',
        'understand', 'understood', 'understood', 'undertake', 'undertook', 'undertaken', 'undo',
        'undid', 'undone', 'wake', 'woke', 'waked', 'woken', 'waked', 'waylay', 'waylaid', 'waylaid',
        'wear', 'wore', 'worn', 'weave', 'wove', 'weaved', 'woven', 'weaved', 'wed', 'wed', 'wedded',
        'wed', 'wedded', 'weep', 'wept', 'wept', 'wet', 'wet', 'wetted', 'wet', 'wetted', 'whet', 'whetted',
        'whetted', 'win', 'won', 'won', 'wind', 'wound', 'wound', 'withdraw', 'withdrew', 'withdrawn',
        'withhold', 'withheld', 'withheld', 'withstand', 'withstood', 'withstood', 'wring', 'wrung',
        'wrung', 'write', 'wrote', 'written',])


class EnglishStopWordsAllVerb(StopWords):
    __regid__ = 'english-all-verb'

    @property
    def stopwords(self):
        regular = EnglishStopWordsRegularVerb.stopwords
        irregular = EnglishStopWordsIrregularVerb.stopwords
        stopwords = regular.union(irregular)
        stopwords = stopwords.union(set([t+'s' for t in regular]))
        stopwords = stopwords.union(set([t+'s' for t in irregular]))
        stopwords = stopwords.union(set([t+'ing' for t in regular]))
        stopwords = stopwords.union(set([t+'ing' for t in irregular]))
        stopwords = stopwords.union(set([t+'ed' for t in regular]))
        return stopwords
