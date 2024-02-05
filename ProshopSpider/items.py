import scrapy


class ProductItem(scrapy.Item):
    name = scrapy.Field()
    info = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
