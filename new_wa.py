from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import mysql.connector


class Whatsapp(object):
    def __init__(self, id=None, mobile=None, message=None, saved_name=None):
        self.id = id
        self.mobile = mobile
        self.message = message
        self.saved_name = saved_name


def start_wp(numbers, cnx, browser):
    for i in range(0, len(numbers)):
        name = str(numbers[i].saved_name)
        id = numbers[i].id
        message = numbers[i].message
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        elem = browser.find_element_by_xpath("//input[@title='Search or start new chat']")
        elem.click()
        elem.send_keys(name)
        time.sleep(10)
        print("id - "+str(id))
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
            time.sleep(10)
        except Exception as e:
            sql = "UPDATE whatsapp SET status = 'failed', update_on = '" + now + "' WHERE id = '" + str(id) + "'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()
            print("failed")


def start_surf(browser):
    try:
        cnx = mysql.connector.connect(
            host="78.47.90.52",
            port=3306,
            user="root",
            password="Surajit@123",
            database="whatsapp")
        mycursor = cnx.cursor()
    except Exception as e:
        print("Invalid DB connection")
        browser.close()
        exit(1)
    print("Connecting DB...")
    print("Getting data...")
    mycursor.execute("SELECT * FROM whatsapp where status = 'pending' limit 100")
    myresult = mycursor.fetchall()
    print("Got - " + str(len(myresult)) + " records")
    if len(myresult) > 0:
        number_list = []
        for x in myresult:
            number_list.append(Whatsapp(x[0], x[1], x[5], x[2]))
        start_wp(number_list, cnx, browser)
    print("Waiting for getting new data")
    time.sleep(60)
    start_surf(browser)


browser = webdriver.Chrome(executable_path='/run/media/surajit/962E95F42E95CE1D/Youtube/chromedriver')
browser.get('https://web.whatsapp.com')
time.sleep(60) # uncomment it
start_surf(browser)
browser.close()