import urllib.request
import re
from bs4 import BeautifulSoup
import pymysql.cursors

def r(s): #formatting and removing white spaces and line breaks
    return re.sub(('^\s+|\s+$'),'',s)
def l(s): #getting only digits
    return re.sub(('\D'),'',s)
def f1ag_spec(): #check for specialisation
    try:
        if(r(ix.find_all("tr")[6].find_all("td")[0].string)=="Specialization"):
            return 1
        elif(r(ix.find_all("tr")[6].find_all("td")[0].string)=="Term and Year"):
            return 0
    except:
        print ("ERROR IN CHECKING FOR SPECIALIZATION")
        return 0
def flag_undergrad(): #check for specialisation
    try:
        if(r(ix.find_all("tr")[6].find_all("td")[0].string)=="Specialization"):
            return 1
        elif(r(ix.find_all("tr")[6].find_all("td")[0].string)=="Term and Year"):
            return 0
    except:
        print ("ERROR IN CHECKING FOR SPECIALIZATION")
        return 0
def ins_gre(a,b,c):
    if((a<=170)&(b<170)&(a>130)&(b>130)&(c<6.0)):
        return int(ins3*10+ins2*100+ins1*100000+100000000)
    if((a<=800)&(b<800)&(a>200)&(b>200)&(c<6.0)):
        return int(ins3*10+ins2*100+ins1*100000+200000000)
    else: 
        print("Error in inputs - GRE Scores not reported correctly")
        return 0
def ins_major(s):
    if(s=="Mechanical Engineering"):
        return 5


urls = 'file:///C:/Users/tarunuday/Documents/scrapdata/mech.html'
print("Connecting to ",urls)
htmlfile = urllib.request.urlopen(urls)
soup = BeautifulSoup(htmlfile,'html.parser')
test=soup.find_all("table", "tdborder")[2].find_all("tr")
print("Connection Established.")
print("Connecting to database and starting loop.")
i=2
info={}

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='secret',
                             db='playhard',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

while(i<5):#len(test)):

    link='http://edulix.com/unisearch/'
    link+=test[i].a["href"]
    profile = urllib.request.urlopen(link)
    data = BeautifulSoup(profile,'html.parser')
    
    print("Connected to profile page no. ",i-1,"/3")

    #initiating variables
    flag_spec=f1ag_spec() #if the "specialisation field is left blank, we'll have a mismatch on the row number for all data following term, year"
    ix=data.find_all("table", "tdborder")[0] #ix is the christened name of the table that holds all relevant info

    #Fetching headings for better navigation
    heading={}
    k=0
    headings_holder=data.find_all("td", "orange_title tdhor")
    for k in len(headings_holder):
        heading[k]=data.find_all("td", "orange_title tdhor")[0].parent
        k+=1

    #EXTRACT ID
    insert_extractid=1000000+int(l(test[i].a["href"]))

    #NAME
    insert_name=r(ix.find_all("tr")[2].find_all("td")[1].string)
    if(insert_name==""):
        insert_name=r(data.find_all("a", "no_uline")[0].string)
    print(insert_extractid,": ", insert_name)


    info["program"]=r(ix.find_all("tr")[4].find_all("td")[1].string)
    insert_major=ins_major(r(ix.find_all("tr")[5].find_all("td")[1].string))
    info["specialization"]=r(ix.find_all("tr")[6].find_all("td")[1].string)
    info["termyear"]=r(ix.find_all("tr")[6+flag_spec].find_all("td")[1].string)
    print(info)
    ins1=int(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[0].find_all("td")[2].string))
    ins2=int(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[0].find_all("td")[4].string))
    ins3=float(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[0].find_all("td")[6].string))
    insert_mainexam=ins_gre(ins1,ins2,ins3)
    
    insert_college=r(ix.find_all("tr")[10+flag_spec].find_all("td")[1].string)
    #chk for toefl and ielts
    if(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[2].find_all("td")[2].string)!=""):
        insert_engexam=int(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[2].find_all("td")[2].string))
    elif(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[3].find_all("td")[2].string)!=""):
        insert_engexam=int(r(ix.find_all("tr")[8+flag_spec].find_all("td")[0].find_all("table")[0].find_all("tr")[3].find_all("td")[2].string))
    print("----------- toefl:", insert_engexam)
    print("-----------", ins1, "---------------", ins2, "--------------------", ins3, "----------------", insert_mainexam)
    
    #entering data to database
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `profiles` (`extractid`, `name`, `current`, `college`, `major`, `gpa`, `gre`, `engexam`, `industry`, `research`, `misc`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (insert_extractid, insert_name, int("0"), insert_college, insert_major, int("66810"), insert_mainexam, insert_engexam, int("0"), int("0"), " " ))
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    try:    
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `extractid`, `name`, `current`, `college`, `major`, `gpa`, `gre`, `engexam`, `industry`, `research`, `misc` FROM `profiles`"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
    finally:
            print("end well")
    
    #increment
    i+=1

connection.close()