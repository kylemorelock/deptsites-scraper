import csv, os, glob
from scrapy import Request
from scrapy.spiders import Spider
from deptsites_scraper.items import BioItem
from bs4 import BeautifulSoup

from scrapy.shell import inspect_response

class DeansOfficeSpider(Spider):

    name = 'deans_office'
    allowed_domains = ["www.cs.cmu.edu"]

    def start_requests(self):
        yield Request('http://www.cs.cmu.edu/about-dean', self.parse)
    
    def parse(self, response):

        bio_item = BioItem()
        homepage_xpath = '//div/p[1]/a/text()'
        bio_xpath = '//p'
        image_url_xpath = '//div/img/@src/text()'
        full_name_xpath = "//div[contains(@class, 'field-item even')]/h2/text()"
        bio_item['department'] = "Dean's Office"
        bio_item['department_url'] = response.url
        bio_item['title'] = "Dean, CMU School of Computer Science"
        bio_item['homepage'] = response.xpath(homepage_xpath).extract()
        all_p_tags = response.xpath(bio_xpath).extract()
        trigger = "<p><strong>Biographical Sketch:</strong></p>"
        for i in range(0,len(all_p_tags)):
            if all_p_tags[i] == trigger:
                trigger_index = i
        bio = all_p_tags[trigger_index + 1: len(all_p_tags) - 3]
        bio_item['biography'] = bio
        bio_item['image_url'] = response.xpath(image_url_xpath).extract()
        bio_item['full_name'] = response.xpath(full_name_xpath).extract()

        print(bio_item)
        return bio_item
