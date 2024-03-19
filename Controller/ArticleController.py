from ControllerDB.ArticleDB import ArticleDB

articleDB = ArticleDB()

class ArticleController():
  def countArticle(
    self
  ):
    return articleDB.countArticle()
  
  def sortArticle(
    self, 
    page = 0, 
    article_per_page = 10,
    order_by = 'LastUpdate',
    filter_order = 'ASC',
    start_time = '',
    end_time = ''
  ):
    return articleDB.sortArticle(
      page=page, 
      article_per_page=article_per_page,
      order_by=order_by,
      filter_order=filter_order,
      start_time=start_time,
      end_time=end_time
    )
    
  def getArticle(
    self, 
    article_id = 0
  ):
    return articleDB.getArticleByID(
      article_id=article_id
    )
    
  def createArticle(
    self,
    title, 
    domain, 
    url, 
    content
  ):
    return articleDB.createArticle(
      title=title,
      domain=domain,
      url=url,
      content=content
    )
    
  def editArticle(
    self, 
    article_id, 
    title, 
    domain, 
    url, 
    content
  ):
    return articleDB.editArticle(
      title=title,
      article_id=article_id,
      domain=domain,
      url=url,
      content=content
    )
    
  def deleteArticle(
    self,
    article_id
  ):
    return articleDB.deleteArticle(
      article_id=article_id
    )
    
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