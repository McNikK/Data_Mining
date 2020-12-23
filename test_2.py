import requests
from path import Path
import time
import json

class StatusCodeError(Exception):

    def __init__(self, txt):
        self.txt = txt


class Parser5ka:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }

    def __init__(self, start_url):
        self.start_url = start_url

    def _get_response(self, url, **kwargs):
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code != 200:
                    raise StatusCodeError(f'status {response.status_code}')
                return response
            except (requests.exceptions.ConnectTimeout,
                    StatusCodeError):
                time.sleep(0.1)

    def parse(self, url):
        while url:
            response = self._get_response(url, headers=self.headers)
            data: dict = response.json()
            url = data['next']
            yield data.get('results', [])

    def save_file(self, file_name, data):
        with open(file_name, 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


class Categorical_Serach(Parser5ka):

    def __init__(self, start_url):
        super().__init__(start_url)

    def parse_cat(self, url):
        response = requests.get(url, headers=self.headers)
        data: dict = response.json()

        categories = {}

        for i in data:
            categories[i['parent_group_code']] = i['parent_group_name']

        return categories

    def constract_url(self):
        initial_url = 'https://5ka.ru/api/v2/special_offers/?categories=&ordering=&page=2&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store='
        list_urls_to_pars = {}
        cats  = self.parse_cat(self.start_url)
        for i in cats:
            new_url = initial_url.replace("?categories=&", f"?categories={i}&")
            list_urls_to_pars[f"Категория товара = {cats[i]}, Код категории {i}"] = new_url
        return list_urls_to_pars

    # def run(self):
    #     urls_to_pars = self.constract_url()
    #     for i in urls_to_pars.values():
    #         par = self.parse(i)
    #         with open('file_name.json', 'w', encoding='UTF-8') as file:
    #             json.dump(par, file, ensure_ascii=False)



if __name__ == '__main__':
    ttt = Categorical_Serach("https://5ka.ru/api/v2/categories/")
    x = ttt.parse('https://5ka.ru/api/v2/special_offers/?categories=870&ordering=&page=2&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store=')
    with open('FILE.json', 'w') as file:
        json.dump(x, file, ensure_ascii=False )

