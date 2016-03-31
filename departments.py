import urllib.request
import re
from bs4 import BeautifulSoup
import pymysql.cursors
import datetime

def printer(string):
    string=datetime.datetime.now()+": "+string
    with open("error.log", "a") as myfile:
        myfile.write(string,"\n")
def r(s):
    """
    formatting and removing white spaces and line breaks
    """
    return re.sub(('^\s+|\s+$'),'',s)
def l(s): 
    """ 
    getting only digits
    """
    return int(re.sub(('\D'),'',s))
def ym(s): 
    """
    getting years and months out of string - used in Experience Section
    """
    a= re.sub((' Years, '),'',s)
    a= re.sub((' Months'),'',a)
    a=int(a)
    if(a<100):
        a=int(a/10)*100+a%10
    return a
def ty(s): 
    """
    getting term and year details 
    """
    s=r(s)
    b=re.sub(('\D'),'',s)
    a=re.sub(('\d'),'',s)
    s=re.sub((' - '),'',a)
    if(s=="Fall"):
        return int("1"+b)
    elif(s=="Spring"):
        return int("2"+b)
    elif(s=="Summer"):
        return int("3"+b)
    else:
        return int("0"+b)
def p(s):
    """
    getting program details
    """
    if(s=="MS"):
        return int("1")
    elif(s=="PhD"):
        return int("2")
    elif(s=="MS/PhD"):
        return int("2")
    elif(s=="Both MS and PhD"):
        return int("2")
    else:
        return "0"

def ins_grade(cursor):
    """
    getting grade details
    """
    grade=float(r(cursor.find_all("td")[1].string))
    cursor=cursor.next_sibling.next_sibling.next_sibling.next_sibling
    scale=int(r(cursor.find_all("td")[1].string))
    if(scale==10): #10grade not percentage
        grade=(int(grade*100))*10+1
    elif(scale==100): #percentage
        grade=(int(grade*100))*10
    elif(scale==4): #4grade not percentage
        grade=(int(grade*100))*10+4
    elif(scale==5): #5grade not percentage
        grade=(int(grade*100))*10+5
    elif(scale==8): #8grade not percentage
        grade=(int(grade*100))*10+8
    return grade

def uni_check(string):
    if(r(string.find_all("table", "tdborder")[1].find_all("tr")[1].td.string))=="University details not updated":
        return 0    
    else:
        return len(data.find_all("table", "tdborder")[1].find_all("tr"))
def uni(s):
    s=r(s)
    if(s=="Result not available"):
        return "0"
    elif(s=="Admit"):
        return "1"
    elif(s=="Reject"):
        return "2"
    else: 
        print("wtf")
        return "wtf"
        
def db_uni_list_searchbyname(uni_name):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `uni_list` WHERE `name`= %s"
        cursor.execute(sql, uni_name)
        res=cursor.fetchone()
    return res

def db_uni_list_enterall(pro_id,uni_id,program,major,term,year,uni_status,attend_status,uni_text):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `uni_data` (`pro_id`,`uni_id`,`program`, `major`, `term`,`year`,`status`,`attend`,`text`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (pro_id, uni_id, program, major, term, year, uni_status, attend_status, uni_text))
    connection.commit()


url="http://www.stupidsid.com/knowledge-hub/ms-in-us/courses-and-university-reviews"
class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

opener = AppURLopener()
response = opener.open(url)
soup = BeautifulSoup(response,'html.parser')
print("Connected")
print("Connecting to database...")
i=0
# Connect to the database
try:
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='secret',
                                 db='playhard',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    print("Connected to Database. Loop begins")

except pymysql.err.OperationalError:
    print("Access denied")
    i=9999999999

htmlcursor=soup.find_all(id="university-reviews")[0].find_all("li")

for college in htmlcursor:
    ###############Start page no i
    link=college.a["href"]
    name=college.a.string
    print(i+1,".",name,":",)

    response1 = opener.open(link)
    data = BeautifulSoup(response1,'html.parser')
    programs=data.section.ul,find_all("li")
    for program in programs:
        print("---",program.string)
    i+=1
#    profile = urllib.request.urlopen(link)
#    data = BeautifulSoup(profile,'html.parser')
#    print("---------------------------------")
#    print("Connected to profile link:",link,i)
#
#    ###############University Data
#    htmlcursor=data.find_all("table", "tdborder")[1].find_all("tr")
#    j=1
#    u=len(data.find_all("table", "tdborder")[1].find_all("tr"))
#    flag=1          ######Flag to chk if we have got the text details about the uni, if any
#    while(j<u):     ######Loop to get all uni info
#        attend_status=0
#        if(flag):
#            uni_name=htmlcursor[j].a.string
#            if(uni_name==attend):
#                attend_status=1
#            uni_status=uni(htmlcursor[j].span.string)
#            uni_text=""
#            try:
#                if htmlcursor[j+1].a is None:
#                    flag=0
#            except IndexError:
#                pass
#        else:
#            uni_text=htmlcursor[j].td.string
#            flag=1
#        j+=1
#        if(flag):    
#            with connection.cursor() as cursor:
#                # Create a new record
#                result=db_uni_list_searchbyname(uni_name)
#                if result is None: #To test is sql returned empty rows
#                    with connection.cursor() as cursor:
#                        sql = "INSERT INTO `uni_list` (`name`) VALUES (%s)"
#                        cursor.execute(sql, uni_name)
#                    connection.commit()
#                    print("INSERTED ",uni_name, "TO LIST OF UNIVERSITIES")
#                    result=db_uni_list_searchbyname(uni_name)
#                    db_uni_data_enterall(pro_id, result["uni_id"], int(program), major, int(term), (year), int(uni_status), attend_status, uni_text)
#                else: #SQL hasn't returned empty rows so do this:
#                    db_uni_data_enterall(pro_id, result["uni_id"], int(program), major, int(term), (year), int(uni_status), attend_status, uni_text)
#            print("INSERTED: ",uni_name)    
#    i+=1
#    print("end well")
#connection.close()