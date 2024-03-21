from ControllerDB.WebsiteSpiderDB import WebsiteSpiderDB, WebsiteSpider
from Controller.SpiderController import SpiderController

websiteSpiderDB = WebsiteSpiderDB()

class WebsiteSpiderController(SpiderController):  
  def getHistory(
    self, 
    spider_id
  ):
    return websiteSpiderDB.getHistory(
      spider_id=spider_id
    )
    
  def getArticles(
    self, 
    spider_id, 
    page = 0, 
    article_per_page = 10    
  ):
    return websiteSpiderDB.getArticles(
      spider_id=spider_id,
      page=page,
      article_per_page=article_per_page
    )
    
  def getCrawlRules(
    self,
    spider_id
  ):
    return websiteSpiderDB.getCrawlRule(
      spider_id=spider_id
    )
    
  def getSearchRules(
    self,
    spider_id
  ):
    return websiteSpiderDB.getSearchRules(
      spider_id=spider_id
    )
    
  def createSpider(
    self,
    url,
    delay=2,
    graphDeep=1,
    maxThread=1,
    fileTypes=[],
    keywords=[],
    subfolder=[]    
  ):
    return websiteSpiderDB.createSpider(
      url=url,
      delay=delay,
      graphDeep=graphDeep,
      maxThread=maxThread,
      fileTypes=fileTypes,
      keywords=keywords,
      subfolder=subfolder      
    )
    
  def updateSubFolder(
    self, 
    spider_id,
    subfolder=[]        
  ):
    return websiteSpiderDB.updateSpiderSubFolder(
      spider_id=spider_id,
      subfolder=subfolder
    )
    
  def updateSetting(
    self,
    spider_id,
    delay = 2.5, 
    graphDeep = 2, 
    maxThread = 1    
  ):
    return websiteSpiderDB.updateSetting(
      spider_id=spider_id,
      delay=delay,
      graphDeep=graphDeep,
      maxThread=maxThread
    )