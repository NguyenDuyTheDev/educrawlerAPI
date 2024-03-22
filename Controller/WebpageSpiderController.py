from ControllerDB.WebpageSpiderDB import WebpageSpiderDB, WebpageSpider
from Controller.SpiderController import SpiderController

webpageSpiderDB = WebpageSpiderDB()

class WebpageSpiderController(SpiderController):  
  def createWebpageSpider(
    self, 
    url, 
    crawlRules = [], 
    fileTypes = [], 
    keywords = []
  ):
    return webpageSpiderDB.createWebpageSpider(
      url=url,
      crawlRules=crawlRules,
      fileTypes=fileTypes,
      keywords=keywords
    )
    
  def updateCrawlRules(
    self, 
    spider_id,
    crawl_rules = []
  ):
    return webpageSpiderDB.updateWebpageCrawlRule(
      spider_id=spider_id,
      crawl_rules=crawl_rules
    )
    
  def getHistory(
    self, 
    spider_id
  ):
    return webpageSpiderDB.getHistory(
      spider_id=spider_id
    )
    
  def getArticles(
    self, 
    spider_id
  ):
    return webpageSpiderDB.getArticles(
      spider_id=spider_id
    )
    
  def getSpiders(self, page = 0, spiderPerPage = 10):
    return webpageSpiderDB.getSpiders(
      page=page,
      spiderPerPage=spiderPerPage
    )
    
  def getSpiderById(self, id):
    return webpageSpiderDB.getSpiderById(
      id=id
    )
    
  def getCrawlRules(self, spider_id):
    return webpageSpiderDB.getCrawlRule(
      spider_id=spider_id
    )