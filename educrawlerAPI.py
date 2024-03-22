from typing import Union, List, Annotated
from enum import Enum
from datetime import datetime, time, timedelta, date

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from databaseAPI import Singleton
from Controller.SpiderController import SpiderController
from Controller.ArticleController import ArticleController
from Controller.WebpageSpiderController import WebpageSpiderController
from Controller.WebsiteSpiderController import WebsiteSpiderController
from Controller.UserController import UserController

# Controller
from Controller.KeywordController import KeywordController

import requests
from urllib.parse import urlparse

#uvicorn educrawlerAPI:app --reload

EDUCRAWLER_SERVICE_API_ENDPOINT = "https://educrawlercrawlerservice.onrender.com/schedule.json"

databaseAPI = Singleton()
spiderController = SpiderController()
articleController = ArticleController()
keywordController = KeywordController()
webpageSpiderController = WebpageSpiderController()
websiteSpiderController = WebsiteSpiderController()
userController = UserController()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel

class Message(BaseModel):
  message: str

@app.get("/", tags=["Introduction"])
def get_introduction():
    return {
      "Name": "EducrawlerAPI",
      "Description": "API for managing Education Article and Spider",
      "API Document Url (Swagger UI)": "https://educrawlerapi.onrender.com/docs",
      "API Document Url (Redoc)": "https://educrawlerapi.onrender.com/redoc",
      "Job Log": {
        "19/02 - 03/03: Spider Info": {
          "Complete": {
            "1": "Add most of fetching infomation for 2 type of spider",
            "2": "Add endpoint for keyword, file type and article"
          },
          "Remaining": {
            "1": "Add endpoint for getting single spider"
          }
        }
      },
      "Change Log": {
        "01/03": {
          "1": "Add simple user endpoint for further feature: User create Spider",
          "2": "Add error handler for most of database change feature",
          "3": "Change every get all feature to get by page"
        },
        "06/03": {
          "1": "Fix bug"
        }
      }
    }

# Keyword
@app.get("/keywords", status_code=200, tags=["Keyword"])
def get_keywords(page: int = 0, keywordPerPage: int = 10):
  res = keywordController.getKeyword(
    page=page,
    keywordPerPage=keywordPerPage
  )
  if res[0] == True:
    return JSONResponse(status_code=200, content=res[1]) 
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1]) 
  return JSONResponse(status_code=500, content=res[1]) 
      
@app.post("/keywords", status_code=201, tags=["Keyword"])
def create_keyword(name: str):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  res = keywordController.addKeyword(name)
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  if res[1] == "Keyword has already existed":
    return JSONResponse(status_code=422, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
@app.put("/keywords/{keyword_id}", status_code=200, tags=["Keyword"])
def update_keyword(keyword_id: int, name: str):
  res = keywordController.editKeyword(
    id=keyword_id, 
    keyword=name
  )
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content={"message": "Keyword Id doesn't exist"})
  if res[1] == "Keyword has already existed":
    return JSONResponse(status_code=422, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  

@app.delete("/keywords/{keyword_id}", status_code=200, tags=["Keyword"])
def delete_keyword(keyword_id: int):
  res = keywordController.deleteKeyword(
    id=keyword_id
  )
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content={"message": "Keyword doesn't exist"})
  return JSONResponse(status_code=500, content={"message": res[1]})  
    
# File Type
@app.get("/filetypes", status_code=200, tags=["Supported File Type"])
def get_supported_file_types(page: int = 0, filetypePerPage: int = 10):
  total_supported_file_types = databaseAPI.getTotalSupportedFileType()
  if total_supported_file_types[0] == False:
    return JSONResponse(status_code=500, content={"message": res[1]})  

  res = databaseAPI.getSupportedFileTypeByPage(
    page=page, 
    pageFileTypesNumber=filetypePerPage
    )
    
  if res[0] == True:
    return JSONResponse(status_code=200, content={
      "total_supported_file_types": total_supported_file_types[1],
      "detail": res[1]
    })  
  else:
    if res[1] == "No data to get":
      return JSONResponse(status_code=404, content={"detail": res[1]})
    return JSONResponse(status_code=500, content={"detail": res[1]})
  
@app.post("/filetypes", status_code=201, tags=["Supported File Type"])
def create_file_type(name: str):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  res = databaseAPI.addSupportedFileType(name)
  
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  else:
    if res[1] == "File Type is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    return JSONResponse(status_code=500, content={"message": res[1]}) 
    
@app.put("/filetypes/{keyword_id}", status_code=200, tags=["Supported File Type"])
def update_file_type(file_type_id: int, name: str):
  res = databaseAPI.editSupportedFileTypeByID(file_type_id, name)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "File Type doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "File Type is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    return JSONResponse(status_code=500, content={"message": "Error when updating!"}) 

@app.delete("/filetypes/{keyword_id}", status_code=200, tags=["Supported File Type"])
def delete_file_type(file_type_id: int):
  res = databaseAPI.deleteSupportedFileTypeByID(file_type_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "File Type doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    return JSONResponse(status_code=500, content={"message": res[1]}) 

# Article
class Article(BaseModel):
    domain: str
    url: str
    filename: str
    content: str
    title: str
    note: str
    spiderid: int

@app.get("/articles", status_code=200, tags=["Article"])
def get_articles(page: int = 0, articlePerPage: int = 10):
  res = articleController.sortArticle(
    page=page,
    article_per_page=articlePerPage,
    order_by="LastUpdate",
    filter_order="DESC",
  )
    
  if res[0] == True:
    return JSONResponse(status_code=200, content=res[1])
  
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])
  
@app.get("/articles/search", status_code=200, tags=["Article"])
def search_articles(content: str ,page: int = 0, articlePerPage: int = 10):
  res = articleController.searchArticle(
    content=content,
    page=page,
    article_per_page=articlePerPage
  )
    
  if res[0] == True:
    return JSONResponse(status_code=200, content=res[1])
  
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])
  
class OrderBy(str, Enum):
    LastUpdate = "LastUpdate"
    FirstCrawlDate = "FirstCrawlDate"

class FilterOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
  
@app.post("/articles/sort", status_code=200, tags=["Article"])
def sort_articles(
  page: int = 0, 
  articlePerPage: int = 10,
  orderBy: OrderBy = "LastUpdate",
  filterOrder: FilterOrder = "DESC",
  startTime: Annotated[date | None, Body()] = None,
  endTime: Annotated[date | None, Body()] = None
  ):
  startTimeReformatted = ''
  endTimeReformatted = ''

  if isinstance(startTime, date) and isinstance(endTime, date):
    #startTime += timedelta(days=1)
    #endTime += timedelta(days=1)
    startTimeReformatted = startTime.strftime("%Y-%m-%d")
    endTimeReformatted = endTime.strftime("%Y-%m-%d")

  elif isinstance(startTime, date):
    #startTime += timedelta(days=1)
    startTimeReformatted = startTime.strftime("%Y-%m-%d")
    today = date.today() + timedelta(days=1)
    endTimeReformatted = today.strftime("%Y-%m-%d")

  elif isinstance(endTime, date):
    day = date.today() - timedelta(weeks=100)
    startTimeReformatted = day.strftime("%Y-%m-%d")
    #endTime += timedelta(days=1)
    endTimeReformatted = endTime.strftime("%Y-%m-%d")
    
  else:
    day = date.today() - timedelta(weeks=100)
    startTimeReformatted = day.strftime("%Y-%m-%d")    
    today = date.today() + timedelta(days=1)
    endTimeReformatted = today.strftime("%Y-%m-%d")
  
  res = articleController.sortArticle(
    page=page,
    article_per_page=articlePerPage,
    order_by=orderBy,
    filter_order=filterOrder,
    start_time=startTimeReformatted,
    end_time=endTimeReformatted
  )
    
  if res[0] == True:
    return JSONResponse(status_code=200, content=res[1])
  
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])  
  
@app.get("/articles/{article_id}", status_code=200, tags=["Article"])
def get_article_by_id(article_id: int):
  res = articleController.getArticle(article_id=article_id)
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])

  if res[1] == "No Article Existes":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.post("/article", status_code=201, tags=["Article"])
def create_article(article: Article):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  res = articleController.createArticle(
    title=article.title,
    domain=article.domain,
    url=article.url,
    content=article.content  
  )
  
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  if res[1] == "Article is already existed!":
    return JSONResponse(status_code=422, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]}) 

@app.post("/article/{article_id}/reCrawl", status_code=201, tags=["Article"])
def recrawl_the_article_with_demo_spider(article_id: int):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."}) 
    
  res = articleController.getArticle(article_id=article_id)
  if res[0] == False:
    return JSONResponse(status_code=404, content={"message": "Article Not Found"}) 
  
  api_endpoint = EDUCRAWLER_SERVICE_API_ENDPOINT
  body = {
    "project": "default",
    "spider": "demoCrawlerURL",
    "link": res[1]["url"]
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    return JSONResponse(status_code=200, content="This article is recrawling")
  return JSONResponse(status_code=res.status_code, content="Can not crawl this article")
      
@app.put("/article/{article_id}", status_code=200, tags=["Article"])
def update_article(article_id: int, article: Article):
  res = articleController.editArticle(
    article_id=article_id,
    title=article.title,
    domain=article.domain,
    url=article.url,
    content=article.content    
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "Article doesn't exist!":
    return JSONResponse(status_code=404, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]}) 

@app.delete("/article/{article_id}", status_code=200, tags=["Article"])
def delete_article(article_id: int):
  res = articleController.deleteArticle(article_id=article_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "No Article Exist":
    return JSONResponse(status_code=404, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": "Error when deleting article!"}) 
  
# Webpage Spider  

class CrawlRule(BaseModel):
    id: int
    tag: str
    HTMLClassName: str
    HTMLIDName: str
    ChildCrawlRuleID: int
  
class WebpageSpider(BaseModel):
    url: str
    keyword: List[int] 
    filetype: List[int]
    crawlRules: List[CrawlRule]

@app.get("/webpageSpider", status_code=200, tags=["Webpage Spider"])
def get_webpage_spider(page: int = 0, spiderPerPage: int = 10):
  res = webpageSpiderController.getSpiders(
    page=page,
    spiderPerPage=spiderPerPage
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/webpageSpider/{spider_id}", status_code=200, tags=["Webpage Spider"])
def get_webpage_spider_by_id(spider_id: int):
  res = webpageSpiderController.getSpiderById(
    id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No Webpage Spider Exist":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/webpageSpider/{spider_id}/history", status_code=201, tags=["Webpage Spider"])
def get_webpage_spider_history(spider_id: int):
  res = webpageSpiderController.getHistory(
    spider_id=spider_id
  )
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/webpageSpider/{spider_id}/article", status_code=200, tags=["Webpage Spider"])
def get_webpage_spider_article(spider_id: int):
  res = webpageSpiderController.getArticles(
    spider_id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/webpageSpider/{spider_id}/crawl_rule", status_code=201, tags=["Webpage Spider"])
def get_webpage_spider_crawl_rule_by_id(spider_id: int):
  res = databaseAPI.getWebpageSpiderCrawlRulebyID(
    id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.post("/webpageSpider", status_code=201, tags=["Webpage Spider"])
def create_webpage_spider(spider_status: WebpageSpider):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  if spider_status.url == "":
    return JSONResponse(status_code=422, content={"detail": "Url can not be empty"})   
    
  crawlRule = []
  
  for rule in spider_status.crawlRules:
    if rule.tag == "":
      return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
    if rule.id < 1:
      return JSONResponse(status_code=422, content={"detail": "Id should start from 1"})    
    
    crawlRule.append({
      "id": rule.id,
      "tag": rule.tag,
      "HTMLClassName": rule.HTMLClassName,
      "HTMLIDName": rule.HTMLIDName,
      "ChildCrawlRuleID": rule.ChildCrawlRuleID
    }) 
  
  relatedCrawlrule = []
  for index in range(0, len(spider_status.crawlRules)):
    isChildrenRule = False
    
    for existedCrawlrule in range(0, len(relatedCrawlrule)):
      for subcrawlRule in relatedCrawlrule[existedCrawlrule]:
        if spider_status.crawlRules[subcrawlRule].ChildCrawlRuleID == spider_status.crawlRules[index].id:
          isChildrenRule = True
          relatedCrawlrule[existedCrawlrule].append(index)
          break
        
      if isChildrenRule == True:
        break
    
    if isChildrenRule == False:
      relatedCrawlrule.append([index])
  
  afterReformatCrawlRules = []
  for longRule in relatedCrawlrule:
    rules = []

    for rule in longRule:
      rules.append(
        [
          spider_status.crawlRules[rule].tag,
          spider_status.crawlRules[rule].HTMLClassName,
          spider_status.crawlRules[rule].HTMLIDName,
        ]
      )
      
    for index in range(1, len(rules)):
      rules[index - 1].append(rules[index])
      
    afterReformatCrawlRules.append(rules[0])
  
  res = webpageSpiderController.createWebpageSpider(
    url=spider_status.url,
    crawlRules=afterReformatCrawlRules,
    fileTypes=spider_status.filetype,
    keywords=spider_status.keyword    
  )  

  if res[0] == True:
    return JSONResponse(
      status_code=201, 
      content={
        "url": spider_status.url,
        "keyword": spider_status.keyword,
        "filetype": spider_status.filetype,
        "crawlRules": crawlRule,
        "relatedRule": relatedCrawlrule,
        "realRule": afterReformatCrawlRules
      }
    )
  if res[1] == "Spider is already existed!":
    return JSONResponse(status_code=422, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]}) 

@app.put("/webpageSpider/{spider_id}/crawlRules", status_code=200, tags=["Webpage Spider"])
def update_webpage_spider_crawl_rules(spider_id: int ,crawl_rules: List[CrawlRule] = []): 
  crawlRule = []
  
  for rule in crawl_rules:
    if rule.tag == "":
      return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
    if rule.id < 1:
      return JSONResponse(status_code=422, content={"detail": "Id should start from 1"})    
    
    crawlRule.append({
      "id": rule.id,
      "tag": rule.tag,
      "HTMLClassName": rule.HTMLClassName,
      "HTMLIDName": rule.HTMLIDName,
      "ChildCrawlRuleID": rule.ChildCrawlRuleID
    }) 
  
  relatedCrawlrule = []
  for index in range(0, len(crawl_rules)):
    isChildrenRule = False
    
    for existedCrawlrule in range(0, len(relatedCrawlrule)):
      for subcrawlRule in relatedCrawlrule[existedCrawlrule]:
        if crawl_rules[subcrawlRule].ChildCrawlRuleID == crawl_rules[index].id:
          isChildrenRule = True
          relatedCrawlrule[existedCrawlrule].append(index)
          break
        
      if isChildrenRule == True:
        break
    
    if isChildrenRule == False:
      relatedCrawlrule.append([index])
  
  afterReformatCrawlRules = []
  for longRule in relatedCrawlrule:
    rules = []

    for rule in longRule:
      rules.append(
        [
          crawl_rules[rule].tag,
          crawl_rules[rule].HTMLClassName,
          crawl_rules[rule].HTMLIDName,
        ]
      )
      
    for index in range(1, len(rules)):
      rules[index - 1].append(rules[index])
      
    afterReformatCrawlRules.append(rules[0])
  
  res = webpageSpiderController.updateCrawlRules(
    spider_id=spider_id,
    crawl_rules=afterReformatCrawlRules
  )

  if res[0] == True:
    return JSONResponse(
      status_code=200, 
      content={
        "spiderId": spider_id,
        "crawlRules": crawlRule,
        "relatedRule": relatedCrawlrule,
        "realRule": afterReformatCrawlRules
      }
    )
  return JSONResponse(status_code=500, content={"message": res[1]}) 

@app.post("/webpageSpider/{spider_id}/run", status_code=201, tags=["Webpage Spider"])
def run_webpage_spider(spider_id: int):
  webpage_spider_information = webpageSpiderController.getSpiderById(spider_id)
  if webpage_spider_information[0] != True:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  if webpage_spider_information[1]["JobId"] != '':
    return JSONResponse(status_code=404, content="The Spider is already running!")

  keywords = webpage_spider_information[1]["Keyword"]
  keywords_as_string: str = ''
  for word in keywords:
    keywords_as_string = keywords_as_string + word["Value"] + ','
  keywords_as_string = keywords_as_string[:-1]
  print(keywords_as_string)
  
  crawl_rule = databaseAPI.getWebpageSpiderCrawlRulebyID(spider_id)
  crawl_rule_as_string = ""
  if crawl_rule[0] == True:
    crawl_rule_as_string = ",".join(crawl_rule[1])
    print(crawl_rule_as_string)
    
  api_endpoint = EDUCRAWLER_SERVICE_API_ENDPOINT
  body = {
    "project": "default",
    "spider": "WebpageSpider",
    "link": webpage_spider_information[1]["Url"],
    "spider_id": spider_id,
    "keywords": keywords_as_string,
    "crawlRule": crawl_rule_as_string,
    "isAcademic": webpage_spider_information[1]["IsAcademic"]
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    res_data = res.json()
    body["jobid"] = res_data["jobid"]
    
    setJobIDResult = databaseAPI.setSpiderJobID(spider_id, body["jobid"])
    if setJobIDResult[0] == True:
      return JSONResponse(status_code=200, content=setJobIDResult[1])
    else:
      return JSONResponse(status_code=200, content="The Spider is running without updating jobid")
  else:
    return JSONResponse(status_code=res.status_code, content="Can not crawl")
  
@app.post("/webpageSpider/{spider_id}/stop", status_code=200, tags=["Webpage Spider"])
def stop_webpage_spider(spider_id: int):
  webpage_spider_information = webpageSpiderController.getSpiderById(spider_id)
  
  if webpage_spider_information[0] == True:
    if webpage_spider_information[1]["JobId"] == '':
      return JSONResponse(status_code=404, content="The Spider is not running!")
  else:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/cancel.json"
  body = {
    "project": "default",
    "job": webpage_spider_information[1]["JobId"]
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    res = databaseAPI.updateSpiderWhenClosingViaID(spider_id)
    if res[0] == True:
      return JSONResponse(status_code=200, content="Close spider successfully!")
    else:
      return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=res.status_code, content="Can not stop")
  
@app.get("/webpageSpider/{spider_id}/lastRunTime", status_code=200, tags=["Webpage Spider"])
def get_last_run_time(spider_id: int):
  res = databaseAPI.calculateLastRunTime(spider_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"TotalRunTime": res[1]}) 
  return JSONResponse(status_code=500, content="Can not calculate")

# Website Spider
class SubFolder(BaseModel):
    url: str
    crawlRules: List[CrawlRule]
    searchRules: List[CrawlRule]

class WebsiteSpider(BaseModel):
    url: str
    delay: float
    graphdeep: int
    maxThread: int
    keyword: List[int] 
    filetype: List[int]
    subfolders: List[SubFolder]
    
@app.get("/websiteSpider", status_code=200, tags=["Website Spider"])
def get_website_spider(page: int = 0, spiderPerPage: int = 10):
  res = websiteSpiderController.getByPage(
    page=page,
    spider_by_page=spiderPerPage
  )
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/websiteSpider/{spider_id}", status_code=200, tags=["Website Spider"])
def get_website_spider_by_id(spider_id: int):
  res = websiteSpiderController.getById(
    spider_id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No Website Spider Exist":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/websiteSpider/{spider_id}/history", status_code=200, tags=["Website Spider"])
def get_website_spider_history(spider_id: int):
  res = websiteSpiderController.getHistory(
    spider_id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.post("/websiteSpider/{spider_id}/run", status_code=201, tags=["Website Spider"])
def run_website_spider(spider_id: int):
  webpage_spider_information = websiteSpiderController.getById(spider_id=spider_id)
  if webpage_spider_information[0] != True:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  if webpage_spider_information[1]["JobId"] != '':
    return JSONResponse(status_code=200, content="The Spider is already running!")
  
  keywords = webpage_spider_information[1]["Keyword"]
  keywords_as_string: str = ''
  for word in keywords:
    keywords_as_string = keywords_as_string + word["Value"] + ','
  keywords_as_string = keywords_as_string[:-1]
  print(keywords_as_string)
  
  api_endpoint = EDUCRAWLER_SERVICE_API_ENDPOINT
  body = {
    "project": "default",
    "spider": "WebsiteSpider",
    "link": webpage_spider_information[1]["Url"],
    "spider_id": spider_id,
    "delay": webpage_spider_information[1]["Delay"],
    "graphDeep": webpage_spider_information[1]["GraphDeep"],
    "maxThread": webpage_spider_information[1]["MaxThread"],
    "keywords": keywords_as_string,
    "isAcademic": webpage_spider_information[1]["IsAcademic"]
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    res_data = res.json()
    body["jobid"] = res_data["jobid"]
    print(body["jobid"])
    
    setJobIDResult = websiteSpiderController.setJobId(
      spider_id=spider_id,
      job_id=body["jobid"]
    )
    
    if setJobIDResult[0] == True:
      return JSONResponse(status_code=200, content=setJobIDResult[1])
    return JSONResponse(status_code=200, content="The Spider is running without updating jobid")
  return JSONResponse(status_code=res.status_code, content="Can not crawl")
  
@app.post("/websiteSpider/{spider_id}/stop", status_code=201, tags=["Website Spider"])
def stop_website_spider(spider_id: int):
  webpage_spider_information = websiteSpiderController.getById(spider_id=spider_id)
  
  if webpage_spider_information[0] == True:
    if webpage_spider_information[1]["JobId"] == '':
      return JSONResponse(status_code=404, content="The Spider is not running!")
  else:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/cancel.json"
  body = {
    "project": "default",
    "job": webpage_spider_information[1]["JobId"]
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    res = websiteSpiderController.removeJobId(spider_id=spider_id)
    if res[0] == True:
      return JSONResponse(status_code=200, content=res[1])
    return JSONResponse(status_code=200, content=res[1])
  return JSONResponse(status_code=res.status_code, content="Can not stop")

  
@app.post("/websiteSpider", status_code=201, tags=["Website Spider"])
def create_website_spider(spider_status: WebsiteSpider):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  # Validate Input
  if spider_status.url == "":
    return JSONResponse(status_code=403, content={"detail": "Url can not be empty"})   
    
  if spider_status.delay < 0.5:
    return JSONResponse(status_code=403, content={"detail": "Spider delay can not be lower than 0.5."})   
   
  if spider_status.graphdeep < 1:
    return JSONResponse(status_code=403, content={"detail": "Spider graph deep can not be lower than 1."})
    
  if spider_status.graphdeep > 3:
    return JSONResponse(status_code=403, content={"detail": "Spider does not support graph deep greater than 3"})
    
  if spider_status.maxThread < 1:
    return JSONResponse(status_code=403, content={"detail": "Spider max Thread can not be lower than 1."})
   
  if spider_status.maxThread > 8:
    return JSONResponse(status_code=403, content={"detail": "Spider does not support max thread deep greater than 8"})
    
  # Format Crawl Rule and search rule for subfolder
  subFolders = []
  afterReformatCrawlRules = []
  
  for folder in spider_status.subfolders:
    crawlRule = []
    folderReformatCrawlRule = []
  
    # Crawl Rules
    for rule in folder.crawlRules:
      if rule.tag == "":
        return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
      
      crawlRule.append({
        "id": rule.id,
        "tag": rule.tag,
        "HTMLClassName": rule.HTMLClassName,
        "HTMLIDName": rule.HTMLIDName,
        "ChildCrawlRuleID": rule.ChildCrawlRuleID
      }) 
    
    relatedCrawlrule = []
    for index in range(0, len(folder.crawlRules)):
      isChildrenRule = False
      
      for existedCrawlrule in range(0, len(relatedCrawlrule)):
        for subcrawlRule in relatedCrawlrule[existedCrawlrule]:
          if folder.crawlRules[subcrawlRule].ChildCrawlRuleID == folder.crawlRules[index].id:
            isChildrenRule = True
            relatedCrawlrule[existedCrawlrule].append(index)
            break
          
        if isChildrenRule == True:
          break
      
      if isChildrenRule == False:
        relatedCrawlrule.append([index])
    
    for longRule in relatedCrawlrule:
      rules = []
      for rule in longRule:
        rules.append(
          [
            folder.crawlRules[rule].tag,
            folder.crawlRules[rule].HTMLClassName,
            folder.crawlRules[rule].HTMLIDName,
          ]
        )
        
      for index in range(1, len(rules)):
        rules[index - 1].append(rules[index])
        
      afterReformatCrawlRules.append(rules[0])
      folderReformatCrawlRule.append(rules[0])
    
    # Search Rules
    searchRules = []
    
    for rule in folder.searchRules:
      if rule.tag == "":
        return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
      
      searchRules.append([
        rule.tag, rule.HTMLClassName, rule.HTMLIDName
      ])
    
    subFolders.append((folder.url, folderReformatCrawlRule, searchRules))
    
  # Create in db
  res = websiteSpiderController.createSpider(
    url=spider_status.url,
    delay=spider_status.delay,
    graphDeep=spider_status.graphdeep,
    maxThread=spider_status.maxThread,
    fileTypes=spider_status.filetype,
    keywords=spider_status.keyword,
    subfolder=subFolders    
  )

  if res[0] == True:
    return JSONResponse(
      status_code=201, 
      content={
        "url": spider_status.url,
        "delay": spider_status.delay,
        "graphdeep": spider_status.graphdeep,
        "maxThread": spider_status.maxThread,
        "keyword": spider_status.keyword,
        "filetype": spider_status.filetype,
        "realRule": afterReformatCrawlRules,
        "Subfolder": subFolders
      }
    )
  else:
    if res[1] == "Spider is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating spider!":
      return JSONResponse(status_code=500, content={"message": res[1]}) 
    return JSONResponse(status_code=500, content={"message": res[1]}) 
  
@app.put("/websiteSpider/{spider_id}/subfolder", status_code=200, tags=["Website Spider"])
def update_website_spider_subfolder(spider_id: int, subfolders: List[SubFolder]):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
    
  # Format Crawl Rule and search rule for subfolder
  subFolders = []
  afterReformatCrawlRules = []
  
  print(subfolders)
  for folder in subfolders:
    crawlRule = []
    folderReformatCrawlRule = []
  
    # Crawl Rules
    for rule in folder.crawlRules:
      if rule.tag == "":
        return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
      
      crawlRule.append({
        "id": rule.id,
        "tag": rule.tag,
        "HTMLClassName": rule.HTMLClassName,
        "HTMLIDName": rule.HTMLIDName,
        "ChildCrawlRuleID": rule.ChildCrawlRuleID
      }) 
    
    relatedCrawlrule = []
    for index in range(0, len(folder.crawlRules)):
      isChildrenRule = False
      
      for existedCrawlrule in range(0, len(relatedCrawlrule)):
        for subcrawlRule in relatedCrawlrule[existedCrawlrule]:
          if folder.crawlRules[subcrawlRule].ChildCrawlRuleID == folder.crawlRules[index].id:
            isChildrenRule = True
            relatedCrawlrule[existedCrawlrule].append(index)
            break
          
        if isChildrenRule == True:
          break
      
      if isChildrenRule == False:
        relatedCrawlrule.append([index])
    
    for longRule in relatedCrawlrule:
      rules = []
      for rule in longRule:
        rules.append(
          [
            folder.crawlRules[rule].tag,
            folder.crawlRules[rule].HTMLClassName,
            folder.crawlRules[rule].HTMLIDName,
          ]
        )
        
      for index in range(1, len(rules)):
        rules[index - 1].append(rules[index])
        
      afterReformatCrawlRules.append(rules[0])
      folderReformatCrawlRule.append(rules[0])
    
    # Search Rules
    searchRules = []
    
    for rule in folder.searchRules:
      if rule.tag == "":
        return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
      
      searchRules.append([
        rule.tag, rule.HTMLClassName, rule.HTMLIDName
      ])
    
    subFolders.append((folder.url, folderReformatCrawlRule, searchRules))
    
  # Create in db
  res = websiteSpiderController.updateSubFolder(
    spider_id=spider_id,
    subfolder=subFolders
  )

  if res[0] == True:
    return JSONResponse(
      status_code=200, 
      content={
        "id": spider_id,
        "realRule": afterReformatCrawlRules,
        "Subfolder": subFolders
      }
    )
  if res[1] == "Spider is already existed!":
    return JSONResponse(status_code=422, content={"message": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]}) 
  
@app.put("/websiteSpider/{spider_id}/basicSetting", status_code=200, tags=["Website Spider"])
def update_basic_setting(spider_id: int, delay: float = 2.5, graph_deep: int = 2, max_thread: int = 2):
  res = websiteSpiderController.updateSetting(
    spider_id=spider_id,
    delay=delay,
    graphDeep=graph_deep,
    maxThread=max_thread
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])  
  
  
@app.get("/websiteSpider/{spider_id}/article", status_code=200, tags=["Website Spider"])
def get_website_spider_article(spider_id: int, page: int = 0, articlePerPage: int = 10):
  res = websiteSpiderController.getArticles(
    spider_id=spider_id,
    page=page,
    article_per_page=articlePerPage
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])
 
@app.get("/websiteSpider/{spider_id}/crawlRules", status_code=200, tags=["Website Spider"])
def get_website_spider_crawl_rules(spider_id: int):
  res = websiteSpiderController.getCrawlRules(
    spider_id=spider_id
  )
    
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=404, content=res[1])
  
@app.get("/websiteSpider/{spider_id}/searchRules", status_code=200, tags=["Website Spider"])
def get_website_spider_crawl_rules(spider_id: int):
  res = websiteSpiderController.getSearchRules(
    spider_id=spider_id
  )
    
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=404, content=res[1])
  
@app.get("/spiders", status_code=200, tags=["Spider"])
def get_spider_per_page(page: int = 0, spider_per_page: int = 10):
  res = spiderController.getSpiders(
    page=page,
    spider_per_page=spider_per_page
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content=res[1])  
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content={"message": "No data to fetch"})  
  return JSONResponse(status_code=500, content=res[1])  
  
@app.get("/spiders/{spider_id}", status_code=200, tags=["Spider"])
def get_spider(spider_id: int):
  if spiderController.isWebsiteSpider(spider_id=spider_id)[0] == True:
    return get_website_spider_by_id(spider_id=spider_id)
  
  if spiderController.isWebpageSpider(spider_id=spider_id)[0] == True:
    return get_webpage_spider_by_id(spider_id=spider_id)
  
  return JSONResponse(status_code=404, content={"message": "No data to fetch"})  
  
@app.post("/spiders/{spider_id}/run", status_code=200, tags=["Spider"])
def run_spider(spider_id: int):
  if spiderController.isWebsiteSpider(spider_id=spider_id)[0] == True:
    return run_website_spider(spider_id=spider_id)
  
  if spiderController.isWebpageSpider(spider_id=spider_id)[0] == True:
    return run_webpage_spider(spider_id=spider_id)
  
  return JSONResponse(status_code=404, content={"message": "No spider to run"})  
  
@app.post("/spiders/{spider_id}/stop", status_code=200, tags=["Spider"])
def stop_spider(spider_id: int):
  if spiderController.isWebsiteSpider(spider_id=spider_id)[0] == True:
    return stop_website_spider(spider_id=spider_id)
  
  if spiderController.isWebpageSpider(spider_id=spider_id)[0] == True:
    return stop_webpage_spider(spider_id=spider_id)
  
  return JSONResponse(status_code=404, content={"message": "No spider to stop"})  
  
@app.get("/spiders/{spider_id}/history", status_code=200, tags=["Spider"])
def get_spider_history(spider_id: int):
  if spiderController.isWebsiteSpider(spider_id=spider_id)[0] == True:
    return get_website_spider_history(spider_id=spider_id)
  
  if spiderController.isWebpageSpider(spider_id=spider_id)[0] == True:
    return get_webpage_spider_history(spider_id=spider_id)
  
  return JSONResponse(status_code=404, content={"message": "No data to fetch"})  
  
@app.get("/spiders/{spider_id}/articles", status_code=200, tags=["Spider"])
def get_spider_article(spider_id: int, page: int = 0, article_per_page: int = 10):
  if spiderController.isWebsiteSpider(spider_id=spider_id)[0] == True:
    return get_website_spider_article(
      spider_id=spider_id,
      page=page,
      articlePerPage=article_per_page
    )
  
  if spiderController.isWebpageSpider(spider_id=spider_id)[0] == True:
    return get_webpage_spider_article(spider_id=spider_id)
  
  return JSONResponse(status_code=404, content={"message": "No data to fetch"})  
  
@app.delete("/spiders/{spider_id}", status_code=200, tags=["Spider"])
def delete_spider(spider_id: int):
  res = spiderController.deleteSpider(spider_id=spider_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
class UserRole(str, Enum):
    Available = "Available"
    Blocked = "Blocked"
  
@app.put("/spiders/{spider_id}", status_code=200, tags=["Spider"])
def edit_base_spider(
  spider_id: int,
  url: str = "",
  status: UserRole = "Available",
  is_academic: bool = False,
  keyword_ids: List[int] = [],
  filetype_ids: List[int] = []
):
  res = spiderController.editSpider(
    spider_id=spider_id,
    url=url,
    status=status.split(".")[-1],
    is_academic=is_academic,
    keyword_ids=keyword_ids
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})    
  
# User

class UserRole(str, Enum):
    user = "User"
    admin = "Admin"
    manager = "Manager"
  
class User(BaseModel):
    Username: str
    Password: str 
    Role: str
  
@app.post("/users", status_code=201, tags=["User"])
def create_user(user: User):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  if user.Role != "User" and user.Role != "Admin" and user.Role != "Manager":
    return JSONResponse(status_code=429, content={"message": "User Role must be 'User', 'Admin' or 'Manager'"})
  
  res = databaseAPI.createUser(
    username=user.Username,
    password=user.Password,
    role=user.Role
    )
  
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  else:
    if res[1] == "This Username is already existed":
      return JSONResponse(status_code=409, content={"message": res[1]})
    if res[1] == "Manager is already existed":
      return JSONResponse(status_code=409, content={"message": res[1]})
    if res[1] == "Error when creating!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    
@app.get("/users", status_code=200, tags=["User"])
def get_users(page: int = 0, userPerPage: int = 10):
  res = userController.getUser(
    page=page,
    user_per_page=userPerPage
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content={"message": "Not Found"})   
  return JSONResponse(status_code=500, content={"message": res[1]})
  
class AccountStatus(str, Enum):
    Good = "Good"
    Restrict = "Restrict"
    Banned = "Banned"
  
@app.put("/users/{user_id}/accountStatus", status_code=200, tags=["User"])
def update_user_status(user_id: int, account_status: AccountStatus = "Good"):
  res = userController.updateUserStatus(
    user_id=user_id,
    account_status=account_status.split(".")[-1]
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
 
class SystemLanguage(str, Enum):
    English = "English"
    Vietnamese = "Vietnamese"
  
@app.put("/users/{user_id}/systemLanguage", status_code=200, tags=["User"])
def update_user_language(user_id: int, user_language: SystemLanguage = "English"):
  res = userController.updateUserLanguage(
    user_id=user_id,
    user_language=user_language.split(".")[-1]
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
class SystemMode(str, Enum):
    Light = "Light"
    Dark = "Dark"
  
@app.put("/users/{user_id}/systemMode", status_code=200, tags=["User"])
def update_user_system_mode(user_id: int, system_mode: SystemMode = "Light"):
  res = userController.updateUserSystemMode(
    user_id=user_id,
    system_mode=system_mode.split(".")[-1]
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
@app.put("/users/{user_id}", status_code=200, tags=["User"])
def update_user(user_id: int, full_name: str, phone: str, mail: str):
  res = userController.updateUser(
    user_id=user_id,
    full_name=full_name,
    phone=phone,
    mail=mail
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
@app.get("/users/{user_id}", status_code=200, tags=["User"])
def get_user_by_id(user_id: int):
  res = userController.getUserById(
    user_id=user_id
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
@app.delete("/users/{user_id}", status_code=200, tags=["User"])
def delete_user(user_id: int):
  res = userController.deleteUser(
    user_id=user_id
  )
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})  
  
# Demo Spider
@app.get("/demoSpider", status_code=201, tags=["Demo Webpage Spider"])
def crawl_single_page(url: str):
  api_endpoint = EDUCRAWLER_SERVICE_API_ENDPOINT
  body = {
    "project": "default",
    "spider": "demoCrawlerURL",
    "link": url
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    res_data = res.json()
    
    body["jobid"] = res_data["jobid"]
    return JSONResponse(status_code=200, content=body)
  else:
    return JSONResponse(status_code=res.status_code, content="Can not crawl")
  
@app.get("/dashboard/totalRunTime", status_code=200, tags=["Dashboard"])
def get_total_runtime():
  totalRunTimeRes = spiderController.getTotalRuntime()
  if totalRunTimeRes[0] == True:
    return JSONResponse(status_code=200, content={"TotalRunTime": totalRunTimeRes[1]})
  return JSONResponse(status_code=500, content={"message": totalRunTimeRes[1]})

@app.get("/dashboard/totalArticle", status_code=200, tags=["Dashboard"])
def get_total_article():  
  totalArticleRes = articleController.countArticle()
  if totalArticleRes[0] == True:
    return JSONResponse(status_code=200, content={"TotalArticle": totalArticleRes[1]})
  return JSONResponse(status_code=500, content={"message": totalArticleRes[1]})

@app.get("/dashboard/totalGoodCrawl", status_code=200, tags=["Dashboard"])
def get_total_good_crawl():
  totalGoodRes = spiderController.getTotalCrawlSuccess()
  if totalGoodRes[0] == True:
    return JSONResponse(status_code=200, content={"TotalGoodCrawl": totalGoodRes[1]})
  return JSONResponse(status_code=500, content={"message": totalGoodRes[1]})

@app.get("/dashboard/totalBadCrawl", status_code=200, tags=["Dashboard"])
def get_total_runtime():
  totalFailRes = spiderController.getTotalCrawlFail()
  if totalFailRes[0] == True:
    return JSONResponse(status_code=200, content={"TotalBadCrawl": totalFailRes[1]})
  return JSONResponse(status_code=500, content={"message": totalFailRes[1]})

@app.get("/dashboard/allSpiderRunningStatus", status_code=200, tags=["Dashboard"])
def get_all_spider_running_status():
  res = spiderController.getAllSpiderRunningStatus()
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})

@app.get("/dashboard/top10spider", status_code=200, tags=["Dashboard"])
def get_top_10_spider_with_most_article():
  res = spiderController.getTop10SpiderWithMostArticle()
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  return JSONResponse(status_code=500, content={"message": res[1]})