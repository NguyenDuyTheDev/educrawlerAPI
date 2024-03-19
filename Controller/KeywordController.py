from ControllerDB.KeywordDB import KeywordDB

keywordDB = KeywordDB()

class KeywordController():
  def getKeyword(self, page, keywordPerPage):
    return keywordDB.getKeywordByPage(
      page=page,
      keywordPerPage=keywordPerPage
    )
    
  def addKeyword(self, keyword):
    return keywordDB.addKeyword(
      keyword=keyword
    )
    
  def editKeyword(self, id, keyword):
    return keywordDB.editKeyword(
      id=id,
      keyword=keyword
    )
    
  def deleteKeyword(self, id):
    return keywordDB.deleteKeywordById(
      id=id
    )