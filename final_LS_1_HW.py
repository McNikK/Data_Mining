import requests
from pathlib import Path
import time
import simplejson as json

class StatusCodeError(Exception):

    def __init__(self, txt):
        self.txt = txt

class Parser5ka_special:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }


    url_cat = 'https://5ka.ru/api/v2/special_offers/?categories=&ordering=&page=2&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store='

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


    def parse_cat(self, start_url):

        response = self._get_response(start_url, headers=self.headers)

        data: dict = response.json()

        categories = {}

        for i in data:
            categories[i['parent_group_code']] = i['parent_group_name']

        return categories

    def constract_url(self):
        list_urls_to_pars = {}
        cats  = self.parse_cat(self.start_url)
        for i in cats:
            new_url = self.url_cat.replace("categories=", f"categories={i}")
            list_urls_to_pars[f"{cats[i]}_код_{i}"] = new_url
        return list_urls_to_pars


    def parse(self, url):
        while url:
            response = self._get_response(url, headers=self.headers)
            data: dict = response.json()
            url = data['next']
            yield data.get('results', [])


    def run(self):
        for i in self.constract_url():
            with open(f'{i}.json', 'w',  encoding='UTF-8') as file:
                    file.write(i)
                    json.dump(self.parse(self.constract_url()[i]), file, ensure_ascii=False, iterable_as_array=True)

if __name__ == '__main__':
    parser  = Parser5ka_special("https://5ka.ru/api/v2/categories/")
    parser.run()