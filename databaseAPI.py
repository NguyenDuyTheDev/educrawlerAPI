import psycopg2
from datetime import datetime
from typing import Any

class PsycopgDBSingleton(type):
  _instances = {}
  
  hostname = 'dpg-co1fo1q1hbls73a3bcu0-a.singapore-postgres.render.com'
  username = 'educrawlerbackup_user'
  password = 'kST7rhkPuXNxaenA3wTdQvvAXvbl7ATX' # your password
  database = 'educrawlerbackup'
  
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
      
class Singleton(metaclass=PsycopgDBSingleton):
  #Propertise
  def getUsageStorage(self): 
    sql_command = '''
      SELECT pg_size_pretty(pg_database_size('educrawlerbackup'));
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
      SELECT count(*) FROM pg_stat_activity WHERE "datname" = 'educrawlerbackup';
    '''
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    return result[0]
  
  def isMaxConnection(self):
    recentConnection = self.getUsedConnection()
    if recentConnection >= 97:
      return True
    return False
  
  # CrawlRules
  def createCrawlRules(self, tag, className, IDName, child = None):
    if child == None or len(child) == 0:
      sql_command = '''
      INSERT INTO public."CrawlRules" ("Tag", "HTMLClassName", "HTMLIDName") Values ('%s', '%s', '%s');
      SELECT * 
      FROM public."CrawlRules" 
      WHERE "Tag" = '%s' AND "HTMLClassName" = '%s' AND "HTMLIDName" = '%s'
      ORDER BY "ID" DESC;
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

  def getWebpageSpiderCrawlRulebyID(self, id):
    sql_command = '''
    SELECT *
    FROM public."WebpageSpiderCrawlRules", public."CrawlRules"
    WHERE public."WebpageSpiderCrawlRules"."CrawlRulesID" = public."CrawlRules"."ID" and public."WebpageSpiderCrawlRules"."SpiderID" = %s;
    ''' % (id)
    
    crawl_rules = []
    sub_crawl_rules = []
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
          sub_crawl_rules.append({
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
    
    crawl_rules_as_string = []
    for mainRule in range(0, len(crawl_rules)):
      mainRuleAsString = crawl_rules[mainRule]["Tag"]
      if len(crawl_rules[mainRule]["ClassName"]) > 0:
        mainRuleAsString = mainRuleAsString + " ." + crawl_rules[mainRule]["ClassName"]
      if len(crawl_rules[mainRule]["IDName"]) > 0:
        mainRuleAsString = mainRuleAsString + " #" + crawl_rules[mainRule]["IDName"]
        
      childID = crawl_rules[mainRule]["ChildId"]
      while childID != None:
        for subRule in range(0, len(sub_crawl_rules)):
          if sub_crawl_rules[subRule]["Id"] == childID:
            mainRuleAsString = mainRuleAsString + " " + sub_crawl_rules[subRule]["Tag"]
            if len(sub_crawl_rules[subRule]["ClassName"]) > 0:
              mainRuleAsString = mainRuleAsString + " ." + sub_crawl_rules[subRule]["ClassName"]
            if len(sub_crawl_rules[subRule]["IDName"]) > 0:
              mainRuleAsString = mainRuleAsString + " #" + sub_crawl_rules[subRule]["IDName"]
            childID = sub_crawl_rules[subRule]["ChildId"]
            break
        
      crawl_rules_as_string.append(mainRuleAsString)
    
    return (True, crawl_rules_as_string)        

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
    