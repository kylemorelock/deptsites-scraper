import csv, os, glob
import html
from scrapy import Request
from scrapy.spiders import Spider
from deptsites_scraper.items import BioItem
from bs4 import BeautifulSoup

from scrapy.shell import inspect_response

class LTISpider(Spider):

    name = "lti_spider_delta"
    allowed_domains = ["www.lti.cs.cmu.edu"]
    attributes_blacklist = [
        "class", "id", "style", "href","align", "target"
    ]
    start_urls = ('http://www.lti.cs.cmu.edu/directory/all/154/1','http://www.lti.cs.cmu.edu/directory/all/154/1?page=1','http://www.lti.cs.cmu.edu/directory/all/154/2728','http://www.lti.cs.cmu.edu/directory/all/154/200')

    def parse(self, response):

        url_ext_xpath = "//tr/td/div/span[contains(@class, 'field-content')]/a/@href"
        url_exts = response.xpath(url_ext_xpath).extract()
        for ext in url_exts:
            print(ext)
            url = "http://www.lti.cs.cmu.edu" + ext
            req = Request(url, callback=self.parseBioPages, dont_filter=True)
            yield req

    def parseBioPages(self, response):
        bio_item = BioItem()
        homepage_xpath = "//div[@class='contact_info']/p[last()]/a/@href"
        bio_xpath = "//div[@class='field-item even']/p"
        full_name_xpath = "//h1/text()"
        title_xpath = "///div[contains(@class, 'field field-name-field-computed-prof-title field-type-computed field-label-hidden')]/div[contains(@class, 'field-items')]/div[contains(@class, 'field-item even')]/text()"
        email_xpath = "//div/p[contains(.,'@')]/text()"
        image_url_xpath = "//div/img/@src"
        bio_item['image_url'] = response.xpath(image_url_xpath).extract()
        bio_item['department'] = "Language Technologies Institute"
        bio_item['department_url'] = response.url
        email = response.xpath(email_xpath).extract()
        full_name = response.xpath(full_name_xpath).extract()
        if len(email) == 1:
            email = email[0].replace("Email: ", "")
            email = email.replace("\xa0", "")
        full_name = full_name[0].replace("\n", "")
        full_name = full_name.replace("&nbsp", " ")
        full_name = full_name.strip()
        home_page = response.xpath(homepage_xpath).extract()
        if len(home_page) >= 1 and type(home_page) == list:
            home_page = [url for url in home_page if url[0] != '/']
        if len(home_page) >= 1 and type(home_page) == str and home_page[0] =='/':
            home_page = ''
        bio_item['email'] = email
        bio_item['title'] = response.xpath(title_xpath).extract()
        bio_item['full_name'] = full_name
        bio_item['homepage'] = home_page
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
        bio_item['biography'] = html.unescape(bio_item['biography'])

        return bio_item