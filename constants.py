from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

#Browser Configuration
OPTION = Options()
OPTION.add_argument("--disable-infobars")
OPTION.add_argument("start-maximized")
OPTION.add_argument("--disable-extensions")
OPTION.add_argument("--disable-notifications")

BROWSER = webdriver.Chrome(executable_path="./chromedriver", options=OPTION)

TEST_GROUP = "https://www.facebook.com/fcbarcelona"

MONTHS_DICTONARY = {
    "January":"01",
    "February":"02",
    "March":"03",
    "April":"04",
    "May":"05",
    "June": "06",
    "July":"07",
    "August":"08",
    "September":"09",
    "October":"10",
    "November":"11",
    "December":"12",
}

SHARES_WORDS = ["share", "shares"]

SEE_MORE_CSS = "div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gpro0wi8.oo9gr5id.lrazzd5p"