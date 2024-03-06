from typing import Union, List
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from databaseAPI import Singleton

import requests
from urllib.parse import urlparse
import re

#uvicorn educrawlerAPI:app --reload


databaseAPI = Singleton()
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
        }
      }
    }

# Keyword
@app.get("/keywords", status_code=200, tags=["Keyword"])
def get_keywords(page: int = 0, keywordPerPage: int = 10):
  total_keywords = databaseAPI.getTotalKeyword()
  if total_keywords[0] == False:
    return JSONResponse(status_code=500, content={"message": res[1]})      
  
  res = databaseAPI.getKeywordByPage(
    page=page, 
    pageKeywordsNumber=keywordPerPage
    )
  
  if res[0] == True:
    return JSONResponse(
      status_code=200, 
      content={
        "total_keywords": total_keywords[1],
        "keywords": res[1]    
      }
    )
  else:
    if res[1] == "No data to fetch":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Error when fetching data":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    return JSONResponse(status_code=500, content={"message": res[1]})  
      
@app.post("/keywords", status_code=201, tags=["Keyword"])
def create_keyword(name: str):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  res = databaseAPI.addKeyword(name)
  
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  else:
    if res[1] == "Keyword is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    return JSONResponse(status_code=500, content={"message": res[1]})  
  
@app.put("/keywords/{keyword_id}", status_code=200, tags=["Keyword"])
def update_keyword(keyword_id: int, name: str):
  res = databaseAPI.editKeywordByID(keyword_id, name)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Keyword doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Keyword is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    return JSONResponse(status_code=500, content={"message": res[1]})  

@app.delete("/keywords/{keyword_id}", status_code=200, tags=["Keyword"])
def delete_keyword(keyword_id: int):
  res = databaseAPI.deleteKeywordByID(keyword_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Keyword doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
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
  res = databaseAPI.getArticlesByPage(
    page=page, 
    pageArticlesNumber=articlePerPage
    )
    
  if res[0] == True:
    return JSONResponse(status_code=200, content=res[1])
  
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])
  
@app.get("/articles/{article_id}", status_code=200, tags=["Article"])
def get_article_by_id(article_id: int):
  res = databaseAPI.getArticleByID(article_id)
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])

  if res[1] == "No Article Existes":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.post("/article", status_code=201, tags=["Article"])
def create_article(article: Article):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  res = databaseAPI.createArticle(
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
    
@app.put("/article/{article_id}", status_code=200, tags=["Article"])
def update_article(article_id: int, article: Article):
  res = databaseAPI.editArticle(
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
  res = databaseAPI.deleteArticleById(article_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  if res[1] == "Article isn't existed!":
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

@app.get("/webpageSpider", status_code=201, tags=["Webpage Spider"])
def get_webpage_spider(page: int = 0, spiderPerPage: int = 10):
  res = databaseAPI.getWebpageSpider(
    page=page,
    spiderPerPage=spiderPerPage
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/webpageSpider/{spider_id}", status_code=201, tags=["Webpage Spider"])
def get_webpage_spider_by_id(spider_id: int):
  res = databaseAPI.getWebpageSpiderById(
    id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No Webpage Spider Exist":
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
    
  res = databaseAPI.createWebpageSpider(
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
  
@app.post("/webpageSpider/{spider_id}/run", status_code=201, tags=["Webpage Spider"])
def run_webpage_spider(spider_id: int):
  webpage_spider_information = databaseAPI.getWebpageSpiderById(spider_id)
  if webpage_spider_information[0] != True:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
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
    
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/schedule.json"
  body = {
    "project": "default",
    "spider": "WebpageSpider",
    "link": webpage_spider_information[1]["Url"],
    "spider_id": spider_id,
    "keywords": keywords_as_string,
    "crawlRule": crawl_rule_as_string
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
  webpage_spider_information = databaseAPI.getWebpageSpiderById(spider_id)
  
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
  res = databaseAPI.getWebsiteSpider(
    page=page,
    spiderPerPage=spiderPerPage
  )
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No data to fetch":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.get("/websiteSpider/{spider_id}", status_code=200, tags=["Website Spider"])
def get_website_spider_by_id(spider_id: int):
  res = databaseAPI.getWebsiteSpiderById(
    id=spider_id
  )
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  if res[1] == "No Website Spider Exist":
    return JSONResponse(status_code=404, content=res[1])
  return JSONResponse(status_code=500, content=res[1])

@app.post("/websiteSpider/{spider_id}/run", status_code=201, tags=["Website Spider"])
def run_website_spider(spider_id: int):
  webpage_spider_information = databaseAPI.getWebsiteSpiderById(spider_id)
  if webpage_spider_information[0] != True:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  keywords = webpage_spider_information[1]["Keyword"]
  keywords_as_string: str = ''
  for word in keywords:
    keywords_as_string = keywords_as_string + word["Value"] + ','
  keywords_as_string = keywords_as_string[:-1]
  print(keywords_as_string)
  
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/schedule.json"
  body = {
    "project": "default",
    "spider": "WebsiteSpider",
    "link": webpage_spider_information[1]["Url"],
    "spider_id": spider_id,
    "delay": webpage_spider_information[1]["Delay"],
    "graphDeep": webpage_spider_information[1]["GraphDeep"],
    "maxThread": webpage_spider_information[1]["MaxThread"],
    "keywords": keywords_as_string
  }  
  res = requests.post(
    api_endpoint,
    body
  )
  
  if res.status_code == 200:
    res_data = res.json()
    body["jobid"] = res_data["jobid"]
    print(body["jobid"])
    
    setJobIDResult = databaseAPI.setWebsiteSpiderJobID(spider_id, body["jobid"])
    if setJobIDResult[0] == True:
      return JSONResponse(status_code=200, content=setJobIDResult[1])
    else:
      return JSONResponse(status_code=200, content="The Spider is running without updating jobid")
  else:
    return JSONResponse(status_code=res.status_code, content="Can not crawl")
  
@app.post("/websiteSpider/{spider_id}/stop", status_code=201, tags=["Website Spider"])
def stop_website_spider(spider_id: int):
  webpage_spider_information = databaseAPI.getWebsiteSpiderById(spider_id)
  
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

  
@app.post("/websiteSpider", status_code=201, tags=["Website Spider"])
def create_website_spider(spider_status: WebsiteSpider):
  if databaseAPI.isOverStorage():
    return JSONResponse(status_code=507, content={"message": "Server is out of free storage space."})  
  
  # Validate Input
  if spider_status.url == "":
    return JSONResponse(status_code=403, content={"detail": "Url can not be empty"})   
  
  '''
  try:
    pattern = r'^(http|https):\/\/([\w.-]+)(\.[\w.-]+)+([\/\w\.-]*)*\/?$'
    if bool(re.match(pattern, spider_status.url)) == False:
      return JSONResponse(status_code=403, content={"detail": "Url field only contain url"})  
  except:
    return JSONResponse(status_code=403, content={"detail": "Url field only contain url"})  
  '''
    
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
  res = databaseAPI.createWebsiteSpider(
    url=spider_status.url,
    delay=spider_status.delay,
    graphDeep=spider_status.graphdeep,
    maxThread=spider_status.maxThread,
    crawlRules=afterReformatCrawlRules,
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
        "crawlRules": crawlRule,
        "relatedRule": relatedCrawlrule,
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
  
@app.get("/websiteSpider/{spider_id}/article", status_code=200, tags=["Website Spider"])
def get_total_article_crawled_from_website_spider(spider_id: int, page: int = 0, articlePerPage: int = 10):
  res = databaseAPI.getSpiderTotalAriticle(spider_id, page=page, articlePerPage=articlePerPage)
    
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=404, content=res[1])
  
# Spider 
@app.delete("/spider", status_code=200, tags=["Spider"])
def delete_spider(spider_id: int):
  res = databaseAPI.deleteSpider(spider_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
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
  res = databaseAPI.getUser(
    page=page,
    userPerPage=userPerPage
  )
  
  if res[0] == True:
    return JSONResponse(status_code=201, content={"detail": res[1]})
  else:
    if res[1] == "Error when fetching data":
      return JSONResponse(status_code=500, content={"message": res[1]})
    if res[1] == "Out of range":
      return JSONResponse(status_code=404, content={"message": "Not Found"})   
    return JSONResponse(status_code=404, content={"message": res[1]})
  
# Demo Spider
@app.get("/demoSpider", status_code=201, tags=["Demo Webpage Spider"])
def crawl_single_page(url: str):
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/schedule.json"
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