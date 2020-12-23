import requests
from path import Path
import time
import json

class Categorical_Serach():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }

    def __init__(self, start_url):
        self.start_url = start_url

    def parse_cat(self, url):
        response = requests.get(url, headers=self.headers)
        data: dict = response.json()

        categories = {}

        for i in data:
            categories[i['parent_group_code']] = i['parent_group_name']

        return categories

    def constract_url(self):
        initial_url = 'https://5ka.ru/api/v2/special_offers/?categories=&ordering=&page=2&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store='
        list_urls_to_pars = []
        for i in self.parse_cat(self.start_url):
            list_urls_to_pars.append(initial_url.replace('?categories=&', f'?categories={i}&'))
        return list_urls_to_pars

    def run_cat_search(self):
        datas = self.parse_cat(self.start_url)
        return datas

ttt = Categorical_Serach("https://5ka.ru/api/v2/categories/")

print(ttt.constract_url())
