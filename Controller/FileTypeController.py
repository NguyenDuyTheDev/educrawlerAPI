from ControllerDB.FileTypeDB import FileTypeDB

fileTypeDB = FileTypeDB()

class FileTypeController():
  def getFileType(self, page, fileTypePerPage):
    return fileTypeDB.getFileTypeByPage(
      page=page,
      fileTypePerPage=fileTypePerPage
    )
    
  def addFileType(self, fileType):
    return fileTypeDB.addFileType(
      fileType=fileType
    )
    
  def editFileType(self, id, fileType):
    return fileTypeDB.editFileType(
      id=id,
      fileType=fileType
    )
    
  def deleteFileType(self, id):
    return fileTypeDB.deleteFileTypeById(
      id=id
    )