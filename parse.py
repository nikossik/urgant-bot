from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests

celeb = input()

def parse_text_ria(name):
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
        for word in celeb.lower().split():
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

def parse_text_cosmo(celeb):
    url = "https://www.cosmo.ru/search/?query="

    for word in celeb.split():
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
        for word in celeb.lower().split():
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

def parse_text_mh(celeb):
    url = "https://www.mhealth.ru/search/?query="

    for word in celeb.split():
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
        for word in celeb.lower().split():
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

a = parse_text_ria(celeb)
print('----------')
b = parse_text_cosmo(celeb)
print('----------')
c = parse_text_mh(celeb)
print(a,'----------', b, '----------', c)