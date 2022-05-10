from selenium.webdriver.chrome.options import Options
from selenium import webdriver

#Browser Configuration
OPTION = Options()
OPTION.add_argument("--disable-infobars")
OPTION.add_argument("start-maximized")
OPTION.add_argument("--disable-extensions")
OPTION.add_argument("--disable-notifications")
OPTION.add_argument("--log-level=3")
OPTION.add_argument("--headless")
BROWSER = webdriver.Chrome(executable_path="./chromedriver", options=OPTION)

TEST_GROUP = "https://www.facebook.com/groups/1405665609742213"

PAID_PARTNERSHIPS_WORDS = ["Paid", "partnership", "Colaboracion", "pagada"]
SHARE_COMPONENT_WORDS = ["share", "compartido"]
COMMENT_COMPONENT_WORDS = ["comentario", "comment"]
ALL_COMMENTS_SELECTION = ["Todos los comentarios", "All comments"]
SEE_MORE_BUTTONS_TEXT = ["Ver más", "See more"]
MORE_COMMENTS_TEXTS = ["respuetas anteriores", "respuesta anterior", "respueta", "anterior", "previous answers", "previous answer", "previous", "answer", "comentarios más", "más", "respuestas", "answers"] 
CURRENT_POSTS_TEXTS = ["Actividad más reciente", "Newest Activity"]
NEWEST_POST_TEXTS = ["Publicaciones nuevas", "New Posts"]
PLAY_VIDEO_TEXTS = ["Play Video", "Reproducir video"]

POST_ID_REGEX = "[0-9]{15,18}"
USER_ID_REGEX = "[0-9]{6,18}"
DATE_DAY_REGEX = "[0-9]{1,2}"
DATE_YEAR_REGEX = "[0-9]{4,4}"
HOUR_REGEX = "[0-9]{1,2}:[0-9]{2,2}"
COMMENT_DATE_REGEX = "[0-9]{1,2}\s[a-zñ]{1,3}"

MONTHS_DICTONARY = {
    "January/Enero":"01",
    "February/Febrero":"02",
    "March/Marzo":"03",
    "April/Abril":"04",
    "May/Mayo":"05",
    "June/Junio": "06",
    "July/Julio":"07",
    "August/Agosto":"08",
    "September/Septiembre":"09",
    "October/Octubre":"10",
    "November/Noviembre":"11",
    "December/Diciembre":"12",
}