import scrapy
from ..items import ProductItem
from scrapy import signals
from dataclasses import dataclass


@dataclass
class Product:
    name: str = None
    info: str = None
    price: int = None
    link: str = None


class ProshopSpider(scrapy.Spider):
    name = 'Proshop_Spider'
    allowed_domains = ['proshop.dk']

    def __init__(self, product_name=None, *args, **kwargs):
        super(ProshopSpider, self).__init__(*args, **kwargs)
        self.product_name = product_name
        self.products = []

    def start_requests(self):
        if self.product_name:
            url = f'https://www.proshop.dk/?s={self.product_name.replace(" ", "+")}'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for product_li in response.xpath('//ul[@id="products"]/li[contains(@class, "row toggle")]'):
            item = ProductItem()
            item['name'] = product_li.xpath('.//a[@class="site-product-link"]/h2/text()').get()
            item['info'] = product_li.xpath('.//div[@class="truncate-overflow"]/text()').get()
            item['price'] = product_li.xpath('.//span[contains(@class,"site-currency-lg")]/text()').get()
            item['link'] = response.urljoin(product_li.xpath('.//a[contains(@class,"site-product-link")]/@href').get())

            self.products.append(Product(item['name'], item['info'], item['price'], item['link']))
            yield item

    """
        Following function connects the spider_closed signal to the spider_closed method.
        :param crawler: The crawler object that will be used to connect the signal to the method.
    """
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ProshopSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    """
        Following function is called when the spider is closed. 
        It prints the products scraped by the spider.
    """

    def spider_closed(self, reason):
        if reason == 'finished':
            for i, product in enumerate(self.products):
                print(f'{i + 1}: Name: {product.name}\nInfo: {product.info}\nPrice: {product.price}\nLink: {product.link}')
        else:
            print(f'Spider closed with reason: {reason}')
