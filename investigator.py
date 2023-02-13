import stdiomask
import hashlib
import base64
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv
import getpass
import time
import tweepy


class Investigator:
    # Tweepy Auth Keys
    auth = tweepy.OAuthHandler("0TGFbb0lQ1hU0W1Qqc2mbTUko", "Y5w31GmIiju6WBvYx6cgtMP0k8xq6EfHp79p0VGUrRBWtPzuv9")
    auth.set_access_token("1069081694982918146-hFPe44hi3K7aLdBsl6N8w57SZl8qWN", "FZUimzCbLBfcJ0ESn8sa2z6xL209FInZ2inmQ5TWpZTz8")
    posts = []
    # Storing a list of dictionaries to push to a "database" file
    linkedin_contacts = []
    linkedin_contact = {}
    # Keeping track of the user who is logged in
    current_user = {}
    current_profile = {}
    # Storing a list of dictionaries to push to a "database" file
    facebook_profiles = []
    facebook_profile = {}
    # Variable to keep track of whether or not a user is logged in
    logged_in = False
    # Files containing information regarding investigators and created profiles
    config_file = "/home/kali/Documents/WebID/operator_config"
    profile_config = "/home/kali/Documents/WebID/profile_config"
    # List of investigators
    users = []
    user_vals = {}

    # Main menu, called often to return to selection
    def menu(self):
        iteration = 0
        menu_selection = input("----------Welcome to WebID------------\n\t1.) Login\n\t2.) Create New Investigator\n\t3.) Create New Profile\n\t4.) Load Profile\n\t5.) Exit\n\t6.) Help\n\t7.) Set Configuration Paths\n")
        if menu_selection == '1':
            if self.logged_in:
                print("You're already logged in.")
                self.menu()
            else:
                if iteration > 0:
                    self.find_investigator()
                else:
                    iteration += 1
                    self.read_investigators()
                    self.find_investigator()
                    self.menu()
        elif menu_selection == '2':
            self.read_investigators()
            self.load_investigator()
        elif menu_selection == '3':
            if self.logged_in == False:
                print("You must be logged in to access this portion of the program.")
                self.menu()
            else:
                self.create_profile()
        elif menu_selection == '4':
            if not self.logged_in:
                print("You must be logged in to access this portion of the program.")
                self.menu()
            else:
                self.load_profile()
        elif menu_selection == '5':
            print("Shutting down...")
            exit(1)
        elif menu_selection == '6':
            print("1.) If the databases aren't working properly. Modify the paths to the configuration files.")
            print("2.) If login isn't working correctly, values are case sensitive. Make sure you're keeping case.")
            print("3.) If you still can't figure it out, or have a suggested improvement. Email the creator at: *********@gmail.com")
            self.menu()
        elif menu_selection == '7':
            self.set_configurations()
        else:
            print("Invalid input.")
            self.menu()

    def set_configurations(self):
        areyousure = input("Are you sure you want to modify the config files? y/n\n")
        if areyousure == "y" or areyousure == "Y":
            new_conf_file = input("Absolute path to config_file: ")
            self.config_file = new_conf_file
            new_profile_file = input("Absolute path to profile_config: ")
            self.profile_config = new_profile_file
        else:
            self.menu()

    # Create a profile -- profiles are used to gather information on a POI
    def create_profile(self):
        which_one = input("Select an individual site or select all.\n\t1.) Facebook\n\t2.) Twitter\n\t3.) Linkedin\n\t4.) All\n\t5.) Cancel\n")
        if which_one == '1':
            self.load_profile_info_facebook()
        if which_one == '2':
            self.load_profile_info_twitter()
        if which_one == '3':
            self.load_profile_info_linkedin()
        if which_one == '4':
            self.load_profile_info_all()
        if which_one == '5':
            self.menu()

    def load_profile(self):
        global t_true
        print("Loading scraped profiles...")
        searchname = input("Name of the POI: ")
        searchscrape = input("Social Media Site: ")
        with open(self.profile_config, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # These are named linkedin but technically they'd be any contact
                self.linkedin_contact = row
                self.linkedin_contacts.append(self.linkedin_contact)
        temp_found = []
        for item in self.linkedin_contacts:
            if item['name'] == searchname:
                temp_found.append(item)
        if len(temp_found) == 0:
            tryagain = input("No user found. Try again? y/n\n")
            if tryagain == "y" or tryagain == "Y":
                self.load_profile()
            else:
                self.menu()
        t_true = False
        for item in temp_found:
            if item['key'] == searchscrape:
                t_true = True
                self.current_profile = item
        if not t_true:
            tryagaintwo = input("Invalid social media site. Try again? y/n\n")
            if tryagaintwo == "y" or tryagaintwo == "Y":
                self.load_profile()
            else:
                self.menu()
        print("Found profile...")
        print(self.current_profile.keys())
        print("Name: {}".format(self.current_profile['name']))
        if self.current_profile['key'] == "facebook" or self.current_profile['key'] == "linkedin":
            print("Information: {}".format(self.current_profile['details']))
            self.menu()
        else:
            print("Details: {}".format(self.current_profile['details']))
            print("Tweets: {}".format(self.current_profile['tweets']))
            self.menu()

    # Create profile from facebook
    def load_profile_info_facebook(self):
        print("For any field, you may input NA.\n")
        facebook_url = input("Facebook URL: ")
        self.facebook(self.current_user['facebook'], facebook_url)
        for item in self.posts:
            print(item)
        print("Completed scrape, returning...")
        self.menu()

    # Create profile from twitter
    def load_profile_info_twitter(self):
        print("For any field, you may input NA.\n")
        self.twitter()

    # Create profile from linkedin
    def load_profile_info_linkedin(self):
        print("For any field, you may input NA.\n")
        linkedin_url = input("LinkedIn URL: ")
        self.linked_in(self.current_user['linkedin'], linkedin_url)
        print("Completed scrape, returning...")
        self.menu()

    # Create profile from all three
    def load_profile_info_all(self):
        print("In development. Come back later...")
        #print("For any field, you may input NA.\n")
        #name = input("POI Name: ")
        #facebook_url = input("Facebook URL: ")
        #twitter_url = input("Twitter URL: ")
        #linkedin_url = input("LinkedIn Url: ")

    # Create new investigator account
    def create_investigator(self):
        print("For any field, you may input NA.\n")
        name = input("Investigator username: ")
        facebook_email = input("Facebook email: ")
        twitter_email = input("Twitter email: ")
        linkedin_email = input("Linkedin email: ")

        # Hashing the password so we're not storing plaintext
        password = stdiomask.getpass()
        hashed = hashlib.sha512(password.encode('utf-8')).hexdigest()
        """
        salt = os.urandom(32)
        print(salt)
        print(type(salt))
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        """
        # new_row = name + ", " + facebook_email + ", " + twitter_email + ", " + linkedin_email
        with open(self.config_file, mode='a') as csv_file:
            fieldnames = ['username', 'facebook', 'twitter', 'linkedin', 'hash']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({'username': name, 'facebook': facebook_email, 'twitter': twitter_email,
                             'linkedin': linkedin_email, 'hash': hashed}) #, 'salt': salt, 'key': key})

    def load_investigator(self):
        self.create_investigator()

    # Read investigator accounts from config file
    def read_investigators(self):
        print("Loading investigator profiles...")
        with open(self.config_file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.user_vals = row
                self.users.append(self.user_vals)

    # Locate investigator account based on username
    def find_investigator(self):
        temp_true = 0
        username = input("Input your username: ")
        for user in self.users:
            if user['username'] == username:
                temp_true = 1
                print("Found user, initiate login...")

                # Evaluating if password hash is correct
                password = stdiomask.getpass()
                hashed = hashlib.sha512(password.encode('utf-8')).hexdigest()
                saved = user['hash']
                if hashed == saved:
                    print("Welcome back, {}".format(user['username']))
                    self.current_user = user
                    self.logged_in = True
                else:
                    print("Incorrect password.")
                    cont = input("Continue? y/n\n")
                    if cont == "y" or cont == "Y":
                        self.find_investigator()
                    else:
                        self.menu()
        # If we don't find a user with that username
        if temp_true == 0:
            print("No users with that username exist...")
            other_cont = input("Try again? y/n\n")
            if other_cont == "y" or other_cont == "Y":
                self.find_investigator()
            else:
                self.menu()

    # LinkedIn scraper function
    def linked_in(self, investigator_email, url):
        name = input("POI Name: ")
        print("Note - Password is referring to your LinkedIn account password.")
        password = stdiomask.getpass()
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")
        driver.maximize_window()
        driver.get("https://www.linkedin.com/")

        # Send login details to linkedin
        driver.find_elements_by_class_name("input__input")[0].send_keys(investigator_email)
        driver.find_elements_by_class_name("input__input")[1].send_keys(password)
        driver.find_element_by_class_name("sign-in-form__submit-button").click()

        # Store contact information
        driver.get(url)
        to_dict = []
        contact_info = driver.find_elements_by_xpath("//a[@class='pv-contact-info__contact-link link-without-visited-state']")
        further_contact_info = driver.find_elements_by_xpath("//a[@class='pv-contact-info__contact-link link-without-visited-state t-14']")
        for item in contact_info:
            to_dict.append(item.text)
        for item in further_contact_info:
            to_dict.append(item.text)
        contact_info = contact_info + further_contact_info
        temp_dict = {'name': name, 'tweets': 'NA', 'details': to_dict, 'key': 'linkedin'}
        with open(self.profile_config, mode='a') as csv_file:
            fieldnames = ['name', 'tweets', 'details', 'key']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(temp_dict)

    # Facebook scraper function
    def facebook(self, investigator_email, url):
        name = input("POI Name: ")
        print("Note - Password is referring to your Facebook account password.")
        password = stdiomask.getpass()
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")
        driver.maximize_window()
        driver.get("https://facebook.com")
        # Send login details to facebook
        driver.find_element_by_id("email").send_keys(investigator_email)
        driver.find_element_by_id("pass").send_keys(password)
        driver.find_element_by_name("login").click()

        driver.get(url)
        post = driver.find_elements_by_xpath("//div[@dir='auto']")
        to_dict = []
        for item in post:
            to_dict.append(item.text)
        temp_dict = {'name': name, 'tweets': 'NA', 'details': to_dict, 'key': 'facebook'}
        with open(self.profile_config, mode='a') as csv_file:
            fieldnames = ['name', 'tweets', 'details', 'key']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(temp_dict)

    # Twitter scraper function
    def twitter(self):
        poi = input("POI Name: ")
        handle = input("Twitter Handle: ")
        api = tweepy.API(self.auth)
        user = api.get_user(handle)
        name = user.name
        desc = user.description
        location = user.location
        tweets = api.user_timeline(handle)
        to_dict = []
        other_to_dict = [user, name, desc, location]
        for item in tweets:
            to_dict.append(item.text)
        temp_dict = {'name': poi, 'tweets': to_dict, 'details': other_to_dict, 'key': 'twitter'}
        with open(self.profile_config, mode='a') as csv_file:
            fieldnames = ['name', 'tweets', 'details', 'key']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(temp_dict)
