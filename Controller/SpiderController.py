from ControllerDB.SpiderDB import SpiderDB, Spider
spiderDB = SpiderDB()

class SpiderController():  
  def getTotalRuntime(self):
    return spiderDB.getTotalRuntime()
    
  def getTotalCrawlSuccess(self):
    return spiderDB.getTotalCrawlSuccess()

  def getTotalCrawlFail(self):
    return spiderDB.getTotalCrawlFail()

  def getAllSpiderRunningStatus(self):
    return spiderDB.getAllSpiderRunningStatus()

  def getTop10SpiderWithMostArticle(self):
    return spiderDB.getTop10SpiderWithMostArticle()

  def editSpider(
    self,
    spider_id,
    url = "",
    status = "Available",
    is_academic = False,
    keyword_ids = []
  ):
    spiderDB.updateKeywords(
      spider_id=spider_id, 
      keyword_ids=keyword_ids
    )
    
    return spiderDB.editSpider(
      spider_id=spider_id,
      url=url,
      status=status,
      is_academic=is_academic
    )
    
  def removeJobId(
    self, 
    spider_id
  ):
    return spiderDB.removeJobId(
      spider_id=spider_id
    )
    
  def deleteSpider(self, spider_id):
    return spiderDB.deleteSpider(spider_id=spider_id)
  
  def isWebsiteSpider(
    self, 
    spider_id
  ):
    return spiderDB.isWebsiteSpider(spider_id=spider_id)
  
  def isWebpageSpider(
    self, 
    spider_id
  ):
    return spiderDB.isWebpageSpider(spider_id=spider_id)
  
  def getSpiders(
    self,
    page = 0,
    spider_per_page = 10
  ):
    return spiderDB.getSpiders(
      page=page,
      spiderPerPage=spider_per_page
    )