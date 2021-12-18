import requests
from bs4 import BeautifulSoup
import re

def create_url(url_start:str, query:str) -> str:
    url = url_start

    for word in query.split():
        url += f"{word}+"

    return url[:-1]

def preprocess_text(corpus) -> list:
    for i in range(len(corpus)):
        corpus[i] = str(corpus[i]).replace('[', '').replace(']', '')
        corpus[i] = re.sub(r"<.*?>", "", corpus[i])
        corpus[i] = re.sub(r"\xa0|\n", " ", corpus[i])
        corpus[i] = re.sub(r"\s+", " ", corpus[i])

    return corpus


def tatler_parser(query:str) -> list:
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

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class': 'body__inner-container'})

        text = str(div_el).replace('[', '').replace(']','')
        p_els = re.findall(r'<p>(.*?)</p>', text)

    return preprocess_text(p_els)

def sobaka_parser(query:str) -> list:
    url = create_url('https://www.sobaka.ru/search/all?q=', query)
    links, texts = [], []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class' : 'b-media__title-link'})

    for a_el in a_els:
        links.append(f"http://sobaka.ru{a_el['href']}")

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html,  "html.parser")

        div_els = soup.find_all('div', {'class':'b-editors-text b-editors-text--lead'})

        preprocessed_text = preprocess_text(div_els)

        if len(preprocessed_text) != 0 : texts.append(preprocess_text(div_els)[0])

    return texts

def esquire_parser(query:str) -> list:
    url = create_url("https://esquire.ru/search/?query=", query)
    texts, links = [], []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    div_els = soup.find_all('div', {'class':'article-listed is-item'})
    
    for div_el in div_els[:10]:
        for a_el in div_el.find_all('a'):
            links.append(f"https://esquire.ru{a_el['href']}")

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        text = soup.find_all('div', {'class':'text-page'})
        p_els = re.findall(r'<p>(.*?)</p>', str(text))

        texts += preprocess_text(p_els)

    return texts

def kommersant_parser(query:str) -> list:
    url = create_url('https://www.kommersant.ru/search/results?search_query=', query)
    print(url)
    links, texts = [], []

    html = requests.get(url).text
    soup = BeautifulSoup(html,"html.parser")

    a_els = soup.find_all('a', {'class':'uho__link uho__link--overlay'})

    for a_el in a_els:
        links.append(f"https://www.kommersant.ru{a_el['href']}")

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        p_els = soup.find_all('p', {'class':'doc__text'})
        #print(p_els)

        texts.append(preprocess_text(p_els)[0])

    return texts

def rbc_parser(query:str) -> list:
    url = create_url('https://www.rbc.ru/search/?project=rbcnews&query=', query)
    links, texts = [], []
    
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'search-item__link'})
    
    for a_el in a_els:
        links.append(a_el['href'])

    for link in links: 
        html  = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        p_els = soup.find_all('p')

        texts.append(preprocess_text(p_els)[0])

    return texts
