from typing import Any
from SpiderDB import SpiderDB, Spider

from datetime import datetime 
from ControllerDB.KeywordDB import Keyword, KeywordDB
 
keywordDB = KeywordDB()
 
class WebpageSpider(Spider):
  id: int
  url: str
  status: str
  crawlStatus: str
  delay: float
  graphDeep: int
  lastRunTime: datetime
  lastEndTime: datetime
  runTime: int
  maxThread: int
  isBlocked: bool
  createBy: int | None
  keywords: list[Keyword]
  
  def __init__(
    self, 
    id, 
    url, 
    status,
    crawlStatus,
    delay,
    graphDeep,
    lastRunTime,
    lastEndTime,
    runTime,
    maxThread,
    isBlocked,
    createBy,
    keywords
  ) -> None:
    self.id = id
    self.url = url
    self.status = status
    self.crawlStatus = crawlStatus
    self.delay = delay
    self.graphDeep = graphDeep
    self.lastRunTime = lastRunTime
    self.lastEndTime = lastEndTime
    self.runTime = runTime
    self.maxThread = maxThread
    self.isBlocked = isBlocked
    self.createBy = createBy
    self.keywords = keywords
        
  def getBasic(self):
    lastRunTime = ''
    if self.lastRunTime:
      lastRunTime = self.lastRunTime.strftime("%m/%d/%Y, %H:%M:%S")
    lastEndTime = ''
    if self.lastEndTime:
      lastEndTime = self.firstCrawlDate.strftime("%m/%d/%Y, %H:%M:%S")
    
    return {
      "id": self.id,
      "url": self.url,
      "status": self.status,
      "crawlStatus": self.crawlStatus,
      "delay": self.delay,
      "graphDeep": self.graphDeep,
      "lastRunTime": lastRunTime,
      "lastEndTime": lastEndTime,
      "runTime": self.runTime,
      "maxThread": self.maxThread,
      "isBlocked": self.isBlocked,
      "createBy": self.createBy,
      "keywords": [ele.get() for ele in self.keywords]
    }
 
  def getDetail(self):
    lastRunTime = ''
    if self.lastRunTime:
      lastRunTime = self.lastRunTime.strftime("%m/%d/%Y, %H:%M:%S")
    lastEndTime = ''
    if self.lastEndTime:
      lastEndTime = self.firstCrawlDate.strftime("%m/%d/%Y, %H:%M:%S")
    
    return {
      "id": self.id,
      "url": self.url,
      "status": self.status,
      "crawlStatus": self.crawlStatus,
      "delay": self.delay,
      "graphDeep": self.graphDeep,
      "lastRunTime": lastRunTime,
      "lastEndTime": lastEndTime,
      "runTime": self.runTime,
      "maxThread": self.maxThread,
      "isBlocked": self.isBlocked,
      "createBy": self.createBy,
      "keywords": [ele.get() for ele in self.keywords]
    }
 
class WebpageSpiderDB(SpiderDB):
  def countSpider(self):
    sql_command = '''
    SELECT COUNT(*) FROM public."Spider";
    '''
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      return (True, result[0])
    except:
      return (False, "Error when checking!")
    
  def editSpider(
    self, 
    spider_id,
    url = "",
    status = "Available",
    is_academic = False,
  ):
    sql_command = '''
    UPDATE public."Spider"
    SET "Url" = '%s',
    "Status" = '%s',
    "IsAcademic" = '%s'
    WHERE "ID" = %s;
    ''' % (url, status, is_academic, spider_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when edit spider!")
    return (True, "Edit spider complete")