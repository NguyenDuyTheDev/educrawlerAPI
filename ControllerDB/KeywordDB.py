from typing import Any
from databaseAPI import Singleton
 
class Keyword:
  id: int
  name: str
  articleAppearance: int
  
  def __init__(
    self, 
    id, 
    name, 
    articleAppearance
  ) -> None:
    self.id = id
    self.name = name
    self.articleAppearance = articleAppearance
    
  def get(self):
    return {
      "id": self.id,
      "name": self.name,
      "articleAppearance": self.articleAppearance
    }
 
class KeywordDB(Singleton):
  def countKeyword(self):
    sql_check_command = '''
    SELECT COUNT(*) FROM public."Keyword";
    '''
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      return (True, result[0])
    except:
      return (False, "Error when checking!")
        
  def getKeywordByPage(self, page, keywordPerPage):
    total_keyword_res = self.countKeyword()
    if total_keyword_res[0] == False:
      return total_keyword_res
    total_keyword = total_keyword_res[1]
    
    sql_command = '''
    SELECT *
    FROM public."Keyword"
    ORDER BY "ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * keywordPerPage, keywordPerPage)
  
    keywords = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:
        keywords.append(Keyword(
          id=result[0],
          name=result[1],
          articleAppearance=result[2]
        ))
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")

    if len(keywords) == 0:
      return (False, "No data to fetch")

    return (True, {
      "totalKeyword": total_keyword,
      "page": page,
      "keywordPerPage": keywordPerPage,
      "detail": [ele.get() for ele in keywords]
    })
    
  def getKeywordByName(self, keyword):
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "Name" = '%s';
    ''' % (keyword)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (True, Keyword(
          id=result[0],
          name=result[1],
          articleAppearance=result[2]
        ))
    except:
      return (False, "Error when checking!")    
    return (False, "No data to fetch")
  
  def getKeywordByID(self, id):
    sql_check_command = '''
    SELECT * FROM public."Keyword" WHERE "ID" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (True, Keyword(
          id=result[0],
          name=result[1],
          articleAppearance=result[2]
        ))
    except:
      return (False, "Error when checking!")    
    return (False, "No data to fetch")
    
  def addKeyword(self, keyword):
    if self.getKeywordByName(keyword=keyword)[0] == True:
      return (False, "Keyword has already existed")
    
    sql_command = '''
    INSERT INTO public."Keyword" ("Name") Values ('%s');
    ''' % (keyword)

    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating!")
    
    if self.getKeywordByName(keyword=keyword)[0] == True:
      return (True, self.getKeywordByName(keyword=keyword)[1].get())
    
    return (False, "Error when creating!")
  
  def editKeyword(self, id, keyword):
    if self.getKeywordByName(keyword=keyword)[0] == True:
      return (False, "Keyword has already existed")
    
    if self.getKeywordByID(id=id)[0] == False:
      return self.getKeywordByID(id=id)
    
    sql_command = '''
    UPDATE public."Keyword"
    SET "Name" = '%s'
    WHERE "ID" = %s;
    ''' % (keyword, id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
        
    if self.getKeywordByName(keyword=keyword)[0] == True:
      return (True, self.getKeywordByName(keyword=keyword)[1].get())    
    
    return (False, "Error when updating!")
  
  def deleteKeywordById(self, id):
    if self.getKeywordByID(id=id)[0] == False:
      return self.getKeywordByID(id=id)
    
    sql_command = '''
    DELETE FROM public."Keyword" WHERE "ID" = %s;
    ''' % (id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    return (True, "Delete completed!")
  
  # Spider Keyword Management
  def addKeywordToSpider(self, keyword_id, spider_id):
    sql_command = '''
    INSERT INTO public."SpiderKeyword" ("KeywordID", "SpiderID")
    VALUES (%s, %s);
    ''' % (keyword_id, spider_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when inserting!")
    
    return (True, "Insert keyword %s to spider %s successfully" % (keyword_id, spider_id))      
  
  def removeAllKeywordFromSpider(self, spider_id):
    sql_command = '''
    DELETE FROM public."SpiderKeyword"
    WHERE "SpiderID" = %s;
    ''' % (spider_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    
    return (True, "Remove all keyword from spider %s successfully" % (spider_id))   
      
  def removeKeywordFromSpider(self, keyword_id, spider_id):
    sql_command = '''
    DELETE FROM public."SpiderKeyword"
    WHERE "KeywordID" = %s AND "SpiderID" = %s;
    ''' % (keyword_id, spider_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    
    return (True, "Remove keyword %s from spider %s successfully" % (keyword_id, spider_id))      
    
  # Article Keyword Management
  def getArticleKeyword(self, article_id):
    sql_command = '''
    SELECT *
    FROM "ArticleKeyword", "Keyword"
    WHERE "ArticleKeyword"."KeywordID" = "Keyword"."ID" AND "ArticleKeyword"."ArticleID" = %s;
    ''' % (article_id)
    keywords = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:        
        keywords.append(Keyword(
          id=result[0],
          name=result[4],
          articleAppearance=0
        ))
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching")    
    return (True, keywords)
  
  def addKeywordToArticle(self, keyword_id, article_id):
    sql_command = '''
    INSERT INTO public."ArticleKeyword" ("KeywordID", "ArticleID")
    VALUES (%s, %s);
    ''' % (keyword_id, article_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when inserting!")
    
    return (True, "Insert keyword %s to article %s successfully" % (keyword_id, article_id)) 
  
  def removeKeywordFromArticle(self, keyword_id, article_id):
    sql_command = '''
    DELETE FROM public."ArticleKeyword"
    WHERE "KeywordID" = %s AND "ArticleID" = %s;
    ''' % (keyword_id, article_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    
    return (True, "Remove keyword %s from article %s successfully" % (keyword_id, article_id))   