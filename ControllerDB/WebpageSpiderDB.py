from typing import Any
from ControllerDB.SpiderDB import SpiderDB, Spider

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
  
  def addCrawlRuleToSpider(
    self, 
    crawlrule_id, 
    spider_id
  ):
    res = self.getSpider(spider_id=spider_id)
    if res[0] == False:
      return res
    
    res = self.getCrawlRule(crawl_rule_id=crawlrule_id)
    if res[0] == False:
      return res
        
    # Create
    sql_command = '''
    INSERT INTO public."WebpageSpiderCrawlRules" ("SpiderID", "CrawlRulesID") Values (%s, %s);
    ''' % (spider_id, crawlrule_id)    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating crawlRules!")
    return (True, {
      "SpiderId": spider_id,
      "CrawlRuleId": crawlrule_id
    })     
    
  def removeAllCrawlRuleFromSpider(self, spider_id):
    sql_command = '''
    DELETE FROM "CrawlRules"
    WHERE "ID" in (
      SELECT "CrawlRulesID"
      FROM "WebpageSpiderCrawlRules"
      WHERE "SpiderID" = %s
    );
    ''' % (spider_id)

    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating base spider!")  
    return (True, "Remove CrawlRules from Spider successfully")
    
  def updateWebpageCrawlRule(
    self, 
    spider_id, 
    crawl_rules = []
  ):
    self.removeAllCrawlRuleFromSpider(spider_id=spider_id)
    
    #Insert CrawlRule
    for rule in crawl_rules:
      if len(rule) == 3:
        ruleRes = self.createCrawlRule(
          tag=rule[0],
          class_name=rule[1],
          id_name=rule[2],
        )
        if ruleRes[0] == False:
          continue
        
        print(ruleRes[1])
        addRuleRes = self.addCrawlRuleToSpider(
          spider_id=spider_id,
          crawlrule_id=ruleRes[1]
        )
        if addRuleRes[0] == False:
          continue
        
      else:
        ruleRes = self.createCrawlRule(
          tag=rule[0],
          class_name=rule[1],
          id_name=rule[2],
          child=rule[3]
        )
        if ruleRes[0] == False:
          continue
        
        addRuleRes = self.addCrawlRuleToSpider(
          spider_id=spider_id,
          crawlrule_id=ruleRes[1]
        )
        if addRuleRes[0] == False:
          continue
    
    return (True, "Update Webpage Spider Crawl Rule Complete")
  
  def createWebpageSpider(
    self, 
    url, 
    crawlRules = [], 
    fileTypes = [], 
    keywords = []
  ):    
    print(crawlRules)
    
    res = self.getSpiderByUrl(url=url)
    if res[0] == True:
      return (False, "Spider is already existed!")  
    if res[1] == "Error when checking!":
      return res

    #Create new spider
    #Create base Spider
    sql_insert_select_command = '''
    INSERT INTO public."Spider" ("Url") Values ('%s');
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url, url)

    try:
      self.cur.execute(sql_insert_select_command)
      self.connection.commit()
      result = self.cur.fetchone()
      if not(result):
        return (False, "Error when fetching base spider!")
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating base spider!")
    
    #Create Webpage Spider
    spider_ID = int(result[0])
 
    sql_insert_command = '''
    INSERT INTO public."WebpageSpider" ("ID") Values (%s);
    ''' % (spider_ID)
    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating webpage spider!")    

    #Insert Keyword
    for keywordID in keywords:
      keywordDB.addKeywordToSpider(
        keyword_id=keywordID,
        spider_id=spider_ID
      )
    
    #Insert File Type
    for fileTypeID in fileTypes:
      self.createSpiderFileType(
        spiderID=spider_ID,
        fileTypeId=fileTypeID
      )
    
    #Insert CrawlRule
    for rule in crawlRules:
      if len(rule) == 3:
        ruleRes = self.createCrawlRule(
          tag=rule[0],
          class_name=rule[1],
          id_name=rule[2],
        )
        if ruleRes[0] == False:
          continue
        
        print(ruleRes[1])
        addRuleRes = self.addCrawlRuleToSpider(
          spider_id=spider_ID,
          crawlrule_id=ruleRes[1]
        )
        if addRuleRes[0] == False:
          continue
        
      else:
        ruleRes = self.createCrawlRule(
          tag=rule[0],
          class_name=rule[1],
          id_name=rule[2],
          child=rule[3]
        )
        if ruleRes[0] == False:
          continue
        
        addRuleRes = self.addCrawlRuleToSpider(
          spider_id=spider_ID,
          crawlrule_id=ruleRes[1]
        )
        if addRuleRes[0] == False:
          continue
    
    return (True, "Create Webpage Spider Complete")
  
  def getHistory(
    self,
    spider_id
  ):
    sql_command = '''
    SELECT *
    FROM "WebpageSpider", "CrawlHistory"
    WHERE "WebpageSpider"."ID" = "CrawlHistory"."SpiderID" AND "WebpageSpider"."ID" = %s;
    ''' % (spider_id)

    data = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()      
      while result:        
        RunDate = ""
        if result[5]:
          RunDate = result[5].strftime("%m/%d/%Y, %H:%M:%S")
        EndDate = ""
        if result[6]:
          EndDate = result[6].strftime("%m/%d/%Y, %H:%M:%S")  
          
        row = {
          "RunDate": RunDate,
          "EndDate": EndDate,
          "RunTime": result[7],
          "CrawlStatus": result[4],
          "IsBlocked": result[8],
          "StatusCode": result[1]
        }
        data.append(row)
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    if len(data) == 0:
      return (False, "No data to fetch")
    return (True, data)
  
  def getArticles(
    self, 
    spider_id
  ):
    sql_command = '''
    SELECT * 
    FROM "Article", "WebpageSpider"
    WHERE "Article"."SpiderId" = "WebpageSpider"."ID"
    AND "Article"."SpiderId" = %s
    ORDER BY "Article"."LastUpdate";
    ''' % (spider_id)

    data = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()      
      while result:        
        LastUpdate = ""
        if result[5]:
          LastUpdate = result[5].strftime("%m/%d/%Y, %H:%M:%S")
        FirstUpdate = ""
        if result[10]:
          FirstUpdate = result[10].strftime("%m/%d/%Y, %H:%M:%S")  
          
        row = {
          "ID": result[0],
          "Domain": result[1],
          "Title": result[9],
          "Url": result[2],
          "FirstCrawlDate": FirstUpdate,
          "LastUpdate": LastUpdate,
          "Content": result[4]
        }
        data.append(row)
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    if len(data) == 0:
      return (False, "No data to fetch")
    return (True, data)

  def getSpiders(self, page = 0, spiderPerPage = 10):
    sql_command = '''
    SELECT count(*)
    FROM public."Spider", public."WebpageSpider"
    WHERE public."Spider"."ID" = public."WebpageSpider"."ID";
    '''
    total_spider = 0
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      total_spider = result[0]
    except:
      return (False, "Error when fetching data")      
    
    sql_command = '''
    SELECT *
    FROM public."Spider", public."WebpageSpider"
    WHERE public."Spider"."ID" = public."WebpageSpider"."ID"
    ORDER BY public."Spider"."ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * spiderPerPage, spiderPerPage)

    return_value = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        LastRunDate = ""
        if result[4]:
          LastRunDate = result[4].strftime("%m/%d/%Y, %H:%M:%S")
          
        LastEndDate = ""
        if result[5]:
          LastEndDate = result[5].strftime("%m/%d/%Y, %H:%M:%S")        
        
        return_value.append({
          "Id": result[0],
          "Url": result[1],
          "Status": result[2],
          "CrawlStatus": result[3],
          "LastRunDate": LastRunDate,
          "LastEndDate": LastEndDate,
          "RunTime": result[6],
          "isBlocked": result[7],
          "JobId": result[12],
        })
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    if len(return_value) == 0:
      return (False, "No data to fetch")
    
    return (True, {
      "total_spider": total_spider,
      "detail": return_value
    })
    
  def getSpiderById(self, id):
    sql_select_command = '''
    SELECT *
    FROM public."Spider", public."WebpageSpider"
    WHERE public."Spider"."ID" = public."WebpageSpider"."ID" and public."Spider"."ID" = %s;
    ''' % (id)

    return_value = {}
    try:
      self.cur.execute(sql_select_command)
      result = self.cur.fetchone()
      if (result):
        LastRunDate = ""
        if result[4]:
          LastRunDate = result[4].strftime("%m/%d/%Y, %H:%M:%S")
        LastEndDate = ""
        if result[5]:
          LastEndDate = result[5].strftime("%m/%d/%Y, %H:%M:%S")
        
        return_value = {
          "Type": "WebpageSpider",
          "Id": result[0],
          "Url": result[1],
          "Status": result[2],
          "CrawlStatus": result[3],
          "LastRunDate": LastRunDate,
          "LastEndDate": LastEndDate,
          "RunTime": result[6],
          "isBlocked": result[7],
          "JobId": result[12],
          "Keyword": [],
          "FileType": [],
          "CrawlRule": [],
          "IsAcademic": result[13],
        }
        result = self.cur.fetchone()
      else:
        return (False, "No Webpage Spider Exist")
    except:
      return (False, "Error when fetching data")
        
    # Keyword
    sql_command = '''
    SELECT *
    FROM public."SpiderKeyword", public."Keyword"
    WHERE public."SpiderKeyword"."KeywordID" = public."Keyword"."ID" and public."SpiderKeyword"."SpiderID" = %s;
    ''' % (id)
    
    spider_keyword = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        spider_keyword.append({
          "Id": result[0],
          "Value": result[3]
        })
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching keyword data")
    
    return_value["Keyword"] = spider_keyword

    # File Type
    sql_command = '''
    SELECT *
    FROM public."SpiderSupportedFileType", public."SupportedFileType"
    WHERE public."SpiderSupportedFileType"."FileTypeID" = public."SupportedFileType"."ID" and public."SpiderSupportedFileType"."SpiderID" = %s;
    ''' % (id)
    
    file_type = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        file_type.append({
          "Id": result[1],
          "Value": result[3]
        })
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching keyword data")
    
    return_value["FileType"] = file_type
    
    # Crawl Rules
    sql_command = '''
    SELECT *
    FROM public."WebpageSpiderCrawlRules", public."CrawlRules"
    WHERE public."WebpageSpiderCrawlRules"."CrawlRulesID" = public."CrawlRules"."ID" and public."WebpageSpiderCrawlRules"."SpiderID" = %s;
    ''' % (id)
    
    crawl_rules = []
    child_crawl_rules_id = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        crawl_rules.append({
          "Id": result[1],
          "Tag": result[3],
          "ClassName": result[4],
          "IDName": result[5],
          "ChildId": result[6],
        })
        if result[6] != None:
          child_crawl_rules_id.append(result[6])
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching crawlrule data")
    
    while len(child_crawl_rules_id) > 0:
      sql_command = '''
      SELECT *
      FROM public."CrawlRules"
      WHERE public."CrawlRules"."ID" = %s;
      ''' % (child_crawl_rules_id[0])
      
      try:
        self.cur.execute(sql_command)
        result = self.cur.fetchone()
        if result:
          crawl_rules.append({
            "Id": result[0],
            "Tag": result[1],
            "ClassName": result[2],
            "IDName": result[3],
            "ChildId": result[4],
          })
          if result[4] != None:
            child_crawl_rules_id.append(result[4])
          child_crawl_rules_id.pop(0)
      except:
        return (False, "Error when fetching crawlrule data")
    
    return_value["CrawlRule"] = crawl_rules
    
    return (True, return_value)    