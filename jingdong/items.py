import scrapy


class JingdongItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    store = scrapy.Field()
    info = scrapy.Field()
    comment = scrapy.Field()
    good_comment = scrapy.Field()
    bad_comment = scrapy.Field()