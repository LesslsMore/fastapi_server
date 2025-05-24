from datetime import timedelta

# 对外开放API相关配置

# 资源有效期
RESOURCE_EXPIRED = timedelta(days=90)
# 采集时原始数据存储key
ORIGINAL_FILM_DETAIL_KEY = "OriginalResource:FilmDetail:Id%d"
FILM_CLASS_KEY = "OriginalResource:FilmClass"
PLAY_FORM = "gfm3u8"
PLAY_FORM_CLOUD = "gofilm"
PLAY_FORM_ALL = "gofilm$$$gfmu38"
RSS_VERSION = "5.1"