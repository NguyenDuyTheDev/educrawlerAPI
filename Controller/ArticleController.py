from databaseAPI import Singleton

class ArticleController(Singleton):
  def getAF(self, article_id):
    return