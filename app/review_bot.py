import os
import random
import time
import json
import datetime
import smtplib


from private import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Setting paths for review templates and filler words as well as all of weedbell site addresses
SITES = os.path.join("data", "sites.json")
RATING_FILLERS = os.path.join('data', 'rating_fillers.json')
REVIEW_TEMPLATES = os.path.join('data', 'review_templates.json')
MOBILE_CARRIERS = os.path.join('data', 'carrier_info.json')
SS_PATH = "C:/Projects/weedmaps_review_bot/data/screenshots/"


# Prompts user to enter weedbell delivery drivers(DD) name and phone number
# This function will keep prompting the user to correct their input until they
# answer yes on the question
DD_NAME = input("\nEnter the drivers name : ")
dd_name_check = input("\n'{}'  Is this correct? Y/N : ".format(DD_NAME))
while dd_name_check.lower() != "y":
    DD_NAME = input("\nEnter the drivers name : ")
    dd_name_check = input("\n'{}'  Is this correct? Y/N : ".format(DD_NAME))

DD_PHONE = input("\nEnter the drivers phone number : ")
dd_phone_check = input("\n'{}'  Is this correct? Y/N : ".format(DD_PHONE))
while dd_phone_check.lower() != "y":
    DD_PHONE = input("\nEnter the drivers phone number : ")
    dd_phone_check = input("\n'{}'  Is this correct? Y/N :".format(DD_PHONE))

with open(MOBILE_CARRIERS, encoding='utf-8') as MC:
    MC_LIST = json.loads(MC.read())

for index, carrier in enumerate(MC_LIST):
    print(index, carrier)

print("Please goto https://freecarrierlookup.com/ and enter the drivers phone number to get their carrier.\n")
DD_CARRIER = input("\n Enter the number cooresponding to the drivers mobile carrier from the list above : ")
DD_C_CHECK = input("\n'{}'  Is this correct? Y/N : ".format(DD_CARRIER))
while DD_C_CHECK.lower() != "y":
    DD_CARRIER = input("\n Enter the number cooresponding to the drivers mobile carrier from the list above : ")
    DD_C_CHECK = input("\n'{}'  Is this correct? Y/N : ".format(DD_CARRIER))

# add an index number to each mobile carrier in the dict and then picks the carrier from the users answer to the carrier prompt
DD_SMS_GATEWAY = ""
for i, (k, v) in enumerate(MC_LIST.items()):
    if i == int(DD_CARRIER):
        DD_SMS_GATEWAY += v


with open(SITES, encoding='utf-8') as sites_json, open(RATING_FILLERS, encoding='utf8') as ratings_json, open(REVIEW_TEMPLATES, encoding='utf8') as reviews_json:
    SITES_LIST = json.loads(sites_json.read())
    RATINGS_LIST = json.loads(ratings_json.read())
    REVIEWS_LIST = json.loads(reviews_json.read())

# Sets two types of delays.  Long delays for waiting for pages to load and short delays for typing text
SHORT_DELAY = random.randrange(0, 2)
LONG_DELAY = random.randrange(9, 20)

# Global weedmaps xpaths that will stay the same throughout the site
REVIEW_XPATH = "//*[@id='content']/div[4]/div/div[2]/div/div[1]/div[2]/h2"

# Opens a chrome instance with debugging enabled to use selenium without chromedriver
os.startfile(r"C:\Projects\weedmaps_review_bot\data\chrome_shortcut.lnk")
time.sleep(10)

# Initialize selenium webdriver and attaches to chrome.exe using debugger port
CHROME_OPTIONS = Options()
CHROME_OPTIONS.debugger_address = "127.0.0.1:9222"
DRIVER = webdriver.Chrome(options=CHROME_OPTIONS, executable_path=r'C:\Utility\Browserdrivers\chromedriver.exe')
DRIVER.get('https://weedmaps.com/login?mode=email')

#Test if element exists to scroll to
def check_exists_by_xpath(xpath):
    try:
        DRIVER.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

print("\nChecking if browser is currently logged into weedmaps...")
DRIVER.implicitly_wait(LONG_DELAY)
if check_exists_by_xpath('//*[@id="user_username"]'):
    print("\nLogging into weedmaps...")
    USER_FIELD = DRIVER.find_element_by_xpath('//*[@id="user_username"]')
    PASSWORD_FIELD = DRIVER.find_element_by_xpath('//*[@id="user_password"]')
    # These functions type the username and password with a short delay randomized between 0-1 seconds between each character
    print("\nTyping username")
    for character in config.WEEDMAPS_USERNAME:
        USER_FIELD.send_keys(character)
        time.sleep(SHORT_DELAY)
    print("\nTyping password")
    for character in config.WEEDMAPS_PASSWORD:
        PASSWORD_FIELD.send_keys(character)
        time.sleep(SHORT_DELAY)

    DRIVER.find_element_by_xpath('//*[@id="login"]').click()
    print("\nLogged in!")
else:
    print("\nAlready logged in. Navigating to the first site.")

# this will be used to check if we have already written a review on the site
FINDPHRASE = lambda s, var: var.lower() in s.lower()
# Goes over each weedbell location one by one and rates the review 5 stars, types a randomly chosen review from 
# the list of reviews and inserts the DRIVERs name to get credit
for site in SITES_LIST:
    DRIVER.get(SITES_LIST[site])
    time.sleep(7)
    if FINDPHRASE(DRIVER.page_source, 'alt="5 Stars"'):
        print("\nNo review posted in the last 30 days.  Posting..")
        page_review_button = DRIVER.find_element_by_xpath("//button[1]")
        page_review_button = DRIVER.find_element_by_xpath("//button[@data-test-id='review-button']")
        page_review_button.click()

        five_star_button = DRIVER.find_element_by_xpath("//button[5]")
        five_star_button = DRIVER.find_element_by_xpath("//button[@alt='5 Stars']")
        five_star_button.click()

        review_title_field = DRIVER.find_element_by_xpath("//textarea")
        review_title_field = DRIVER.find_element_by_xpath("//textarea[@data-test-id='title-input']")
        for letter in DD_NAME:
            review_title_field.send_keys(letter)
            time.sleep(SHORT_DELAY)

        review_body_field = DRIVER.find_element_by_xpath("//textarea")
        review_body_field = DRIVER.find_element_by_xpath("//textarea[@data-test-id='body-input']")

        random_review = random.choice(list(REVIEWS_LIST.values()))
        random_rating = random.choice(list(RATINGS_LIST.values()))
        randomized_body = random_review.format(DD_NAME, random_rating)

        for char in randomized_body:
            review_body_field.send_keys(char)
            time.sleep(SHORT_DELAY)

        post_review_button = DRIVER.find_element_by_xpath("//button")
        post_review_button = DRIVER.find_element_by_xpath("//button[@data-test-id='submit-review']")
        post_review_button.click()
        time.sleep(LONG_DELAY)

        ok_review_button = DRIVER.find_element_by_xpath("//button")
        ok_review_button.click()
        time.sleep(LONG_DELAY)
        #
        file_number = 1

        if check_exists_by_xpath(REVIEW_XPATH):
            REVIEW_ELEMENT = DRIVER.find_element_by_xpath(REVIEW_XPATH)
            print("Review header found.. proceeding..")
            time.sleep(5)
            #Execute script runs javascript code to scroll to the beginning of the user reviews and the scrolls back up by 150px to get the proper screenshot
            DRIVER.execute_script("return arguments[0].scrollIntoView();", REVIEW_ELEMENT)
            DRIVER.execute_script("window.scrollBy(0, -150);")
            TODAY = datetime.date.today()
            TODAY.strftime("%m-%d-%y")
            DRIVER.save_screenshot("{}{}_{}_{}.png".format(SS_PATH, DD_NAME, TODAY, file_number))
            print("\nReview complete & screenshot taken!")
        else:
            print("Review header not found.. skipping screenshot")
            DRIVER.quit()
            file_number += 1
    else:
        # checks source code of site for the number of days you have to wait until you can post another review
        print("\nYou have already written a review in the past 30 days.")
        for num in list(range(0, 31)):
            if FINDPHRASE(DRIVER.page_source, 'create a new one in<!-- --> <!-- -->{} days'.format(str(num))):
                print("You must wait {} days to post another review".format(num))

    time.sleep(LONG_DELAY)
    DRIVER.quit()


# Sends the collected screenshots via text message to the delivery driver
def text_screenshots(phone, gateway, ss_folder, attach_file):
    # Setup which email and cooresponding server to use to send sms. We will be using gmail.
    email = config.SMS_EMAIL
    pas = config.SMS_PASSWORD
    smtp = "smtp.gmail.com"
    port = 587
    server = smtplib.SMTP(smtp, port)
    server.starttls()
    server.login(email, pas)
    msg = MIMEMultipart()
    msg['Subject'] = 'Weedmaps reviews'
    msg.preamble = 'Weedmaps reviews'
    # Iterates over the screenshot folder and sends all screenshots from today
    for file in os.listdir(ss_folder):
        filename = os.fsdecode(file)
        # looks for images with the drivers name and todays date
        if filename.startswith("{}_{}".format(DD_NAME, TODAY)):
            msg['From'] = email
            msg['To'] = "{}{}".format(phone, gateway)
            fp = open("{}/{}".format(ss_folder, attach_file), 'rb')
            img = MIMEImage(fp.read())
            msg.attach(img)
            server.send_message(msg)
            time.sleep(2)
            print("\nPicture sent to driver")
    server.quit()
print("\nAll reviews sent to driver! Enjoy your free joints :D")
