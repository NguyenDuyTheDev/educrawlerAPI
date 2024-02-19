from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

import psycopg2
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
    self.cur.execute(sql_command)
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
    
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    print(result)
    return
  
  def getArticlesByPage(self, page, pageArticlesNumber):
    sql_command = '''
    SELECT
        "Id", "Url"
    FROM
        public."Article"
    ORDER BY
        "Id" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * pageArticlesNumber, pageArticlesNumber)
  
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    while (result):
      print(result)
      result = self.cur.fetchone()
    
    return
  
  # Keyword Management
  def getTotalKeyword(self) -> int:
    sql_check_command = '''
    SELECT Count(*) FROM public."Keyword";
    '''
    try:
      self.cur.execute(sql_check_command)
    except:
      return (-1, "Error when checking!")
    finally:
      result = self.cur.fetchone()
      return (result[0], "Checking success")
    
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
  
    try:
      self.cur.execute(sql_command)
    except:
      return []
    finally:
      return_value = []
      result = self.cur.fetchone()
      while result:
        return_value.append(result)
        result = self.cur.fetchone()
      return return_value
  
  def addKeyword(self, keyword) -> bool:
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "Name" = '%s';
    ''' % (keyword)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Keyword is already existed!")
    
    # Insert
    sql_insert_command = '''
    INSERT INTO public."Keyword" ("Name") Values ('%s');
    ''' % (keyword)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating!")
    finally:
      return (True, "New keyword created!")
  
  def deleteKeywordByID(self, id) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = '%s';
    ''' % (id)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Keyword doesn't exist!")
    
    # Delete
    sql_delete_command = '''
    DELETE FROM public."Keyword" WHERE "ID" = '%s';
    ''' % (id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      return (False, "Error when deleting!")
    finally:
      return (True, "Delete completed!")
    
  def editKeywordByID(self, id, new_value) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = '%s';
    ''' % (id)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Keyword doesn't exist!")
    
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "Name" = '%s';
    ''' % (new_value)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Keyword is already existed!")
    
    # Edit
    sql_delete_command = '''
    UPDATE public."Keyword"
    SET "Name" = '%s'
    WHERE "ID" = %s;
    ''' % (new_value, id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      return (False, "Error when updating!")
    finally:
      return (True, "Update completed!")
 
  # File Type Management
  def getTotalSupportedFileType(self) -> int:
    sql_check_command = '''
    SELECT Count(*) FROM public."SupportedFileType";
    '''
    try:
      self.cur.execute(sql_check_command)
    except:
      return (-1, "Error when checking!")
    finally:
      result = self.cur.fetchone()
      return (result[0], "Checking success")
    
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
  
    try:
      self.cur.execute(sql_command)
    except:
      return []
    finally:
      return_value = []
      result = self.cur.fetchone()
      while result:
        return_value.append(result)
        result = self.cur.fetchone()
      return return_value
  
  def addSupportedFileType(self, fileType) -> bool:
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "Type" = '%s';
    ''' % (fileType)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "File Type is already existed!")
    
    # Insert
    sql_insert_command = '''
    INSERT INTO public."SupportedFileType" ("Type") Values ('%s');
    ''' % (fileType)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating!")
    finally:
      return (True, "New File Type created!")
  
  def deleteSupportedFileTypeByID(self, id) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = '%s';
    ''' % (id)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "File Type doesn't exist!")
    
    # Delete
    sql_delete_command = '''
    DELETE FROM public."SupportedFileType" WHERE "ID" = '%s';
    ''' % (id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      return (False, "Error when deleting!")
    finally:
      return (True, "Delete completed!")
    
  def editSupportedFileTypeByID(self, id, new_value) -> bool:
    # Check if not exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = '%s';
    ''' % (id)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "File Type doesn't exist!")
    
    # Check if exist
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "Type" = '%s';
    ''' % (new_value)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "File Type is already existed!")
    
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
      return (False, "Error when updating!")
    finally:
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
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Article is already existed!")
    
    #Create new article
    sql_insert_command = '''
    INSERT INTO public."Article" ("Domain", "Url", "Content", "Title") Values ('%s', '%s', '%s', '%s');
    ''' % (domain, url, content, title)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating article!")
    finally:
      return (True, "New article created!")
    
  def deleteArticleByUrl(self, url):
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Article" WHERE "Url" = '%s';
    ''' % (url)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Article isn't existed!")
    
    # Delete article
    sql_delete_command = '''
    DELETE FROM public."Article" WHERE "Url" = '%s';
    ''' % (url)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      return (False, "Error when deleting article!")
    finally:
      return (True, "Delete article completed!")
  
  # CrawlRules
  def createCrawlRules(self, tag, className, IDName, child = None):
    if child == None or len(child) == 0:
      sql_insert_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName") Values ('%s', '%s', '%s');
      ''' % (tag, className, IDName)
      sql_check_command = '''
      SELECT * FROM public."CrawlRules" WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s';
      ''' % (tag, className, IDName)

      try:
        self.cur.execute(sql_insert_command)
        self.connection.commit()
        self.cur.execute(sql_check_command)
        result = self.cur.fetchone()
        if not(result):
          return (-1, "Error when creating crawlRules!")
      except:
        return (-1, "Error when creating crawlRules!")
      finally:
        return (result[0], "Create crawlRules successfully")
        
    else:
      childID = self.createCrawlRules(child[0], child[1], child[2], child[3])
      if childID[0] == -1:
        return (-1, "Error when creating crawlRules!")
      
      sql_insert_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName", "ChildCrawlRuleID") Values ('%s', '%s', '%s', %s);
      ''' % (tag, className, IDName, childID[0])
      sql_check_command = '''
      SELECT * FROM public."CrawlRules" WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s' AND "ChildCrawlRuleID" = %s;
      ''' % (tag, className, IDName, childID[0])

      try:
        self.cur.execute(sql_insert_command)
        self.connection.commit()
        self.cur.execute(sql_check_command)
        result = self.cur.fetchone()
        if not(result):
          return (-1, "Error when creating crawlRules!")
      except:
        return (-1, "Error when creating crawlRules!")
      finally:
        return (result[0], "Create crawlRules successfully")      
      
  # Webpage Spider CrawlRules
  def createWebpageSpiderCrawlRules(self, spiderID, crawlRuleId): 
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = '%s';
    ''' % (spiderID)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Spider is not existed!")      
    
    sql_check_command = '''
    SELECT * FROM public."CrawlRules" WHERE "ID" = '%s';
    ''' % (crawlRuleId)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "CrawlRule is not existed!")      
    
    # Create
    sql_insert_command = '''
    INSERT INTO public."WebpageSpiderCrawlRules" ("SpiderID", "CrawlRulesID") Values (%s, %s);
    ''' % (spiderID, crawlRuleId)    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating crawlRules!")
    finally:
      return (True, "Create crawlRules successfully")     
        
  #Spider
  def createSpiderKeyword(self, spiderID, keywordId): 
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = '%s';
    ''' % (spiderID)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Spider is not existed!")      
    
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = '%s';
    ''' % (keywordId)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Keyword is not existed!")      
    
    # Create
    sql_insert_command = '''
    INSERT INTO public."SpiderKeyword" ("KeywordID", "SpiderID") Values (%s, %s);
    ''' % (keywordId, spiderID)    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating keyword!")
    finally:
      return (True, "Create keyword successfully")   

  def createSpiderFileType(self, spiderID, fileTypeId): 
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "ID" = '%s';
    ''' % (spiderID)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Spider is not existed!")      
    
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = '%s';
    ''' % (fileTypeId)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Keyword is not existed!")      
    
    # Create
    sql_insert_command = '''
    INSERT INTO public."SpiderSupportedFileType" ("SpiderID", "FileTypeID") Values (%s, %s);
    ''' % (spiderID, fileTypeId)    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating keyword!")
    finally:
      return (True, "Create keyword successfully")   

  #Webpage Spider  
  def createWebpageSpider(self, url, delay = 2.5, graphDeep = 3, maxThread = 1, crawlRules = [], fileTypes = [], keywords = []):
    #Check if existed
    sql_check_command = '''
    SELECT * FROM public."Spider" WHERE "Url" = '%s';
    ''' % (url)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Spider is already existed!")  
    
    #Create new spider
    #Create base Spider
    sql_insert_command = '''
    INSERT INTO public."Spider" ("Url", "Delay", "GraphDeep", "MaxThread") Values ('%s', '%s', '%s', '%s');
    ''' % (url, delay, graphDeep, maxThread)

    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating spider!")
    
    # Create fileType
    for index in range(0, len(fileTypes)):
      self.createSpiderFileType(spiderID=spider_ID, fileTypeId=fileTypes[index]) 

    # Create keyword
    for index in range(0, len(keywords)):
      self.createSpiderKeyword(spiderID=spider_ID, keywordId=keywords[index]) 
    
    #Create Webpage Spider
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Error when creating spider!")
    
    spider_ID = result[0]
    sql_insert_command = '''
    INSERT INTO public."Webpage" ("ID") Values ('%s');
    ''' % (spider_ID)
    
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      return (False, "Error when creating spider!")    
    
    # Create CrawlRules
    # CrawlRules Format (ID, Tag, ClassName, IDName, ())
    for index in range(0, len(crawlRules)):
      crawlRule_ID = self.createCrawlRules(crawlRules[index][0], crawlRules[index][1], crawlRules[index][2], crawlRules[index][3])
      self.createWebpageSpiderCrawlRules(spiderID=spider_ID, crawlRuleId=crawlRule_ID)

#uvicorn educrawlerAPI:app --reload


databaseAPI = Singleton()
app = FastAPI()
from pydantic import BaseModel

class Message(BaseModel):
  message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
  
@app.get("/keywords", status_code=200, tags=["keywords"])
def get_keywords():
  total_keywords = databaseAPI.getTotalKeyword()[0]
  keywords_list = databaseAPI.getKeywordByPage(page=0, pageKeywordsNumber=total_keywords)
  
  return {
    "total_keywords": total_keywords,
    "keywords_list": keywords_list
  }
  
@app.post("/keywords", status_code=201, tags=["keywords"])
def create_keyword(name: str):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  res = databaseAPI.addKeyword(name)
  
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  else:
    if res[1] == "Keyword is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
  
@app.put("/keywords/{keyword_id}", status_code=200, tags=["keywords"])
def update_keyword(keyword_id: int, name: str):
  res = databaseAPI.editKeywordByID(keyword_id, name)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Keyword doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Keyword is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating!":
      return JSONResponse(status_code=500, content={"message": res[1]})  

@app.delete("/keywords/{keyword_id}", status_code=200, tags=["keywords"])
def delete_keyword(keyword_id: int):
  res = databaseAPI.deleteKeywordByID(keyword_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Keyword doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Error when deleting!":
      return JSONResponse(status_code=500, content={"message": res[1]})  