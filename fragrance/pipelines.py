# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class FragrancePipeline:
    def open_spider(self, spider):
        self.file = open('items-0.json', 'w')
    
    def close_spider(self, spider):
        self.file.close()
    
    def process_item(self, item, spider):
        block_size = 30
        try:
            line = json.dumps(ItemAdapter(item).asdict()) + "\n"
            self.file.write(line)
            if spider.acquired_item_count % block_size == 0 and spider.acquired_item_count > 0:
                self.file.close()
                #open new file
                self.file = open(f'items-{int(spider.acquired_item_count / block_size)}.json', 'w')
        except:
            print('Error in item saving!')
        return item
