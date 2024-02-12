from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
import logging
from scrapy import signals
from datetime import *

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

#import selenium
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#import modules
import time

class FragranceDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.driver = None
        self.load_mode = 'none'

    def process_request(self, request, spider):
        try:
            if spider.mode == 0:
                self.restart_driver('normal')
                self.driver.get(request.url)
                time.sleep(1)
                while True:
                    try:
                        elements = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-1qe8tjm'))
                        )
                        if len(elements) >= 1:
                            break
                    except:
                        pass
                elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.css-1qe8tjm')
                for element in elements:
                    self.driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
                    time.sleep(0.5)   
            elif spider.mode == 1:
                self.restart_driver('eager')
                self.driver.get(request.url)
                dealy_time = 0
                acquired_count = 0
                while True:
                    try:
                        WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'h2[data-at="about_the_product_title"]'))
                        )
                        acquired_count += 1
                        WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="ingredients"]/div'))
                        )
                        acquired_count += 1
                        break
                    except:
                        # print(self.driver.current_url)
                        if self.driver.current_url.find('search?') != -1:
                            break
                        if acquired_count >= 1:
                            break
                        dealy_time += 1
                        if dealy_time >= 10:
                            break
            return HtmlResponse(self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)                                
        except Exception as e:
            print(f'{str(e)}')
            return HtmlResponse(self.driver.current_url, body='', encoding='utf-8', request=request)

    def restart_driver(self, load_mode):
        if self.load_mode == load_mode:
            return
        self.load_mode = load_mode
        if self.driver is not None:
            self.driver.quit()
        proxy_username = '14a5457296037'
        proxy_password = 'e18d25498f'
        seleniumwire_options = {
            'proxy': {
                'https': f'socks5://{proxy_username}:{proxy_password}@198.143.21.188:12324',
            },
        }

        # other Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.page_load_strategy = self.load_mode
        self.driver = webdriver.Chrome(options = chrome_options, seleniumwire_options = seleniumwire_options)
        self.driver.request_interceptor = lambda r: self.request_interceptor(r)
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self):
        print('end')
        self.driver.close()
    
    def request_interceptor(self, request):
        if request.path.endswith(('.png', '.svg', '.gif', '.jpg')):
            request.abort()


class FragranceSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
