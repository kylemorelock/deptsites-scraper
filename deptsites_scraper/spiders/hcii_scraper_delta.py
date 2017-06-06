import csv, os, glob
from scrapy import Request
from scrapy.spiders import Spider
from deptsites_scraper.items import BioItem
from bs4 import BeautifulSoup

from scrapy.shell import inspect_response

class HCIISpider(Spider):

    name = "hcii_spider_delta"
    allowed_domains = ["www.hcii.cmu.edu"]
    attributes_blacklist = [
        "class", "id", "style", "href","align"
    ]
    start_urls = ('http://www.hcii.cmu.edu/people/faculty','http://www.hcii.cmu.edu/people/affiliated-faculty','http://www.hcii.cmu.edu/people/special-faculty','http://www.hcii.cmu.edu/people/adjunct-faculty')
        

    def parse(self, response):

        url_ext_xpath = '//h3/a/@href'
        url_exts = response.xpath(url_ext_xpath).extract()
        for ext in url_exts:
            print(ext)
            url = "http://www.hcii.cmu.edu" + ext
            req = Request(url, callback=self.parseBioPages, dont_filter=True)
            yield req

    def parseBioPages(self, response):
        bio_item = BioItem()
        homepage_xpath = "//div[@class='panel-pane pane-entity-field pane-node-field-up2-webpage']/a/@href"
        bio_xpath = "//td/p  | //div[contains(@class, 'panel-pane pane-entity-field pane-node-field-up2-bio')]/p"
        title_xpath = "//div/h2[@class='a-subtitle--primary o-card__subtitle o-card__subtitle--primary']/text()"
        full_name_xpath = "//h1/text()"
        email_xpath = "//div/div[@class='panel-pane pane-entity-field pane-node-field-up2-email']/a/text()"
        image_url_xpath = "//div[last()]/img/@src"
        bio_item['image_url'] = response.xpath(image_url_xpath).extract()
        bio_item['department'] = "Human-Computer Interaction Institute"
        bio_item['department_url'] = response.url
        bio_item['email'] = response.xpath(email_xpath).extract()
        bio_item['full_name'] = response.xpath(full_name_xpath).extract()
        bio_item['full_name'] = bio_item['full_name'][0].strip()
        bio_item['title'] = response.xpath(title_xpath).extract()
        if len(bio_item['title']) == 1:
            bio_item['title'] = bio_item['title'][0].strip()
        bio_item['homepage'] = response.xpath(homepage_xpath).extract()
        bio_item['biography'] = response.xpath(bio_xpath).extract()
        bio_item['biography'] = ' '.join(bio_item['biography'])
        soup = BeautifulSoup(bio_item['biography'], 'html.parser')
        for tag in soup.recursiveChildGenerator():
            try:
                print(tag.attrs)
                tag.attrs = dict((key, value) for key, value in tag.attrs.items() if key not in self.attributes_blacklist)
            except AttributeError:
                pass
        
        bio_item['biography'] = soup.prettify()

        return bio_item
        