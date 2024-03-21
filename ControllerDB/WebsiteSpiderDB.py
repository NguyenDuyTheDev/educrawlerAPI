from typing import Any
from ControllerDB.SpiderDB import SpiderDB, Spider

from datetime import datetime 
from ControllerDB.KeywordDB import Keyword, KeywordDB
 
keywordDB = KeywordDB()
 
class WebsiteSpider(Spider):
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
 
class WebsiteSpiderDB(SpiderDB):
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
    FROM "WebsiteSpider", "CrawlHistory", "WebsiteSpiderHistory"
    WHERE "WebsiteSpider"."ID" = "CrawlHistory"."SpiderID" 
    AND "WebsiteSpiderHistory"."ID" = "CrawlHistory"."ID"
    AND "WebsiteSpider"."ID" = %s;
    ''' % (spider_id)

    data = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()      
            
      while result:    
        RunDate = ""
        if result[11]:
          RunDate = result[11].strftime("%m/%d/%Y, %H:%M:%S")
        EndDate = ""
        if result[12]:
          EndDate = result[12].strftime("%m/%d/%Y, %H:%M:%S")  
          
        row = {
          "RunDate": RunDate,
          "EndDate": EndDate,
          "RunTime": result[13],
          "CrawlStatus": result[10],
          "IsBlocked": result[14],
          "TotalPage": result[18],
          "CrawlSuccess": result[19],
          "CrawlFail": result[20],
          "StatusCode200": result[21],
          "StatusCode300": result[22],
          "StatusCode400": result[23],
          "StatusCode500": result[24]
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
    spider_id, 
    page = 0, 
    article_per_page = 10
  ):
    sql_command = '''
    SELECT * 
    FROM "Article", "WebsiteSpider"
    WHERE "Article"."SpiderId" = "WebsiteSpider"."ID"
    AND "Article"."SpiderId" = %s
    ORDER BY "Article"."LastUpdate"
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY;
    ''' % (spider_id, page * article_per_page, article_per_page)

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
  
  def getCrawlRule(self, spider_id):
    sql_command = '''
    SELECT *
    FROM public."Subfolder", public."SubfolderCrawlRules", public."CrawlRules"
    WHERE public."SubfolderCrawlRules"."SubfolderID" = public."Subfolder"."ID" 
	  and public."SubfolderCrawlRules"."CrawlRuleID" = public."CrawlRules"."ID"
	  and public."SubfolderCrawlRules"."SpiderID" = %s;
    ''' % (spider_id)
    
    data = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "No data to fetch")
      
      while result:        
        crawlRuleAsText = result[7]
        if result[8]:
          crawlRuleAsText = crawlRuleAsText + " ." + result[8]
        if result[9]:
          crawlRuleAsText = crawlRuleAsText + " #" + result[9]          
          
        row = {
          "SubfolderID": result[0],
          "Name": result[1],
          "CrawlRuleID": result[6],
          "Tag": result[7],
          "ClassName": result[8],
          "IDName": result[9],
          "ChildCrawlRuleID": result[10],
          "CssSelector": crawlRuleAsText
        }
        data.append(row)
        result = self.cur.fetchone()
      
    except:
      return (False, "Error when fetching data")
    
    for row in data:
      if row["ChildCrawlRuleID"]:
        childRuleID = row["ChildCrawlRuleID"]
        while childRuleID:
          sql_command = '''
          SELECT *
          FROM public."CrawlRules"
          WHERE "ID" = %s;
          ''' % (childRuleID)
          
          try:
            self.cur.execute(sql_command)
            result = self.cur.fetchone()
            if not(result):
              childRuleID = None
              
            subRule = result[1]
            if result[2]:
              crawlRuleAsText = crawlRuleAsText + " ." + result[2]
            if result[3]:
              crawlRuleAsText = crawlRuleAsText + " #" + result[3]   
            childRuleID = result[4]
            
            row["CssSelector"] = row["CssSelector"] + " " + subRule
          except Exception as error:
            print(error)
            
    return (True, data)    
  
  def getCrawlRuleAsCssSelector(
    self, 
    spider_id
  ):
    res = self.getCrawlRule(spider_id=spider_id)
    if (res[0] == True):
      cssSelector = []
      for row in res[1]:
        cssSelector.append({
          "Subfolder": row["Name"],
          "Rule": row["CssSelector"]
        })
      return (True, cssSelector)
    else:
      return res
    
  def getSearchRules(
    self, 
    spider_id
  ):
    sql_command = '''
	  SELECT *
    FROM public."Subfolder", public."SubfolderSearchRules", public."CrawlRules"
    WHERE public."SubfolderSearchRules"."SubfolderID" = public."Subfolder"."ID" 
	  and public."SubfolderSearchRules"."SearchRuleID" = public."CrawlRules"."ID"
	  and public."SubfolderSearchRules"."SpiderID" = %s;
    ''' % (spider_id)
    
    data = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "No data to fetch")
      
      while result:        
        searchRuleAsText = result[7]
        if result[8]:
          searchRuleAsText = searchRuleAsText + " ." + result[8]
        if result[9]:
          searchRuleAsText = searchRuleAsText + " #" + result[9]          
          
        row = {
          "SubfolderID": result[0],
          "Name": result[1],
          "SearchRuleID": result[6],
          "Tag": result[7],
          "ClassName": result[8],
          "IDName": result[9],
          "ChildCearchRuleID": result[10],
          "CssSelector": searchRuleAsText
        }
        data.append(row)
        result = self.cur.fetchone()
      
    except:
      return (False, "Error when fetching data")
    
    for row in data:
      if row["ChildCearchRuleID"]:
        childRuleID = row["ChildCearchRuleID"]
        while childRuleID:
          sql_command = '''
          SELECT *
          FROM public."CrawlRules"
          WHERE "ID" = %s;
          ''' % (childRuleID)
          
          try:
            self.cur.execute(sql_command)
            result = self.cur.fetchone()
            if not(result):
              childRuleID = None
              
            subRule = result[1]
            if result[2]:
              crawlRuleAsText = crawlRuleAsText + " ." + result[2]
            if result[3]:
              crawlRuleAsText = crawlRuleAsText + " #" + result[3]   
            childRuleID = result[4]
            
            row["CssSelector"] = row["CssSelector"] + " " + subRule
          except Exception as error:
            print(error)
            
    return (True, data)
  
  def getSearchRulesAsCssSelector(
    self, 
    spider_id
  ):
    res = self.getSearchRules(spider_id=spider_id)
    if (res[0] == True):
      cssSelector = []
      for row in res[1]:
        cssSelector.append({
          "Subfolder": row["Name"],
          "Rule": row["CssSelector"]
        })
      return (True, cssSelector)
    else:
      return res
    
  def createSubFolder(
    self,
    subFolder,
    spider_id
  ):
    sql_command = '''
    INSERT INTO public."Subfolder" ("SpiderID", "Name")
    VALUES (%s, '%s');
    SELECT * 
    FROM public."Subfolder"
    WHERE "SpiderID" = %s
    ORDER BY "ID" DESC;
    ''' % (spider_id, subFolder[0], spider_id)
    print(sql_command)
    
    subFolder_id = -1
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
      result = self.cur.fetchone()
      if not(result):
        return
      
      subFolder_id = result[0]
    except Exception as error:
      print(error)
      self.cur.execute("ROLLBACK;")
      
    for crawlRule in subFolder[1]:
      crawlRuleID = -1
      if len(crawlRule) == 3:
        res = self.createCrawlRules(crawlRule[0], crawlRule[1], crawlRule[2])
        if res[0] == True:
          crawlRuleID = res[1]
        else:
          continue
      else:
        res = self.createCrawlRules(crawlRule[0], crawlRule[1], crawlRule[2], crawlRule[3])
        if res[0] == True:
          crawlRuleID = res[1]
        else:
          continue        
        
      self.addCrawlRuleToSubfolder(
        subFolderId=subFolder_id,
        crawlRulesID=crawlRuleID,
        spiderID=spider_id
      )
            
    for searchRule in subFolder[2]:
      searchRuleID = -1
      if len(searchRule) == 3:
        res = self.createCrawlRules(searchRule[0], searchRule[1], searchRule[2])
        if res[0] == True:
          searchRuleID = res[1]
        else:
          continue
      else:
        res = self.createCrawlRules(searchRule[0], searchRule[1], searchRule[2], searchRule[3])
        if res[0] == True:
          searchRuleID = res[1]
        else:
          continue       
        
      self.addSearchRuleToSubfolder(
        subFolderId=subFolder_id,
        searchRuleId=searchRuleID,
        spiderID=spider_id
      )
    
  def createSpider(
    self, 
    url, 
    delay = 2.5, 
    graphDeep = 2, 
    maxThread = 1, 
    fileTypes = [], 
    keywords = [], 
    subfolder = []
  ):    
    print(subfolder)
    
    res = self.getSpiderByUrl(url=url)
    if res[0] == True:
      return (False, "Spider is already existed!")  
    if res[1] == "Error when checking!":
      return res

    #Create new spider
    #Create base Spider
    sql_insert_select_command = '''
    INSERT INTO public."Spider" ("Url", "Delay", "GraphDeep", "MaxThread") Values ('%s', %s, %s, %s);
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url, delay, graphDeep, maxThread, url)

    try:
      self.cur.execute(sql_insert_select_command)
      self.connection.commit()
      result = self.cur.fetchone()
      if not(result):
        return (False, "Error when fetching base spider!")
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating base spider!")
    
    #Create website spider
    spider_ID = int(result[0])
 
    sql_insert_command = '''
    INSERT INTO public."WebsiteSpider" ("ID") Values (%s);
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

    #Inser SubFolder
    for folder in subfolder:
      self.createSubFolder(
        spider_id=spider_ID,
        subFolder=folder
      )

    return (True, "Create Website Spider Complete")
    
  def removeSubFolderFromSpider(
    self, 
    spider_id
  ):
    crawl_rules_id = []
    
    sql_command = '''
    SELECT "CrawlRuleID"
    FROM "SubfolderCrawlRules"
    WHERE "SpiderID" = %s    
    ''' % (spider_id)
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:
        crawl_rules_id.append(result[0])
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    sql_command = '''
    SELECT "SearchRuleID"
    FROM "SubfolderSearchRules"
    WHERE "SpiderID" = %s    
    ''' % (spider_id)
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:
        crawl_rules_id.append(result[0])
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    sql_command = '''
	  DELETE FROM "SubfolderCrawlRules"
    WHERE "SpiderID" = %s;
	  DELETE FROM "SubfolderSearchRules"
    WHERE "SpiderID" = %s;
    DELETE FROM "Subfolder"
    WHERE "SpiderID" = %s;
    ''' % (spider_id, spider_id, spider_id)

    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when remove subfolder base spider!")
    
    for ele in crawl_rules_id:
      sql_command = '''
      DELETE FROM "CrawlRules"
      WHERE "ID" = %s;
      ''' % (ele)

      try:
        self.cur.execute(sql_command)
        self.connection.commit()
      except KeyError as err:
        print(err)
        self.cur.execute("ROLLBACK;")
    
    return (True, "Remove CrawlRule Successfully")
    
  def updateSpiderSubFolder(
    self, 
    spider_id,
    subfolder = []
  ):    
    print(subfolder)
    
    self.removeSubFolderFromSpider(
      spider_id=spider_id
    )
    
    #Inser SubFolder
    for folder in subfolder:
      self.createSubFolder(
        spider_id=spider_id,
        subFolder=folder
      )

    return (True, "Update CrawlRule Successfully")
    
  def updateSetting(
    self,
    spider_id,
    delay = 2.5, 
    graphDeep = 2, 
    maxThread = 1
  ):
    sql_command = '''
    UPDATE public."Spider"
    SET "Delay" = %s,
    "GraphDeep" = %s,
    "MaxThread" = %s
    WHERE "ID" = %s;
    ''' % (delay, graphDeep, maxThread, spider_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when edit spider!")
    return (True, "Edit spider complete")
  