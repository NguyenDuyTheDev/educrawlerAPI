def getArticleByID(id):
    sql_command = '''
    select * from "FinalProject"."Article" where id = %d
    ''' % (id)
    
    print(sql_command)
    return
  
getArticleByID(1)