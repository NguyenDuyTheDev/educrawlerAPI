from typing import Any, Optional
import scrapy
from scrapy.http import Response
from scrapy.utils.log import configure_logging
from urllib.parse import urlparse, urljoin
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from educrawlerCrawlerService.utils import CssSelectorGenerator, CSSAttributeType, CSSContentType, countExistedTimes, removeEmptySpaceParagraph, removeHTMLTag, removeEmptyLine, countLetterInParagraph, countExistedTimesTokenize
import math

class DemoCrawler(scrapy.Spider):
  name = "demoCrawler"
  allowed_domains = []
  start_urls = []
  visited = []
  upcomming = []
  allowed_file_format = []
  allowed_keyword = [
    "giáo dục",
    "đại học",
    "trường",
    "học",
    "dạy",
    "phổ thông",
    "tiểu học",
    "mầm non",
    "giáo viên",
    "đào tạo",
    "nghề",
    "sinh viên",
    "học sinh",
    "ngành",
    "khoa",
    "trung học",
    "môn",
    "ngữ văn",
    "bài tập",
    "chuyên",
    "học đường",
    "trải nghiệm",
    "vận động",
    "kĩ năng",
    "kiến trúc",
    "học tập",
    "kĩ năng mềm",
    "rèn luyện",
    "giảng viên",
    "sư phạm",
    "tư duy",
    "phân tích",
    "thực nghiệm",
    "giải quyết vấn đề",
    "toán",
    "tự học",
    "hướng dẫn",
    "đánh giá",
    "kết quả",
  ]

  uncrawlable_link = [
    "mailto", "javascript", "commentbox", "tel"
  ] 
  
  custom_settings = {
    'DEPTH_LIMIT': 3
  }
  
  def __init__(self, user_settings, custom_crawl_rules = [], name: str | None = None, **kwargs: Any):
    super(DemoCrawler, self).__init__(name, **kwargs)

    #self.allowed_file_format = user_settings["ALLOWED_FILE_FORMAT"]
    #self.allowed_keyword = user_settings["ALLOWED_KEYWORD"]

    for link in user_settings["LINKS"]:
      self.start_urls.append(link)
        
    for url in self.start_urls:
      parsed_uri = urlparse(url)
      domain = '{uri.netloc}'.format(uri=parsed_uri)
      self.allowed_domains.append(domain)
          
    self.download_delay                                     = user_settings["DOWNLOAD_DELAY"]
    self.custom_settings["DEPTH_LIMIT"]                     = user_settings["DEPTH_LIMIT"]
    #self.custom_settings["CONCURRENT_REQUESTS_PER_DOMAIN"]  = user_settings["CONCURRENT_REQUESTS_PER_DOMAIN"]
    #self.custom_settings["CONCURRENT_REQUESTS_PER_IP"]      = user_settings["CONCURRENT_REQUESTS_PER_IP"]
        
    #self.custom_crawl_rules = custom_crawl_rules
    
  def start_requests(self):
    for url in self.start_urls:
      yield scrapy.Request(
        url=url, 
        callback=self.parse,
        errback=self.errback_httpbin,
      )
      
  def parse(self, response):
    converted_headers = self.convert(response.headers)
    
    if ("text/html" in converted_headers["Content-Type"]):
      academic_keywords = 0
    
      # Crawl Basic Data
      websiteTitle = response.css('title::text').get()
      content   = response.css('p').getall()
          
      # Content Checking and Reformatted
      found_keywords = []
      raw_content = " ".join(content)
      raw_content = removeHTMLTag(raw_content)
      raw_content = removeEmptyLine(raw_content)
      raw_content = removeEmptySpaceParagraph(raw_content)
      total_words = countLetterInParagraph(raw_content)
      minimum_keywords = math.floor(total_words * 1.0 / 200)

      # Check academic content      
      for keyword in self.allowed_keyword:
        count = countExistedTimesTokenize(websiteTitle, keyword)
        if count > 0:
          found_keywords.append(keyword)
          academic_keywords += count
      
        count = countExistedTimesTokenize(raw_content, keyword)
        if count > minimum_keywords:
          found_keywords.append(keyword)
          academic_keywords += count
          
      # Check before save
      if len(self.allowed_keyword) == 0 or (len(self.allowed_keyword) > 0 and academic_keywords > 0):
        items = {
          "crawlerType": "demo",
          "domain": self.allowed_domains[0],
          "url": response.url,
          "academic_keyword": academic_keywords,
          "keywords": found_keywords,
          "title": websiteTitle,
          "reformatted_content": raw_content,
          "total_words": total_words,
          "minimum_keywords": minimum_keywords
        }
        yield items
        
  def errback_httpbin(self, failure):
    # log all failures
    self.logger.error(repr(failure))

    if failure.check(HttpError):
      # these exceptions come from HttpError spider middleware
      # you can get the non-200 response
      response = failure.value.response
      self.logger.error("HttpError on %s", response.url)

    elif failure.check(DNSLookupError):
      # this is the original request
      request = failure.request
      self.logger.error("DNSLookupError on %s", request.url)

    elif failure.check(TimeoutError, TCPTimedOutError):
      request = failure.request
      self.logger.error("TimeoutError on %s", request.url)
    
  def convert(self, data):
    if isinstance(data, bytes):  return data.decode('ascii')
    if isinstance(data, list):   return data.pop().decode('ascii')
    if isinstance(data, dict):   return dict(map(self.convert, data.items()))
    if isinstance(data, tuple):  return map(self.convert, data)
    return data