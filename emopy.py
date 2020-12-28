import requests as rq
from lxml import html
import re


class emopy(object):
    """**class emopy**
    For emoji extraction from text using the unicode emoji list found at
        https://unicode.org/emoji/charts/full-emoji-list.html
    """
    def __init__(self):
        self.emojis_re = None
        self.not_emojis_re = None
        pass
    
    @staticmethod
    def _create_positive_regex(emojis):
        emojis_re_str = "(" + "|".join(["(%s)"%el.replace("*","\*") for el in emojis]) + ")"
        return re.compile(emojis_re_str)
    
    @staticmethod
    def _create_negative_regex(emojis):
        not_emojis_re_str = "[^" + "".join([el.replace("*","\*") for el in emojis]) + "]"
        return re.compile(not_emojis_re_str)
    
    def text_emojis_from_doc(self, doc):
        extr = self.emojis_re.findall(doc)
        emojis, descrs = zip(*[(tup[0], self.descrs[tup[1:].index(tup[0])]) for tup in extr])
        text = "".join(self.not_emojis_re.findall(doc))
        return emojis, descrs, text
    
    def text_emojis_from_docs(self, docs):
        return [self.text_emojis_from_doc(doc) for doc in docs]