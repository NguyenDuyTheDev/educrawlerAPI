from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from databaseAPI import Singleton

#uvicorn educrawlerAPI:app --reload


databaseAPI = Singleton()
app = FastAPI()
from pydantic import BaseModel

class Message(BaseModel):
  message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
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