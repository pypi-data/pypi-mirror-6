# -*- coding: utf-8 -*-
""" This module provides tools for named entities matching in a document.
It is based on two adapter classes:

- INamedEntitiesContentAbstract: this adapter is used to indicate that an etype may
  be parse to recognize the named entities. It defines which attribute of the entity should
  be parse, and thus iterates over tokens that should be recognized.

- INamedEntitiesSource: this adapter is used to indicate that an etype may
  be use as as ner source. It defines a function 'match_word'
  that takes a token and return a list of uris.
"""
import itertools
import collections
import re

from cubicweb.selectors import is_instance
from cubicweb.view import EntityAdapter
from cubicweb.appobject import AppObject
import cubes.ner.entities.stopwords as sto


FRENCH_STOPWORDS = sto.FrenchStopWordsLong.stopwords.union(sto.FrenchStopWords.stopwords)
STOPWORDS = {'en': sto.EnglishStopWordsMySql.stopwords,
             'fr': FRENCH_STOPWORDS}


###############################################################################
### NER UTILS #################################################################
###############################################################################
Token = collections.namedtuple('Token', ['word', 'start', 'stop'])

class RichStringTokenizer(object):
    """Tokenizer for Yams' RichString content.

    The tokenizer uses a variable-length sliding window, i.e. a sliding
    window yielding tokens of N words.

    The following example will tokenize groups of 1 and 2 words in the
    given text :

    >>> tokenizer = RichStringTokenizer(u'Hello everyone, this is   me speaking',
    ...                                 token_max_size=2)
    >>> for t in tokenizer:
    ...     print t
    ...
    Token(word=u'Hello', start=0, stop=5)
    Token(word=u'everyone', start=6, stop=14)
    Token(word=u'Hello everyone', start=0, stop=14)
    Token(word=u'this', start=16, stop=20)
    Token(word=u'everyone, this', start=6, stop=20)
    Token(word=u'is', start=21, stop=23)
    Token(word=u'this is', start=16, stop=23)
    Token(word=u'me', start=26, stop=28)
    Token(word=u'is me', start=21, stop=28)
    Token(word=u'speaking', start=29, stop=37)
    Token(word=u'me speaking', start=26, stop=37)
    """
    def __init__(self, text, token_min_size=1, token_max_size=3):
        """
        :text: the text to tokenize
        :token_min_size: minimum number of words required to be a valid token
        :token_max_size: minimum number of words required to be a valid token
        :content_skipped_rgx: a regexp object defining text zones to be skipped
                              during tokenization. The default value corresponds
                              to HTML and REST link definitions
        """
        self.text = text
        self.token_min_size = token_min_size
        self.token_max_size = token_max_size
        self.success_notified = False

    def __iter__(self):
        window = []
        words = list([m.group() for m in re.finditer(r'[\w-]+', self.text, re.UNICODE)])
        indice = 0
        while indice < len(words):
            # Sliding windows over the different words for each sentence
            for length in range(self.token_max_size, self.token_min_size, -1):
                start = indice
                end = indice+length
                normalized_word = ' '.join(words[start:end]).strip()
                yield Token(normalized_word, start, end)
            indice += 1


###############################################################################
### CONTENT ADAPTER ###########################################################
###############################################################################
class INamedEntitiesContentAbstract(EntityAdapter):
    __regid__ = 'INamedEntitiesContent'
    __abstract__ = True
    contentname = None

    def recognized_entities(self, ner_processes,
                            token_min_size=1, token_max_size=5,
                            break_at_first=True, lang='fr'):
        """ Process a content and recognize entities
        """
        content = getattr(self.entity, self.contentname)
        if not content:
            return {}
        tokenizer = RichStringTokenizer(content,
                                        token_min_size=token_min_size,
                                        token_max_size=token_max_size)
        last_stop = 0
        named_entities = set()
        preprocessor = self._cw.vreg['word-preprocessor'].select('article', self._cw,
                                                                 entity=self.entity)
        for token in tokenizer:
            if token.start < last_stop:
                continue # this token overlaps with a previous match
            word = token.word
            # Article dependant preprocessing
            if preprocessor:
                word = preprocessor.preprocess_word(word)
            if not self.is_word_valid(word, lang):
                continue # this word is invalid
            for process in ner_processes:
                named_entity = process.match_word(word)
                if named_entity:
                    named_entities.add((named_entity, process.eid))
                    last_stop = token.stop
                    if break_at_first:
                        break
        return named_entities

    def is_word_valid(self, word, lang='fr'):
        """ Check if the word is valid """
        stopwords = STOPWORDS.get(lang, FRENCH_STOPWORDS)
        if word.lower() in stopwords:
            return False
        if len(word)<=3:
            return False
        return True


###############################################################################
### WORD PREPROCESSOR #########################################################
###############################################################################
class WordPreprocessorStandard(AppObject):
    __registry__ = 'word-preprocessor'

    def preprocess_word(self, word):
        return word
