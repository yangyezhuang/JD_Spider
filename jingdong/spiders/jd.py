import json
import scrapy
from scrapy import Request
from urllib.parse import quote
from ..items import JingdongItem


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['search.jd.com']
    keyword = quote('手机')
    max_page = 5  # 以单页爬取，一页30个商品
    start_url = 'https://search.jd.com/s_new.php?keyword={keyword}&page={page}&s={s}'
    info_url = 'https://item.jd.com/{id}.html'
    comment_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={id}'

    def start_requests(self):
        """
        生成初始请求
        :return: 初始请求
        """
        # 请求 商品列表页的第1页，获取前30个商品
        page = s = 1
        yield Request(url=self.start_url.format(keyword=self.keyword, page=page, s=s),
                      meta={'page': page, 's': s})

    def parse(self, response):
        '''
        列表页
        :param response:
        :return:
        '''
        lists = response.xpath('//ul[@class="gl-warp clearfix"]/li')
        for li in lists:
            item = JingdongItem()
            id = li.xpath('./@data-sku').extract_first()
            name = li.xpath('.//div[@class="p-name p-name-type-2"]/a/em/text()[1]').extract_first()
            # store = li.xpath('.//div[@class="p-shop"]//a/text()').extract_first()
            info_url = f'https://item.jd.com/{id}.html'
            price = li.xpath(f'.//strong[@class="J_{id}"]/i/text()').extract_first('')
            # item['store'] = store
            item['id'] = id
            item['name'] = name
            item['url'] = info_url
            item['price'] = price
            yield Request(url=info_url, callback=self.info_parse, meta={'item': item}, dont_filter=True)

        # page 代表半页，即30个商品
        page = response.meta['page'] + 1
        s = response.meta['s'] + 25
        if page < self.max_page * 2 + 1:
            # 回调解析后30个商品
            yield Request(url=self.start_url.format(keyword=self.keyword, page=page, s=s),
                          callback=self.parse, meta={'page': page, 's': s})

    def info_parse(self, response):
        '''
        解析详情页
        :param response:
        :return:
        '''
        item = response.meta['item']
        # id = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li[2]/@title').extract_first()
        # store = response.xpath('//div[@class="J-hove-wrap EDropdown fr"]//a/@title').extract_first()
        store = response.css('.J-hove-wrap.EDropdown.fr .item .name a::text').extract_first('')
        # info = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li/text()').extract()
        item['store'] = store
        # item['info'] = info
        id = item['id']
        comment_url = self.comment_url.format(id=id)
        yield Request(url=comment_url, callback=self.comment_parse, meta={'item': item}, dont_filter=True)

    def comment_parse(self, response):
        '''
        解析评论页
        :param response:
        :return:
        '''
        item = response.meta['item']
        dict = json.loads(response.text)['CommentsCount'][0]
        comment = dict.get('CommentCountStr', 0)
        good_comment = dict.get('GoodCountStr', 0)
        bad_comment = dict.get('PoorCountStr', 0)
        item['comment'] = comment
        item['good_comment'] = good_comment
        item['bad_comment'] = bad_comment
        yield item
