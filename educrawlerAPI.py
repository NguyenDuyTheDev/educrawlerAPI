from typing import Union, List
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from databaseAPI import Singleton

import requests
from urllib.parse import urlparse
import re

#uvicorn educrawlerAPI:app --reload


databaseAPI = Singleton()
app = FastAPI()
from pydantic import BaseModel

class Message(BaseModel):
  message: str

@app.get("/")
def read_root():
    return {
      "Name": "EducrawlerAPI",
      "Description": "API for managing Education Article and Spider",
      "API Document Url (Swagger UI)": "https://educrawlerapi.onrender.com/docs",
      "API Document Url (Redoc)": "https://educrawlerapi.onrender.com/redoc"
    }

@app.get("/items/{item_id}")
def test_api(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
  
@app.get("/keywords", status_code=200, tags=["keywords"])
def get_keywords():
  total_keywords = databaseAPI.getTotalKeyword()[0]
  keywords_list = databaseAPI.getKeywordByPage(page=0, pageKeywordsNumber=total_keywords)
  
  return {
    "total_keywords": total_keywords,
    "keywords_list": keywords_list
  }
  
@app.post("/keywords", status_code=201, tags=["keywords"])
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
  
@app.put("/keywords/{keyword_id}", status_code=200, tags=["keywords"])
def update_keyword(keyword_id: int, name: str):
  res = databaseAPI.editKeywordByID(keyword_id, name)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Keyword doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Keyword is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating!":
      return JSONResponse(status_code=500, content={"message": res[1]})  

@app.delete("/keywords/{keyword_id}", status_code=200, tags=["keywords"])
def delete_keyword(keyword_id: int):
  res = databaseAPI.deleteKeywordByID(keyword_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Keyword doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Error when deleting!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    
@app.get("/filetypes", status_code=200, tags=["Supported File Type"])
def get_supported_file_types():
  total_supported_file_types = databaseAPI.getTotalSupportedFileType()[0]
  supported_file_types_list = databaseAPI.getSupportedFileTypeByPage(page=0, pageFileTypesNumber=total_supported_file_types)
    
  return JSONResponse(status_code=200, content={
    "total_supported_file_types": total_supported_file_types,
    "supported_file_types_list": supported_file_types_list
  })  

  
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
    if res[1] == "Error when creating!":
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
    if res[1] == "Error when updating!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    return JSONResponse(status_code=500, content={"message": "Error when updating!"}) 

@app.delete("/filetypes/{keyword_id}", status_code=200, tags=["Supported File Type"])
def delete_file_type(file_type_id: int):
  res = databaseAPI.deleteSupportedFileTypeByID(file_type_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "File Type doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Error when deleting!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    return JSONResponse(status_code=500, content={"message": "Error when deleting!"}) 

@app.get("/articles", status_code=200, tags=["Article"])
def get_articles_numbers():
  total_article = databaseAPI.getTotalArticle()[0]
    
  return JSONResponse(status_code=200, content={
    "total_article": total_article,
  })  
  
@app.get("/articles/page/{page_id}", status_code=200, tags=["Article"])
def get_articles_by_page(page_id: int):
  total_article = databaseAPI.getArticlesByPage(page=page_id, pageArticlesNumber=10)
    
  return JSONResponse(status_code=200, content=total_article)  
  
@app.get("/articles/article/{article_id}", status_code=200, tags=["Article"])
def get_articles_by_id(article_id: int):
  res = databaseAPI.getArticleByID(article_id)
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=404, content=res[1])

class Article(BaseModel):
    domain: str
    url: str
    filename: str
    content: str
    title: str
    note: str
    spiderid: int

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
  else:
    if res[1] == "Article is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating article!":
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
  else:
    if res[1] == "Article doesn't exist!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Error when updating article!":
      return JSONResponse(status_code=500, content={"message": res[1]}) 

@app.delete("/article/{article_id}", status_code=200, tags=["Article"])
def delete_article(article_id: int):
  res = databaseAPI.deleteArticleById(article_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"detail": res[1]})
  else:
    if res[1] == "Article isn't existed!":
      return JSONResponse(status_code=404, content={"message": res[1]})
    if res[1] == "Error when deleting article!":
      return JSONResponse(status_code=500, content={"message": res[1]})  
    return JSONResponse(status_code=500, content={"message": "Error when deleting article!"}) 
  
class CrawlRule(BaseModel):
    id: int
    tag: str
    HTMLClassName: str
    HTMLIDName: str
    ChildCrawlRuleID: int
  
class WebpageSpider(BaseModel):
    url: str
    delay: float
    graphdeep: int
    keyword: List[int] 
    filetype: List[int]
    crawlRules: List[CrawlRule]

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
    if rule.HTMLClassName == "" and rule.HTMLIDName == "":
      return JSONResponse(status_code=422, content={"detail": "HTMLClassName or HTMLIDName must have value"})
    
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
    delay=spider_status.delay,
    graphDeep=spider_status.graphdeep,
    maxThread=1,
    crawlRules=afterReformatCrawlRules,
    fileTypes=spider_status.filetype,
    keywords=spider_status.keyword
  )

  if res[0] == True:
    return JSONResponse(
      status_code=201, 
      content={
        "url": spider_status.url,
        "delay": spider_status.delay,
        "graphdeep": spider_status.graphdeep,
        "keyword": spider_status.keyword,
        "filetype": spider_status.filetype,
        "crawlRules": crawlRule,
        "relatedRule": relatedCrawlrule,
        "realRule": afterReformatCrawlRules
      }
    )
  else:
    if res[1] == "Spider is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating spider!":
      return JSONResponse(status_code=500, content={"message": res[1]}) 
    return JSONResponse(status_code=500, content={"message": res[1]}) 
  
@app.get("/webpageSpider", status_code=201, tags=["Webpage Spider"])
def get_webpage_spider():
  res = databaseAPI.getWebpageSpider()
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=404, content=res[1])
  
@app.get("/demoSpider", status_code=201, tags=["Demo Spider"])
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
  
@app.post("/webpageSpider/{spider_id}/run", status_code=201, tags=["Webpage Spider"])
def run_webpage_spider(spider_id: int):
  webpage_spider_information = databaseAPI.getWebpageSpiderById(spider_id)
  url = ""
  if webpage_spider_information[0] == True:
    print(webpage_spider_information[1]["Url"])
    url = webpage_spider_information[1]["Url"]
  else:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/schedule.json"
  body = {
    "project": "default",
    "spider": "WebpageSpider",
    "link": url,
    "spider_id": spider_id
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
  
@app.post("/webpageSpider/{spider_id}/stop", status_code=201, tags=["Webpage Spider"])
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
    return JSONResponse(status_code=200, content="Close spider successfully!")
  else:
    return JSONResponse(status_code=res.status_code, content="Can not stop")
  
@app.get("/webpageSpider/{spider_id}/lastRunTime", status_code=200, tags=["Webpage Spider"])
def get_last_run_time(spider_id: int):
  res = databaseAPI.calculateLastRunTime(spider_id)
  
  if res[0] == True:
    return JSONResponse(status_code=200, content={"TotalRunTime": res[1]}) 
  else:
    return JSONResponse(status_code=res.status_code, content="Can not calculate")

# Website Spider

@app.get("/websiteSpider", status_code=200, tags=["Website Spider"])
def get_website_spider():
  res = databaseAPI.getWebsiteSpider()
  
  if res[0]:
    return JSONResponse(status_code=200, content=res[1])
  else:
    return JSONResponse(status_code=404, content=res[1])

@app.post("/websiteSpider/{spider_id}/run", status_code=201, tags=["Website Spider"])
def run_website_spider(spider_id: int):
  webpage_spider_information = databaseAPI.getWebsiteSpiderById(spider_id)
  url = ""
  if webpage_spider_information[0] == True:
    print(webpage_spider_information[1]["Url"])
    url = webpage_spider_information[1]["Url"]
  else:
    return JSONResponse(status_code=404, content=webpage_spider_information[1])
  
  api_endpoint = "https://educrawlercrawlerservice.onrender.com/schedule.json"
  body = {
    "project": "default",
    "spider": "WebsiteSpider",
    "link": url,
    "spider_id": spider_id,
    "delay": webpage_spider_information[1]["Delay"],
    "graphDeep": webpage_spider_information[1]["GraphDeep"],
    "maxThread": webpage_spider_information[1]["MaxThread"],
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
    return JSONResponse(status_code=200, content="Close spider successfully!")
  else:
    return JSONResponse(status_code=res.status_code, content="Can not stop")
  
class WebsiteSpider(BaseModel):
    url: str
    delay: float
    graphdeep: int
    maxThread: int
    keyword: List[int] 
    filetype: List[int]
    crawlRules: List[CrawlRule]
  
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
    
  # Format Crawl Rule
  crawlRule = []
  
  for rule in spider_status.crawlRules:
    if rule.tag == "":
      return JSONResponse(status_code=422, content={"detail": "Tag can not be empty"})      
    if rule.HTMLClassName == "" and rule.HTMLIDName == "":
      return JSONResponse(status_code=422, content={"detail": "HTMLClassName or HTMLIDName must have value"})
    
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
    
  # Create in db
  res = databaseAPI.createWebsiteSpider(
    url=spider_status.url,
    delay=spider_status.delay,
    graphDeep=spider_status.graphdeep,
    maxThread=spider_status.maxThread,
    crawlRules=afterReformatCrawlRules,
    fileTypes=spider_status.filetype,
    keywords=spider_status.keyword
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
        "realRule": afterReformatCrawlRules
      }
    )
  else:
    if res[1] == "Spider is already existed!":
      return JSONResponse(status_code=422, content={"message": res[1]})
    if res[1] == "Error when creating spider!":
      return JSONResponse(status_code=500, content={"message": res[1]}) 
    return JSONResponse(status_code=500, content={"message": res[1]}) 
  
@app.get("/websiteSpider/{spider_id}/totalArticle", status_code=200, tags=["Website Spider"])
def get_total_article_get_from_website_spider(spider_id: int):
  res = databaseAPI.getSpiderTotalAriticle(spider_id)
    
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
  
class UserRole(str, Enum):
    user = "User"
    admin = "Admin"
    manager = "Manager"
  
class User(BaseModel):
    Username: str
    Password: str 
    Role: str
  
# User
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