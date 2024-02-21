from educrawlerCrawlerService.spiders.demoCrawler import DemoCrawler
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import scrapy

class DemoCrawlerAPI:
  def __init__(
    self, 
    links = [],
    rules = [],
    type = "website",
    download_delay = 2,
    depth_limit = 3, 
    concurrent_pdomain = 8, 
    concurrent_pid = 0, 
  ) -> None:  
    self.type   = type
    self.spider = None
    self.settings = {}
    self.settings["LINKS"]                          = links
    self.settings["DOWNLOAD_DELAY"]                 = download_delay
    self.settings["DEPTH_LIMIT"]                    = depth_limit
    self.settings["CONCURRENT_REQUESTS_PER_DOMAIN"] = concurrent_pdomain
    self.settings["CONCURRENT_REQUESTS_PER_IP"]     = concurrent_pid
    self.settings["CUSTOM_CRAWL"]                   = []
    self.custom_crawl = rules

    # Custom Rules: (tag_name, class or id, name, inner)
    
  def init_spider(self):
    if self.spider != None:
      return
    
    spider_default_setting = get_project_settings()    
    self.runner = CrawlerRunner(settings=spider_default_setting)
    self.spider = self.runner.crawl(DemoCrawler, user_settings=self.settings, custom_crawl_rules=self.custom_crawl)
    self.spider.addBoth(lambda _: reactor.stop())
    #self.spider = CrawlerRunner(settings=spider_default_setting)
    #self.spider.crawl(DemoCrawler, user_settings=self.settings, custom_crawl_rules=self.custom_crawl)

  def get_settings(self):
    return self.settings

  def is_init(self):
    return self.spider != None

  def start_crawling(self):
    if self.spider == None:
      return
    
    reactor.run()
    #self.spider.start()
    #self.spider.stop()
