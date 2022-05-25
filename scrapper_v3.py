from operator import index
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import os
import time
import datetime
import dateutil.parser
import pytz
import json
import re
import sys
import random
import pandas as pd
import warnings
from constants import *
from cssSelectors import *

class FacebookScrapper:
    def __init__(self):
        """Initialization function when FB Scrapper is executed"""
        self.recovered_posts = 0
        self.posts_selenium_ids = set()
        self.group_name = ""
        self.from_date = None
        self.to_date = None
        self.metadata = None

    def read_credentials(self):
        """Set Facebook Credentials"""
        with open("./credentials.txt") as file:
            user = file.readline().split('"')
            user = user[0][0:len(user[0])-1]
            password = file.readline().split('"')[0]
        return(user, password)

    def login(self):
        """Login with Credentials"""
        user, password = self.read_credentials()
        BROWSER.get("http://facebook.com")
        BROWSER.maximize_window()
        BROWSER.find_element(By.NAME, "email").send_keys(user)
        time.sleep(2)
        BROWSER.find_element(By.NAME, "pass").send_keys(password)
        time.sleep(1)
        BROWSER.find_element(By.NAME, "login").click()
        time.sleep(5)
        print("Inicio de sesión exitoso")

    def extractGroupName(self):
        group_name_text = BROWSER.find_element(By.CSS_SELECTOR, GROUP_NAME)
        self.group_name = group_name_text.text

    def seeMoreButtons(self,comm):
        """Auxiliary function to search See more buttons"""
        buttons = comm.find_elements(By.CSS_SELECTOR, SEE_MORE_BUTTONS)
        if buttons:
            for button in buttons:
                try:
                    move = ActionChains(BROWSER).move_to_element(button)
                    move.perform()
                    time.sleep(random.random())
                    if button.text in SEE_MORE_BUTTONS_TEXT:
                        click = ActionChains(BROWSER).click(button)
                        click.perform()
                except: pass

    def moreCommentsButtons(self,comments_area):
        """Auxiliary function to search and click for all buttons used to display more comments"""
        comments_area_id = comments_area.get_attribute("id")
        while True:
            more_comments_buttons = comments_area.find_elements(By.CSS_SELECTOR, MORE_COMMENTS_BUTTONS)
            more_comments_buttons += comments_area.find_elements(By.CSS_SELECTOR, MORE_RELEVANT_COMMENTS_BUTTONS_SECOND_CLASS)
            if more_comments_buttons == None: return
            if len(more_comments_buttons) == 0:
                time.sleep(1)
                return
            for button in more_comments_buttons:
                try:
                    if any(word in button.text for word in MORE_COMMENTS_TEXTS):
                        ActionChains(BROWSER).move_to_element(button).click().perform()
                        time.sleep(.8)
                except: pass
            try:
                time.sleep(0.7)
                comments_area = BROWSER.find_element(By.ID, comments_area_id)
            except: return

    def extractCommentTotalReactions(self,reactions_component):
        """Auxiliary function to extract total number of reactions from any comment"""
        try:
            comment_text_components = reactions_component.find_element(By.CSS_SELECTOR, COMMENT_TEXT_COMPONENT)
            return int(comment_text_components.text)
        except: return 1

    def newestPosts(self):
        """Auxiliary function to configure FB's group to order posts based on publication date (descending order)"""
        newest_posts_possible_buttons = BROWSER.find_elements(By.CSS_SELECTOR, NEWEST_POSTS_POSSIBLE_BUTTONS)
        if len(newest_posts_possible_buttons) > 0:
            for button in newest_posts_possible_buttons:
                if button.text in CURRENT_POSTS_TEXTS:
                    ActionChains(BROWSER).move_to_element(button).click().perform()
                    time.sleep(2)
                    comments_options = BROWSER.find_elements(By.CSS_SELECTOR, COMMENTS_OPTIONS)
                    for option in comments_options:
                        text = [x for x in NEWEST_POST_TEXTS if x in option.text]
                        if text != []:
                            ActionChains(BROWSER).move_to_element(option).click().perform()
                            time.sleep(2)
                            return

    def createJSON(self,info):
        """Creates JSON file to dump scrapped data"""
        with open("sampleNewFlow.json", "w", encoding="utf-8") as outfile:
            outfile.write(info)

    def writeInJSON(self,post_info):
        """Write new post information in JSON file"""
        with open("sampleNewFlow.json", "r+", encoding="utf-8") as outfile:
            existing_data = json.load(outfile)
            existing_data.append(post_info)
            outfile.seek(0)
            json.dump(existing_data, outfile, indent=4, ensure_ascii=False)
            time.sleep(0.3)

    def scrollDown(self, groupPageLength, maximum):
        """Scroll down in the group's page"""
        scrollCount = -1
        match = False
        while not match and scrollCount < maximum:
            self.getPosts(scrollCount)
            time.sleep(random.randint(2,4))
            scrollCount += 1
            BROWSER.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if scrollCount == groupPageLength:
                match = True

    def getToGroup(self):
        """Obtain html/raw information"""
        BROWSER.get(TEST_GROUP)
        time.sleep(5)
        self.extractGroupName()
        self.newestPosts()
        groupPageLength = BROWSER.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        
        self.scrollDown(groupPageLength, 1) #groupPageLength, 100

    def getPosts(self,scrollCount):
        """Identify posts HTML elements"""
        posts = BROWSER.find_elements(By.CLASS_NAME, POSTS)
        for post in posts:
            try: 
                if post.id not in self.posts_selenium_ids:
                    self.seeMoreButtons(post)
                    post_object = list()
                    self.posts_selenium_ids.add(post.id)
                    ActionChains(BROWSER).move_to_element(post).perform()
                    post_link, post_id, date, hour = self.extractPostLinkId(post)
                    user_name, user_link, user_id = self.extractPostUser(post)
                    post_message = self.getPostMessage(post)
                    hashtags = [x for x in post_message.split(" ") if "#" in x]
                    hashtags = ", ".join([str(h) for h in hashtags])
                    reactions, shares = self.extractReactionTotalAndShares(post)
                    total_comments, comments = self.extractTotalComments(post, date, post_link, post_id, hour)
                    scrapped_date = datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+0000"
                    post_info = {"post_text":post_message, "hashtags":hashtags, "post_link":post_link, "post_id":post_id, "user_name":user_name, "user_link":user_link, "user_id":user_id, 
                        "date":date, "hour":hour, "reactions":reactions, "shares":shares, "total_comments":total_comments,  "comments":comments, "type": "post", 
                        "group_name": self.group_name, "scrapped_date":scrapped_date} 
                    post_object.append(post_info)
                    if scrollCount != -1:
                        self.writeInJSON(post_info)
                    else: #In case JSON file is Empty
                        post_info = json.dumps(post_object, indent=4, ensure_ascii=False)
                        self.createJSON(post_info)
                    self.recovered_posts += 1
                    print('Se han recuperado {0} posts'.format(self.recovered_posts))
            except: pass          

    def getPostMessage(self,comm):
        """Obtain message contained in the group's post"""
        texts = comm.find_elements(By.CLASS_NAME, TEXTS_CLASS_ONE)
        texts = texts + comm.find_elements(By.XPATH, TEXTS_CLASS_TWO)
        texts = texts + comm.find_elements(By.XPATH, TEXTS_CLASS_THREE)
        texts_temp = comm.find_elements(By.CSS_SELECTOR, POSSIBLE_TEXTS_CLASS_FOUR)
        for text in texts_temp:
            parent_text = text.find_element(By.XPATH, "..")
            if parent_text.get_attribute("class") != TEXTS_CLASS_FOUR:
                texts.append(text)
        final_text = ""
        if texts:
            texts_used = []
            for post in texts:
                if post.text not in texts_used:
                    texts_used.append(post.text)
            for text in texts_used:
                final_text = final_text + text + " "
        if final_text == "": return final_text
        final_text = ' '.join(final_text.splitlines())
        final_text.strip()
        return final_text[:-1]

    def extractPostLinkId(self,comm):
        """Obtain post link and id"""
        link_elements = comm.find_elements(By.CLASS_NAME, LINK_ELEMENTS)
        if link_elements:
            index = 0
            true_date = False
            while not true_date:
                date_element = link_elements[index]
                if not any(word in date_element.text for word in PAID_PARTNERSHIPS_WORDS):
                    ActionChains(BROWSER).move_to_element(date_element).perform()
                    time.sleep(random.randint(3,4))
                    try:      
                        date_html_component = BROWSER.find_element(By.CSS_SELECTOR, DATE_COMPONENT)
                    except:
                        pass
                    try:
                        BROWSER.execute_script("window.scrollBy(0, -40);")
                        ActionChains(BROWSER).move_to_element(date_element).perform()
                        time.sleep(3)
                        date_html_component = BROWSER.find_element(By.CSS_SELECTOR, DATE_COMPONENT)
                    except:
                        BROWSER.execute_script("window.scrollBy(0, -100);")
                        ActionChains(BROWSER).move_to_element(date_element).perform()
                        time.sleep(3)
                        date_html_component = BROWSER.find_element(By.CSS_SELECTOR, DATE_COMPONENT)
                        
                    date, hour = self.extractPostDateHour(str(date_html_component.text))
                    beautify_data = bs(date_element.get_attribute("href"), 'html.parser')
                    with open('./bs.html',"w", encoding="utf-8") as file:
                        file.write(str(beautify_data.prettify()))
                        time.sleep(0.3)
                    true_date = True
                else: index += 1
            with open('./bs.html',"r", encoding="utf-8") as file:
                link = str(file.readline())
                id_start = link.index("posts") + 6
                base_post_link = link[0:id_start]
                post_id = re.match(POST_ID_REGEX, link[id_start:]).group()
                post_link = base_post_link + str(post_id) + "/"
                return post_link, post_id, date, hour 
        return "", "", date, hour  

    def extractPostUser(self,comm):
        """Extract post creator user information"""
        user_element = comm.find_element(By.CLASS_NAME, USER_ELEMENT)
        if user_element:
            user_element = user_element.find_element(By.CLASS_NAME, USER_ELEMENT_SECOND_INSTANCE)
            if user_element:
                user_name = user_element.text
                beautify_data = bs(user_element.get_attribute("href"), 'html.parser')
                with open('./bs.html',"w", encoding="utf-8") as file:
                    file.write(str(beautify_data.prettify()))
                    time.sleep(0.3)
                with open('./bs.html',"r", encoding="utf-8") as file:
                    link = str(file.readline())
                    try:
                        id_start = link.index("user") + 5
                        base_post_link = link[0:id_start]
                        user_id = re.match(USER_ID_REGEX, link[id_start:]).group()
                        user_link = base_post_link + str(user_id) + "/"
                    except:
                        diagonal_indexes = [i.start() for i in re.finditer("\/", link)]
                        user_link = "https://facebook.com" + link[diagonal_indexes[2]:diagonal_indexes[3]]
                        user_id = link[diagonal_indexes[2]+1:diagonal_indexes[3]-1]
                    return user_name, user_link, user_id  

    def extractPostDateHour(self,comm):
        """Extract post's date and hour of publication"""
        try:
            day = re.search(DATE_DAY_REGEX, comm).group()
            if len(day) == 1:
                day = "0"+ day
            year = re.search(DATE_YEAR_REGEX, comm).group()
            hour = re.search(HOUR_REGEX, comm).group()
            months_options = MONTHS_DICTONARY.keys()
            for month in months_options:
                month_p_options = month.split("/")
                month_p_options = list(map(lambda x: x.lower(), month_p_options))
                for m in month_p_options:
                    if m in comm.lower():
                        date = dateutil.parser.parse(day + "/" + MONTHS_DICTONARY[month] + "/" + year).strftime("%Y-%m-%d")
                        if self.from_date is None:
                            self.from_date = date
                            self.to_date = date
                        else:
                            self.from_date = min(date, self.from_date)
                            self.to_date = max(date, self.from_date)
                        return year + "-" + MONTHS_DICTONARY[month] + "-" + day, hour
                        #return day + "/" + MONTHS_DICTONARY[month] + "/" + year, hour
        except Exception: return "1999-01-01", "00:00"

    def extractReactionTotalAndShares(self,comm):
        """Extract post's total reactions and shares"""
        total_reactions = 0
        total_shares = 0
        try:
            data_bar = comm.find_element(By.CSS_SELECTOR, POST_DATA_BAR)
        except: return total_reactions, total_shares
        try:
            reactions_component = data_bar.find_element(By.CSS_SELECTOR, REACTIONS_COMPONENT)
            if "," in reactions_component.text or "." in reactions_component.text: total_reactions = self.extractOver1KReactionsShares(reactions_component)
            else:
                total_reactions = reactions_component.text.split()
                total_reactions = int(total_reactions[0])
        except:
            pass
        possible_shares_components = data_bar.find_elements(By.CSS_SELECTOR, SHARE_COMPONENTS)
        shares_component = ""
        for possible_share_component in possible_shares_components:
            if any(word in possible_share_component.text for word in SHARE_COMPONENT_WORDS):
                shares_component = possible_share_component
                break
        if shares_component == "":
            pass
        else: 
            if "," in shares_component.text or "." in shares_component.text: total_shares = self.extractOver1KReactionsShares(shares_component)
            else:
                total_shares = shares_component.text.split()
                total_shares = int(total_shares[0])
        return total_reactions, total_shares

    def extractOver1KReactionsShares(self,comm):
        """Function used to extract reaction or share total if it is over 1,000"""
        ActionChains(BROWSER).move_to_element(comm).perform()
        time.sleep(random.randint(3,4))
        component = BROWSER.find_element(By.CSS_SELECTOR, HIDDEN_SHARES_REACTIONS_COMPONENT)
        total = component.text.splitlines()[-1]
        total = total.split()
        total_number = total[1]
        total_number = total_number.replace(".","")
        total_number = total_number.replace(",","")
        return int(total_number)

    def extractTotalComments(self, comm, date, post_link, post_id, hour):
        """Extract total amount of comments, as well as its information"""
        total_comments = 0
        comments = []
        try:
            data_bar = comm.find_element(By.CSS_SELECTOR, POST_DATA_BAR)
        except: return total_comments, comments
        possible_commments_components = data_bar.find_elements(By.CSS_SELECTOR, COMMENTS_COMPONENTS)
        comments_component = None
        for possible_comment_component in possible_commments_components:
            if any(word in possible_comment_component.text for word in COMMENT_COMPONENT_WORDS):
                comments_component = possible_comment_component
                break
        if comments_component == None: pass
        else:
            if "," in comments_component.text or "." in comments_component.text: total_comments = self.extractCommentsEstimateOver1K(comments_component)
            else:
                total_comments = comments_component.text.split()
                total_comments = int(total_comments[0])
        self.defineCommentSelection(comm, "all")
        time.sleep(1)
        comments = self.extractPostComments(comm, date, post_link, post_id, hour)
        return total_comments, comments

    def extractCommentsEstimateOver1K(self,comm):
        """Function used to extract estimated comments total if it is over 1,000"""
        total = comm.text.split()[0]
        total = float(total.replace(",","."))
        if "mill" in comm.text:  total = int(total * 1000000)
        else: total = int(total * 1000)
        return total

    def defineCommentSelection(self,comm,type):
        """Auxilairy function to make sure All Comments/Relevant Comments mode is activated"""
        if type == "all": options = ALL_COMMENTS_SELECTION
        else: options = RELEVANT_COMMENTS_SELECTION
        try:
            comment_list_buttons = comm.find_elements(By.CSS_SELECTOR, COMMENTS_LIST_BUTTONS)
            comment_list_button = [x for x in comment_list_buttons if x.get_attribute("aria-label") not in PLAY_VIDEO_TEXTS]
            if comment_list_button[0].text not in options:
                ActionChains(BROWSER).move_to_element(comment_list_button[0]).click().perform()
                time.sleep(random.randint(1,2))
                possible_comment_showing_options = BROWSER.find_elements(By.CSS_SELECTOR, POSSIBLE_COMMENT_SHOWING_OPTIONS)
                for option in possible_comment_showing_options:
                    all_comments_text = [x for x in options if x in option.text]
                    if all_comments_text != []:
                        ActionChains(BROWSER).move_to_element(option).click().perform()
                        return
                ActionChains(BROWSER).move_to_element(comment_list_button[0]).click().perform()
            else: return
        except: pass

    def extractPostComments(self, comm, date, post_link, post_id, hour):
        """Function to extract information from comments regarding any post"""
        ActionChains(BROWSER).move_to_element(comm)
        comments_area = comm.find_element(By.CSS_SELECTOR, COMMENTS_AREA)
        post_comments = list()
        for _ in range(2):
            self.seeMoreButtons(comments_area)
            self.moreCommentsButtons(comments_area)
            comments_area = comm.find_element(By.CSS_SELECTOR, COMMENTS_AREA)
        comments_list = comments_area.find_element(By.TAG_NAME, "ul")
        comments = comments_list.find_elements(By.TAG_NAME, "li")
        scrapped_comments = 0
        for comment in comments:
            comment_author = ""
            comment_reactions = 0
            if (len(comment.text.splitlines()) > 1):
                self.seeMoreButtons(comment)
                date_component = comment.find_element(By.CLASS_NAME, POST_COMMENT_DATE)
                estimated_date = self.extractCommentEstimatedDate(date_component, date, hour)
                comment_author = comment.text.splitlines()[0]
                try:
                    comment_text = comment.find_element(By.CSS_SELECTOR, POST_COMMENT_TEXT).text
                    comment_text = ' '.join(comment_text.splitlines())
                    comment_text.strip()
                except: comment_text = ""
                try:
                    comment_reactions_component = comment.find_element(By.CSS_SELECTOR, POST_COMMENT_REACTIONS)
                    comment_reactions = self.extractCommentTotalReactions(comment_reactions_component)
                except:
                    pass
                if comment_text == comment_reactions: comment_reactions = 0
                comment_author_link = comment.find_element(By.CSS_SELECTOR, COMMENT_AUTHOR_LINK)
                beautify_data = bs(comment_author_link.get_attribute("href"), 'html.parser')
                with open('./bsC.html',"w", encoding="utf-8") as file:
                    file.write(str(beautify_data.prettify()))
                    time.sleep(0.3)
                with open('./bsC.html',"r", encoding="utf-8") as file:
                    link = str(file.readline())
                    try:
                        id_start = link.index("user") + 5
                        base_post_link = link[0:id_start]
                        user_id = re.match(USER_ID_REGEX, link[id_start:]).group()
                        user_link = base_post_link + str(user_id) + "/"
                    except:
                        diagonal_indexes = [i.start() for i in re.finditer("\/", link)]
                        user_link = "https://facebook.com" + link[diagonal_indexes[2]:diagonal_indexes[3]]
                        user_id = link[diagonal_indexes[2]+1:diagonal_indexes[3]-1]
                hashtags = [x for x in comment_text.split(" ") if "#" in x]
                hashtags = ", ".join([str(h) for h in hashtags])
                scrapped_date = datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+0000"
                post_comments.append({"user_name":comment_author, "user_link":user_link, "user_id":user_id, "post_text":comment_text, "hashtags":hashtags, "reactions":comment_reactions, "estimated_date":estimated_date, 
                                      "type": "reply", "scrapped_date":scrapped_date})
                scrapped_comments += 1
                if scrapped_comments >= 125: return post_comments
        return post_comments

    def extractCommentEstimatedDate(self, date_component, date, hour):
        """This function will calculate the estimated date in which every registered comment was posted"""
        comment_date = ""
        text = re.search(COMMENT_DATE_REGEX, date_component.text).group()
        quantity_time = int(text.split()[0])
        if "año" in text or "y" in text:
            comment_date = (datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")) - datetime.timedelta(quantity_time*365))
            comment_date = comment_date.strftime("%Y-%m-%d")
        elif "sem" in text or "wk" in text:
            comment_date = (datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")) - datetime.timedelta(quantity_time*7))
            comment_date = comment_date.strftime("%Y-%m-%d")
        elif "d" in text:
            comment_date = (datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")) - datetime.timedelta(quantity_time))
            comment_date = comment_date.strftime("%Y-%m-%d")
        elif "h" in text:
            current_hour = datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")).strftime("%H")
            current_hour = int(current_hour)
            if current_hour - quantity_time < 0:
                comment_date = (datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")) - datetime.timedelta(1))
                comment_date = comment_date.strftime("%Y-%m-%d")
            else: comment_date = date 
        elif "min" in text: comment_date = date #falta "m en ingles" y segundos
        else: 
            comment_date = (datetime.datetime.now(tz=pytz.timezone("Etc/GMT+5")) - datetime.timedelta(quantity_time*30))
            comment_date = comment_date.strftime("%Y-%m-%d")
        return comment_date + " " + hour + ":00.0"

    def writeCSVFirstRows(self):
        """This function will emulate the first 7 rows from a BW file, later to be uploaded to Netai"""
        self.metadata = [self.group_name, self.from_date, self.to_date, self.group_name, self.group_name]
        commas = [","]
        top_row = sorted(commas*(len(CSV_COLUMNS)-2)) 
        top_row = "".join([str(c) for c in top_row]) + '\n'
        top_rows = []
        for row in range(len(self.metadata)):
            top_rows.append(CSV_METADATA[row]+","+self.metadata[row] + '\n')#+","+top_row
        publications = self.JSONToCSV()
        with open("./sampleNewFlow.csv", "w", encoding='utf-8', newline='') as file:
            for line in top_rows:
                file.write(line)
            file.write('\n') #"".join([str(c) for c in [","]*(len(CSV_COLUMNS))]) + 
            publications.to_csv(file, index=False)
        
    def JSONToCSV(self):
        publications = pd.DataFrame(columns=CSV_COLUMNS)
        json_file = open("./sampleNewFlow.json", encoding="utf-8")
        json_info = json.load(json_file)
        for publication in json_info:
            post_id = publication["post_id"]
            post_link = publication["post_link"]
            date = publication["date"] + " " + publication["hour"] + ":00.0"
            comments = publication["total_comments"]
            shares = publication["shares"]
            data = [post_id, date, post_link, comments, shares]
            self.extractInfoFromJSON(publication, publications, data)
            if publication["comments"] != []:
                for comment in publication["comments"]:
                    data = [post_id, comment["estimated_date"], post_link, 0, 0]
                    self.extractInfoFromJSON(comment, publications, data)
        return publications
    
    def extractInfoFromJSON(self, publication, publications, json_data):
        default_row = default_row = [""]*(len(CSV_COLUMNS))
        publications.loc[publications.shape[0]] = default_row
        row = int(publications.shape[0])-1
        publications.iloc[row, CSV_COLUMNS.index("Query Id")] = "2000882456"#(json_data[0])
        publications.iloc[row, CSV_COLUMNS.index("Query Name")] = self.group_name
        publications.iloc[row, CSV_COLUMNS.index("Date")] = json_data[1]
        if len(publication["post_text"])> 280: publications.iloc[row, CSV_COLUMNS.index("Title")] = publication["post_text"][0:277] + "..."
        else: publications.iloc[row, CSV_COLUMNS.index("Title")] = publication["post_text"]    
        publications.iloc[row, [CSV_COLUMNS.index("Url"), CSV_COLUMNS.index("Original Url")]] = json_data[2]
        publications.iloc[row, CSV_COLUMNS.index("Domain")] = "twitter.com"
        publications.iloc[row, [CSV_COLUMNS.index("Page Type")]] = "twitter"
        publications.iloc[row, CSV_COLUMNS.index("Account Type")] = "individual"
        publications.iloc[row, [CSV_COLUMNS.index("Added"), CSV_COLUMNS.index("Updated")]] = publication["scrapped_date"]
        publications.iloc[row, CSV_COLUMNS.index("Author")] = publication["user_name"].replace(" ","")
        publications.iloc[row, [CSV_COLUMNS.index("Mentioned Authors")]] = "@"+publication["user_name"].replace(" ","")
        publications.iloc[row, [CSV_COLUMNS.index("Full Name")]] = publication["user_name"].replace(" ","") + " ({0})".format(publication["user_name"].replace(" ",""))
        #publications.iloc[row, CSV_COLUMNS.index("Avatar")] = publication["user_link"]
        publications.iloc[row, [CSV_COLUMNS.index("Facebook Author ID"), CSV_COLUMNS.index("Twitter Author ID")]] = publication["user_id"]
        publications.iloc[row, CSV_COLUMNS.index("Facebook Comments")] = json_data[3]
        publications.iloc[row, [CSV_COLUMNS.index("Facebook Likes")]] = publication["reactions"]
        publications.iloc[row, [CSV_COLUMNS.index("Facebook Shares"), CSV_COLUMNS.index("Twitter Retweets")]] = json_data[4]
        publications.iloc[row, CSV_COLUMNS.index("Full Text")] = publication["post_text"]
        publications.iloc[row, CSV_COLUMNS.index("Hashtags")] = publication["hashtags"]
        if publication["type"] == "reply": 
            publications.iloc[row, CSV_COLUMNS.index("Thread Author")] = publication["user_name"].replace(" ","")
            publications.iloc[row, CSV_COLUMNS.index("Thread Created Date")] =  publication["scrapped_date"]
            publications.iloc[row, CSV_COLUMNS.index("Thread Entry Type")] =  "reply"
        else: publications.iloc[row, CSV_COLUMNS.index("Thread Entry Type")] = "post"
        publications.iloc[row, [CSV_COLUMNS.index("Reach (new)")]] = int(publication["reactions"]) + int(json_data[3]) + int(json_data[4])
        publications.iloc[row, [CSV_COLUMNS.index("Page Type Name")]] = "Twitter"""

    def unifyingFunction(self):
        """Unique function to be executed in order for the scrapper to work"""
        self.login()
        startTime = time.time()
        self.getToGroup()
        self.writeCSVFirstRows()
        print("El tiempo transcurrido para este ejercicio fue de: ", round((time.time() - startTime), 2), " segundos")
        BROWSER.close()
        os.remove("./bs.html")
        os.remove("./bsC.html")
        sys.exit()

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

scrapper_instance = FacebookScrapper()
scrapper_instance.unifyingFunction()


