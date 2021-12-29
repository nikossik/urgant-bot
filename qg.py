from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
from typing import Text
import re
from requests.utils import select_proxy
from selenium.webdriver.common.by import By
from time import sleep

from question_generation.pipelines import pipeline

import transformers
from deep_translator import GoogleTranslator

class QgTrans:
    def __init__(self, translator_ru_to_en, translator_en_to_ru, nlp, link_limit=10):
        self.translator_ru_to_en = translator_ru_to_en
        self.translator_en_to_ru = translator_en_to_ru
        self.nlp = nlp
        self.link_limit = link_limit

    def preprocess_text(self, corpus) -> list:
        for i in range(len(corpus)):
            corpus[i] = str(corpus[i]).replace('[', '').replace(']', '')
            corpus[i] = re.sub(r"<.*?>", "", corpus[i])
            corpus[i] = re.sub(r"[{}]|[()]", " ", corpus[i])
            corpus[i] = re.sub(r"\xa0|\n", " ", corpus[i])
            corpus[i] = re.sub(r"\s+", " ", corpus[i])

        return corpus
    
    def create_url(self, url_start:str, query:str) -> str:
        url = url_start

        for word in query.split():
            url += f"{word}+"

        return url[:-1]

    # Parsers
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

    def tatler_parser(self, query:str) -> list:

        url_parts = ['https://www.tatler.ru/search?q=','&sort=score+desc']
        links = []

        for word in query.split():
            url_parts[0] += f'{word}+'

        url_parts[0] = url_parts[0][:-1]
        url = ''.join(url_parts)

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        
        a_els = soup.find_all('a', {'class':'summary-item-tracking__hed-link summary-item__hed-link summary-item__hed-link--underline-disable'})

        for a_el in a_els:
            links.append(f"https://www.tatler.ru/{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            div_el = soup.find_all('div', {'class': 'body__inner-container'})

            text = str(div_el).replace('[', '').replace(']','')
            p_els = re.findall(r'<p>(.*?)</p>', text)

        return self.preprocess_text(p_els)

    def sobaka_parser(self, query:str) -> list:

        url = self.create_url('https://www.sobaka.ru/search/all?q=', query)
        links, texts = [], []

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        a_els = soup.find_all('a', {'class' : 'b-media__title-link'})

        for a_el in a_els:
            links.append(f"http://sobaka.ru{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html,  "html.parser")

            div_els = soup.find_all('div', {'class':'b-editors-text b-editors-text--lead'})

            preprocessed_text = self.preprocess_text(div_els)

            if len(preprocessed_text) != 0 : texts.append(self.preprocess_text(div_els)[0])

        return texts

    def esquire_parser(self, query:str) -> list:
        
        url = self.create_url("https://esquire.ru/search/?query=", query)
        texts, links = [], []

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        div_els = soup.find_all('div', {'class':'article-listed is-item'})
        
        for div_el in div_els[:10]:
            for a_el in div_el.find_all('a'):
                links.append(f"https://esquire.ru{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            text = soup.find_all('div', {'class':'text-page'})
            p_els = re.findall(r'<p>(.*?)</p>', str(text))

            texts += self.preprocess_text(p_els)

        return texts

    def kommersant_parser(self, query:str) -> list:
        
        url = self.create_url('https://www.kommersant.ru/search/results?search_query=', query)
        print(url)
        links, texts = [], []

        html = requests.get(url).text
        soup = BeautifulSoup(html,"html.parser")

        a_els = soup.find_all('a', {'class':'uho__link uho__link--overlay'})

        for a_el in a_els:
            links.append(f"https://www.kommersant.ru{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            p_els = soup.find_all('p', {'class':'doc__text'})
            #print(p_els)

            texts.append(self.preprocess_text(p_els)[0])

        return texts

    # def rbc_parser(self, query:str) -> list:
        
    #     url = self.create_url('https://www.rbc.ru/search/?project=rbcnews&query=', query)
    #     links, texts = [], []
        
    #     html = requests.get(url).text
    #     soup = BeautifulSoup(html, "html.parser")

    #     a_els = soup.find_all('a', {'class':'search-item__link'})
        
    #     for a_el in a_els:
    #         links.append(a_el['href'])

    #     for link in links[:self.link_limit]: 
    #         html  = requests.get(link).text
    #         soup = BeautifulSoup(html, "html.parser")

    #         p_els = soup.find_all('p')

    #         texts.append(self.preprocess_text(p_els)[0])

    #     return texts
 
    def dp_parsing(self, query:str) -> list:

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://www.dp.ru/search')

        search_input = driver.find_element(By.TAG_NAME,"input")
        search_input.send_keys(str(query))

        search_button = driver.find_element(By.XPATH, "/html/body/app-root/div/div[1]/div[2]/app-search/div/div/div[1]/form/div[2]/div[3]/div[2]/div[1]/button")
        search_button.click()

        sleep(5)

        html = driver.page_source
        driver.close()

        links, texts = [], []

        soup = BeautifulSoup(html, "html.parser")
        a_els = soup.find_all('a', {'class': 'article-fav-block-headline'})

        for a_el in a_els:
            links.append(f"https://dp.ru{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            div_els = soup.find_all('div', {'class': 'paragraph paragraph-text'})

            for div_el in div_els:
                text = self.preprocess_text([div_el.text])[0]
                texts.append(text)

        return texts

    def forbes_parser(self, query:str) -> list:
        ok = False

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://www.forbes.ru/')

        while not ok:
            try:
                sleep(2)

                search_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[1]/header/div[1]/div/button[2]')
                search_button.click()

                search_input = driver.find_element(By.XPATH,'//*[@id="__layout"]/div/div[1]/header/div[2]/div/label/input')
                search_input.send_keys(str(query))

                sleep(5)

                ok = True     
            except:
                pass

        html = driver.page_source
        driver.close()

        links, texts = [], []

        soup = BeautifulSoup(html, "html.parser")
        a_els = soup.find_all('a', {'class', 'Lg33y'})

        for a_el in a_els:
            links.append(f"https://forbes.ru{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            p_els = soup.find_all('p', {'class':'yl27R'})

            for p_el in p_els:
                text = self.preprocess_text([p_el.text])[0]
                texts.append(text)

        return texts
    
    def sports_ru_parser(self, query:str) -> list:

        url = self.create_url('https://www.sports.ru/search/?query=', query)
        link, links, texts = '', [], []

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class': 'overBox'})
        soup = BeautifulSoup(str(div_el), "html.parser")
        a_el = soup.find_all('a')[0]

        link = a_el['href']

        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        h_els = soup.find_all('h2', {'class':'titleH2'})

        for h_el in h_els:
            soup = BeautifulSoup(str(h_el), "html.parser")
            a_el = soup.find_all('a')[0]
            links.append(a_el['href'])

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            div_els = soup.find_all('div', {'class':'material-item__content js-mediator-article'})

            soup = BeautifulSoup(str(div_els), "html.parser")
            p_els = soup.find_all('p')

            for p_el in p_els:
                text = self.preprocess_text([p_el.text])[0]
                texts.append(text)

        return texts

    def village_parser(self, query:str) -> list:

        url = self.create_url('https://www.the-village.ru/search?query=', query)
        links, texts = [], []

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        a_els = soup.find_all('a', {'class':'screens-SearchResult-_-SearchResultItem--SearchResultItem__link'})

        for a_el in a_els:
            links.append(f"https://www.the-village.ru{a_el['href']}")

        for link in links[:self.link_limit]:
            html = requests.get(link).text
            soup = BeautifulSoup(html, "html.parser")

            div_el = soup.find_all('div', {'class':'article-text'})

            soup = BeautifulSoup(str(div_el), "html.parser")
            p_els = soup.find_all('p')

            texts.extend(self.preprocess_text(p_els))

        return texts

    # def flow_parser(self, query:str) -> list:

    #     url = self.create_url('https://the-flow.ru/catalog/search/index?title=', query)
    #     links, texts = [], []

    #     html = requests.get(url).text

    #     soup = BeautifulSoup(html, "html.parser")

    #     a_els = soup.find_all('a', {'class':'search_article_item__title'})

    #     for a_el in a_els:
    #         links.append(f"https://the-flow.ru{a_el['href']}")

    #     for link in links[:self.link_limit]:
    #         html = requests.get(link).text
    #         soup = BeautifulSoup(html, "html.parser")

    #         div_el = soup.find_all('div', {'class':'article__text'}) 

    #         soup = BeautifulSoup(str(div_el), "html.parser")
    #         p_els = soup.find_all('p')

    #         texts.extend(self.preprocess_text(p_els))

    #     return texts


    def parse(self, name, lim=5000):
        ria = self.parse_text_ria(name)
        cosmo = self.parse_text_cosmo(name)
        mh = self.parse_text_mh(name)
        tatler = self.tatler_parser(name)
        sobaka = self.sobaka_parser(name)
        esquire = self.esquire_parser(name)
        kommersant = self.kommersant_parser(name)
        #rbc = self.rbc_parser(name)
        dp = self.dp_parsing(name)
        forbes = self.forbes_parser(name)
        sports_ru = self.sports_ru_parser(name)
        village = self.village_parser(name)
        #flow = self.flow_parser(name)

        parsed = ria + cosmo + mh + tatler + sobaka + esquire + kommersant + dp + forbes + sports_ru + village
 
        for i in range(len(parsed)):
            parsed[i] = parsed[i][:lim]

        return parsed 


    def translate_ru_to_en(self, corpus):
        translated = []
        for sentence in corpus:
            translated.append(self.translator_ru_to_en.translate(text=sentence))
        return translated


    def qg_en_to_en(self, corpus):
        qg = []
        for i in corpus:
            qg.append(self.nlp(i))
        return qg


    def translate_en_to_ru(self, corpus):
        translated = []
        for t in corpus:
            for sentence in t:
                translated.append(self.translator_en_to_ru.translate(text=sentence))
        return translated


    def predict(self, name):
        corpus = self.parse(name, lim=1000)
        self.preprocess_text(corpus)
        print(corpus)
        ru_to_en = self.translate_ru_to_en(corpus)
        qg = self.qg_en_to_en(ru_to_en)
        en_to_ru = self.translate_en_to_ru(qg)
        return en_to_ru