from flask import Flask,session,request,redirect
import requests
import threading
from pprint import pprint
from bs4 import BeautifulSoup
import requests
from selenium  import webdriver
from functools import wraps
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
import os
from app import session

ENV = os.environ.get('APPLICATION_ENV')
if ENV == 'dev':
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

if ENV == 'prod':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #login url for hac
def hac_api_main(function,api,username,password):
    if function == "":
        return {"error":"go to https://github.com/bolivarc3/HacApi or information on usage of the api"}
    if username == '' or password == '':
        return {"error":"you didnt put the username and password of the hac user. make url like -> /<insert what you want(grades,attendance,etc)>/<insert username>/<insert password>/"}
    if "HacStatus" not in session:
        session["HacStatus"] = False
    if session["HacStatus"] == False or api:
        try:
            driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f")
            wait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Database")))
        except TimeoutException:
            # If WebDriverWait times out, handle it here
            return "Timeout: Element not found within specified time"
        except WebDriverException as e:
            return {"error":"An error occurred:" + str(e)}
        finally:
            print("It has been Run")
        dropdown = Select(driver.find_element(By.ID,'Database'))
        dropdown.select_by_visible_text("Bentonville School District");
        element = driver.find_element(By.XPATH, '//input[@id="LogOnDetails_UserName"]')
        element.clear()

        # Use the WebElement to find the element by CSS selector
        # element = element_by_id.find_element(By.CSS_SELECTOR,'input')
        element.send_keys(username)
        anotherelement = driver.find_element(By.ID,"LogOnDetails_Password")
        anotherelement.send_keys(password)
        anotherelement.send_keys(Keys.ENTER)
        url = 'https://hac20.esp.k12.ar.us/HomeAccess20/Account/LogOn?ReturnUrl=%2fHomeAccess20%2f'
    session["HacStatus"] = True
    #Grab __RequestVerifcationToken(token needed to login)
    #checks if login was successful
    soup = BeautifulSoup(driver.page_source.encode('utf-8'))
    validation = soup.find('div', {'class':'validation-summary-errors'})
    if validation != None:
        error = validation.find('span')
        error = error.text
        return {"error": error}
    #checks if login was successful
    if function == 'both':
        driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Content/Student/Assignments.aspx")
        try:
            element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sg-header-heading")))
        finally:
            pass
        classnames = grabclasses(driver)
        assignmentgrades = grabassignmentgrades(driver,classnames)
        gradesum = graboverallgrades(driver,classnames)
        #returns in dictionary form
        attendance = grabcalendar(driver,username,password)
        reset(api,driver)
        return classnames,gradesum,assignmentgrades,attendance
    if function == 'attendance':
        driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Content/Attendance/MonthlyView.aspx")
        try:
            element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sg-main-content")))
        finally:
            pass
    #grabs the attendance using selenium
        attendance = grabcalendar(driver,username,password)
        reset(api,driver)
        return attendance
    if function == 'grades':
        driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Content/Student/Assignments.aspx")
        try:
            element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sg-header-heading")))
        finally:
            pass
        classnames = grabclasses(driver)
        assignmentgrades = grabassignmentgrades(driver,classnames)
        gradesum = graboverallgrades(driver,classnames)
        reset(api,driver)
        return classnames,gradesum,assignmentgrades
    #returns in a dictionary

def reset(api,driver):
    if api:
        driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Home/WeekView")
        try:
            wait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="/HomeAccess/Account/Logoff"]')))
        finally:
            print("not there")
        link = driver.find_element(By.XPATH, '//a[@href="/HomeAccess/Account/Logoff"]')
        link.click()
        driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f")

def grabclasses(driver):
    soup = BeautifulSoup(driver.page_source.encode('utf-8'))
    classes = soup.findAll('a', {'class':'sg-header-heading'})
    courses = []
    #grabs all classes and add them into a list/array
    for course in classes:
        text = course.text
        text = processcell(text)
        courses.append(text)
    return (courses)

def grabassignmentgrades(driver,classes):
    soup = BeautifulSoup(driver.page_source.encode('utf-8'))
    tables = soup.findAll('table', {'class':'sg-asp-table'})
    grades = {}
    #iterates through tables(each table is a different class)
    #checks each table to find the correct table
    for table in tables:
        components = table.get('id').split("plnMain_rptAssigmnetsByCourse_dgCourseAssignments_")
        if len(components) == 2:
            number = int(components[1])
            course = classes[number]
            id = table.get('id')
            rows = table.findAll('tr', {'class':'sg-asp-table-data-row'})
            classgrades = []
            for row in rows:
                cells = row.findAll('td')
                assignment = []
                for cell in cells:
                    celltext = cell.text
                    celltextprocessed = processcell(celltext)
                    assignment.append(celltextprocessed)
                classgrades.append(assignment)
            current_class = classes[number]
            grades[current_class] = classgrades
    for class_name in classes:
        if class_name not in grades.keys():
            grades[class_name] = ["null"]
    return(grades)

def graboverallgrades(driver,classes):
    soup = BeautifulSoup(driver.page_source.encode('utf-8'))
    tables = soup.findAll('table', {'class':'sg-asp-table'})
    grades = {}
    overall_grades = {}
    classes = grabclasses(driver)
    #iterates through tables(each table is a different class)
    #checks each table to find the correct table
    for table in tables:
        components = table.get('id').split('plnMain_rptAssigmnetsByCourse_dgCourseCategories_')
        if len(components) ==2:
            number = int(components[1])
            course = classes[number]
            id = table.get('id')
            rows = table.findAll('tr', {'class':'sg-asp-table-data-row'})
            classgrades = []
            for row in rows:
                cells = row.findAll('td')
                assignment = []
                for cell in cells:
                    celltext = cell.text
                    celltextprocessed = processcell(celltext)
                    assignment.append(celltextprocessed)
                classgrades.append(assignment)
            current_class = classes[number]
            grades[current_class] = classgrades
    for class_name in classes:
        if class_name not in grades.keys():
            grades[class_name] = ["null"]
    return (grades)

def grabcalendar(driver, username, password):
    driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Content/Attendance/MonthlyView.aspx")
    driver.maximize_window();

    #driver goes to page and adds the cookies needed to access the page
    driver.get("https://hac23.esp.k12.ar.us/HomeAccess/Content/Attendance/MonthlyView.aspx")
    #driver goes to page and adds the cookies needed to access the page

    driver = gobackfirst(driver)
    calendar = calendarcreation(driver)
    return calendar

def gobackfirst(driver):
    pastmonthavalilbilty = 'yes'
    while pastmonthavalilbilty != None:
        #grabs html and finds the past month availibility(if there is a button for the past month)
        calendarhtml = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(calendarhtml)
        try:
            wait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@title='Go to the previous month']")))
        finally:
            print("not there")
        pastmonthlink = soup.find('a', {'title':'Go to the previous month'})
        pastmonthavalilbilty = pastmonthlink.find('span')
        #grabs html and finds the past month availibility(if there is a button for the past month)
        if pastmonthavalilbilty != None:
            l = driver.find_element(By.CSS_SELECTOR,"[title*='Go to the previous month']")
            l.click()
    return driver

def calendarcreation(driver):
    calendardict = {}
    nextmonthavalilbilty = 'yes'

    #while there is a past month, loop
    while nextmonthavalilbilty != None:
        #grabs html and finds the past month availibility(if there is a button for the past month)
        calendarhtml = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(calendarhtml)
        nextmonthlink = soup.find('a', {'title':'Go to the next month'})
        nextmonthavalilbilty = nextmonthlink.find('span')
        #grabs html and finds the past month availibility(if there is a button for the past month)

        #grabs months and weeks to loop through
        month = soup.find('table', {'id':'plnMain_cldAttendance'})
        weeks = month.findAll('tr')
        #grabs months and weeks to loop through

        #iterates through the weeks
        usermonth = []
        for week in weeks:
            dates = week.findAll('td')
            userweek = []

            #iterates through specific dates
            for date in dates:
                #grabs the number of the dates and processes
                celltext = date.text
                celltextprocessed = processcell(celltext)

                #grabs the school code(abcent...etc)
                schoolcode = date.get('title')
                #if there is a school code, process it
                if schoolcode != None:
                    schoolcodeprocessed = processcell(schoolcode)
                else:
                    schoolcodeprocessed = None

                #link the date and the school code together
                celltext = [celltextprocessed,schoolcodeprocessed]
                #add to the week
                userweek.append(celltext)
            #add week to month
            usermonth.append(userweek)

        #seperates month name and data and adds creates a dictionary
        monthdata = []
        monthname = []
        monthname = processcell(usermonth[0][0][0])
        for i in range(6):
            monthdata.append(usermonth[3+i])
        calendardict[monthname] = monthdata
        #dictionary looks like -> {'monthname and year':'[monthdata[weekdata[date data]]]}
        #{'September 2021':'[[['5', None], ['6', None], ['7', 'schoolcode'], ['8', None], ['9', None], ['10', None], ['11', None]]] . . . '}

        if nextmonthavalilbilty != None:
            l = driver.find_element(By.CSS_SELECTOR,"[title*='Go to the next month']")
            l.click()
    return calendardict

def processcell(text):
    text = text.strip()
    text = text.replace('\r\n                                \n*', '')
    text = text.replace('\n', ' ')
    text = text.replace('<<','')
    text = text.replace('>>','')
    text = text.replace('                                  *','')
    return(text)