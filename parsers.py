import requests
from bs4 import BeautifulSoup
import re

def tatler_parser(query:str) -> list:
    url_parts = ['https://www.tatler.ru/search?q=','&sort=score+desc']
    links, texts = [], []

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

        for i in range(len(p_els)):
            p_els[i] = re.sub(r"<.*?>", "", p_els[i])
            p_els[i] = re.sub(r"\xa0|\n", "", p_els[i])
            p_els[i] = re.sub(r"\s+", " ", p_els[i])

        texts += p_els
    
    return texts

def sobaka_parser(query:str) -> list:
    url = 'https://www.sobaka.ru/search/all?q='
    links, texts = [], []

    for word in query.split():
        url += f"{word}+"
    url = url[:-1]

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class' : 'b-media__title-link'})

    for a_el in a_els:
        links.append(f"http://sobaka.ru{a_el['href']}")

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html,  "html.parser")

        div_els = soup.find_all('div', {'class':'b-editors-text b-editors-text--lead'})

        text = str(div_els).replace('[', '').replace(']', '')
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"\xa0|\n", " ", text)
        text = re.sub(r"\s+", " ", text)

        if text != '': texts.append(text)

    return texts

def esquire_parser(query:str) -> list:
    url = "https://esquire.ru/search/?query="
    texts, links = [], []

    for word in query.split():
        url+= f'{word}+'
    
    url = url[:-1]

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

        for i in range(len(p_els)):
            p_els[i] = re.sub(r"<.*?>", "", p_els[i])
            p_els[i] = re.sub(r"\xa0|\n", " ", p_els[i])
            p_els[i] = re.sub(r"\s+", " ", p_els[i])

        texts += p_els

    return texts

def kommersant_parser(query:str) -> list:
    url = 'https://www.kommersant.ru/search/results?search_query='
    links, texts = [], []

    for word in query.split():
        url += f'{word}+'
    url = url[:-1]

    html = requests.get(url).text
    soup = BeautifulSoup(html,"html.parser")

    a_els = soup.find_all('a', {'class':'uho__link uho__link--overlay'})

    for a_el in a_els:
        links.append(f"https://www.kommersant.ru{a_el['href']}")

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        p_els = soup.find_all('p', {'class':'doc__text'})

        text = str(p_els).replace('[', '').replace(']', '')
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"\xa0|\n", " ", text)
        text = re.sub(r"\s+", " ", text)

        texts.append(text)

    return texts
kommersant_parser('сергей лавров')