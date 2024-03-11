from databaseAPI import Singleton

class CrawlRulesController(Singleton):
  def getCrawlRules(self, crawlRuleID):
    return