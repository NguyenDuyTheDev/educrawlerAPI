# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from educrawlerAPI import Singleton

class EducrawlercrawlerservicePipeline:
  def process_item(self, item, spider):
    return item

class DemoPipeline:
  def __init__(self) -> None:
    self.databaseAPI = Singleton()
  
  def open_spider(self, spider):
    pass
  
  def close_spider(self, spider):
    pass
  
  def process_item(self, item, spider):
    if item["crawlerType"] != "demo":
      print("Not Demo")
      return item
    print("Demo Pipeline is working!")
    
    isExisted = self.databaseAPI.getArticleByUrl(item["url"])
    print(isExisted)
    
    # Process Data
    title = ""
    if item["title"] is not None: 
      title = item["title"].replace("'", "").replace('"', '')
    
    # Save
    if isExisted[0] == True:
      self.databaseAPI.editArticle(
        article_id=isExisted[1]["Id"],
        title=title,
        domain=item["domain"],
        url=item["url"],
        content=item["reformatted_content"],
      )
    else:
      self.databaseAPI.createArticle(
        title=title,
        domain=item["domain"],
        url=item["url"],
        content=item["reformatted_content"],        
      )
      
    print("Save Success")
    return item