import csv, os, glob
from scrapy import Request
from scrapy.spiders import Spider
from deptsites_scraper.items import BioItem
from bs4 import BeautifulSoup

from scrapy.shell import inspect_response

class RoboticsInstituteSpider(Spider):

    name = 'robotics_institute'
    allowed_domains = ["www.ri.cmu.edu"]
    attributes_blacklist = [
        "class", "id", "style", "href",""
    ]

    def start_requests(self):
        requests = []
        input_path = os.path.join(os.getcwd(), "ri_input_csvs", "*.csv")
        for file in glob.glob(input_path):
            with open(file) as csvfile:
                csvreader = csv.DictReader(csvfile)
                for row in csvreader:
                    bio_item = BioItem()

                    for field, value in row.items():
                        bio_item[field] = value

                    if row['department_url'] != '':
                        print(row['department_url'])
                        req = Request(row['department_url'])
                        req.meta['bio_item'] = bio_item
                        requests.append(req)
        
        return requests

    def parse(self, response):
        bio_item = response.meta['bio_item']
        homepage_xpath = "//td[@height='10']/a/@href"
        bio_xpath = "//td[@class='td_text']/p"
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
