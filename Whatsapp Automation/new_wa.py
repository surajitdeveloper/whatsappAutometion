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
        # browser.find_element_by_xpath("//*[@title='"+name+"']").click()
        try:
            browser.find_element_by_xpath('//span[@title = "{}"]'.format(name)).click()
            time.sleep(5)
        except Exception as e:
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
        except Exception as e:
            sql = "UPDATE whatsapp SET status = 'failed', update_on = '" + now + "' WHERE id = '" + str(id) + "'"
            mycursor = cnx.cursor()
            mycursor.execute(sql)
            cnx.commit()


def start_surf(cnx, browser):
    mycursor = cnx.cursor()
    mycursor.execute("SELECT * FROM whatsapp where status = 'pending' limit 100")

    myresult = mycursor.fetchall()
    number_list = []
    for x in myresult:
        number_list.append(Whatsapp(x[0], x[1], x[5], x[2]))
    # print(number_list[5].message)
    # print(number_list[5].id)
    start_wp(number_list, cnx, browser)
    time.sleep(60)
    start_surf(cnx, browser)


cnx = mysql.connector.connect(
    host="78.47.90.52",
    port=3306,
    user="root",
    password="Surajit@123",
    database="whatsapp")

browser = webdriver.Chrome(executable_path='/run/media/surajit/962E95F42E95CE1D/Youtube/chromedriver')
browser.get('https://web.whatsapp.com')
time.sleep(60)
start_surf(cnx, browser)
# exit(1)
# name='+91 85850 25948'
# message=""


# for i in range(20):
#     elem.send_keys("hello this is from python " + Keys.ENTER)
#     time.sleep(1)
# browser.close()