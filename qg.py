from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
from tqdm import tqdm

from question_generation.pipelines import pipeline

import transformers
from deep_translator import GoogleTranslator

class QgTrans:
    def __init__(self, translator_ru_to_en, translator_en_to_ru, nlp):
        self.translator_ru_to_en = translator_ru_to_en
        self.translator_en_to_ru = translator_en_to_ru
        self.nlp = nlp


    def preprocessing(self, corpus, lim=4999):
        n = 0
        for i in range(len(corpus)):
            if len(corpus[i-n]) == 0:
                corpus.pop(i-n)
                n+=1
                continue
            corpus[i-n] = corpus[i-n].replace('\xa0', ' ')[:lim]

        return corpus


    def parse_text_ria(self, name):
        link = 'https://ria.ru/search/?query='

        for word in name.split():
            link += f'{word}+'
        link = link[:-1]

        
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url=link)
        sleep(2.5)
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        a = soup.findAll("a", {"class" : "list-item__title"})

        els = []
        for link in a:
            for word in name.lower().split():
                if word in link.text.lower():
                    els.append((link.text, link['href']))
                    break

        res = []

        for el in els:
            
            url = el[1]

            main_text = ""
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            texts = soup.findAll("div", {"class" : "article__text"})
            for text in texts:
                main_text += text.text

            res.append(main_text)

        return res

    def parse_text_cosmo(self, name):
        url = "https://www.cosmo.ru/search/?query="

        for word in name.split():
            url += f'{word}%20'
        url = url[:-3]

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url=url)
        sleep(2.5)
        html = driver.page_source
        driver.close()

        soup = BeautifulSoup(html, "html.parser")
        a = soup.findAll("a", {"class" : "search-article search__article"})

        els = []
        for link in a:
            for word in name.lower().split():
                if word in link.text.lower():
                    els.append((link.text, link['href']))
                    break

        res = []
        for el in els:
            url = f"https://www.cosmo.ru{el[1]}"
            main_text = ""
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            texts = soup.findAll("p", {"class" : "article-element"})
            for text in texts:
                main_text += text.text
            
            res.append(main_text)

        return res

    def parse_text_mh(self, name):
        url = "https://www.mhealth.ru/search/?query="

        for word in name.split():
            url += f'{word}%20'
        url = url[:-3]

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url=url)
        sleep(2.5)
        html = driver.page_source
        driver.close()

        soup = BeautifulSoup(html, "html.parser")
        a = soup.findAll("a", {"class" : "search-article search__article"})

        els = []
        for link in a:
            for word in name.lower().split():
                if word in link.text.lower():
                    els.append((link.text, link['href']))
                    break

        res = []
        for el in els:
            url = f"https://www.mhealth.ru{el[1]}"
            main_text = ""
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            texts = soup.findAll("p", {"class" : "article-element"})
            for text in texts:
                main_text += text.text
            
            res.append(main_text)

        return res


    def parse(self, name,):
        ria = self.parse_text_ria(name)
        cosmo = self.parse_text_cosmo(name)
        mh = self.parse_text_mh(name)

        parsed = ria + cosmo + mh
        return parsed


    def translate_ru_to_en(self, sentence):
        translated = []
        
        for text in sentence.split('.'):
            translated.append(self.translator_ru_to_en.translate(text=sentence))

        return translated


    def qg_en_to_en(self, corpus):
        qg = []
        for i in corpus:
            qg.append(self.nlp(i))
        return qg


    def translate_en_to_ru(self, sentence):
        return self.translator_en_to_ru.translate(text=sentence)


    def predict(self, name):
        ru_to_en = []
        en_to_ru = []
        corpus = self.parse(name,)
        print(corpus)
        corpus = self.preprocessing(corpus)[:9]
        for text in tqdm(corpus):
            ru_to_en.append(self.translate_ru_to_en(text))
        qg = self.qg_en_to_en(ru_to_en)
        return qg















