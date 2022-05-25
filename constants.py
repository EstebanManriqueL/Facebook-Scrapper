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

TEST_GROUP = "https://www.facebook.com/groups/681316119297894"    #"https://www.facebook.com/groups/1405665609742213" #https://www.facebook.com/groups/681316119297894 #"https://www.facebook.com/groups/bandolerosfrases"

PAID_PARTNERSHIPS_WORDS = ["Paid", "partnership", "Colaboracion", "pagada"]
SHARE_COMPONENT_WORDS = ["share", "compartido"]
COMMENT_COMPONENT_WORDS = ["comentario", "comment"]
ALL_COMMENTS_SELECTION = ["Todos los comentarios", "All comments"]
RELEVANT_COMMENTS_SELECTION = ["Comentarios destacados", "Top Comments"]
SEE_MORE_BUTTONS_TEXT = ["Ver más", "See more"]
MORE_COMMENTS_TEXTS = ["respuetas anteriores", "respuesta anterior", "respueta", "anterior", "previous answers", "previous answer", "previous", "answer", "comentarios más", "más", "respuestas", "answers", "comentarios anteriores", "previous comments"] 
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

CSV_COLUMNS = ['Query Id', 'Query Name', 'Date', 'Title', 'Url', 'Domain', 'Sentiment', 'Page Type', 'Language', 'Country Code', 'Continent Code', 'Continent', 'Country', 'City Code', 'Account Type', 'Added', 'Assignment', 'Author', 'Avatar', 'Category Details', 'Checked', 'City', 'Display URLs', 'Expanded URLs', 'Facebook Author ID', 'Facebook Comments', 'Facebook Likes', 'Facebook Role', 'Facebook Shares', 'Facebook Subtype', 'Full Name', 'Full Text', 'Gender', 'Hashtags', 'Impact', 'Impressions', 'Instagram Comments', 'Instagram Followers', 'Instagram Following', 'Instagram Interactions Count', 'Instagram Likes', 'Instagram Posts', 'Interest', 'Last Assignment Date', 'Latitude', 'Location Name', 'Longitude', 'Media Filter', 'Media URLs', 'Mentioned Authors', 'Original Url', 'Priority', 'Professions', 'Resource Id', 'Short URLs', 'Starred', 'Status', 'Subtype', 'Thread Author', 'Thread Created Date', 'Thread Entry Type', 'Thread Id', 'Thread URL', 'Total Monthly Visitors', 'Twitter Author ID', 'Twitter Channel Role', 'Twitter Followers', 'Twitter Following', 'Twitter Reply Count', 'Twitter Reply to', 'Twitter Retweet of', 'Twitter Retweets', 'Twitter Tweets', 'Twitter Verified', 'Updated', 'Reach (new)', 'Air Type', 'Blog Name', 'Broadcast Media Url', 'Broadcast Type', 'Copyright', 'Engagement Type', 'Is Syndicated', 'Item Review', 'Linkedin Comments', 'Linkedin Engagement', 'Linkedin Impressions', 'Linkedin Likes', 'Linkedin Shares', 'Linkedin Sponsored', 'Linkedin Video Views', 'Page Type Name', 'Parent Blog Name', 'Parent Post Id', 'Pub Type', 'Publisher Sub Type', 'Rating', 'Reddit Author Awardee Karma', 'Reddit Author Awarder Karma', 'Reddit Author Karma', 'Reddit Comments', 'Reddit Score', 'Reddit Score Upvote Ratio', 'Region', 'Region Code', 'Root Blog Name', 'Root Post Id', 'Subreddit', 'Subreddit Subscribers', 'Weblog Title']
CSV_METADATA = ["Report:", "Brand:", "From:", "To:", "Label"]