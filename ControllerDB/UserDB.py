from typing import Any
from datetime import datetime
from databaseAPI import Singleton
 
class User:
  id: int
  username: str
  password: str
  onlineStatus: str
  lastAccess: datetime
  accountStatus: str
  fullName: str
  role: str
  systemLanguage: str
  systemMode: str
  
  def __init__(
    self,
    id,
    username,
    password = "",
    onlineStatus = "Offline",
    lastAccess = None,
    accountStatus = "Good",
    fullName = "",
    role = "User",
    systemLanguage = "Vietnamese",
    systemMode = "light"
  ) -> None:
    self.id = id
    self.username = username
    self.password = password
    self.onlineStatus = onlineStatus
    self.lastAccess = lastAccess
    self.accountStatus = accountStatus
    self.fullName = fullName
    self.role = role
    self.systemLanguage = systemLanguage
    self.systemMode = systemMode
    
  def getBasic(self):
    lastAccess = ''
    if self.lastAccess:
      lastAccess = self.lastAccess.strftime("%m/%d/%Y, %H:%M:%S")
    
    return {
      "id": self.id,
      "username": self.username,
      "onlineStatus": self.onlineStatus,
      "lastAccess": lastAccess,
      "accountStatus": self.accountStatus,
      "role": self.role
    }
    
  def getDetail(self):
    lastAccess = ''
    if self.lastAccess:
      lastAccess = self.lastAccess.strftime("%m/%d/%Y, %H:%M:%S")
    
    return {
      "id": self.id,
      "username": self.username,
      "onlineStatus": self.onlineStatus,
      "lastAccess": lastAccess,
      "accountStatus": self.accountStatus,
      "fullName": self.fullName,
      "role": self.role,
      "systemLanguage": self.systemLanguage,
      "systemMode": self.systemMode
    }
 
class UserDB(Singleton):
  def countUser(self):
    sql_command = '''
    SELECT count(*)
    FROM "User";     
    '''    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not result:
        return (False, "Error when fetching")
    except Exception as err:
      print(err)
      return (False, "Error when fetching")
    return (True, result[0])
  
  def getUser(
    self, 
    page = 0,
    user_per_page = 10
  ): 
    sql_command = '''
    SELECT *
    FROM "User"
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY;     
    ''' % (page, user_per_page)
    
    users = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while (result):                         
        users.append(User(
          id=result[0],
          username=result[1],
          password=result[2],
          onlineStatus=result[3],
          lastAccess=result[4],
          accountStatus=result[5],
          fullName=result[6],
          role=result[9],
          systemLanguage=result[10],
          systemMode=result[11]
        ))
        result = self.cur.fetchone()
    except Exception as err:
      print(err)      
      return (False, "Error when fetching")
    
    if len(users) == 0:
      return (False, "No data to fetch")
    
    return (True, {
      "page": page,
      "userPerPage": user_per_page,
      "detail": [ele.getBasic() for ele in users]
    })
    
  def getUserById(
    self, 
    user_id
  ): 
    sql_command = '''
    SELECT *
    FROM "User"
    WHERE "ID" = %s;
    ''' % (user_id)
    
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      if not (result):                         
        return (False, "No data to fetch")
    except Exception as err:
      print(err)      
      return (False, "Error when fetching")
    
    user = User(
      id=result[0],
      username=result[1],
      password=result[2],
      onlineStatus=result[3],
      lastAccess=result[4],
      accountStatus=result[5],
      fullName=result[6],
      role=result[9],
      systemLanguage=result[10],
      systemMode=result[11]      
    )
    return (True, user.getDetail())
    
  def updateUserStatus(
    self, 
    user_id,
    status = "Good"
  ):
    sql_command = '''
    UPDATE public."User"
    SET "AccountStatus" = '%s'
    WHERE "ID" = %s;
    ''' % (status, user_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except Exception as err:
      print(err)
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    
    return (True, {
      "Id": user_id,
      "Status": status
    })
    
  def updateUserLanguage(
    self, 
    user_id,
    user_language = "English"
  ):
    sql_command = '''
    UPDATE public."User"
    SET "SystemLanguage" = '%s'
    WHERE "ID" = %s;
    ''' % (user_language, user_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except Exception as err:
      print(err)
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    
    return (True, {
      "Id": user_id,
      "SystemLanguage": user_language
    })
    
  def updateUserSystemMode(
    self, 
    user_id,
    system_mode = "Light"
  ):
    sql_command = '''
    UPDATE public."User"
    SET "SystemMode" = '%s'
    WHERE "ID" = %s;
    ''' % (system_mode, user_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except Exception as err:
      print(err)
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    
    return (True, {
      "Id": user_id,
      "SystemMode": system_mode
    })
    
  def updateUser(
    self, 
    user_id,
    fullName = "",
    phone = "",
    mail = ""
  ):
    sql_command = '''
    UPDATE public."User"
    SET "FullName" = '%s',
    "Phone" = '%s',
    "Mail" = '%s'
    WHERE "ID" = %s;
    ''' % (fullName, phone, mail, user_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except Exception as err:
      print(err)
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    
    return (True, {
      "Id": user_id,
      "FullName": fullName,
      "Phone": phone,
      "Mail": mail
    })
    
  def deleteUser(
    self, 
    user_id
  ):
    sql_command = '''
    DELETE FROM public."User"
    WHERE "ID" = %s;
    ''' % (user_id)
    
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except Exception as err:
      print(err)
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
    
    return (True, {
      "Id": user_id
    })