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
MOVIE_LIST_INFO_KEY = "MovieList:Cid%d"
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

# MySQL 配置
MYSQL_DSN = "root:root@(localhost:3610)/FilmSite?charset=utf8mb4&parseTime=True&loc=Local"
# MysqlDsn = "root:shv4d4k7@(dbprovider.eu-central-1.clawcloudrun.com:32283)/FilmSite?charset=utf8mb4&parseTime=True&loc=Local"

MYSQL_USER = "root"
MYSQL_PASSWORD = "shv4d4k7"
MYSQL_HOST = "dbprovider.eu-central-1.clawcloudrun.com"
MYSQL_PORT = 32283
MYSQL_DB = "FilmSite"

# MYSQL_USER = "root"
# MYSQL_PASSWORD = "root"
# MYSQL_HOST = "localhost"
# MYSQL_PORT = 3610
# MYSQL_DB = "FilmSite"

# Redis 配置
# REDIS_ADDR = "localhost:3620"
# REDIS_PASSWORD = "root"
# REDIS_DB_NO = 0

REDIS_ADDR = "dbprovider.eu-central-1.clawcloudrun.com:30236"
REDIS_PASSWORD = "t2lz4nb4"
REDIS_DB_NO = 0