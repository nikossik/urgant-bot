import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from deep_translator import GoogleTranslator
from tqdm import trange

translator = GoogleTranslator(source='russian', target='english')
link_limit = 10 #maximum links parsed

def create_url(url_start:str, query:str) -> str:
    url = url_start

    for word in query.split():
        url += f"{word}+"

    return url[:-1]

def preprocess_text(corpus, translator=translator, translate=False) -> list:
    for i in trange(len(corpus)):
        corpus[i] = str(corpus[i]).replace('[', '').replace(']', '').replace('/', '')
        corpus[i] = re.sub(r"<.*?>", "", corpus[i])
        corpus[i] = re.sub(r"[{}]|[()]", " ", corpus[i])
        corpus[i] = re.sub(r"\xa0|\n", " ", corpus[i])
        corpus[i] = re.sub(r"\s+", " ", corpus[i])

        if translate:
            try:
                corpus[i] = translator.translate(corpus[i]).replace('"', '')
                corpus[i] = re.sub(r"\'|\u200b|“", "", corpus[i])
            except:
                corpus[i] = ''

    while '' in corpus:
        corpus.remove('')

    while ' ' in corpus:
        corpus.remove(' ')

    return corpus

def tatler_parser(query:str, results:list) -> list:
    global link_limit

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

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class': 'body__inner-container'})

        text = str(div_el).replace('[', '').replace(']','')
        p_els = re.findall(r'<p>(.*?)</p>', text)

    results.extend(preprocess_text(p_els))

def sobaka_parser(query:str, results:list) -> list:
    global link_limit
    
    url = create_url('https://www.sobaka.ru/search/all?q=', query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class' : 'b-media__title-link'})

    for a_el in a_els:
        links.append(f"http://sobaka.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html,  "html.parser")

        div_els = soup.find_all('div', {'class':'b-editors-text b-editors-text--lead'})

        preprocessed_text = preprocess_text(div_els)

        if len(preprocessed_text) != 0 : results.extend(preprocess_text(div_els))

def esquire_parser(query:str, results:list) -> list:
    global link_limit
    
    url = create_url("https://esquire.ru/search/?query=", query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    div_els = soup.find_all('div', {'class':'article-listed is-item'})
    
    for div_el in div_els[:10]:
        for a_el in div_el.find_all('a'):
            links.append(f"https://esquire.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        text = soup.find_all('div', {'class':'text-page'})
        p_els = re.findall(r'<p>(.*?)</p>', str(text))

        results.extend(preprocess_text(p_els))

def kommersant_parser(query:str, results:list) -> list:
    global link_limit
    
    url = create_url('https://www.kommersant.ru/search/results?search_query=', query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html,"html.parser")

    a_els = soup.find_all('a', {'class':'uho__link uho__link--overlay'})

    for a_el in a_els:
        links.append(f"https://www.kommersant.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        p_els = soup.find_all('p', {'class':'doc__text'})

        results.extend(preprocess_text(p_els))

def rbc_parser(query:str, results:list) -> list:
    global link_limit
    
    url = create_url('https://www.rbc.ru/search/?project=rbcnews&query=', query)
    links = []
    
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'search-item__link'})
    
    for a_el in a_els:
        links.append(a_el['href'])

    for link in links[:link_limit]: 
        html  = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        p_els = soup.find_all('p')

        results.extend(preprocess_text(preprocess_text(p_els)))

def dp_parsing(query:str, results:list) -> list:
    global link_limit

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

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_els = soup.find_all('div', {'class': 'paragraph paragraph-text'})

        for div_el in div_els:
            text = preprocess_text([div_el.text])[0]
            texts.append(text)

    results.extend(texts)

def forbes_parser(query:str, results:list) -> list:
    global link_limit
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

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        p_els = soup.find_all('p', {'class':'yl27R'})

        results.extend(preprocess_text(p_els))

    print(results)

def sports_ru_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url('https://www.sports.ru/search/?query=', query)
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

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_els = soup.find_all('div', {'class':'material-item__content js-mediator-article'})

        soup = BeautifulSoup(str(div_els), "html.parser")
        p_els = soup.find_all('p')[:-2]

        texts = preprocess_text(p_els)
        results.extend(texts)

def village_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url('https://www.the-village.ru/search?query=', query)
    links, texts = [], []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'screens-SearchResult-_-SearchResultItem--SearchResultItem__link'})

    for a_el in a_els:
        links.append(f"https://www.the-village.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class':'article-text'})

        soup = BeautifulSoup(str(div_el), "html.parser")
        p_els = soup.find_all('p')

        results.extend(preprocess_text(p_els))

def flow_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url('https://the-flow.ru/catalog/search/index?title=', query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'search_article_item__title'})

    for a_el in a_els:
        links.append(f"https://the-flow.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class':'article__text'}) 

        soup = BeautifulSoup(str(div_el), "html.parser")
        p_els = soup.find_all('p')

        results.extend(preprocess_text(p_els))
    print(results)

def elle_parser(query:str, results:list) -> list:
    global link_limit 

    url = 'https://www.elle.ru/'
    links = []

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    sleep(2)

    search_button = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/header/div[2]/div[1]/div[1]/div/nav/ul/li[10]/button')
    search_button.click()

    search_input = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div/div[1]/input')
    search_input.send_keys(str(query))

    sleep(1)

    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'announce-inline__title-link'})

    for a_el in a_els:
        links.append(f"https://elle.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_els = soup.find_all('div', {'class':'block-text'})

        soup = BeautifulSoup(str(div_els), "html.parser")
        
        p_els = soup.find_all('p')

        results.extend(preprocess_text(p_els))

def glamour_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url("https://www.glamour.ru/search?q=", query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'summary-item-tracking__hed-link summary-item__hed-link'})

    for a_el in a_els:
        links.append(f"https://glamour.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class':'body__inner-container'})

        soup = BeautifulSoup(str(div_el), "html.parser")
        p_els = soup.find_all('p')

        results.extend(preprocess_text(p_els))

def afisha_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url("https://www.afisha.ru/search/?query=", query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'_3NqYW DWsHS _3lmHp wkn_c'})

    for a_el in a_els:
        links.append(f"https://afisha.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class':'article'})
        soup = BeautifulSoup(str(div_el), "html.parser")

        p_els = soup.find_all('p')

        results.extend(preprocess_text(p_els))

def rtvi_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url("https://rtvi.com/search/?q=", query)
    links = []

    html = requests.get(url).text

    soup = BeautifulSoup(html, "html.parser")
    div_els = soup.find_all('div', {'class' : 'zag'})
    
    soup = BeautifulSoup(str(div_els), "html.parser")
    a_els = soup.find_all('a')

    for a_el in a_els:
        links.append(f"https://rtvi.com{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")

        div_el = soup.find_all('div', {'class' : 'text'})
        soup = BeautifulSoup(str(div_el), "html.parser")

        p_els = soup.find_all('p')

        results.extend(preprocess_text(p_els))

def tvrain_parser(query:str, results:list) -> list:
    global link_limit

    url = create_url("https://tvrain.ru/archive/?query=", query)
    links = []

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    a_els = soup.find_all('a', {'class':'chrono_list__item__info__name chrono_list__item__info__name--nocursor'})

    for a_el in a_els:
        links.append(f"https://tvrain.ru{a_el['href']}")

    for link in links[:link_limit]:
        html = requests.get(link).text
    
        soup = BeautifulSoup(html, "html.parser")
        div_els = soup.find_all('div', {'class' : 'article-full__text'})

        soup = BeautifulSoup(str(div_els), "html.parser")
        p_els = soup.find_all('p')\
    
        results.extend(preprocess_text(p_els))
