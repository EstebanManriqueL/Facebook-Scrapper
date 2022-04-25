from matplotlib.pyplot import text
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import json
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constants import *

# pip install selenium
# pip install beautifulsoup4

shares_amounts = []
shares_ids = set()
share_bars = []
share_bars_ids = set()
reactions_amounts = []
reactions_amounts_ids = set()

#Set Facebook Credentials
def read_credentials():
    with open("./credentials.txt") as file:
        user = file.readline().split('"')
        user = user[0][0:len(user[0])-1]
        password = file.readline().split('"')[0]
    return(user, password)

def closeChat():
    chat_buttons = BROWSER.find_elements_by_css_selector("div.i09qtzwb.n7fi1qx3.b5wmifdl.hzruof5a.pmk7jnqg.j9ispegn.kr520xx4.c5ndavph.art1omkt.ot9fgl3s.rnr61an3.s45kfl79.emlxlaya.bkmhp75w.spb7xbtv")
    try:
        for button in chat_buttons:
            try:
                if button.get_attribute("aria-label") == "Close chat":
                    ActionChains(BROWSER).move_to_element(button).click().perform()
            except: pass
    except: pass

#Login with Credentials
def login():
    user, password = read_credentials()
    BROWSER.get("http://facebook.com")
    BROWSER.maximize_window()
    BROWSER.find_element_by_name("email").send_keys(user)
    time.sleep(2)
    BROWSER.find_element_by_name("pass").send_keys(password)
    time.sleep(1)
    BROWSER.find_element_by_name('login').click()
    time.sleep(5)

#Auxiliary function to search "See more buttons"
def seeMoreButtons():
    buttons = BROWSER.find_elements_by_css_selector(SEE_MORE_CSS)
    if buttons:
        for button in buttons:
            try:
                move = ActionChains(BROWSER).move_to_element(button)
                move.perform()
                time.sleep(random.randint(1,2))
                if "Message" not in button.text:
                    click = ActionChains(BROWSER).click(button)
                    click.perform()
            except: pass

#Shares and total reactions are scrapped with this function
def sharesAndTotalReactions():
    data_bars = BROWSER.find_elements_by_css_selector("div.bp9cbjyn.m9osqain.j83agx80.jq4qci2q.bkfpd7mw.a3bd9o3v.kvgmc6g5.wkznzc2l.oygrvhab.dhix69tm.jktsbyx5.rz4wbd8a.osnr6wyh.a8nywdso.s1tcr66n")
    sharesAndReactions(data_bars)
    time.sleep(random.randint(2,3))

#Function to obtain number of shares por each post
def sharesAndReactions(share_barss): 
    global shares_amounts
    for share_bar in share_barss:
        closeChat()
        #Obtain share information
        if share_bar.id not in share_bars_ids:
            text_components = share_bar.find_elements_by_css_selector("div.gtad4xkn")
            share_bars_ids.add(share_bar.id)
            shares = -1
            for text_component in text_components:
                time.sleep(1)
                ActionChains(BROWSER).move_to_element(text_component).perform()
                if "share" in text_component.text: 
                    if len(text_component.text.split()) < 3 and len(text_component.text.split()) > 0: 
                        shares_amounts.append(int(text_component.text.split()[0]))
                        shares = int(text_component.text.split()[0])
                    elif len(text_component.text.split()) >= 3:
                        hover = ActionChains(BROWSER).move_to_element(text_component)
                        hover.perform()
                        time.sleep(4)
                        actual_shares = BROWSER.find_element_by_css_selector(".hcukyx3x.tvmbv18p.cxmmr5t8.aahdfvyu")
                        actual_shares = actual_shares.text.split()
                        and_instance = 0
                        for index in range(0,len(actual_shares)):
                            if actual_shares[index] == "and":
                                and_instance = index
                        shares_amounts.append((int(actual_shares[and_instance+1].replace(",",""))))
                        shares = (int(actual_shares[and_instance+1].replace(",","")))
            if shares == -1: shares_amounts.append(0)
        
        #Obtain total reactions information
        reaction_bar = share_bar
        if reaction_bar.id not in reactions_amounts_ids:
            closeChat()
            reactions_amounts_ids.add(reaction_bar.id)
            reactions = -1
            try:
                reaction_bar = reaction_bar.find_element_by_css_selector("div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.l9j0dhe7.abiwlrkh.p8dawk7l.lzcic4wl.gmql0nx0.ce9h75a5.ni8dbmo4.stjgntxs.a8c37x1j")
                BROWSER.execute_script("arguments[0].scrollIntoView(false);", reaction_bar)
                reaction_text = reaction_bar.find_element_by_css_selector("span.pcp91wgn")
                if len(reaction_text.text.split()) < 2 and len(reaction_text.text.split()) > 0:
                    reactions_amounts.append(int(reaction_text.text))
                elif len(reaction_text.text.split()) >= 2:
                    ActionChains(BROWSER).move_to_element(reaction_bar).perform()
                    time.sleep(3)
                    reactions = BROWSER.find_element_by_css_selector(".hcukyx3x.tvmbv18p.cxmmr5t8.aahdfvyu")
                    reactions = reactions.text.split()
                    and_instance = 0
                    for index in range(0,len(reactions)):
                        if reactions[index] == "and":
                            and_instance = index
                    reactions_amounts.append((int(reactions[and_instance+1].replace(",",""))))
            except: 
                reactions_amounts.append(0)

#Scroll down in the group's page
def scrollDown(groupPageLength):
    scrollCount = -1
    match = False
    while not match:
        #Click on all "See more" buttons to get complete post content
        seeMoreButtons()
        time.sleep(random.randint(2,3))
        sharesAndTotalReactions()
        scrollCount += 1
        time.sleep(random.randint(2,4)) #sleep variable 3-6 segundos
        BROWSER.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

        if scrollCount == groupPageLength:
            match = True

#Obtain html/raw information
def getToGroup():
    BROWSER.get(TEST_GROUP)
    time.sleep(5)

    #Get number of scrolls to reach the end of the group
    groupPageLength = BROWSER.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    scrollDown(5)
    try: shares_amounts.remove("-1")
    except: pass
    
    #Get posts dates from hidden components by hovering over component
    dates = BROWSER.find_elements_by_css_selector("a.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw")
    preProcessedDates = []
    BROWSER.execute_script("window.scrollTo(0, 200)")
    time.sleep(2)
    for element in dates:
        if "/bookmarks/" not in element.get_attribute("outerHTML"): 
            ActionChains(BROWSER).move_to_element(element).perform()
            hover = ActionChains(BROWSER).move_to_element(element)
            #hover.perform()
            time.sleep(random.randint(2,3))
            actual_date = BROWSER.find_elements_by_css_selector("div.j34wkznp.qp9yad78.pmk7jnqg.kr520xx4.hzruof5a")
            for act_date in actual_date:
                if "Paid" in act_date.text or "partnership" in act_date.text or "," in act_date.text:
                    preProcessedDates.append(act_date.text)
    sourceData = BROWSER.page_source
    try:
        BROWSER.execute_script("window.scrollTo(0, 200)")
        header = BROWSER.find_element_by_xpath("//div[@class='rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t pfnyh3mw d2edcug0 sj5x9vvc jb3vyjys']")
        header = str(header.get_attribute("outerHTML"))
        dates_to_ignore = header.count("oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw")
    except: dates_to_ignore = 0
    seeMoreButtons()

    beautifyData = bs(sourceData, 'html.parser')
    return beautifyData, preProcessedDates[dates_to_ignore:len(preProcessedDates)-1]

#Obtain message contained in the group's post
def extract_post(comm):
    posts = comm.find_all(attrs={"class":["d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw oo9gr5id hzawbc8m"]})
    posts = posts + comm.find_all("div", attrs={'class':"hv4rvrfc dati1w0a jb3vyjys qt6c0cv9"})
    posts = posts + comm.find_all("div", attrs={'class':"sfj4j7ms pvbba8z0 rqr5e5pd dy7m38rt j7igg4fr"})
    posts_temp = comm.find_all("span", attrs={'class':"d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw oo9gr5id"})
    for p in posts_temp:
        if "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql" not in str(p):
            posts += p
    final_post = ""
    if posts:
        posts_text = []
        for post in posts:
            if post.text not in posts_text:
                posts_text.append(post.text)
        for text in posts_text:
            final_post = final_post + text + " " 
        if final_post != "": return final_post[0:len(final_post)-1]
        else: return ""
    return ""

#Obtain post link and id
def extract_post_link(comm):
    posts = comm.find_all(class_="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw")
    if posts:
        index = 0
        true_date = False
        while not true_date:
            link = posts[index]
            if "Paid" not in link.text and "partnership" not in link.text:
                link = link.get("href")
                true_date = True
            else: index += 1
        diagonal_indexes = [i.start() for i in re.finditer("\/", link)]
        if len(diagonal_indexes) == 7:
            link_id = link[diagonal_indexes[5]+1:diagonal_indexes[6]]
            return link[0:diagonal_indexes[6]+1], link_id
        else:
            link_id = link[diagonal_indexes[4]+1:diagonal_indexes[4]+18]
            return link, link_id 
    else: return "", ""

#Extract post creator user information
def extract_post_user(comm):
    users = comm.find_all(class_="d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw m9osqain hzawbc8m")   
    if users:
        user = users[0]
        user = user.find_all(class_="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p")
        if user:
            user = user[0]
            user_link = user.get("href") 
            diagonal_indexes = [i.start() for i in re.finditer("\/", user_link)]
            user_link = "https://facebook.com" + user_link[0:diagonal_indexes[len(diagonal_indexes)-1]+1]
            diagonal_indexes = [i.start() for i in re.finditer("\/", user_link)]
            user_id = user_link[diagonal_indexes[len(diagonal_indexes)-2]+1:diagonal_indexes[len(diagonal_indexes)-1]]
            user_name = user.find("span").text
            return user_link, user_name, user_id
    return "", "", ""

#Auxiliary function to get dates in adequate format
def extract_formatted_date(comm, date_array_index, dates_array):
    dates = comm.find_all(class_="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw")
    for date in dates:
        if "Paid" in date.text or "partnership" in date.text or "," in date.text:
            dates.remove(date)
    index_modification = len(dates)
    date = dates_array[date_array_index]
    return index_modification, date

#Extract post comments and shares
def extract_post_comments_shares(comm):
    shares = comments = 0
    posts_comments = comm.find_all(class_="bp9cbjyn j83agx80 pfnyh3mw p1ueia1e")
    if posts_comments:
        posts_comments = comm.find_all("div", attrs={"class": "gtad4xkn"})
        for found_class in posts_comments:
            if "share" in found_class.text:
                s_index = found_class.text.index("s")
                shares = found_class.text[0:s_index-1]
            elif "comment" in found_class.text:
                c_index = found_class.text.index("c")
                comments = found_class.text[0:c_index-1]
            else: pass
    return shares, comments #shares, comments

#Extract all types information from the html/raw information
def extractHtml(beautifyData, preProcessedDates):
    posts = []
    with open('./bs.html',"w", encoding="utf-8") as file:
        file.write(str(beautifyData.prettify()))

    html_data = beautifyData.find_all(class_="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0")
    date_array_index = 0
    shares_array_index = 0
    total_reactions_index = 0
    for comm, in html_data:
        message = extract_post(comm)
        link, link_id = extract_post_link(comm)
        user_link_group, user_name, user_id = extract_post_user(comm)
        date_index_increment, date = extract_formatted_date(comm, date_array_index, preProcessedDates)
        date_array_index += date_index_increment
        date, hour = str(date.split()[1]) + "/" + MONTHS_DICTONARY[str(date.split()[2])] + "/" + str(date.split()[3]), str(date.split()[5])
        if len(date) == 9: date = "0" + date 
        if comm.find(class_="bp9cbjyn j83agx80 pfnyh3mw p1ueia1e") is None: shares = 0
        else:
            global shares_amounts 
            shares = shares_amounts[shares_array_index]
            shares_array_index += 1
        global reactions_amounts
        total_reactions = reactions_amounts[total_reactions_index]
        total_reactions_index += 1
        posts.append({"message_text":message, "post_link":link, "post_id":link_id, "user_link_group":user_link_group, "user_name":user_name, "user_id":user_id, "date":date, "hour":hour, "shares":shares, "total_reactions": total_reactions})
        if date_array_index >= len(preProcessedDates) or shares_array_index >= len(shares_amounts) or total_reactions_index >= len(reactions_amounts) : break 

    json_posts = json.dumps(posts, indent=4, ensure_ascii=False)
    with open("sample.json", "w", encoding='utf-8') as outfile:
        outfile.write(json_posts)

#Unique function to be executed in order for the scrapper to work
def unifyingFunctions():
    login()
    html_data, preProcessedDates = getToGroup()
    extractHtml(html_data, preProcessedDates)
    #BROWSER.close()

unifyingFunctions()