# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from datetime import datetime


class NewsspiderPipeline(object):

    def process_item(self, item, spider):
        if not os.path.exists('./news'):
            os.mkdir('./news')

        today = datetime.now().strftime('%Y/%m/%d')
        # if item['time'] == today:
        #     return None
        # with open('{}-{}-news.txt'.format(item['name'], item['cat']), 'a') as file:
        with open('news/{}-news.txt'.format(item['name']), 'a', encoding='utf8') as file:
            file.write("{}\n".format(item['content']))

        return item
