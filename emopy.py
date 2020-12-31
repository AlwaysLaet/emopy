import requests as rq
from lxml import html
import re
from os import path
import pickle

class scrapeEmojis(object):
    """**class scrapeEmojis**
    Intended as a parent class with the sole purpose of keeping track
    of the scraping of emoji-unicode from 
        https://unicode.org/emoji/charts/full-emoji-list.html
    """
    def __init__(self, emojis_path = 'data/emojis.pk', scrape_anew = False, save_scrape = True):
        self.emojis_path = emojis_path
        self.__emojis = None
        self.__descrs = None
        path_exists = path.exists(emojis_path)
        if path_exists and (not scrape_anew):
            try:
                with open(emojis_path, 'rb') as fin:
                    self.__emojis, self.__descrs = pickle.load(fin)
            except Exception as e:
                ret = str(input(f"Exception {e} thrown. Scrape anew? ([y] or n): ")).lower()
                if ret in ['n', 'no']:
                    raise e
                else:
                    scrape_anew = True
        if scrape_anew or (not path_exists):
            resp = rq.get("https://unicode.org/emoji/charts/full-emoji-list.html")
            html_tree = html.fromstring(resp.text)
            emojis = html_tree.xpath('//td[@class="chars"]//text()')
            descrs = html_tree.xpath('//td[contains(@class,"name")]//text()')
            self.__emojis, self.__descrs = zip(*sorted(list(zip(emojis, descrs)), key=lambda x: len(x[0]), reverse=True))
            if save_scrape:
                try:
                    with open(emojis_path, 'wb') as fout:
                        pickle.dump((self.emojis, self.descrs), fout)
                except Exception as e:
                    print(f"Exception {e} thrown while saving scraped data. File may not have been written.")
            else:
                print(f"Scraped data not saved due to save_scrape=False in parameters.")
            
    @property
    def emojis(self):
        return self.__emojis
    
    @property
    def descrs(self):
        return self.__descrs
    

class emopy(scrapeEmojis):
    """**class emopy**
    For emoji extraction from text using the emoji list in scrapeEmojis parent class.
        
    """
    def __init__(self, emojis_path = 'data/emojis.pk', scrape_anew = False, save_scrape = True):
        super().__init__(emojis_path, scrape_anew, save_scrape)
        self.__emojis_re = re.compile(self._create_positive_regex(self.emojis))
        self.__not_emojis_re = re.compile(self._create_negative_regex(self.emojis))
        pass
    
    @staticmethod
    def _create_positive_regex(emojis):
        emojis_re_str = "(" + "|".join(["(%s)"%el.replace("*","\*") for el in emojis]) + ")"
        return re.compile(emojis_re_str)
    
    @staticmethod
    def _create_negative_regex(emojis):
        not_emojis_re_str = "[^" + "".join([el.replace("*","\*") for el in emojis]) + "]"
        return re.compile(not_emojis_re_str)
    
    @property
    def emojis_re(self):
        return self.__emojis_re
    
    @property
    def not_emojis_re(self):
        return self.__not_emojis_re
        
    
    def emojis_descrs_text_from_doc(self, doc):
        extr = self.emojis_re.findall(doc)
        if extr:
            emojis, descrs = zip(*[(tup[0], self.descrs[tup[1:].index(tup[0])]) for tup in extr])
        else:
            emojis, descrs = (), ()
        text = "".join(self.not_emojis_re.findall(doc))
        return emojis, descrs, text
    
    def emojis_descrs_text_from_docs(self, docs):
        for doc in docs:
            yield self.emojis_descrs_text_from_doc(doc)