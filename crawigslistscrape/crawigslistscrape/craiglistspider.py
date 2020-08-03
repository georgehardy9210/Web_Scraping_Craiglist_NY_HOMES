import os
import scrapy
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
from items import CraigslistscrapeItem

class RealestateSpider(scrapy.Spider):


       name = 'realestate_loader'

       start_urls = ['https://newyork.craigslist.org/d/real-estate/search/rea/']


       try:
            os.remove('results.csv')
       except OSError:
            pass


       def __init__(self):

           self.lat = ""
           self.lon = ""

       def start_request(self):
           yield scrapy.Request('https://newyork.craigslist.org/d/real-estate/search/rea', callback=self.parse)

       def parse(self, response):

          all_ads = response.xpath('//p[@class="result-info"]')
          for ads in all_ads:

            # details_link = The Link to the Detail page that contains the geo data #
             details_link = ads.xpath(".//a[@class='result-title hdrlnk']/@href").get()

            # get GEO data from details link - and come back with geo data for loader #
             yield response.follow(url=details_link, callback=self.parse_detail)

            #
             loader = ItemLoader(item=CraigslistscrapeItem(),selector=ads,response=response)
             loader.add_xpath("price",".//span[@class='result-price']/text()")
             loader.add_xpath("date",".//time[@class='result-date']/text()")
             loader.add_xpath("title",".//a[@class='result-title hdrlnk']/text()")
             loader.add_xpath("hood",".//span[@class='result-hood']/text()")
             loader.add_xpath("details_link",".//a[@class='result-title hdrlnk']/@href")
             loader.add_value("lon",self.lon)
             loader.add_value("lat",self.lat)
             yield loader.load_item()

          # Get the next 25 properties from 'next page' - persist until no more #
          next_page = response.xpath("//a[@class='button next']/@href").get()
          if next_page:
              yield response.follow(url=next_page, callback=self.parse)



       def parse_detail(self,response):

            self.lon = response.xpath('//meta[@name="geo.position"]/@content').get().split(";")[0]
            self.lat = response.xpath('//meta[@name="geo.position"]/@content').get().split(";")[1]


if __name__ == "__main__":


      cl = CrawlerProcess(settings={
      "FEEDS": {
           "results.csv": {"format": "csv"},
       }
       })
      cl.crawl(RealestateSpider)
      cl.start()
