from typing import Any
from databaseAPI import Singleton

from datetime import datetime 
from ControllerDB.KeywordDB import Keyword, KeywordDB
 
keywordDB = KeywordDB()
 
class CrawlRule: 
  id: int
  tag: str
  className: str
  idName: str
  childId: int
  
  def __init__(
    self,
    id, 
    tag,
    className = "",
    idName = "",
    childId = None
  ) -> None:
    self.id = id
    self.tag = tag
    self.className = className
    self.idName = idName
    self.childId = childId

  def get(self):
    return {
      "id": self.id,
      "tag": self.tag,
      "className": self.className,
      "idName": self.idName,
      "childId": self.childId
    }
    
  def getCSSSelector(self):
    result = self.tag
    if self.className != "":
      result = result + "." + self.className
    if self.idName != "":
      result = result + "#" + self.idName   
    return result
 
class Spider:
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
 
class SpiderDB(Singleton):
  def __init__(self) -> None:
    super().__init__()
  
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
    
  def getSpider(
    self, 
    spider_id
  ):
    sql_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = %s;
    ''' % (spider_id)
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Spider is not existed!")    
    except:
      return (False, "Error when checking!")
    return (True, result[0])
    
  def getSpiderByUrl(
    self, 
    url
  ):
    sql_command = '''
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url)
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Spider is not existed!")    
    except:
      return (False, "Error when checking!")
    return (True, result[0])
    
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
  
  def updateKeywords(
    self, 
    spider_id,
    keyword_ids = []
  ):
    keywordDB.removeAllKeywordFromSpider(spider_id=spider_id)
    
    for keyword in keyword_ids:
      keywordDB.addKeywordToSpider(
        keyword_id=keyword,
        spider_id=spider_id
      )
      
  # CrawlRule
  def getCrawlRule(self, crawl_rule_id):
    sql_command = '''
    SELECT * FROM public."CrawlRules" WHERE "ID" = %s;
    ''' % (crawl_rule_id)
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "CrawlRule is not existed!")      
    except:
      return (False, "Error when checking!")
    return (True, result[0])
  
  def createCrawlRule(self, tag, class_name, id_name, child = None):
    if child == None or len(child) == 0:
      sql_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName") Values ('%s', '%s', '%s');
      SELECT * 
      FROM public."CrawlRules" 
      WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s'
      ORDER BY "ID" DESC;
      ''' % (tag, class_name, id_name, tag, class_name, id_name)

      try:
        self.cur.execute(sql_command)
        self.connection.commit()
        result = self.cur.fetchone()
        if not(result):
          return (False, "Error when creating crawlRule")
      except:
        self.cur.execute("ROLLBACK;")
        return (False, "Error when creating crawlRule")
      return (True, result[0])
        
    else:
      childID = ()
      if len(child) == 3:
        childID = self.createCrawlRule(child[0], child[1], child[2])
      else:
        childID = self.createCrawlRule(child[0], child[1], child[2], child[3])
      if childID[0] == False:
        return (False, "Error when creating crawlRule")
      
      sql_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName", "ChildCrawlRuleID") Values ('%s', '%s', '%s', %s);
      SELECT * FROM public."CrawlRules" WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s' AND "ChildCrawlRuleID" = %s;
      ''' % (tag, class_name, id_name, childID[1], tag, class_name, id_name, childID[1])

      try:
        self.cur.execute(sql_command)
        self.connection.commit()
        result = self.cur.fetchone()
        if not(result):
          return (False, "Error when creating crawlRule")
      except:
        self.cur.execute("ROLLBACK;")
        return (False, "Error when creating crawlRule")
      return (True, result[0])    
    
  def getTotalRuntime(self):
    sql_command = '''
    SELECT SUM("RunTime")
    FROM "Spider";
    '''
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()     
      if result:
        return (True, result[0])
    except:
      return (False, "Error when fetching data")  
    
  def getTotalCrawlSuccess(self):
    sql_command = '''
    SELECT SUM("CrawlSuccess")
    FROM "WebsiteSpider";
    '''
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()     
      if result:
        return (True, result[0])
    except:
      return (False, "Error when fetching data")  
    
  def getTotalCrawlFail(self):
    sql_command = '''
    SELECT SUM("CrawlFail")
    FROM "WebsiteSpider";
    '''
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()     
      if result:
        return (True, result[0])
    except:
      return (False, "Error when fetching data")  
    
  def getAllSpiderRunningStatus(self):
    sql_command = '''
    SELECT "Status", COUNT(*)
    FROM "Spider"
    GROUP BY "Status";
    '''
    return_value = {
      "Available": 0,
      "Running": 0,
      "Suspend": 0,
      "Closing": 0     
    }
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()     
      while result:
        return_value[result[0]] = result[1]
        result = self.cur.fetchone()  
    except:
      return (False, "Error when fetching data")  
    return (True, return_value)
  
  def getTop10SpiderWithMostArticle(self):
    sql_command = '''
    SELECT "Article"."SpiderId", "Spider"."Url", COUNT("Article"."Id")
    FROM "Article", "Spider"
    WHERE "Article"."SpiderId" = "Spider"."ID" 
    GROUP BY "Article"."SpiderId", "Spider"."Url"
    ORDER BY COUNT("Article"."Id") DESC
    FETCH FIRST 10 ROW ONLY;
    '''
    return_value = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()     
      while result:
        return_value.append({
          "SpiderID": result[0],
          "Url": result[1],
          "Domain": result[1].split("//")[1].split("/")[0],
          "Total": result[2],
        })
        result = self.cur.fetchone()  
    except:
      return (False, "Error when fetching data")  
    return (True, return_value)