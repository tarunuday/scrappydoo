import urllib.request
import re
from bs4 import BeautifulSoup
import pymysql.cursors

def r(s): #formatting and removing white spaces and line breaks
    return re.sub(('^\s+|\s+$'),'',s)
def l(s): #getting only digits
    return re.sub(('\D'),'',s)
def ins_major(s):
    if(s=="Mechanical Engineering"):
        return 5
def ins_grade(htmlcursor):
    grade=float(r(htmlcursor.find_all("td")[1].string))
    htmlcursor=htmlcursor.next_sibling.next_sibling.next_sibling.next_sibling
    scale=int(r(htmlcursor.find_all("td")[1].string))
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

    ##############initiating variables
    flag_spec=f1ag_spec() #if the "specialisation field is left blank, we'll have a mismatch on the row number for all data following term, year"
    ix=data.find_all("table", "tdborder")[0] #ix is the christened name of the table that holds all relevant info

    ###############EXTRACT ID
    insert_extractid=1000000+int(l(test[i].a["href"]))

    ###############Section 1 - NAME
    insert_name=r(ix.find_all("tr")[2].find_all("td")[1].string)
    if(insert_name==""):
        insert_name=r(data.find_all("a", "no_uline")[0].string)

    ###############Section 2 - Standardized Test Scores
    htmlcursor=data.find_all("td", "orange_title tdhor")[2].parent
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insidecursor=htmlcursor.td.table.find_all("tr")[0]
    insert_gre=int(r(insidecursor.find_all("td")[2].string)+r(insidecursor.find_all("td")[4].string)+str(int(float(r(insidecursor.find_all("td")[6].string))*10)))
    insidecursor=insidecursor.next_sibling.next_sibling.next_sibling.next_sibling
    try:
        insert_toefl=int(r(insidecursor.find_all("td")[2].string))
    except ValueError:
        insert_toefl=0
    insidecursor=insidecursor.next_sibling.next_sibling
    try:
        insert_ielts=int(r(insidecursor.find_all("td")[2].string))
    except ValueError:
        insert_ielts=0

    ###############Section 3 - UG Details
    htmlcursor=data.find_all("td", "orange_title tdhor")[3].parent
    htmlcursor=htmlcursor.next_sibling
    htmlcursor=htmlcursor.next_sibling
    insert_college=""
    if(htmlcursor.find_all("td")[0].string=="University/College"):
        insert_college=r(htmlcursor.find_all("td")[1].string)
        print(insert_college)
        htmlcursor=htmlcursor.next_sibling.next_sibling
        if(htmlcursor.find_all("td")[0].string=="Department"):
            insert_major=r(htmlcursor.find_all("td")[1].string)
            htmlcursor=htmlcursor.next_sibling.next_sibling
            print(insert_major)
            if(htmlcursor.find_all("td")[0].string=="Grade"):
                insert_gpa=ins_grade(htmlcursor)
    elif(htmlcursor.find_all("td")[0].string=="Department"):
        insert_major=r(htmlcursor.find_all("td")[1].string)
        htmlcursor=htmlcursor.next_sibling.next_sibling
        print(insert_major)
        if(htmlcursor.find_all("td")[0].string=="Grade"):
            insert_gpa=ins_grade(htmlcursor)
    elif(htmlcursor.find_all("td")[0].string=="Grade"):
        insert_gpa=ins_grade(htmlcursor)

    #---------------
    
    #entering data to database
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `profiles` (`extractid`, `name`, `current`, `college`, `major`, `gpa`, `gre`, `toefl`, `ielts`, `industry`, `research`, `misc`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (insert_extractid, insert_name, int("0"), insert_college, insert_major, int("66810"), insert_gre, insert_toefl, insert_ielts, int("0"), int("0"), " " ))
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