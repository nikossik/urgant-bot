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

    for word in query.split():
        url += f"{word}+"
    url = url[:-1]

    print(url)

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class' : 'b-media__title-link'})

    links, texts = [], []

    for a_el in a_els:
        links.append(f"http://sobaka.ru{a_el['href']}")

    for link in links:
        html = requests.get(link).text
        soup = BeautifulSoup(html,  "html.parser")

        div_els = soup.find_all('div', 
                                {'class':'b-editors-text b-editors-text--lead'})

        text = str(div_els).replace('[', '').replace(']', '')
        text = re.sub(r"<.*?>", '', text)
        text = re.sub(r"\xa0|\n", '', text)
        text = re.sub(r"\s+", ' ', text)

        if text != '': texts.append(text)

    return texts