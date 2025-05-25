import datetime


# -------------------------System Config-----------------------------------
LISTENER_PORT = "3601"
MAX_GOROUTINE = 10
FILM_PICTURE_UPLOAD_DIR = "./static/upload/gallery"
FILM_PICTURE_URL_PATH = "/upload/pic/poster/"
FILM_PICTURE_ACCESS = "/api/upload/pic/poster/"

# -------------------------Redis Key-----------------------------------
CATEGORY_TREE_KEY = "CategoryTree"
FILM_EXPIRED = datetime.timedelta(days=365*10)
MOVIE_DETAIL_KEY = "MovieDetail:Cid%d:Id%d"
MOVIE_BASIC_INFO_KEY = "MovieBasicInfo:Cid%d:Id%d"
MULTIPLE_SITE_DETAIL = "MultipleSource:%s"
SEARCH_INFO_TEMP = "Search:SearchInfoTemp"
SEARCH_TITLE = "Search:Pid%d:Title"
SEARCH_TAG = "Search:Pid%d:%s"
VIRTUAL_PICTURE_KEY = "VirtualPicture"
MAX_SCAN_COUNT = 300
AUTH_USER_CLAIMS = "UserClaims"

# -------------------------管理后台相关key----------------------------------
FILM_SOURCE_LIST_KEY = "Config:Collect:FilmSource"
MANAGE_CONFIG_EXPIRED = datetime.timedelta(days=365*10)
SITE_CONFIG_BASIC = "SystemConfig:SiteConfig:Basic"
BANNERS_KEY = "SystemConfig:Banners"
FILM_CRONTAB_KEY = "Cron:Task:Film"
DEFAULT_UPDATE_SPEC = "0 */20 * * * ?"
EVERY_WEEK_SPEC = "0 0 4 * * 0"
DEFAULT_UPDATE_TIME = 3

# -------------------------Web API相关redis key-----------------------------------
INDEX_CACHE_KEY = "IndexCache"

# -------------------------Database Connection Params-----------------------------------
SEARCH_TABLE_NAME = "search"
USER_TABLE_NAME = "users"
USER_ID_INITIAL_VAL = 10000
FILE_TABLE_NAME = "files"
FAILURE_RECORD_TABLE_NAME = "failure_records"