from databaseAPI import Singleton

class ArticleController(Singleton):
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
      
    print(sql_command)
      
    article = []
  
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):
        LastUpdate = ''
        if result[5]:
          LastUpdate = result[5].strftime("%m/%d/%Y, %H:%M:%S")
        FirstCrawlDate = ''
        if result[10]:
          FirstCrawlDate = result[10].strftime("%m/%d/%Y, %H:%M:%S")
        
        article.append({
          "Id": result[0],
          "Url": result[2],
          "Title": result[2],
          "FirstCrawlDate": FirstCrawlDate,
          "LastUpdate": LastUpdate,
          "CrawlStatus": result[6],
          "Note": result[7]
        })
        result = self.cur.fetchone()
    except Exception as err :
      print(err)
      return(False, "Error when fetching")
    
    if len(article) == 0:
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
      "detail": article
    })
    
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