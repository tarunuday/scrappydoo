import urllib.request
import re
from bs4 import BeautifulSoup
import pymysql.cursors
import datetime

def printer(string):
    string=datetime.datetime.now()+": "+string
    with open("error.log", "a") as myfile:
        myfile.write(string,"\n")
def r(s): #formatting and removing white spaces and line breaks
    return re.sub(('^\s+|\s+$'),'',s)
def l(s): #getting only digits
    return int(re.sub(('\D'),'',s))
def ym(s): #getting years and months out of string - used in Experience Section
    a= re.sub((' Years, '),'',s)
    a= re.sub((' Months'),'',a)
    a=int(a)
    if(a<100):
        a=int(a/10)*100+a%10
    return a
def ty(s): #getting term and year details 
    s=r(s)
    b=re.sub(('\D'),'',s)
    a=re.sub(('\d'),'',s)
    s=re.sub((' - '),'',a)
    if(s=="Fall"):
        return int("1"+b)
    if(s=="Spring"):
        return ("2"+b)
    if(s=="Summer"):
        return ("3"+b)
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
def uni_check():
    if(r(htmlcursor[1].td.string))=="University details not updated":
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
    sql = "SELECT * FROM `uni_list` WHERE `name`= %s"
    cursor.execute(sql, uni_name)
    return cursor.fetchone()
    
def db_profile(extractid):
    with connection.cursor() as cursor:
        sql = "SELECT pro_id FROM `profiles` WHERE `extractid`= %s"
        cursor.execute(sql, extractid)
        connection.commit()
    return cursor.fetchone()["pro_id"]

def db_uni_data_enterall(pro_id,uni_id,major,term,year,uni_status,uni_text):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `uni_data` (`pro_id`,`uni_id`, `major`, `term`,`year`,`status`,`text`) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (pro_id,uni_id,major,term,year,uni_status,uni_text))
        print(uni_name, "entered")
    connection.commit()


urls = 'file:///C:/Users/tarunuday/Documents/scrapdata/mech.html'
print("Connecting to ",urls)

htmlfile = urllib.request.urlopen(urls)
soup = BeautifulSoup(htmlfile,'html.parser')
test=soup.find_all("table", "tdborder")[2].find_all("tr")
print("Connection established")
print("Connecting to database...")
i=8
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
    print("Access denied for ",user,"@",host)
flibbets=1
while(flibbets):#len(test)):
    ###############Start page no i
    link='http://edulix.com/unisearch/'
    link+=test[i].a["href"]
    profile = urllib.request.urlopen(link)
    data = BeautifulSoup(profile,'html.parser')
    print("Connected to profile link:",link,i)

    ###############EXTRACT ID
    insert_extractid=1000000+int(l(test[i].a["href"]))

    ###############Checking for Universities
    if(uni_check):
        print('No Universities to show')
        i+=1
        continue;
    else:
        flibbets=0

    ###############Section 0 - NAME
    insert_name=r(data.find_all("table", "tdborder")[0].find_all("tr")[2].find_all("td")[1].string)
    if(insert_name==""):
        insert_name=r(data.find_all("a", "no_uline")[0].string)

    ###############Section 1 - App Details
    htmlcursor=data.find_all("td", "orange_title tdhor")[1].parent
    while(True):
        htmlcursor=htmlcursor.next_sibling.next_sibling
        if(htmlcursor.td.string=="Standardized Test Scores"):
            break
        else:
            if(htmlcursor.td.string=="University (will be) Attending"):
                attend=htmlcursor.find_all("td")[1].string
            if(htmlcursor.td.string=="Program"):
                program=htmlcursor.find_all("td")[1].string
            if(htmlcursor.td.string=="Major"):
                major=htmlcursor.find_all("td")[1].string
            if(htmlcursor.td.string=="Specialization"):
                special=htmlcursor.find_all("td")[1].string
            if(htmlcursor.td.string=="Term and Year"):
                year=(ty(htmlcursor.find_all("td")[1].string))%10000
                term=int(ty(htmlcursor.find_all("td")[1].string)/10000)

    ###############Section 2 - Standardized Test Scores
    htmlcursor=data.find_all("td", "orange_title tdhor")[2].parent
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insidecursor=htmlcursor.td.table.find_all("tr")[0]
    try: 
        insert_gre=int(r(insidecursor.find_all("td")[2].string)+r(insidecursor.find_all("td")[4].string)+str(int(float(r(insidecursor.find_all("td")[6].string))*10)))
    except ValueError:
        insert_gre=0
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
    insert_major=""
    insert_gpa=0
    if(htmlcursor.find_all("td")[0].string=="University/College"):
        insert_college=r(htmlcursor.find_all("td")[1].string)
        htmlcursor=htmlcursor.next_sibling.next_sibling
        if(htmlcursor.find_all("td")[0].string=="Department"):
            insert_major=r(htmlcursor.find_all("td")[1].string)
            htmlcursor=htmlcursor.next_sibling.next_sibling
            if(htmlcursor.find_all("td")[0].string=="Grade"):
                insert_gpa=ins_grade(htmlcursor)
    elif(htmlcursor.find_all("td")[0].string=="Department"):
        insert_major=r(htmlcursor.find_all("td")[1].string)
        htmlcursor=htmlcursor.next_sibling.next_sibling
        if(htmlcursor.find_all("td")[0].string=="Grade"):
            insert_gpa=ins_grade(htmlcursor)
    elif(htmlcursor.find_all("td")[0].string=="Grade"):
        insert_gpa=ins_grade(htmlcursor)
    
    ###############Section 4 - experience
    ######## ym returns values in ymm format   
    htmlcursor=data.find_all("td", "orange_title tdhor")[4].parent
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insert_journal=l(htmlcursor.find_all("td")[1].string)
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insert_conference=l(htmlcursor.find_all("td")[1].string)
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insert_industry=ym(r(htmlcursor.find_all("td")[1].string))
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insert_research=ym(r(htmlcursor.find_all("td")[1].string))
    htmlcursor=htmlcursor.next_sibling.next_sibling
    insert_internship=ym(r(htmlcursor.find_all("td")[1].string))

    ###############Section 8 - Miscellaneous   
    ########if there is no data entered by a user in their misc section, that section will not be displayed in the profile summary page
    ########that means find_all("td", "orange_title tdhor")[8] wouldn't exist and cause an index error
    try:
        htmlcursor=data.find_all("td", "orange_title tdhor")[8].parent
        htmlcursor=htmlcursor.next_sibling.next_sibling
        insert_misc=htmlcursor.td.contents
    except IndexError:
        insert_misc=""

    ###############ENTERING PROFILE DATA TO DATABASE
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `profiles` (`pro_id`, `extractid`, `name`, `current`, `college`, `major`, `gpa`, `gre`, `toefl`, `ielts`, `journal`, `conference`, `industry`, `research`, `internship`, `misc`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (NULL, insert_extractid, insert_name, int("1"), insert_college, insert_major, insert_gpa, insert_gre, insert_toefl, insert_ielts, insert_journal, insert_conference, insert_industry, insert_research, insert_internship, insert_misc))
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    pro_id=db_profile(insert_extractid) #### We just got the last piece of the puzzle. the auto-incremented id of the latest entry

    ###############University Data
    htmlcursor=data.find_all("table", "tdborder")[1].find_all("tr")
    j=1
    u=len(data.find_all("table", "tdborder")[1].find_all("tr"))
    flag=1          ######Flag to chk if we have got the text details about the uni, if any
    while(j<u):     ######Loop to get all uni info
        if(flag):
            uni_name=htmlcursor[j].a.string
            uni_status=uni(htmlcursor[j].span.string)
            uni_text=""
            try:
                if htmlcursor[j+1].a is None:
                    flag=0
            except IndexError:
                pass
        else:
            uni_text=htmlcursor[j].td.string
            flag=1
        j+=1
        if(flag):    
            print("uni:",uni_name,",",uni_status,",",uni_text)    
            with connection.cursor() as cursor:
                # Create a new record
                result=db_uni_list_searchbyname(uni_name)
                print(result)
                if result is None: #To test is sql returned empty rows
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `uni_list` (`name`) VALUES (%s)"
                        cursor.execute(sql, uni_name)
                        print(uni_name, "entered")
                    connection.commit()
                    result=db_uni_list_searchbyname(uni_name)
                    db_uni_data_enterall(pro_id,result["id"],"1",term,year,uni_status,uni_text)
                else: #SQL hasn't returned empty rows so do this:
                    db_uni_data_enterall(pro_id,result["id"],"1",term,year,uni_status,uni_text)
                    

    try:    
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `profiles`"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
    finally:
            print("end well")
    
    #increment
    i+=1

connection.close()