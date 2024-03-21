from ControllerDB.UserDB import UserDB
import math 

userDB = UserDB()

class UserController():
  def getUser(
    self,
    page = 0, 
    user_per_page = 10
  ):
    total = userDB.countUser()
    if total[0] == False:
      return total
    
    detail = userDB.getUser()
    if detail[0] == False:
      return detail
    
    return (True, {
      "total": total[1],
      "page": page,
      "userPerPage": user_per_page,
      "totalPage": math.ceil(total[1] / user_per_page),
      "detail": detail[1]["detail"]
    })
  
  def getUserById(
    self,
    user_id
  ):
    return userDB.getUserById(
      user_id=user_id
    )
  
  def updateUserStatus(
    self,
    user_id,
    account_status
  ):
    return userDB.updateUserStatus(
      user_id=user_id,
      status=account_status
    )
    
  def updateUserLanguage(
    self, 
    user_id,
    user_language = "English"
  ):
    return userDB.updateUserLanguage(
      user_id=user_id,
      user_language=user_language
    )
    
  def updateUserSystemMode(
    self, 
    user_id,
    system_mode = "Light"
  ):
    return userDB.updateUserSystemMode(
      user_id=user_id,
      system_mode=system_mode
    )
    
  def updateUser(
    self, 
    user_id,
    full_name = "",
    phone = "",
    mail = ""
  ):
    return userDB.updateUser(
      user_id=user_id,
      fullName=full_name,
      phone=phone,
      mail=mail
    )
    
  def deleteUser(
    self, 
    user_id
  ):
    return userDB.deleteUser(
      user_id=user_id
    )