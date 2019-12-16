from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import mysql.connector
#enter perfect name as in your contact (it is case sensitive)
# name=input("to whom you want to send message?")
#replace /chromedriver with loaction of chromedriver on your computer


class Whatsapp(object):
    """__init__() functions as the class constructor"""
    def __init__(self, id=None, mobile=None, message=None, saved_name=None):
        self.id = id
        self.mobile = mobile
        self.message = message
        self.saved_name = saved_name


def start_wp(numbers, cnx, browser):
    # print(numbers)
    for i in range(0, len(numbers)):
        # print(i)
        # print(numbers[i].message + " " + str(numbers[i].id))
        name = str(numbers[i].saved_name)
        id = numbers[i].id
        message = numbers[i].message
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        elem = browser.find_element_by_xpath("//input[@title='Search or start new chat']")
        elem.click()
        elem.send_keys(name)
        time.sleep(10)
        print(id)
        # browser.find_element_by_xpath("//*[@title='"+name+"']").click()
        try:
            browser.find_element_by_xpath('//span[@title = "{}"]'.format(name)).click()
            time.sleep(5)
        except Exception as e:
            print("failed")
            elem = browser.find_element_by_xpath("//input[@title='Search or start new chat']")
            elem.click()
            elem.send_keys("")
            sql = "UPDATE whatsapp SET status = 'failed', update_on = '" + now + "' WHERE id = '" + str(id) + "'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            return

        try:
            elem = browser.find_element_by_xpath("//div[@data-tab='1']")
            elem.click()
            elem.send_keys(message + Keys.ENTER)
            sql = "UPDATE whatsapp SET status = 'successful', update_on = '"+now+"' WHERE id = '"+str(id)+"'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            print("successful")
            time.sleep(25)
        except Exception as e:
            sql = "UPDATE whatsapp SET status = 'failed', update_on = '" + now + "' WHERE id = '" + str(id) + "'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            print("failed")


def start_surf(cnx, browser):
    mycursor = cnx.cursor()
    print("Connecting DB...")
    print("Getting data...")
    mycursor.execute("SELECT * FROM whatsapp where status = 'pending' limit 100")
    myresult = mycursor.fetchall()
    print("Got -" + str(len(myresult)) + " results")
    if len(myresult) > 0:
        number_list = []
        for x in myresult:
            number_list.append(Whatsapp(x[0], x[1], x[5], x[2]))
        start_wp(number_list, cnx, browser)
    start_surf(cnx, browser)


try:
    cnx = mysql.connector.connect(
        host="78.47.90.52",
        port=3306,
        user="root",
        password="Surajit@123",
        database="whatsapp")
except Exception as e:
    print("Invalid DB connection");
    exit(1)


browser = webdriver.Chrome(executable_path='/run/media/surajit/962E95F42E95CE1D/Youtube/chromedriver')
browser.get('https://web.whatsapp.com')
time.sleep(60) # uncomment it
start_surf(cnx, browser)
browser.close()