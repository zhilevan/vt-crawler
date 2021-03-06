# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from vitrinbot.items import ProductItem
from vitrinbot.base import utils
import re

from vitrinbot.base.spiders import VitrinSpider

removeCurreny =utils.removeCurrency
getCurrency = utils.getCurrency


class MarkafoniSpider(VitrinSpider):
    name = 'markafoni'
    allowed_domains = ['markafoni.com']
    start_urls = ['https://www.markafoni.com/']
    xml_filename = 'markafoni-%d.xml'

    rules = (
        Rule(LinkExtractor(allow=('.com/(\w+)/$',))),
        Rule(LinkExtractor(allow=('.com/([\w-]+)-(\d+)/',))),
        Rule(LinkExtractor(allow=('/product/([\w-]+)-(\d+)/(\w+)/',))),
        Rule(LinkExtractor(allow=('/product/(\d+)/$',)), callback='parse_item'),
    )

    def parse_item(self, response):
        i = ProductItem()
        i['id'] = re.compile('product/(\d+)').findall(response.url)[0]
        i['url'] = response.url
        i['title'] = response.xpath('//p[@class="product-head-toptitle-first lh20"]/text()').extract()[0]

        i['category'] = response.xpath('//p[@class="product-head-toptitle-second"]/text()').extract()[0]
        i['brand'] = response.xpath("//a[@class='detail_name']/text()").extract()[0]

        description = ''
        for li in response.xpath("//div[@class='lh1-2 dgray']//li/text()").extract():
            description += li
        i['description'] = description

        specialPriceText = ''
        for price in response.xpath("//div[contains(@class,'buying_price')]/text()").extract():
            specialPriceText += price
        i['special_price'] = removeCurreny(specialPriceText)


        priceText = response.xpath("//del[contains(@class,'old_price')]/text()").extract()[0]
        i['price'] =removeCurreny(priceText)

        try:
            i['images'] =  response.xpath('//div[@id="thumbnails"]//img/@src').extract()
        except:
            i['images'] = ''
            self.log("HATA! image lar cekilemedi. Url: %s" %response.url)
        # i['images'] = response.xpath("//meta[@itemprop='image']/@content").extract()

        try:
            i['sizes'] = response.xpath("//div[@id='size_select']//label/text()").extract()
        except:
            i['sizes'] = ''
            self.log("sizes yok. Url: %s" %response.url)


        i['expire_timestamp']=i['colors'] = ''

        # i['currency'] = response.xpath('//div[@class="fl buying_price_tl green3"]/text()').extract()[0].strip()
        i['currency'] = getCurrency(priceText)

        return i



