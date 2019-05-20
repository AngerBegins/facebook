# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field
from scrapy.loader.processors import TakeFirst


class FacebookspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class FacebookProfile(scrapy.Item):
    id = Field(output_processor=TakeFirst())
    name = Field(output_processor=TakeFirst())
    profile_url = Field(output_processor=TakeFirst())


    friend_with = Field()
    friend = Field()