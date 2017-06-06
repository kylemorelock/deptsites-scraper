import csv 
import os
from scrapy import Request
from scrapy.spiders import Spider
from deptsites_scraper.items import BioItem
from bs4 import BeautifulSoup

from scrapy.shell import inspect_response

class MachineLearningSpider(Spider):

    name = 'machine_learning'
    allowed_domains = ["www.ml.cmu.edu"]
    attributes_blacklist = ['class','id']

    # This function opens a csv file located in the project_path and navigates to 
    # 'department_url', and appends requests with the value stored under the department_url
    # column.

    def start_requests(self):
        requests = []
        project_path = os.path.realpath(os.getcwd())
        input_filepath = os.path.realpath(os.path.join(project_path, "ml_people_test.csv"))
        with open(input_filepath) as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                bio_item = BioItem()
                
                for field, value in row.items():
                    bio_item[field] = value

                if row['department_url'] != '':
                    req = Request(row['department_url'])
                    req.meta['bio_item'] = bio_item
                    requests.append(req)
        return requests


    def parse(self, response):
        bio_item = response.meta['bio_item']
        homepage_xpath = "//div/p/a/@href"
        bio_xpath = "//div/div/div/div/div/p[2] | //div/div/div/div/div/text()"
        full_name_xpath = "//div/h1"
        title_xpath = "//div/div[@class='content']/h2"
        bio_item['homepage'] = response.xpath(homepage_xpath).extract()
        bio_item['full_name'] = response.xpath(full_name_xpath).extract()
        bio_item['title'] = response.xpath(title_xpath).extract()
        bio_item['biography'] = response.xpath(bio_xpath).extract()
        bio_item['biography'] = ' '.join(bio_item['biography'])
        soup = BeautifulSoup(bio_item['biography'], 'html.parser')
        for tag in soup.recursiveChildGenerator():
            try:
                print(tag.attrs)
                tag.attrs = [(key, value) for key, value in tag.attrs.items() if key not in self.attributes_blacklist]
            except AttributeError:
                pass

        bio_item['biography'] = soup.prettify()

        return bio_item