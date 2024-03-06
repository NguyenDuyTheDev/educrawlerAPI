import psycopg2
from datetime import datetime
from typing import Any

class SingletonMeta(type):
  _instances = {}
  
  hostname = 'dpg-cmoefq6d3nmc739ks8o0-a.singapore-postgres.render.com'
  username = 'educrawler_user'
  password = 'qmwJ3In1mklqjxYalptpYP8g8D5akctU' # your password
  database = 'educrawler'
  
  def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self not in self._instances:
            ## Create/Connect to database
            self.connection = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
                
            ## Create cursor, used to execute commands
            self.cur = self.connection.cursor()
           
            instance = super().__call__(*args, **kwds)
            self._instances[self] = instance
            
            print("New connection has been created!")
        else:
          print("Connection has already existed")

        return self._instances[self]
      
  def __del__(self):
    self.cur.close()
    self.connection.close()
    
    print('Close db connection!')
    return
      
class Singleton(metaclass=SingletonMeta):
  #Propertise
  def getUsageStorage(self): 
    sql_command = '''
      SELECT pg_size_pretty(pg_database_size('educrawler'));
    '''
    
    try:
      self.cur.execute(sql_command)
      
    except:
      return (False, "Error when checking!")
    finally:
      result = self.cur.fetchone()
      return result[0]
      
  def isOverStorage(self):
    storage = int(self.getUsageStorage().split(" ")[0])
    if storage > 800000:
      return True
    return False
  
  def getUsedConnection(self):
    sql_command = '''
      SELECT count(*) FROM pg_stat_activity WHERE "datname" = 'educrawler';
    '''
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    return result[0]
  
  def isMaxConnection(self):
    recentConnection = self.getUsedConnection()
    if recentConnection >= 97:
      return True
    return False
      
  #Data
  def getArticleByID(self, id):
    sql_command = '''
    select * from public."Article" where "Id" = %d
    ''' % (id)
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if result:
        return (True, {
          "Id": result[0],
          "Domain": result[1],
          "Url": result[2],
          "FileName": result[3],
          "Content": result[4],
          "LastUpdate": result[5].strftime("%m/%d/%Y, %H:%M:%S"),
          "CrawlStatus": result[6],
          "Note": result[7],
          "SpiderId": result[8],
          "Title": result[9],
          "FirstCrawlDate": result[10].strftime("%m/%d/%Y, %H:%M:%S"),
        })
      else:
        return (False, "No Article Exist")
    except:
      return (False, "Error when fetching")
    
  def getArticleByUrl(self, url):
    sql_command = '''
    select * from public."Article" where "Url" = '%s'
    ''' % (url)
    
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    
    if result:
      return (True, {
        "Id": result[0],
        "Domain": result[1],
        "Url": result[2],
        "FileName": result[3],
        "Content": result[4],
        "LastUpdate": result[5].strftime("%m/%d/%Y, %H:%M:%S"),
        "CrawlStatus": result[6],
        "Note": result[7],
        "SpiderId": result[8],
        "Title": result[9],
        "FirstCrawlDate": result[10].strftime("%m/%d/%Y, %H:%M:%S"),
      })
    else:
      return (False, "No Article Existes")
  
  def getArticlesByPage(self, page, pageArticlesNumber):
    sql_command = '''
    SELECT
        count(*)
    FROM
        public."Article";
    '''
    total_article = 0
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      total_article = result[0]
    except:
      return(False, "Error when checking")
    
    sql_command = '''
    SELECT
        "Id", "Url", "Title", "FirstCrawlDate", "LastUpdate", "CrawlStatus", "Note"
    FROM
        public."Article"
    ORDER BY
        "Id" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * pageArticlesNumber, pageArticlesNumber)
  
    article = []
  
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        article.append({
          "Id": result[0],
          "Url": result[1],
          "Title": result[2],
          "FirstCrawlDate": result[3].strftime("%m/%d/%Y, %H:%M:%S"),
          "LastUpdate": result[4].strftime("%m/%d/%Y, %H:%M:%S"),
          "CrawlStatus": result[5],
          "Note": result[6]
        })
        result = self.cur.fetchone()
    except:
      return(False, "Error when fetching")
    
    if len(article) == 0:
      return(False, "No data to fetch")
    
    return (True, {
      "total_article": total_article,
      "detail": article
    })
  
  # Keyword Management
  def getTotalKeyword(self) -> int:
    sql_check_command = '''
    SELECT Count(*) FROM public."Keyword";
    '''
    
    total_keyword = 0
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      total_keyword = result[0]
    except:
      return (False, "Error when checking!")
      
    return (True, total_keyword)
    
  def getKeywordByPage(self, page, pageKeywordsNumber):
    sql_command = '''
    SELECT
        *
    FROM
        public."Keyword"
    ORDER BY
        "ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * pageKeywordsNumber, pageKeywordsNumber)
  
    return_value = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:
        return_value.append({
          "ID": result[0],
          "Name": result[1],
          "TotalArticles": result[2],
          "TotalWords": result[3]
        })
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")

    if len(return_value) == 0:
      return (False, "No data to fetch")

    return (True, return_value)
  
  def addKeyword(self, keyword) -> bool:
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "Name" = '%s';
    ''' % (keyword)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (False, "Keyword is already existed!")
    except:
      return (False, "Error when checking!")
    
    # Insert
    sql_insert_command = '''
    INSERT INTO public."Keyword" ("Name") Values ('%s');
    ''' % (keyword)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating!")
    return (True, "New keyword created!")
  
  def deleteKeywordByID(self, id) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Keyword doesn't exist!")
    except:
      return (False, "Error when checking!")
    
    # Delete
    sql_delete_command = '''
    DELETE FROM public."Keyword" WHERE "ID" = %s;
    ''' % (id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    return (True, "Delete completed!")
    
  def editKeywordByID(self, id, new_value) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Keyword doesn't exist!")
    except:
      return (False, "Error when checking data!")
    
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "Name" = '%s';
    ''' % (new_value)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (False, "Keyword is already existed!")
    except:
      return (False, "Error when checking data!")
        
    # Edit
    sql_command = '''
    UPDATE public."Keyword"
    SET "Name" = '%s'
    WHERE "ID" = %s;
    ''' % (new_value, id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    return (True, "Update completed!")
 
  # File Type Management
  def getTotalSupportedFileType(self) -> int:
    sql_check_command = '''
    SELECT Count(*) FROM public."SupportedFileType";
    '''
    total_file_type = 0
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      total_file_type = result[0]
    except:
      return (False, "Error when checking!")
    return (True, total_file_type)
    
  def getSupportedFileTypeByPage(self, page, pageFileTypesNumber):
    sql_command = '''
    SELECT
        *
    FROM
        public."SupportedFileType"
    ORDER BY
        "ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * pageFileTypesNumber, pageFileTypesNumber)
  
    file_types = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:
        file_types.append({
          "ID": result[0],
          "Name": result[1]
        })
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching")
    
    if len(file_types) == 0:
      return (False, "No data to get")
    
    return (True, file_types)
  
  def addSupportedFileType(self, fileType) -> bool:
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "Type" = '%s';
    ''' % (fileType)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (False, "File Type is already existed!")
    except:
      return (False, "Error when fetching")

    # Insert
    sql_insert_command = '''
    INSERT INTO public."SupportedFileType" ("Type") Values ('%s');
    ''' % (fileType)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating!")
    
    return (True, "New File Type created!")
  
  def deleteSupportedFileTypeByID(self, id) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "File Type doesn't exist!")
    except:
      return (False, "Error when checking")
    
    # Delete
    sql_delete_command = '''
    DELETE FROM public."SupportedFileType" WHERE "ID" = %s;
    ''' % (id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    return (True, "Delete completed!")
    
  def editSupportedFileTypeByID(self, id, new_value) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "File Type doesn't exist!")
    except:
      return (False, "Error when fetching")

    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "Type" = '%s';
    ''' % (new_value)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (False, "File Type is already existed!")
    except:
      return (False, "Error when fetching")
        
    # Edit
    sql_delete_command = '''
    UPDATE public."SupportedFileType"
    SET "Type" = '%s'
    WHERE "ID" = %s;
    ''' % (new_value, id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    
    return (True, "Update completed!") 
    
  #Article
  def getTotalArticle(self) -> int:
    sql_check_command = '''
    SELECT Count(*) FROM public."Article";
    '''
    try:
      self.cur.execute(sql_check_command)
    except:
      return (-1, "Error when checking!")
    finally:
      result = self.cur.fetchone()
      return (result[0], "Checking success")
  
  def createArticle(self, title, domain, url, content):
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Article" WHERE "Url" = '%s';
    ''' % (url)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (False, "Article is already existed!")
    except:
      return (False, "Error when checking")
    
    #Create new article
    sql_insert_command = '''
    INSERT INTO public."Article" ("Domain", "Url", "Content", "Title") Values ('%s', '%s', '%s', '%s');
    ''' % (domain, url, content, title)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating article!")
    return (True, "New article created!")
    
  def editArticle(self, article_id, title, domain, url, content):
    #Check if not existed
    sql_check_command = '''
    SELECT * FROM public."Article" WHERE "Id" = %s;
    ''' % (article_id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Article doesn't exist!")
    except:
      return (False, "Error when checking")
    
    #Update article
    current = datetime.now()
    reformatted_current = current.strftime("%m-%d-%Y %H:%M:%S")
    
    sql_update_command = '''
    UPDATE public."Article"
    SET "Domain" = '%s',
    "Url" = '%s',
    "Content" = '%s',
    "Title" = '%s',
    "LastUpdate" = TIMESTAMP '%s'
    WHERE "Id" = %s;
    ''' % (domain, url, content, title, reformatted_current, article_id)

    try:
      self.cur.execute(sql_update_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating article!")
    return (True, "Article has been updated successfully!")
    
  def deleteArticleById(self, id):
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Article" WHERE "Id" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Article isn't existed!")
    except:
      return (False, "Error when fetching")
    
    # Delete article
    sql_delete_command = '''
    DELETE FROM public."Article" WHERE "Id" = %s;
    ''' % (id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting article!")
    finally:
      return (True, "Delete article completed!")
  
  # CrawlRules
  def createCrawlRules(self, tag, className, IDName, child = None):
    if child == None or len(child) == 0:
      sql_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName") Values ('%s', '%s', '%s');
      SELECT * FROM public."CrawlRules" WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s';
      ''' % (tag, className, IDName, tag, className, IDName)

      try:
        self.cur.execute(sql_command)
        self.connection.commit()
        result = self.cur.fetchone()
        if not(result):
          return (False, "Error when creating crawlRules!")
      except:
        self.cur.execute("ROLLBACK;")
        return (False, "Error when creating crawlRules!")
      return (True, result[0])
        
    else:
      childID = ()
      if len(child) == 3:
        childID = self.createCrawlRules(child[0], child[1], child[2])
      else:
        childID = self.createCrawlRules(child[0], child[1], child[2], child[3])
      if childID[0] == False:
        return (False, "Error when creating crawlRules!")
      
      sql_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName", "ChildCrawlRuleID") Values ('%s', '%s', '%s', %s);
      SELECT * FROM public."CrawlRules" WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s' AND "ChildCrawlRuleID" = %s;
      ''' % (tag, className, IDName, childID[1], tag, className, IDName, childID[1])

      try:
        self.cur.execute(sql_command)
        self.connection.commit()
        result = self.cur.fetchone()
        if not(result):
          return (False, "Error when creating crawlRules!")
      except:
        self.cur.execute("ROLLBACK;")
        return (False, "Error when creating crawlRules!")
      return (True, result[0])      
      
  # Webpage Spider CrawlRules
  def createWebpageSpiderCrawlRules(self, spiderID, crawlRuleId): 
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = %s;
    ''' % (spiderID)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Spider is not existed!")    
    except:
      return (False, "Error when checking!")
        
    sql_check_command = '''
    SELECT * FROM public."CrawlRules" WHERE "ID" = %s;
    ''' % (crawlRuleId)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "CrawlRule is not existed!")      
    except:
      return (False, "Error when checking!")

    # Create
    sql_insert_command = '''
    INSERT INTO public."WebpageSpiderCrawlRules" ("SpiderID", "CrawlRulesID") Values (%s, %s);
    ''' % (spiderID, crawlRuleId)    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating crawlRules!")
    return (True, "Create crawlRules successfully")     
        
  #Spider
  def createSpiderKeyword(self, spiderID, keywordId): 
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = %s;
    ''' % (spiderID)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Spider is not existed!")   
    except:
      return (False, "Error when checking!")
             
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = %s;
    ''' % (keywordId)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Keyword is not existed!")      
    except:
      return (False, "Error when creating!")

    # Create
    sql_insert_command = '''
    INSERT INTO public."SpiderKeyword" ("KeywordID", "SpiderID") Values (%s, %s);
    ''' % (keywordId, spiderID)    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating keyword!")
    
    return (True, "Create keyword successfully")   

  def createSpiderFileType(self, spiderID, fileTypeId): 
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = %s;
    ''' % (spiderID)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "Spider is not existed!")   
    except:
      return (False, "Error when checking!")    
    
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = %s;
    ''' % (fileTypeId)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if not(result):
        return (False, "FileType is not existed!")      
    except:
      return (False, "Error when creating!")
    
    # Create
    sql_insert_command = '''
    INSERT INTO public."SpiderSupportedFileType" ("SpiderID", "FileTypeID") Values (%s, %s);
    ''' % (spiderID, fileTypeId)    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating file type for spider!")
    
    return (True, "Create keyword successfully")   

  #Webpage Spider  
  def createWebpageSpider(self, url, crawlRules = [], fileTypes = [], keywords = []):    
    print(crawlRules)
    
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (False, "Spider is already existed!")  
    except:
      return (False, "Error when fecthing checking data")  

    #Create new spider
    #Create base Spider
    sql_insert_select_command = '''
    INSERT INTO public."Spider" ("Url") Values ('%s');
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url, url)

    try:
      self.cur.execute(sql_insert_select_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating base spider!")
    
    try:
      result = self.cur.fetchone()
      if not(result):
        return (False, "Error when fetching base spider!")
    except:
      return (False, "Error when fecthing base spider")  
    
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
      self.createSpiderKeyword(
        spiderID=spider_ID,
        keywordId=keywordID
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
        ruleRes = self.createCrawlRules(
          tag=rule[0],
          className=rule[1],
          IDName=rule[2]
        )
        if ruleRes[0] == False:
          print(addRuleRes[1])
          continue
        
        print(ruleRes[1])
        addRuleRes = self.createWebpageSpiderCrawlRules(
          spiderID=spider_ID,
          crawlRuleId=ruleRes[1]
        )
        if addRuleRes[0] == False:
          print(addRuleRes[1])
          continue
        
      else:
        ruleRes = self.createCrawlRules(
          tag=rule[0],
          className=rule[1],
          IDName=rule[2],
          child=rule[3]
        )
        if ruleRes[0] == False:
          continue
        
        addRuleRes = self.createWebpageSpiderCrawlRules(
          spiderID=spider_ID,
          crawlRuleId=ruleRes[1]
        )
        if addRuleRes[0] == False:
          continue
    
    return (True, "Create Webpage Spider Complete")
  
  def getWebpageSpider(self, page = 0, spiderPerPage = 10):
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
  
  def getWebpageSpiderById(self, id):
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

  def setSpiderJobID(self, spider_id, job_id):
    sql_select_command = '''
    SELECT *
    FROM public."Spider", public."WebpageSpider"
    WHERE public."Spider"."ID" = public."WebpageSpider"."ID" and public."Spider"."ID" = %s;
    ''' % (spider_id)
  
    try:
      self.cur.execute(sql_select_command)
      result = self.cur.fetchone()
      if (result):
        current = datetime.now()
        reformatted_current = current.strftime("%m-%d-%Y %H:%M:%S")
        
        sql_select_command = '''
        UPDATE public."Spider"
        SET "JobId" = '%s',
        "Status" = 'Running',
        "CrawlStatus" = 'Good',
        "LastRunDate" = TIMESTAMP '%s'
        WHERE "ID" = %s;            
        ''' % (job_id, reformatted_current, spider_id)        
        
      else:
        return (False, "No Webpage Spider Exist")
    except:
      return (False, "Error when fetching data")
    
    try:
      self.cur.execute(sql_select_command)
      self.connection.commit()
    except:
      return (False, "Error when assigning data")
    
    return (True, "Update Spider JobId Successfully") 
  
  def updateSpiderWhenClosingViaID(self, spider_id):    
    sql_select_command = '''
    SELECT *
    FROM public."Spider"
    WHERE public."Spider"."ID" = %s;
    ''' % (spider_id)
  
    try:
      self.cur.execute(sql_select_command)
      result = self.cur.fetchone()
      if (result):                
        current = datetime.now()
        reformatted_current = current.strftime("%m-%d-%Y %H:%M:%S")
        
        totalRunTime = current - result[4]
        totalRunTimeAsInt = totalRunTime.seconds + result[6]
        
        sql_select_command = '''
        UPDATE public."Spider"
        SET "JobId" = '',
        "Status" = 'Available',
        "CrawlStatus" = 'Good', 
        "LastEndDate" = TIMESTAMP '%s',
        "RunTime" = '%s'
        WHERE "ID" = %s;            
        ''' % (reformatted_current, totalRunTimeAsInt, result[0])   
      else:
        return (False, "No Webpage Spider Exist")
    except:
      return (False, "Error when fetching data")
    
    try:
      self.cur.execute(sql_select_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when assigning data")
    
    return (True, "Update Spider Closing Status Successfully") 

  def calculateLastRunTime(self, spider_id):    
    sql_select_command = '''
    SELECT *
    FROM public."Spider"
    WHERE public."Spider"."ID" = %s;
    ''' % (spider_id)
  
    try:
      self.cur.execute(sql_select_command)
      result = self.cur.fetchone()
      if (result):                
        print(type(result[4]))
        print(result[5])
        
        totalRunTime = result[5] - result[4]
        return (True, totalRunTime.seconds)  
      else:
        return (False, "No Webpage Spider Exist")
    except:
      return (False, "Error when fetching data")
      
  #Website Spider  
  def createWebsiteSpider(self, url, delay = 2.5, graphDeep = 2, maxThread = 1, crawlRules = [], fileTypes = [], keywords = []):
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url)
    
    try:
      self.cur.execute(sql_check_command)
      self.connection.commit()
    except:
      return (False, "Error when checking!")

    try: 
      result = self.cur.fetchone()
      if result:
        return (False, "Spider is already existed!")  
    except: 
      return (False, "Error when fecthing checking data")  

    #Create new spider
    #Create base Spider
    sql_insert_select_command = '''
    INSERT INTO public."Spider" ("Url", "Delay", "GraphDeep", "MaxThread") Values ('%s', %s, %s, %s);
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url, delay, graphDeep, maxThread, url)

    try:
      self.cur.execute(sql_insert_select_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating base spider!")
    
    try:
      result = self.cur.fetchone()
      if not(result):
        return (False, "Error when fetching base spider!")
    except:
      return (False, "Error when fecthing base spider")  
    
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
      self.createSpiderKeyword(
        spiderID=spider_ID,
        keywordId=keywordID
      )
    
    #Insert File Type
    for fileTypeID in fileTypes:
      self.createSpiderFileType(
        spiderID=spider_ID,
        fileTypeId=fileTypeID
      )

    return (True, "Create Website Spider Complete")
  
  def getWebsiteSpider(self, page = 0, spiderPerPage = 10):
    sql_command = '''
    SELECT COUNT(*)
    FROM public."Spider", public."WebsiteSpider"
    WHERE public."Spider"."ID" = public."WebsiteSpider"."ID";
    '''
    total_spider = 0
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      total_spider = result[0]
    except:
      return (False, "Error when checking data")
    
    sql_select_command = '''
    SELECT *
    FROM public."Spider", public."WebsiteSpider"
    WHERE public."Spider"."ID" = public."WebsiteSpider"."ID"
    ORDER BY public."Spider"."ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * spiderPerPage, spiderPerPage)

    return_value = []
  
    try:
      self.cur.execute(sql_select_command)
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
          "Delay": result[8],
          "GraphDeep": result[9],
          "MaxThread": result[10],
          "JobId": result[12],
          "TotalPage": result[14],
          "CrawlSuccess": result[15],
          "CrawlFail": result[16],
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
  
  def getWebsiteSpiderById(self, id):
    sql_select_command = '''
    SELECT *
    FROM public."Spider", public."WebsiteSpider"
    WHERE public."Spider"."ID" = public."WebsiteSpider"."ID" and public."Spider"."ID" = %s;
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
          "Id": result[0],
          "Url": result[1],
          "Status": result[2],
          "CrawlStatus": result[3],
          "LastRunDate": LastRunDate,
          "LastEndDate": LastEndDate,
          "RunTime": result[6],
          "isBlocked": result[7],
          "Delay": result[8],
          "GraphDeep": result[9],
          "MaxThread": result[10],
          "JobId": result[12],
          "TotalPage": result[14],
          "CrawlSuccess": result[15],
          "CrawlFail": result[16],
          "Keyword": [],
          "FileType": [],
        }
        result = self.cur.fetchone()
      else:
        return (False, "No Website Spider Exist")
    except:
      return (False, "Error when fetching data")

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
    
    return (True, return_value)    

  def setWebsiteSpiderJobID(self, spider_id, job_id):
    sql_select_command = '''
    SELECT *
    FROM public."Spider", public."WebsiteSpider"
    WHERE public."Spider"."ID" = public."WebsiteSpider"."ID" and public."Spider"."ID" = %s;
    ''' % (spider_id)
  
    try:
      self.cur.execute(sql_select_command)
      result = self.cur.fetchone()
      if (result):
        current = datetime.now()
        reformatted_current = current.strftime("%m-%d-%Y %H:%M:%S")
        
        sql_select_command = '''
        UPDATE public."Spider"
        SET "JobId" = '%s',
        "Status" = 'Running',
        "CrawlStatus" = 'Good',
        "LastRunDate" = TIMESTAMP '%s'
        WHERE "ID" = %s;            
        ''' % (job_id, reformatted_current, spider_id)        
        
      else:
        return (False, "No Webpage Spider Exist")
    except:
      return (False, "Error when fetching data")
    
    try:
      self.cur.execute(sql_select_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when assigning data")
    
    return (True, "Update Spider JobId Successfully") 
  
  # Spider
  def getSpiderTotalAriticle(self, spider_id, page = 0, articlePerPage = 10):
    sql_select_command = '''
    SELECT count(*)
    FROM public."Article"
    WHERE "SpiderId" = %s;
    ''' % (spider_id)
  
    total_article = 0
    try:
      self.cur.execute(sql_select_command)
      result = self.cur.fetchone()
      if (result):
        total_article = result[0]
      else:
        return (False, "Error when fetching data")
    except:
      return (False, "Error when fetching data")
    
    sql_command = '''
    SELECT *
    FROM public."Article"
    WHERE "SpiderId" = %s
    ORDER BY public."Article"."Id" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (spider_id, page * articlePerPage, articlePerPage)

    detail = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        LastUpdate = ""
        if result[5]:
          LastUpdate = result[5].strftime("%m-%d-%Y %H:%M:%S")
 
        FirstCrawlDate = ""
        if result[10]:
          FirstCrawlDate = result[10].strftime("%m-%d-%Y %H:%M:%S")
        
        detail.append({
          "Id": result[0],
          "Domain": result[1],
          "Url": result[2],
          #"Content": result[4],
          "LastUpdate": LastUpdate,
          "CrawlStatus": result[6],
          "Note": result[7],
          "Title": result[9],
          "FirstCrawlDate": FirstCrawlDate,
        })
        result = self.cur.fetchone()
    except(KeyError):
      print(KeyError)
      return (False, "Error when fetching article data")
    
    if len(detail) == 0: 
      return (False, "No data to fetch")
    
    return (True, {
      "total_article": total_article,
      "detail": detail
    })
  
  def deleteSpider(self, spider_id):
    sql_select_command = '''
    DELETE FROM public."Spider"
    WHERE "ID" = %s;
    ''' % (spider_id)
  
    try:
      self.cur.execute(sql_select_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting data")    
  
    return (True, "Delete Spider %s successfully!" % spider_id)    
  
  # User
  def createUser(
    self, 
    username: str, 
    password: str,
    role: str
    ):
    sql_command = '''
    SELECT count(*)
    FROM public."User"
    WHERE "Username" = '%s';
    ''' % (username)    
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if (result[0] > 0):
        return (False, "This Username is already existed")
    except:
      return (False, "Error when fetching data")
    
    if role == "Manager":
      sql_command = '''
      SELECT count(*)
      FROM public."User"
      WHERE "Role" = 'Manager';
      '''
      
      try:
        self.cur.execute(sql_command)
        result = self.cur.fetchone()
        if (result[0] > 0):
          return (False, "Manager is already existed")
      except:
        return (False, "Error when fetching data")
    
    sql_command = '''
    INSERT
    INTO public."User" ("Username", "Password", "Role") 
    VALUES ('%s', '%s', '%s');
    ''' % (username, password, role)    
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating user")    
    
    return (True, "Create User Successfully!")
  
  def getUser(self, page, userPerPage):
    sql_command = '''
    SELECT
        *
    FROM
        public."User"
    ORDER BY
        "ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * userPerPage, userPerPage)
  
    return_value = []
  
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        return_value.append({
          "Username": result[1],
          "OnlineStatus": result[3],
          "AccountStatus": result[5],
          "Role": result[9]
        })
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")
      
    if len(return_value) == 0:
      return (False, "Out of range")
      
    sql_command = '''
    SELECT
        count(*)
    FROM
        public."User"; 
    ''' 
    
    total_user = 0
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      total_user = result[0]
    except:
      return (False, "Error when counting user")
      
    return (True, {
      "Total_user": total_user,
      "Detail": return_value
    })