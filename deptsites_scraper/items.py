# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BioItem(Item):
    full_name = Field()
    email = Field()
    title = Field()
    department = Field()
    image_url = Field()
    homepage = Field()
    biography = Field()
    department_url = Field()
    photo_ext = Field()
    position = Field()
    homepages = Field()
    

class PageItem(Item):
    name = Field()
    url = Field()

