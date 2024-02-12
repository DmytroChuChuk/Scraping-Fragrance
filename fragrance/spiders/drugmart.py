from scrapy import Spider
import os
from time import sleep
from scrapy.selector import Selector
import scrapy
from fragrance.items import FragranceItem
from scrapy.utils.defer import maybe_deferred_to_future
class SephoraSpider(scrapy.Spider):
    name = "drugmart"
    allowed_domains = ["shop.shoppersdrugmart.ca"]     
    def start_requests(self):
       url = "https://shop.shoppersdrugmart.ca/Shop/Categories/Beauty/Fragrance/c/FS-Fragrance?sort=trending&page=0"
       self.mode = 0
       self.total_count = 0
       self.acquired_item_count = 0
       self.current_page = 0
       yield scrapy.Request(url=url, callback=self.parse)
            
    async def parse(self, response):
        try:
            if self.total_count == 0:
                self.total_count = self.parsePageCount(response)
            products = response.css("a.css-klx76")
            for product in products:
                item = FragranceItem()
                item['name'] = product.css('span.ProductTile-name::text').get()
                item['price'] = product.css('b.css-1f35s9q').css('span::text').get()
                item['image_url'] = product.css('img').attrib['src']
                
                #Here get description, ingredients
                self.mode = 1
                url_for_detail = "https://www.sephora.com/" + product.attrib['href']
                request_for_detail = scrapy.Request(url_for_detail)
                deferred = self.crawler.engine.download(request_for_detail)
                response_for_detail = await maybe_deferred_to_future(deferred)

                item['description'] = self.parseDescription(response_for_detail)
                item['ingredients'] = self.parseIngredients(response_for_detail)
                self.acquired_item_count += 1
                yield item            

            #Go to next page
            self.current_page += 1
            next_page = f'https://www.sephora.com/ca/en/shop/fragrance?currentPage={self.current_page}'
            if self.acquired_item_count < int(self.total_count):
                yield response.follow(next_page, self.parse) 
        except Exception as e:
            print(f'{str(e)}')         
    #Custom functions
    def parsePageCount(self, response):
        element = response.css('p:contains("Results")')
        if element:
            return element.css('::text').get().split()[0]
        pass
    def parseIngredients(self, response):
        try:
            ingredients = response.xpath('//*[@id="ingredients"]/div//text()').get()
            if len(description) > 0:
                return description
            return ''
        except Exception as e:
            # print(f'{str(e)}')
            return ''

    def parseDescription(self, response):
        try:
            description = response.css('h2[data-at="about_the_product_title"]').xpath('./following-sibling::div[2]/div[2]//text()').getall()
            if len(description) > 0:
                return description
            return ''
        except Exception as e:
            # print(f'{str(e)}')
            return ''