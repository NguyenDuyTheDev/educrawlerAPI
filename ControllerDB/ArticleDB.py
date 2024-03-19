from typing import Any
from databaseAPI import Singleton

from datetime import datetime 
from ControllerDB.KeywordDB import Keyword, KeywordDB
 
keywordDB = KeywordDB()
 
class Article:
  id: int
  title: str
  domain: str
  url: str
  firstCrawlDate: datetime | None
  lastUpdate: datetime | None
  content: str
  crawlStatus: str
  note: str
  keyword: list[Keyword]
  
  def __init__(
    self, 
    id, 
    title, 
    domain,
    url,
    firstCrawlDate,
    lastUpdate,
    content,
    crawlStatus,
    note,
    keyword
  ) -> None:
    self.id = id
    self.title = title
    self.domain = domain
    self.url = url
    self.firstCrawlDate = firstCrawlDate
    self.lastUpdate = lastUpdate
    self.content = content
    self.crawlStatus = crawlStatus
    self.note = note
    self.keyword = keyword
        
  def getBasic(self):
    LastUpdate = ''
    if self.lastUpdate:
      LastUpdate = self.lastUpdate.strftime("%m/%d/%Y, %H:%M:%S")
    FirstCrawlDate = ''
    if self.firstCrawlDate:
      FirstCrawlDate = self.firstCrawlDate.strftime("%m/%d/%Y, %H:%M:%S")
    
    return {
      "id": self.id,
      "title": self.title,
      "domain": self.domain,
      "url": self.url,
      "firstCrawlDate": FirstCrawlDate,
      "lastUpdate": LastUpdate,
      "crawlStatus": self.crawlStatus,
      "note": self.note
    }
 
  def getDetail(self):
    LastUpdate = ''
    if self.lastUpdate:
      LastUpdate = self.lastUpdate.strftime("%m/%d/%Y, %H:%M:%S")
    FirstCrawlDate = ''
    if self.firstCrawlDate:
      FirstCrawlDate = self.firstCrawlDate.strftime("%m/%d/%Y, %H:%M:%S")
    
    return {
      "id": self.id,
      "title": self.title,
      "domain": self.domain,
      "url": self.url,
      "firstCrawlDate": FirstCrawlDate,
      "lastUpdate": LastUpdate,
      "content": self.content,
      "crawlStatus": self.crawlStatus,
      "note": self.note,
      "keyword": [ele.get() for ele in self.keyword]
    }
 
class ArticleDB(Singleton):
  def countArticle(self):
    sql_command = '''
    SELECT COUNT(*) FROM public."Article";
    '''
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      return (True, result[0])
    except:
      return (False, "Error when checking!")
    
  def sortArticle(
    self, 
    page = 0, 
    article_per_page = 10,
    order_by = 'LastUpdate',
    filter_order = 'ASC',
    start_time = '',
    end_time = ''
  ):
    sql_count_command = '''
    SELECT count(*)
    FROM public."Article"
    '''
    
    sql_command = '''
    SELECT *
    FROM public."Article"
    '''
    
    if len(start_time) > 0:
      print(start_time)
      sql_sub_command = '''
      WHERE "Article"."LastUpdate" BETWEEN TIMESTAMP '%s' AND TIMESTAMP '%s'
      ''' % (start_time, end_time)
      sql_command = sql_command + sql_sub_command
      sql_count_command = sql_count_command + sql_sub_command
    
    sql_sub_command = '''
    ORDER BY "Article"."%s" %s
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY;     
    ''' % (order_by.split('.')[-1], filter_order.split('.')[-1], page * article_per_page, article_per_page)
    sql_command = sql_command + sql_sub_command
            
    articles = []
  
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):                         
        articles.append(Article(
          id=result[0],
          domain=result[1],
          url=result[2],
          title=result[9],
          content=result[4],
          firstCrawlDate=result[10],
          lastUpdate=result[5],
          crawlStatus=result[6],
          note=result[7],
          keyword=[]
        ))
        result = self.cur.fetchone()
    except Exception as err :
      print(err)
      return(False, "Error when fetching")
    
    if len(articles) == 0:
      return(False, "No data to fetch")

    total_article = 0

    try:
      self.cur.execute(sql_count_command)
      result = self.cur.fetchone()
      if (result):
        total_article = result[0]
    except Exception as err :
      print(err)
      return(False, "Error when fetching")
    
    return (True, {
      "total_article": total_article,
      "detail": [ele.getBasic() for ele in articles]
    })
    
  def getArticleByID(self, article_id):
    sql_command = '''
    select * from public."Article" where "Id" = %d
    ''' % (article_id)
        
    article = None
        
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not result:
        return (False, "No Article Exist")
    except:
      return (False, "Error when fetching")
    
    article = Article(
      id=result[0],
      title=result[9],
      domain=result[1],
      url=result[2],
      firstCrawlDate=result[10],
      lastUpdate=result[5],
      content=result[4],
      crawlStatus=result[6],
      note=result[7],
      keyword=[]
    )
    
    keywords_res = keywordDB.getArticleKeyword(article_id=article_id)
    if keywords_res[0] == False:
      return keywords_res
    article.keyword = keywords_res[1]
    
    return (True, article.getDetail())    
      
  def getArticleByUrl(self, url):
    sql_command = '''
    select * from public."Article" where "Url" = '%s'
    ''' % (url)
        
    article = None
        
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not result:
        return (False, "No Article Exist")
    except:
      return (False, "Error when fetching")
    
    article = Article(
      id=result[0],
      title=result[9],
      domain=result[1],
      url=result[2],
      firstCrawlDate=result[10],
      lastUpdate=result[5],
      content=result[4],
      crawlStatus=result[6],
      note=result[7],
      keyword=[]
    )
    
    keywords_res = keywordDB.getArticleKeyword(article_id=result[0])
    if keywords_res[0] == False:
      return keywords_res
    article.keyword = keywords_res[1]
    
    return (True, article.getDetail())    
  
  def createArticle(self, title, domain, url, content):    
    article_res = self.getArticleByUrl(url=url)
    if article_res[0] == True:
      return (False, "Article has already existed")
    
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
    article_res = self.getArticleByUrl(url=url)
    if article_res[0] == False:
      return article_res
    
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
  
  def deleteArticle(self, article_id):
    article_res = self.getArticleByID(article_id=article_id)
    
    if article_res[0] == False:
      return article_res
    
    sql_delete_command = '''
    DELETE FROM public."Article" WHERE "Id" = %s;
    ''' % (article_id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting article!")
    return (True, "Delete article completed!")
    
  def addKeywordToArticle(self, keyword_id, article_id):
    if self.getArticleByID(article_id=article_id)[0] == False:
      return self.getArticleByID(article_id=article_id)
    
    if keywordDB.getKeywordByID(id=keyword_id)[0] == False:
      return keywordDB.getKeywordByID(id=keyword_id)
    
    sql_insert_command = '''
    INSERT INTO public."SpiderKeyword" ("KeywordID", "SpiderID")
    VALUES (%s, %s);
    ''' % (keyword_id, article_id)
    try:
      self.cur.execute(sql_insert_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when adding keyword!")
    return (True, "Add keyword complete")
  
  def compareArticle(self, article1, article2):
    return article1 == article2