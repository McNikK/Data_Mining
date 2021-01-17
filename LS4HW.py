import scrapy
import pymongo


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    css_query = {
        'brands': 'div.TransportMainFilters_block__3etab a.blackLink',
        'pagination': 'div.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': "div.SerpSnippet_titleWrapper__38bZM a.blackLink",
    }

    data_query = {
        'title': lambda resp: resp.css('div.AdvertCard_advertTitle__1S1Ak::text ').get(),
        'url': lambda resp: resp.url,
        "price": lambda resp: float(resp.css('div.AdvertCard_price__3dDCr::text').get().replace("\u2009", '')),
        "features": lambda resp: resp.css('div.AdvertCard_descriptionInner__KnuRi::text').get()
    }

    def parse(self, response, **kwargs):
        brand_links = response.css(self.css_query['brands'])
        yield from self.gen_task(response, brand_links, self.brand_parse)

    def brand_parse(self, response):
        pagination_link = response.css(self.css_query['pagination'])
        yield from self.gen_task(response, pagination_link, self.brand_parse)
        ads_links = response.css(self.css_query['ads'])
        yield from self.gen_task(response, ads_links, self.ads_pars)

    def ads_pars(self, response):
        data = {}
        for key, selector in self.data_query.items():
            try:
                data[key] = selector(response)
            except (ValueError, AttributeError):
                continue
        print(data) # переставил принт тут если что останов
        db = pymongo.MongoClient()['DM_NVK'][self.name]
        db.insert_one(data)


    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib["href"], callback=callback)

