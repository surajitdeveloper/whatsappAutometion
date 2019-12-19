from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import mysql.connector
import os
import pipes
import platform


class Whatsapp(object):
    def __init__(self, id=None, mobile=None, message=None, saved_name=None):
        self.id = id
        self.mobile = mobile
        self.message = message
        self.saved_name = saved_name


def start_wp(numbers, cnx, browser, id_str):
    for i in range(0, len(numbers)):
        name = str(numbers[i].saved_name)
        id = numbers[i].id
        message = numbers[i].message
        number = "91"+str(numbers[i].mobile)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            whatsappUrl = "https://web.whatsapp.com/send?phone=" + number + "&text=" + message
            browser.get(whatsappUrl)
            time.sleep(1)
            wait = WebDriverWait(browser, 600)
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@title='Search or start new chat']")))
            time.sleep(4)
            print("Whatsapp contact loaded")
            print("id - " + str(id))
        except Exception as e:
            print("failed")
            sql = "UPDATE whatsapp SET status = 'failed', update_on = '" + now + "' WHERE id = '" + str(id) + "'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            return False
        try:
            elem = browser.find_element_by_xpath("//div[@data-tab='1']")
            # elem.click()
            elem.send_keys(Keys.ENTER)
            sql = "UPDATE whatsapp SET status = 'successful', update_on = '"+now+"' WHERE id = '"+str(id)+"'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            print("successful")
            # time.sleep(10)
        except Exception as e:
            sql = "UPDATE whatsapp SET status = 'failed', update_on = '" + now + "' WHERE id = '" + str(id) + "'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            print("failed")


def start_surf(browser):
    try:
        host = '78.47.90.52'
        port = 3306
        user = "root"
        password = "Surajit@123"
        dbname = "whatsapp"
        cnx = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname)
        mycursor = cnx.cursor()
    except Exception as e:
        print("Invalid DB connection")
        browser.close()
        exit(1)
    print("Connecting DB...")
    print("Getting data...")
    mycursor.execute("SELECT * FROM whatsapp where status = 'pending' and read_flag = 0 limit 100")
    myresult = mycursor.fetchall()
    print("Got - " + str(len(myresult)) + " records")
    if len(myresult) > 0:
        number_list = []
        for x in myresult:
            number_list.append(Whatsapp(x[0], x[1], x[5], x[2]))
        # print(number_list)
        id_str = ""
        for i in range(0, len(number_list)):
            id_str += str(number_list[i].id)
            if i + 1 != len(number_list):
                id_str += ","
        # print(id_str)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        uodate_query = "update whatsapp set read_flag = 1, read_start_flag = '"+now+"' where id in ("+id_str+")"
        # print(uodate_query)
        # exit(1)
        mycursor = cnx.cursor()
        mycursor.execute(uodate_query)
        cnx.commit()
        start_wp(number_list, cnx, browser, id_str)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        uodate_query = "update whatsapp set read_flag = 0, read_end_flag = '"+now+"' where id in (" + id_str + ")"
        mycursor = cnx.cursor()
        mycursor.execute(uodate_query)
        cnx.commit()
    try:
        DATETIME = time.strftime('%Y%m%d-%H%M%S')
        TODAYBACKUPPATH = './db_backup/' + DATETIME
        db = dbname
        dumpcmd = "mysqldump -h " + host + " -u " + user + " -p" + password + " " + db + " > " + pipes.quote(
            TODAYBACKUPPATH) + "_" + db + ".sql"
        os.system(dumpcmd)
        gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "_" + db + ".sql"
        os.system(gzipcmd)
    except Exception as e:
        print("DB cant be backup")
    print("Waiting for getting new data")
    # time.sleep(60) #uncomment it
    start_surf(browser)

if platform.system() == "Linux":
    browser = webdriver.Chrome(executable_path='chromedriver')
elif platform.system() == "Windows":
    browser = webdriver.Chrome(executable_path='chromedriver.exe')
else:
    print(platform.system())
    exit(1)
browser.get('https://web.whatsapp.com')
wait = WebDriverWait(browser, 600)
wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@title='Search or start new chat']")))
time.sleep(5)
print("You are successfully logged in whatsApp web")
start_surf(browser)
browser.close()