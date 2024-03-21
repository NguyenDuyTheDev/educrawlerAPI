

import re
 
# Define a function for
# for validating an Email
def check(s):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat,s):
        print("Valid Email")
    else:
        print("Invalid Email")
 
def checkPhone(s):
    pat = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'

    if re.match(pat,s):
        print("Valid Phone")
    else:
        print("Invalid Phone")
 
def checkUrl(s):
    pat = r"(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?\/[a-zA-Z0-9]{2,}|((https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?)|(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})? "

    if re.match(pat,s):
        print("Valid Url")
    else:
        print("Invalid Url")
 
# Driver Code
if __name__ == '__main__':
 
    # Enter the email
    email = "ankitrai326@gmail.com"
 
    # calling run function
    check(email)
 
    email = "my.ownsite@our-earth.org"
    check(email)
 
    email = "duy.nguyenit19112@hcmut.edu.vn"
    check(email)
 
    email = "ankitrai326.com"
    check(email)
    
    phone = "0937079327"
    checkPhone(phone)
    
    phone = "+84937079327"
    checkPhone(phone)
    
    phone = "+12223334444"
    checkPhone(phone)
    
    url = "giaoduc.vn"
    checkUrl(url)