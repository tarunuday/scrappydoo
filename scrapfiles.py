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
    elif(s=="Spring"):
        return int("2"+b)
    elif(s=="Summer"):
        return int("3"+b)
    else:
        return int("0"+b)
def p(s):
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
    
def db_profile(extractid):
    with connection.cursor() as cursor:
        sql = "SELECT pro_id FROM `profiles` WHERE `extractid`= %s"
        cursor.execute(sql, extractid)
        res=cursor.fetchone()["pro_id"]
    return res

def db_uni_data_enterall(pro_id,uni_id,program,major,term,year,uni_status,attend_status,uni_text):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `uni_data` (`pro_id`,`uni_id`,`program`, `major`, `term`,`year`,`status`,`attend`,`text`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (pro_id, uni_id, program, major, term, year, uni_status, attend_status, uni_text))
    connection.commit()


urls = 'file:///C:/Users/tarunuday/Documents/scrapdata/mech.html'
print("Connecting to ",urls)

htmlfile = urllib.request.urlopen(urls)
soup = BeautifulSoup(htmlfile,'html.parser')
test=soup.find_all("table", "tdborder")[2].find_all("tr")
print("Connection established")
print("Connecting to database...")
i=37
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

while(i<100):
    ###############Start page no i
    link='http://edulix.com/unisearch/'
    link+=test[i].a["href"]
    profile = urllib.request.urlopen(link)
    data = BeautifulSoup(profile,'html.parser')
    print("---------------------------------")
    print("Connected to profile link:",link,i)

    ###############EXTRACT ID
    insert_extractid=1000000+int(l(test[i].a["href"]))

    ###############Checking for Universities
    if(not(uni_check(data))):
        print('No Universities to show')
        i+=1
        continue

    ###############Section 0 - NAME
    insert_name=r(data.find_all("table", "tdborder")[0].find_all("tr")[2].find_all("td")[1].string)
    if(insert_name==""):
        insert_name=r(data.find_all("a", "no_uline")[0].string)

    ###############Section 1 - App Details
    attend=""
    program=""
    major=""
    special=""
    year=0
    term=0
    htmlcursor=data.find_all("td", "orange_title tdhor")[1].parent
    while(True):
        htmlcursor=htmlcursor.next_sibling.next_sibling
        if(htmlcursor.td.string=="Standardized Test Scores"):
            break
        else:
            if(htmlcursor.td.string=="University (will be) Attending"):
                attend=r(htmlcursor.find_all("td")[1].a.string)
            if(htmlcursor.td.string=="Program"):
                program=p(r(htmlcursor.find_all("td")[1].string))
            if(htmlcursor.td.string=="Major"):
                major=r(htmlcursor.find_all("td")[1].string)
            if(htmlcursor.td.string=="Specialization"):
                special=r(htmlcursor.find_all("td")[1].string)
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
    try:
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
    except AttributeError:
        pass #this happens when there are no undergrad details given
    
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
        insert_misc=r(htmlcursor.td.contents[0])       #This got me stuck for a couple of days. .contents gives output as a list
    except IndexError:
        insert_misc=""
    

    ###############ENTERING PROFILE DATA TO DATABASE
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `profiles` (`pro_id`, `extractid`, `name`, `current`, `college`, `major`, `gpa`, `gre`, `toefl`, `ielts`, `journal`, `conference`, `industry`, `research`, `internship`, `misc`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, [None, insert_extractid, insert_name, int("1"), insert_college, insert_major, insert_gpa, insert_gre, insert_toefl, insert_ielts, insert_journal, insert_conference, insert_industry, insert_research, insert_internship, insert_misc])
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    pro_id=db_profile(insert_extractid) #### We just got the last piece of the puzzle. the auto-incremented id of the latest entry
    print("Data for ",pro_id,"entered")

    ###############University Data
    htmlcursor=data.find_all("table", "tdborder")[1].find_all("tr")
    j=1
    u=len(data.find_all("table", "tdborder")[1].find_all("tr"))
    flag=1          ######Flag to chk if we have got the text details about the uni, if any
    while(j<u):     ######Loop to get all uni info
        attend_status=0
        if(flag):
            uni_name=htmlcursor[j].a.string
            if(uni_name==attend):
                attend_status=1
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
            with connection.cursor() as cursor:
                # Create a new record
                result=db_uni_list_searchbyname(uni_name)
                if result is None: #To test is sql returned empty rows
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `uni_list` (`name`) VALUES (%s)"
                        cursor.execute(sql, uni_name)
                    connection.commit()
                    print("INSERTED ",uni_name, "TO LIST OF UNIVERSITIES")
                    result=db_uni_list_searchbyname(uni_name)
                    db_uni_data_enterall(pro_id, result["uni_id"], int(program), major, int(term), (year), int(uni_status), attend_status, uni_text)
                else: #SQL hasn't returned empty rows so do this:
                    print(pro_id,result["uni_id"],program,major,term,year,uni_status,attend_status,uni_text)
                    db_uni_data_enterall(pro_id, result["uni_id"], int(program), major, int(term), (year), int(uni_status), attend_status, uni_text)
            print("INSERTED: ",uni_name,",",uni_status,attend_status,uni_text)    
    i+=1
    print("end well")
connection.close()