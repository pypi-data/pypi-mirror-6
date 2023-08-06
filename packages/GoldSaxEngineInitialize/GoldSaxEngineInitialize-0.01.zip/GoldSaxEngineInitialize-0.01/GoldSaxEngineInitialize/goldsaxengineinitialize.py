import urllib3
import re
import os
import os.path
import socket
import sys



def check(message,value):
    if value=="i":
        print (message)
        got = input()
        while not re.match('^[+]{1}[0-9]+$', got):
          print (message)
          got = input()
    if value=="e":
        print (message)
        got = input()
        while not re.search('[0-9][A-Z][a-z]@.', got):
          print (message)
          got = input()
    return got
def emailcheck(url):
    http = urllib3.PoolManager()
    try:
   
       r = http.request('GET', url)
       r.release_conn()
    except urllib3.exceptions.MaxRetryError:
       return 0
    except ConnectionResetError:
       return 0
    return 0
def recheck(url):
    http = urllib3.PoolManager()
    try:
   
       r = http.request('GET', url)
       r.release_conn()
    except urllib3.exceptions.MaxRetryError:
       return 0
    except ConnectionResetError:
       return 0
    return r.data.decode("latin-1")

def interactions():
    print("Please enter your First Name!")
    name=input()
    print("Please enter your Full Name now..!")
    nam=input()
    print("Dear ", name," Please enter the Country that you are logged in currently!")
    country=input()
    print ("Dear ", name," Please enter your State/Province!")
    state=input()
    print ("Dear ", name," Please enter your City!")
    city=input()
    print ("Please enter your Full Address!")
    address=input()
    print("Dear ", name,"Please enter your Email-Address!")
    email=input()
    print("Please enter your Alternate Email-Address!")
    email2=input()
    anumber=check("Please enter your Mobile Number! (like +919345673456)","i")
    pnumber=check("Please enter your Alternate Contact Number!","i")
    ccname = socket.gethostname()
    return name,ccname, country,state,city,address,email,email2,anumber,pnumber

def initialize(informatcia,flg):
    ul = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/India/admin/"+flg+".php?name="+informatcia[0]+"&cname="+informatcia[1]+"&ui="+informatcia[2]
    
    http = urllib3.PoolManager()
    try:
       r = http.request('GET', ul)
       return r.data.decode("latin-1")
    except urllib3.exceptions.MaxRetryError:
        r.release_conn()
        return 0
    except ConnectionResetError:
        r.release_conn()
        return 0

    
def authenticate():
    urlt="http://charity-goldsax.rhcloud.com/GoldSaxEngine/info.php"
    http = urllib3.PoolManager()
    try:
       r = http.request('GET', urlt)
       print(r.data.decode("latin-1"))
    except urllib3.exceptions.MaxRetryError:
        r.release_conn()
    except ConnectionResetError:
        r.release_conn()
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.isfile('.goldsax'):
        fil = open('.goldsax', 'a')
        fil.close()
    if not os.path.isfile('data/INDIA.db'):
        fil = open('data/INDIA.db', 'a')
        fil.close()
    jiu = open('.goldsax',"r+")
    ji = jiu.read()
    if ji:
            informatia = ji
        
            informatcia=informatia.split(":")
            
    else:
            return 0,0,0,0
    
    url = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/India/admin/authenticate.php?name="+informatcia[0]+"&cname="+informatcia[1]+"&ui="+informatcia[2]
    http = urllib3.PoolManager()
    try:
   
       r = http.request('GET', url)
    
       if r.data.decode("latin-1")=="OK":
           r.release_conn()
           trade = initialize(informatcia,"u")
           invest = initialize(informatcia,"t")
           reinvest = initialize(informatcia,"n")
    
           return 1, trade,invest,reinvest
       
       
    except urllib3.exceptions.MaxRetryError:
        r.release_conn()
        return 0 , 0,0,0
    except ConnectionResetError:
        r.release_conn()
        return 0,0,0,0
def engineinitialize():
  goldsax, money, treasury, bank = authenticate()
  if not goldsax:
    name,ccname, country,state,city,address,email,email2,anumber,pnumber = interactions()

    url = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/India/admin/register.php?email="+email+"&name="+name+"&cname="+ccname+"&country="+country+"&state="+state+"&city="+city+"&address="+address+"&email2"+email2+"&number="+anumber+"&number2="+pnumber

    recieved = recheck(url)
    if len(str(recieved)) > 10:
        fo = open(".goldsax", "w+")
        fo.write(name+":"+ccname+":"+recieved)
        fo.close()
    while len(str(recieved))<10:
        print ("your details provided is invalid...Please re-enter...")
        name,ccname, country,state,city,address,email,email2,anumber,pnumber = interactions()

        url = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/India/admin/register.php?email="+email+"&name="+name+"&cname="+ccname+"&country="+country+"&state="+state+"&city="+city+"&address="+address+"&email2"+email2+"&number="+anumber+"&number2="+pnumber
        url = url.replace(" ","%20")
        recieved = recheck(url)
        if len(str(recieved)) > 10:
            fo = open(".goldsax", "w+")
            fo.write(name+":"+ccname+":"+recieved)
            fo.close()
    print("Thank you for registering", name, "The Markets Engine starts now...")
  print("market starts")
  return money, treasury,bank
