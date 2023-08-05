from nose.tools import assert_equal, assert_true, assert_false

from unfromm import is_profane, split_words


def test_split_words():
    def check(text, words):
        assert_equal(split_words(text), words)
    for text, words in [
        (
            'brcqzxzzqyy',
            ['brcqzxzzqyy'],
        ),
        (
            'single',
            ['single'],
        ),
        (
            'saturday',
            ['saturday'],
        ),
        (
            'togetherback',
            ['together', 'back'],
        ),
        (
            'filesaveas',
            ['file', 'save', 'as'],
        ),
        (
            'thisisshit',
            ['this', 'is', 'shit'],
        ),
        (
            'crack whore',
            ['crack', 'whore'],
        ),
        (
            'wheninthecourseofhumanevents',
            ['when', 'in', 'the', 'course', 'of', 'human', 'events'],
        ),
    ]:
        yield check, text, words


def test_whitelist():
    def check(word):
        assert_false(is_profane(word), word)
    for word in process_words(whitelist):
        yield check, word


def test_blacklist():
    def check(word):
        assert_true(is_profane(word), word)
    for word in process_words(blacklist):
        yield check, word


def process_words(words_text):
    return [
        word.strip() for word in
        words_text.lower().split('\n')
        if len(word.strip()) > 0
    ]


whitelist = """
scunthorpe
assassin
assassinscreed
circumspection
sussex
cockburn
ashita
mauyamashita
ashitaka
yamashita
Aishiteru
amanashitra
WhoReallyCares
saturday
Hancock
JohnHancock
cockerel
cockney
cocktail
connorpeacock
dickinson
adamdickinson
brucedickings
DickWasovski
"""

blacklist = """
cunt
shit
shitty
amotherfucker
badmotherfucker
BadMothaFuckef
BADMUTHAFUCKA
BigFuckOffSpel
henchfucktard
hornyfuck
cumbucket
nigger123
niggeratti
niggerbang
Niggerbicth
niggerdick
niggerfagbag
niggerfaggot69
niggerjoe
niggerkiller
Niggerloo
niggermang
niggershit
niggerslave
niggersmell
niggerss
niggertits
dr.Faggot
totoasshole
eatthepoopoo
eatshit2
shiteater2
fuckedyouup
fuckencio
fucker
fuckerfucker
fuckenshit
TheDick
thickdick
Trevor2dicks
Trickydick
Uncle_Nigga
youngniggacome
anuthanigga
bigassnigga
Nastybitch
niggabitch3217
FCUK-Hero
fcukme
fcukoyu
Buttholeyo
asspoop
gayaids
EvilPenis
homosapenis
LordPenis
noblepenis
penis33152
vaginaface
vaginabasher
Alottavagina
Massive Vagina
Mr.Pooper
Mr.Pooperskank
pooperino
sirturdboy
turdburglar
turdface
turdmuffin
unicornturd
wankerspanker
Wankoff
BigWanker
Asswhore
crack whore
darkwhore
bigfatdick
TheBigDick
thisgameisshit
CockMonger
poopcock
poopdick13
poopycock
poopydick
Pound&Fuck
pussyncock
cockandballs
cocksalot
CocksAreNice
cravecock
bigdickhead
dickhead222
dickhead74
dicksuckerz
hejdickhead
H0LySh1t
"""
#TODO blacklist testcases
#CRAVExCOCK
#cockslayer
#cocknballs
