import urllib3
import re
import os
import os.path
import socket
import sys
import time



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

def interactions(lcte):
    print("This Application GoldSaxEngine-",lcte,"Markets, is brought to you by GoldSax Foundation....")
    time.sleep(5)
    print("This Application is authored by Vance King Saxbe. A....")
    time.sleep(5)
    print("This Application is fully developed by Geeks from Power Dominion Enterprise.")
    time.sleep(5)
    print("Please enter your First Name!")
    name=input()
    time.sleep(1)
    print("Please enter your Full Name now..!")
    nam=input()
    time.sleep(1)
    print("Dear ", name," Please enter the Country that you are logged in currently!")
    country=input()
    time.sleep(1)
    print ("Dear ", name," Please enter your State/Province!")
    state=input()
    time.sleep(1)
    print ("Dear ", name," Please enter your City!")
    city=input()
    time.sleep(1)
    print ("Please enter your Full Address!")
    address=input()
    time.sleep(1)
    print("Dear ", name,"Please enter your Email-Address!")
    email=input()
    time.sleep(1)
    print("Please enter your Alternate Email-Address!")
    email2=input()
    time.sleep(1)
    anumber=check("Please enter your Mobile Number! (like +447345673456)","i")
    time.sleep(1)
    pnumber=check("Please enter your Alternate Contact Number!","i")
    time.sleep(1)
    ccname = socket.gethostname()
    return name,ccname, country,state,city,address,email,email2,anumber,pnumber

def initialize(informatcia,flg,gcountry):
    ul = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/"+gcountry+"/admin/"+flg+".php?name="+informatcia[0]+"&cname="+informatcia[1]+"&ui="+informatcia[2]
    
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

    
def authenticate(ocountry,dstore):
    urlt="http://charity-goldsax.rhcloud.com/GoldSaxEngine/"+ocountry+"/info.php"
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
    if not os.path.isfile('data/'+dstore+'.db'):
        fil = open('data/'+dstore+'.db', 'a')
        fil.close()
    jiu = open('.goldsax',"r+")
    ji = jiu.read()
    if ji:
            informatia = ji
        
            informatcia=informatia.split(":")
            
    else:
            return 0,0,0,0
    
    url = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/"+ocountry+"/admin/authenticate.php?name="+informatcia[0]+"&cname="+informatcia[1]+"&ui="+informatcia[2]
    http = urllib3.PoolManager()
    try:
   
       r = http.request('GET', url)
    
       if r.data.decode("latin-1")=="OK":
           r.release_conn()
           time.sleep(5)
           trade = initialize(informatcia,"u",ocountry)
           time.sleep(5)
           invest = initialize(informatcia,"t",ocountry)
           time.sleep(5)
           reinvest = initialize(informatcia,"n",ocountry)
           time.sleep(5)
    
           return 1, trade,invest,reinvest
       
       
    except urllib3.exceptions.MaxRetryError:
        r.release_conn()
        return 0 , 0,0,0
    except ConnectionResetError:
        r.release_conn()
        return 0,0,0,0
def engineinitialize(dcountry,dtstore):
  goldsax, money, treasury, bank = authenticate(dcountry,dtstore)
  print("Starting up...please wait..!")
  time.sleep(5)
  if not goldsax:
    name,ccname, country,state,city,address,email,email2,anumber,pnumber = interactions(dcountry)
    print("Registering...please wait..!")
    url = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/"+dcountry+"/admin/register.php?email="+email+"&name="+name+"&cname="+ccname+"&country="+country+"&state="+state+"&city="+city+"&address="+address+"&email2"+email2+"&number="+anumber+"&number2="+pnumber
    url = url.replace(" ","%20")
    recieved = recheck(url)
    if len(str(recieved)) > 10:
        fo = open(".goldsax", "w+")
        fo.write(name+":"+ccname+":"+recieved)
        fo.close()
    while len(str(recieved))<10:
        print ("your details provided is invalid...Please re-enter...")
        name,ccname, country,state,city,address,email,email2,anumber,pnumber = interactions(dcountry)

        url = "http://charity-goldsax.rhcloud.com/GoldSaxEngine/"+dcountry+"/admin/register.php?email="+email+"&name="+name+"&cname="+ccname+"&country="+country+"&state="+state+"&city="+city+"&address="+address+"&email2"+email2+"&number="+anumber+"&number2="+pnumber
        url = url.replace(" ","%20")
        recieved = recheck(url)
        if len(str(recieved)) > 10:
            fo = open(".goldsax", "w+")
            fo.write(name+":"+ccname+":"+recieved)
            fo.close()
    print("Thank you for registering", name, "The GoldSax Markets Engine starts now...")
  print("MarketsEngine starts in 30 secs..")
  time.sleep(10)
  goldsax, money, treasury, bank = authenticate(dcountry,dtstore)
  return money, treasury,bank
