import csv, os, glob
from scrapy import Request
from scrapy.spiders import Spider
from deptsites_scraper.items import BioItem
from bs4 import BeautifulSoup

from scrapy.shell import inspect_response

class ComputationalBiologySpider(Spider):

    name = 'cbd_scraper_delta'
    allowed_domains = ["www.cbd.cmu.edu"]
    attributes_blacklist = [
        "class", "id", "style", "href",""
    ]
    start_urls = ('http://www.cbd.cmu.edu/directory/faculty/voting-faculty/','http://www.cbd.cmu.edu/directory/faculty/affiliated-faculty/','http://www.cbd.cmu.edu/directory/faculty/visiting-faculty/','http://www.cbd.cmu.edu/directory/faculty/adjunct-faculty/')

    def parse(self, response):

        url_xpath = "//div/div[contains(@class, 'cn-entry')]/div/span/strong/a/@href"
        url_list = response.xpath(url_xpath).extract()
        for url in url_list:
            print(url)
            req = Request(url, callback=self.parseBioPages, dont_filter=True)
            yield req

    def parseBioPages(self, response):
        bio_item = BioItem()
        homepage_xpath = "//div/span/span[last()]/a/@href[1]"
        bio_xpath = "//div[@id='refHTML'] | //div[contains(@class, 'cn-biography')]/p"
        given_name_xpath = "//span[contains(@class, 'given-name')]/text()"
        family_name_xpath = "//span[contains(@class, 'family-name')]/text()"
        additional_name_xpath = "//span[contains(@class, 'additional-name')]/text()"
        email_xpath = "//a[contains(@class, 'value')]/text()"
        title_xpath = "//span[contains(@class, 'title notranslate')]/text()"
        image_url_xpath = "//img[contains(@class, 'cn-image photo')]/@srcset"
        bio_item['department'] = "Computational Biology"
        bio_item['department_url'] = response.url
        bio_item['email'] = response.xpath(email_xpath).extract()
        bio_item['title'] = response.xpath(title_xpath).extract()
        image_url = response.xpath(image_url_xpath).extract()
        bio_item['image_url'] = image_url[0].rstrip(" 1x")
        given_name = response.xpath(given_name_xpath).extract()
        family_name = response.xpath(family_name_xpath).extract()
        additional_name = response.xpath(additional_name_xpath).extract()
        if additional_name != []:
            bio_item['full_name'] = given_name[0] + " " + additional_name[0] + " " + family_name[0]
        else:
            bio_item['full_name'] = given_name[0] + " " + family_name[0]
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