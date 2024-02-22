from bs4 import BeautifulSoup
import requests

def parsing_akipress():
    url = 'https://akipress.org/'
    response = requests.get(url=url)
    print(response)
    soup = BeautifulSoup(response.text, 'lxml')
    # print(soup)
    all_news = soup.find_all('a', class_='newslink')
    # print(all_news)
    n = 0
    for news in all_news:
        n += 1
        print(n, news.text)
        with open('news.txt', 'a+', encoding='utf-8') as news_file:
            news_file.write(f"{n}) {news.text}\n")

def parsing_laptops():
    url = 'https://www.ultra.kg/catalog/noutbuki-i-pk/noutbuki/'
    response = requests.get(url=url)
    print(response)
    soup = BeautifulSoup(response.text, 'lxml')
    # print(soup)
    all_laptops = soup.find_all('span', class_='middle')
    # print(all_laptops)
    n = 0
    for laptops in all_laptops:
        n += 1
        print(n, laptops.text)
# parsing_laptops()
    
def parsing_mnogosushi():
    url = 'https://mnogosushi.kg/category/pitstsy/'
    response = requests.get(url=url)
    print(response)
    soup = BeautifulSoup(response.text, 'lxml')
    foods = soup.find_all('div', class_='item_title')
    # print(foods)
    for food in foods:
        print(food.text)
parsing_mnogosushi()
