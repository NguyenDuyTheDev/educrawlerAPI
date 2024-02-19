import psycopg2
from typing import Any

class SingletonMeta(type):
  _instances = {}
  
  hostname = 'localhost'
  username = 'postgres'
  password = 'k0K0R0som@lI' # your password
  database = 'FinalProject'
  
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
      
class Singleton(metaclass=SingletonMeta):
  def getData(self):
    sql_command = '''
    select * from "FinalProject"."Article"
    '''
    
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    print(result)
    return
  
  def createArticle(self):
    return 
  
  def updateArticle(self):
    return
  
  def getTotalArticle(self):
    sql_command = '''
    select count(*) from "FinalProject"."Article";
    '''
    
    self.cur.execute(sql_command)
    result = self.cur.fetchone()
    print(result[0])
    result[0]
  
  def getArticleByID(self, id):
    sql_command = '''
    select * from "FinalProject"."Article" where "Id" = %d
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
        "FinalProject"."Article"
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
    SELECT Count(*) FROM "FinalProject"."Keyword";
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
        "FinalProject"."Keyword"
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
    SELECT * FROM "FinalProject"."Keyword" WHERE "Name" = '%s';
    ''' % (keyword)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Keyword is already existed!")
    
    # Insert
    sql_insert_command = '''
    INSERT INTO "FinalProject"."Keyword" ("Name") Values ('%s');
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
    SELECT * FROM "FinalProject"."Keyword" WHERE "ID" = '%s';
    ''' % (id)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Keyword doesn't exist!")
    
    # Delete
    sql_delete_command = '''
    DELETE FROM "FinalProject"."Keyword" WHERE "ID" = '%s';
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
    SELECT * FROM "FinalProject"."Keyword" WHERE "ID" = '%s';
    ''' % (id)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if not(result):
      return (False, "Keyword doesn't exist!")
    
    # Check if exist
    sql_check_command = '''
    SELECT * FROM "FinalProject"."Keyword" WHERE "Name" = '%s';
    ''' % (new_value)
    
    self.cur.execute(sql_check_command)
    result = self.cur.fetchone()
    if result:
      return (False, "Keyword is already existed!")
    
    # Edit
    sql_delete_command = '''
    UPDATE "FinalProject"."Keyword"
    SET "Name" = '%s'
    WHERE "ID" = %s;
    ''' % (new_value, id)
    try:
      self.cur.execute(sql_delete_command)
      self.connection.commit()
    except:
      return (False, "Error when deleting!")
    finally:
      return (True, "Delete completed!")
  
if __name__ == "__main__":
    # The client code.

    s1 = Singleton()
    s2 = Singleton()

    if id(s1) == id(s2):
        print("Singleton works, both variables contain the same instance.")
    else:
        print("Singleton failed, variables contain different instances.")
        
    print(s1.addKeyword("Trường"))
    print(s1.getTotalKeyword())
    print(s1.editKeywordByID(8, 'THPT'))
    print(s1.getKeywordByPage(0, 5))
    
    passwordReal = "aabbcc"
    
    s1.getData()