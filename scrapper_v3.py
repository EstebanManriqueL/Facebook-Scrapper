from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import time
import datetime
import json
import re
import sys
import random
from constants import *

recovered_posts = 0
posts_selenium_ids = set()

def read_credentials():
    """Set Facebook Credentials"""
    with open("./credentials.txt") as file:
        user = file.readline().split('"')
        user = user[0][0:len(user[0])-1]
        password = file.readline().split('"')[0]
    return(user, password)

def login():
    """Login with Credentials"""
    user, password = read_credentials()
    BROWSER.get("http://facebook.com")
    BROWSER.maximize_window()
    BROWSER.find_element(By.NAME, "email").send_keys(user)
    time.sleep(2)
    BROWSER.find_element(By.NAME, "pass").send_keys(password)
    time.sleep(1)
    BROWSER.find_element(By.NAME, "login").click()
    time.sleep(5)
    print("Inicio de sesión exitoso")

def seeMoreButtons(comm):
    """Auxiliary function to search See more buttons"""
    buttons = comm.find_elements(By.CSS_SELECTOR, "div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gpro0wi8.oo9gr5id.lrazzd5p")
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

def moreCommentsButtons(comments_area):
    """Auxiliary function to search and click for all buttons used to display more comments"""
    while True:
        #Evitar clicks en videos
        more_comments_buttons = comments_area.find_elements(By.CSS_SELECTOR, "div.oajrlxb2.g5ia77u1.mtkw9kbi.tlpljxtp.qensuy8j.ppp5ayq2.goun2846.ccm00jje.s44p3ltw.mk2mc5f4.rt8b4zig.n8ej3o3l.agehan2d.sk4xxmp2.rq0escxv.nhd2j8a9.mg4g778l.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.tgvbjcpo.hpfvmrgz.jb3vyjys.qt6c0cv9.a8nywdso.l9j0dhe7.i1ao9s8h.esuyzwwr.f1sip0of.du4w35lb.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.pq6dq46d.btwxx1t3.abiwlrkh.lzcic4wl.bp9cbjyn.m9osqain.buofh1pr.g5gj957u.p8fzw8mz.gpro0wi8")
        if more_comments_buttons == None: return
        if len(more_comments_buttons) == 0:
            return
        for button in more_comments_buttons:
            if any(word in button.text for word in MORE_COMMENTS_TEXTS):
                ActionChains(BROWSER).move_to_element(button).click().perform()
                time.sleep(0.5)

def newestPosts():
    """Auxiliary function to configure FB's group to order posts based on publication date (descending order)"""
    newest_posts_possible_buttons = BROWSER.find_elements(By.CSS_SELECTOR, "div.oajrlxb2.gs1a9yip.g5ia77u1.mtkw9kbi.tlpljxtp.qensuy8j.ppp5ayq2.goun2846.ccm00jje.s44p3ltw.mk2mc5f4.rt8b4zig.n8ej3o3l.agehan2d.sk4xxmp2.rq0escxv.nhd2j8a9.mg4g778l.pfnyh3mw.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.tgvbjcpo.hpfvmrgz.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.l9j0dhe7.i1ao9s8h.esuyzwwr.f1sip0of.du4w35lb.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.pq6dq46d.btwxx1t3.abiwlrkh.p8dawk7l.lzcic4wl")
    if len(newest_posts_possible_buttons) > 0:
        for button in newest_posts_possible_buttons:
            if button.text in CURRENT_POSTS_TEXTS:
                ActionChains(BROWSER).move_to_element(button).click().perform()
                time.sleep(2)
                comments_options = BROWSER.find_elements(By.CSS_SELECTOR, "div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.p7hjln8o.esuyzwwr.f1sip0of.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.abiwlrkh.p8dawk7l.lzcic4wl.dwo3fsh8.rq0escxv.nhd2j8a9.j83agx80.btwxx1t3.pfnyh3mw.opuu4ng7.kj2yoqh6.kvgmc6g5.oygrvhab.pybr56ya.dflh9lhu.f10w8fjw.scb9dxdr.l9j0dhe7.i1ao9s8h.du4w35lb")
                for option in comments_options:
                    text = [x for x in NEWEST_POST_TEXTS if x in option.text]
                    if text != []:
                        ActionChains(BROWSER).move_to_element(option).click().perform()
                        time.sleep(2)
                        return

def createJSON(info):
    """Creates JSON file to dump scrapped data"""
    with open("sampleNewFlow.json", "w", encoding="utf-8") as outfile:
        outfile.write(info)

def writeInJSON(post_info):
    """Write new post information in JSON file"""
    with open("sampleNewFlow.json", "r+", encoding="utf-8") as outfile:
        existing_data = json.load(outfile)
        existing_data.append(post_info)
        outfile.seek(0)
        json.dump(existing_data, outfile, indent=4, ensure_ascii=False)
        time.sleep(0.3)

def scrollDown(groupPageLength):
    """Scroll down in the group's page"""
    scrollCount = -1
    match = False
    while not match:
        getPosts(scrollCount)
        time.sleep(random.randint(2,4))
        scrollCount += 1
        BROWSER.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if scrollCount == groupPageLength:
            match = True

def getToGroup():
    """Obtain html/raw information"""
    BROWSER.get(TEST_GROUP)
    time.sleep(5)
    newestPosts()
    groupPageLength = BROWSER.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    
    scrollDown(1)

def getPosts(scrollCount):
    """Identify posts HTML elements"""
    posts = BROWSER.find_elements(By.CLASS_NAME, "du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0")
    global recovered_posts
    for post in posts:
        if post.id not in posts_selenium_ids:
            seeMoreButtons(post)
            post_object = list()
            posts_selenium_ids.add(post.id)
            ActionChains(BROWSER).move_to_element(post).perform()
            post_link, post_id, date, hour = extractPostLinkId(post)
            user_name, user_link, user_id = extractPostUser(post)
            post_message = getPostMessage(post)
            reactions, shares = extractReactionTotalAndShares(post)
            total_comments, comments = extractTotalComments(post)
            scrapped_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
            post_info = {"post_text":post_message, "post_link":post_link, "post_id":post_id, "user_name":user_name, "user_link":user_link, "user_id":user_id, 
                "date":date, "hour":hour, "reactions":reactions, "total_comments":total_comments, "shares":shares, "comments":comments, "scrapped_date":scrapped_date}
            post_object.append(post_info)
            if scrollCount != -1:
                writeInJSON(post_info)
            else: #In case JSON file is Empty
                post_info = json.dumps(post_object, indent=4, ensure_ascii=False)
                createJSON(post_info)
            recovered_posts += 1
            print('Se han recuperado {0} posts'.format(recovered_posts))

def getPostMessage(comm):
    """Obtain message contained in the group's post"""
    texts = comm.find_elements(By.CLASS_NAME, "d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.lr9zc1uh.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d3f4x2em.iv3no6db.jq4qci2q.a3bd9o3v.b1v8xokw.oo9gr5id.hzawbc8m")
    texts = texts + comm.find_elements(By.XPATH, ".//div[@class='hv4rvrfc dati1w0a jb3vyjys qt6c0cv9']")
    texts = texts + comm.find_elements(By.XPATH, ".//div[@class='ll8tlv6m j83agx80 jifvfom9 l9j0dhe7 k4urcfbm']")
    texts_temp = comm.find_elements(By.CSS_SELECTOR, "span.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.lr9zc1uh.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d3f4x2em.iv3no6db.jq4qci2q.a3bd9o3v.b1v8xokw.oo9gr5id")
    for text in texts_temp:
        parent_text = text.find_element(By.XPATH, "..")
        if parent_text.get_attribute("class") != "ecm0bbzt e5nlhep0 a8c37x1j":
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
    final_text = ''.join(final_text.splitlines())
    final_text.strip()
    return final_text[:-1]

def extractPostLinkId(comm):
    """Obtain post link and id"""
    link_elements = comm.find_elements(By.CLASS_NAME, "oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw")
    if link_elements:
        index = 0
        true_date = False
        while not true_date:
            date_element = link_elements[index]
            if not any(word in date_element.text for word in PAID_PARTNERSHIPS_WORDS):
                ActionChains(BROWSER).move_to_element(date_element).perform()
                time.sleep(random.randint(3,4))
                try:      
                    date_html_component = BROWSER.find_element(By.CSS_SELECTOR, "div.j34wkznp.qp9yad78.pmk7jnqg.kr520xx4.hzruof5a")
                except:
                    pass
                try:
                    BROWSER.execute_script("window.scrollBy(0, -40);")
                    ActionChains(BROWSER).move_to_element(date_element).perform()
                    time.sleep(2)
                    date_html_component = BROWSER.find_element(By.CSS_SELECTOR, "div.j34wkznp.qp9yad78.pmk7jnqg.kr520xx4.hzruof5a")
                except:
                    BROWSER.execute_script("window.scrollBy(0, -100);")
                    ActionChains(BROWSER).move_to_element(date_element).perform()
                    time.sleep(2)
                    date_html_component = BROWSER.find_element(By.CSS_SELECTOR, "div.j34wkznp.qp9yad78.pmk7jnqg.kr520xx4.hzruof5a")
                    
                date, hour = extractPostDateHour(str(date_html_component.text))
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

def extractPostUser(comm):
    """Extract post creator user information"""
    user_element = comm.find_element(By.CLASS_NAME, "d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.lr9zc1uh.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d3f4x2em.iv3no6db.jq4qci2q.a3bd9o3v.b1v8xokw.m9osqain.hzawbc8m")
    if user_element:
        user_element = user_element.find_element(By.CLASS_NAME, "oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gpro0wi8.oo9gr5id.lrazzd5p")
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

def extractPostDateHour(comm):
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
                    return day + "/" + MONTHS_DICTONARY[month] + "/" + year, hour
    except Exception: return "01/01/1999", "00:00"

def extractReactionTotalAndShares(comm):
    """Extract post's total reactions and shares"""
    total_reactions = 0
    total_shares = 0
    try:
        data_bar = comm.find_element(By.CSS_SELECTOR, "div.bp9cbjyn.m9osqain.j83agx80.jq4qci2q.bkfpd7mw.a3bd9o3v.kvgmc6g5.wkznzc2l.oygrvhab.dhix69tm.jktsbyx5.rz4wbd8a.osnr6wyh.a8nywdso.s1tcr66n")
    except: return total_reactions, total_shares
    try:
        reactions_component = data_bar.find_element(By.CSS_SELECTOR, "div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.l9j0dhe7.abiwlrkh.p8dawk7l.lzcic4wl.gmql0nx0.ce9h75a5.ni8dbmo4.stjgntxs.a8c37x1j")
        total_reactions = reactions_component.text.split()
        total_reactions = int(total_reactions[0])
    except:
        pass
    possible_shares_components = data_bar.find_elements(By.CSS_SELECTOR, "div.gtad4xkn")
    shares_component = ""
    for possible_share_component in possible_shares_components:
        if any(word in possible_share_component.text for word in SHARE_COMPONENT_WORDS):
            shares_component = possible_share_component
            break
    if shares_component == "":
        pass
    else: 
        total_shares = shares_component.text.split()
        total_shares = int(total_shares[0])
    return total_reactions, total_shares

def extractTotalComments(comm):
    """Extract total amount of comments, as well as its information"""
    total_comments = 0
    comments = []
    try:
        data_bar = comm.find_element(By.CSS_SELECTOR, "div.bp9cbjyn.m9osqain.j83agx80.jq4qci2q.bkfpd7mw.a3bd9o3v.kvgmc6g5.wkznzc2l.oygrvhab.dhix69tm.jktsbyx5.rz4wbd8a.osnr6wyh.a8nywdso.s1tcr66n")
    except: return total_comments, comments
    possible_commments_components = data_bar.find_elements(By.CSS_SELECTOR, "div.gtad4xkn")
    comments_component = None
    for possible_comment_component in possible_commments_components:
        if any(word in possible_comment_component.text for word in COMMENT_COMPONENT_WORDS):
            comments_component = possible_comment_component
            break
    if comments_component == None: pass
    else:
        total_comments = comments_component.text.split()
        total_comments = int(total_comments[0])
    if total_comments > 100:
        pass
    elif total_comments > 0 and total_comments < 100:
        defineAllComments(comm)
        time.sleep(1)
        comments = extractPostComments(comm)
    return total_comments, comments

def defineAllComments(comm):
    """Auxilairy function to make sure All Comments mode is activated"""
    try:
        comment_list_buttons = comm.find_elements(By.CSS_SELECTOR, "div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.l9j0dhe7.abiwlrkh.p8dawk7l.lzcic4wl")
        comment_list_button = [x for x in comment_list_buttons if x.get_attribute("aria-label") not in PLAY_VIDEO_TEXTS]
        if comment_list_button[0].text not in ALL_COMMENTS_SELECTION:
            ActionChains(BROWSER).move_to_element(comment_list_button[0]).click().perform()
            time.sleep(random.randint(1,2))
            possible_comment_showing_options = BROWSER.find_elements(By.CSS_SELECTOR, "div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.p7hjln8o.esuyzwwr.f1sip0of.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.abiwlrkh.p8dawk7l.lzcic4wl.dwo3fsh8.rq0escxv.nhd2j8a9.j83agx80.btwxx1t3.pfnyh3mw.opuu4ng7.kj2yoqh6.kvgmc6g5.oygrvhab.pybr56ya.dflh9lhu.f10w8fjw.scb9dxdr.l9j0dhe7.i1ao9s8h.du4w35lb.bp9cbjyn")
            for option in possible_comment_showing_options:
                all_comments_text = [x for x in ALL_COMMENTS_SELECTION if x in option.text]
                if all_comments_text != []:
                    ActionChains(BROWSER).move_to_element(option).click().perform()
                    return
        ActionChains(BROWSER).move_to_element(comment_list_button[0]).click().perform()
    except: pass

def extractPostComments(comm):
    """Function to extract information from comments regarding any post"""
    comments_area = comm.find_element(By.CSS_SELECTOR, "div.cwj9ozl2.tvmbv18p")
    post_comments = list()
    seeMoreButtons(comments_area)
    moreCommentsButtons(comments_area)
    comments_list = comments_area.find_element(By.TAG_NAME, "ul")
    comments = comments_list.find_elements(By.TAG_NAME, "li")
    for comment in comments:
        comment_author = ""
        comment_reactions = 0
        comment_text_components = ""
        if (len(comment.text.splitlines()) > 1):
            comment_author = comment.text.splitlines()[0]
            comment_text_components = comment.text.splitlines()[1:-2]
            try:
                comment_reactions = int(comment_text_components[-1])
            except:
                if len(comment.find_elements(By.CSS_SELECTOR, "div.bp9cbjyn.j83agx80.r9r71o1u.jwdofwj8.n8tt0mok.r8blr3vg.hyh9befq.hn33210v.jkio9rs9.e72ty7fz.qlfml3jp.inkptoze.qmr60zad.hm271qws")) > 0:
                    comment_reactions = 1
                else: pass
            comment_text = ' '.join(comment_text_components)
            post_comments.append({"author":comment_author, "text":comment_text, "reactions":comment_reactions})
    return post_comments

def unifyingFunctions():
    """Unique function to be executed in order for the scrapper to work"""
    login()
    startTime = time.time()
    getToGroup()
    print("El tiempo transcurrido para este ejercicio fue de: ", time.time() - startTime, " segundos")
    #BROWSER.close()
    sys.exit()

unifyingFunctions()