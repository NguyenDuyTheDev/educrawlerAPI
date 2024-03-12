from databaseAPI import Singleton

class SpiderController(Singleton):
  def getWebsiteSpiderCrawlRules(self, spider_id):
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
  
  def getWebsiteSpiderCrawlRulesAsCssSelector(self, spider_id):
    res = self.getWebsiteSpiderCrawlRules(spider_id=spider_id)
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
  
  def getWebsiteSpiderSearchRules(self, spider_id):
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
  
  def getWebsiteSpiderSearchRulesAssCssSelector(self, spider_id):
    res = self.getWebsiteSpiderSearchRules(spider_id=spider_id)
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
    
  def getWebpageSpiderHistory(self, spider_id):
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
        if result[4]:
          RunDate = result[4].strftime("%m/%d/%Y, %H:%M:%S")
        EndDate = ""
        if result[5]:
          EndDate = result[5].strftime("%m/%d/%Y, %H:%M:%S")  
          
        row = {
          "RunDate": RunDate,
          "EndDate": EndDate,
          "RunTime": result[6],
          "CrawlStatus": result[3],
          "IsBlocked": result[7]
        }
        data.append(row)
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    if len(data) == 0:
      return (False, "No data to fetch")
    return (True, data)
  
  def getWebpageSpiderArticle(
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
  
  def getWebsiteSpiderHistory(self, spider_id):
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
        if result[7]:
          RunDate = result[7].strftime("%m/%d/%Y, %H:%M:%S")
        EndDate = ""
        if result[8]:
          EndDate = result[8].strftime("%m/%d/%Y, %H:%M:%S")  
          
        row = {
          "RunDate": RunDate,
          "EndDate": EndDate,
          "RunTime": result[9],
          "CrawlStatus": result[6],
          "IsBlocked": result[10],
          "TotalPage": result[13],
          "CrawlSuccess": result[14],
          "CrawlFail": result[15],
          
        }
        data.append(row)
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
    
    if len(data) == 0:
      return (False, "No data to fetch")
    return (True, data)
  
  def getWebsiteSpiderArticle(
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