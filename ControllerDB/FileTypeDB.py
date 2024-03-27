from typing import Any
from databaseAPI import Singleton
import math
 
class FileType:
  id: int
  type: str
  
  def __init__(
    self, 
    id, 
    type
  ) -> None:
    self.id = id
    self.type = type
    
  def get(self):
    return {
      "id": self.id,
      "type": self.type
    }
 
class FileTypeDB(Singleton):
  def countFileType(self):
    sql_check_command = '''
    SELECT COUNT(*) FROM public."SupportedFileType";
    '''
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      return (True, result[0])
    except:
      return (False, "Error when checking!")
        
  def getFileTypeByPage(self, page, fileTypePerPage):
    total_file_type_res = self.countFileType()
    if total_file_type_res[0] == False:
      return total_file_type_res
    total_file_type = total_file_type_res[1]
    
    sql_command = '''
    SELECT *
    FROM public."SupportedFileType"
    ORDER BY "ID" 
    OFFSET %s ROWS 
    FETCH FIRST %s ROW ONLY; 
    ''' % (page * fileTypePerPage, fileTypePerPage)
  
    filetypes = []
    try:
      self.cur.execute(sql_command)
      result = self.cur.fetchone()
      while result:
        filetypes.append(FileType(
          id=result[0],
          type=result[1]
        ))
        result = self.cur.fetchone()
    except:
      return (False, "Error when fetching data")

    if len(filetypes) == 0:
      return (False, "No data to fetch")

    return (True, {
      "totalFileType": total_file_type,
      "page": page,
      "fileTypePerPage": fileTypePerPage,
      "totalPage": math.ceil(total_file_type / fileTypePerPage),
      "detail": [ele.get() for ele in filetypes]
    })
    
  def getFileTypeByName(self, fileType):
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "Type" = '%s';
    ''' % (fileType)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (True, FileType(
          id=result[0],
          type=result[1]
        ))
    except:
      return (False, "Error when checking!")    
    return (False, "No data to fetch")
  
  def getFileTypeByID(self, id):
    sql_check_command = '''
    SELECT * FROM public."SupportedFileType" WHERE "ID" = %s;
    ''' % (id)
    
    try:
      self.cur.execute(sql_check_command)
      result = self.cur.fetchone()
      if result:
        return (True, FileType(
          id=result[0],
          type=result[1]
        ))
    except:
      return (False, "Error when checking!")    
    return (False, "No data to fetch")
    
  def addFileType(self, fileType):
    if self.getFileTypeByName(fileType=fileType)[0] == True:
      return (False, "File Type has already existed")
    
    sql_command = '''
    INSERT INTO public."SupportedFileType" ("Type") Values ('%s');
    ''' % (fileType)

    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when creating!")
    
    if self.getFileTypeByName(fileType=fileType)[0] == True:
      return (True, self.getFileTypeByName(fileType=fileType)[1].get())
    
    return (False, "Error when creating!")
  
  def editFileType(self, id, fileType):
    if self.getFileTypeByName(fileType=fileType)[0] == True:
      return (False, "File Type has already existed")
    
    if self.getFileTypeByID(id=id)[0] == False:
      return self.getFileTypeByID(id=id)
    
    sql_command = '''
    UPDATE public."SupportedFileType"
    SET "Type" = '%s'
    WHERE "ID" = %s;
    ''' % (fileType, id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when updating!")
        
    if self.getFileTypeByName(fileType=fileType)[0] == True:
      return (True, self.getFileTypeByName(fileType=fileType)[1].get())    
    
    return (False, "Error when updating!")
  
  def deleteFileTypeById(self, id):
    if self.getFileTypeByID(id=id)[0] == False:
      return self.getFileTypeByID(id=id)
    
    sql_command = '''
    DELETE FROM public."SupportedFileType" WHERE "ID" = %s;
    ''' % (id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    return (True, {
      "id": id
    })
  
  # Spider File Type Management
  def addFileTypeToSpider(self, file_type_id, spider_id):
    sql_command = '''
    INSERT INTO public."SpiderSupportedFileType" ("FileTypeID", "SpiderID")
    VALUES (%s, %s);
    ''' % (file_type_id, spider_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when inserting!")
    
    return (True, "Insert file type %s to spider %s successfully" % (file_type_id, spider_id))      
  
  def removeAllFileTypeFromSpider(self, spider_id):
    sql_command = '''
    DELETE FROM public."SpiderSupportedFileType"
    WHERE "SpiderID" = %s;
    ''' % (spider_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    
    return (True, "Remove all file type from spider %s successfully" % (spider_id))   
      
  def removeFileTypeFromSpider(self, file_type_id, spider_id):
    sql_command = '''
    DELETE FROM public."SpiderSupportedFileType"
    WHERE "FileTypeID" = %s AND "SpiderID" = %s;
    ''' % (file_type_id, spider_id)
    try:
      self.cur.execute(sql_command)
      self.connection.commit()
    except:
      self.cur.execute("ROLLBACK;")
      return (False, "Error when deleting!")
    
    return (True, "Remove file type %s from spider %s successfully" % (file_type_id, spider_id))      
    