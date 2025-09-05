import json

from dao.collect.MacVodDao import MacVodDao
from model.collect.movie_entity import MovieDetailModel, movie_detail_dao


def test_upsert_movie_detail():
    movie_detail = MovieDetailModel(**json.loads(
        '''
        {
    "id": 100405,
    "cid": 30,
    "pid": 4,
    "name": "药屋少女的呢喃第二季",
    "picture": "https://img.lzzyimg.com/upload/vod/20250110-1/0689b1db97cbd024c93cc0ec7020ac0e.jpg",
    "playFrom": [
        "liangzi",
        "lzm3u8"
    ],
    "DownFrom": "http",
    "playList": [
        [
            {
                "episode": "第01集",
                "link": "https://v.cdnlz22.com/20250110/10929_12be53cc/index.m3u8"
            },
            {
                "episode": "第02集",
                "link": "https://v.cdnlz22.com/20250117/11298_4220b062/index.m3u8"
            },
            {
                "episode": "第03集",
                "link": "https://v.cdnlz22.com/20250124/11693_ba44ed0e/index.m3u8"
            },
            {
                "episode": "第04集",
                "link": "https://v.cdnlz22.com/20250131/11987_e545772c/index.m3u8"
            },
            {
                "episode": "第05集",
                "link": "https://v.cdnlz22.com/20250207/12371_a721eb05/index.m3u8"
            },
            {
                "episode": "第06集",
                "link": "https://v.cdnlz22.com/20250214/12707_4e219845/index.m3u8"
            },
            {
                "episode": "第07集",
                "link": "https://v.cdnlz22.com/20250221/13071_9502100f/index.m3u8"
            },
            {
                "episode": "第08集",
                "link": "https://v.cdnlz22.com/20250228/13403_43b72aad/index.m3u8"
            },
            {
                "episode": "第09集",
                "link": "https://v.cdnlz22.com/20250307/13726_5c39d715/index.m3u8"
            },
            {
                "episode": "第10集",
                "link": "https://v.cdnlz22.com/20250314/14063_d581821e/index.m3u8"
            },
            {
                "episode": "第11集",
                "link": "https://v.cdnlz22.com/20250322/14490_b46651db/index.m3u8"
            },
            {
                "episode": "第12集",
                "link": "https://v.cdnlz22.com/20250328/14798_ef5683a0/index.m3u8"
            },
            {
                "episode": "第13集",
                "link": "https://v.cdnlz22.com/20250404/15127_e9c455e9/index.m3u8"
            },
            {
                "episode": "第14集",
                "link": "https://v.cdnlz22.com/20250411/15468_ad23eecd/index.m3u8"
            },
            {
                "episode": "第15集",
                "link": "https://v.cdnlz22.com/20250419/15800_f920fdce/index.m3u8"
            },
            {
                "episode": "第16集",
                "link": "https://v.cdnlz22.com/20250425/16104_fd99b29b/index.m3u8"
            },
            {
                "episode": "第17集",
                "link": "https://v.cdnlz22.com/20250503/16405_bfce67e1/index.m3u8"
            },
            {
                "episode": "第18集",
                "link": "https://v.cdnlz22.com/20250509/16767_82ec6c42/index.m3u8"
            },
            {
                "episode": "第19集",
                "link": "https://v.cdnlz22.com/20250524/17534_a29f2402/index.m3u8"
            }
        ]
    ],
    "downloadList": [
        [
            {
                "episode": "第01集",
                "link": "https://dow.dowlz17.com/20250110/10929_12be53cc/药屋少女的呢喃第二季01.mp4"
            },
            {
                "episode": "第02集",
                "link": "https://dow.dowlz17.com/20250117/11298_4220b062/药屋少女的呢喃第二季02.mp4"
            },
            {
                "episode": "第03集",
                "link": "https://dow.dowlz17.com/20250124/11693_ba44ed0e/药屋少女的呢喃第二季03.mp4"
            },
            {
                "episode": "第04集",
                "link": "https://dow.dowlz17.com/20250131/11987_e545772c/药屋少女的呢喃第二季04.mp4"
            },
            {
                "episode": "第05集",
                "link": "https://lzdown26.com/20250207/12371_a721eb05/药屋少女的呢喃第二季05.mp4"
            },
            {
                "episode": "第06集",
                "link": "https://lzdown26.com/20250214/12707_4e219845/药屋少女的呢喃第二季06.mp4"
            },
            {
                "episode": "第07集",
                "link": "https://lzdown26.com/20250221/13071_9502100f/药屋少女的呢喃第二季07.mp4"
            },
            {
                "episode": "第08集",
                "link": "https://lzdown26.com/20250228/13403_43b72aad/药屋少女的呢喃第二季08.mp4"
            },
            {
                "episode": "第09集",
                "link": "https://lzdown26.com/20250307/13726_5c39d715/药屋少女的呢喃第二季09.mp4"
            },
            {
                "episode": "第10集",
                "link": "https://lzdown26.com/20250314/14063_d581821e/药屋少女的呢喃第二季10.mp4"
            },
            {
                "episode": "第11集",
                "link": "https://lzdown26.com/20250322/14490_b46651db/药屋少女的呢喃第二季11.mp4"
            },
            {
                "episode": "第12集",
                "link": "https://lzdown26.com/20250328/14798_ef5683a0/药屋少女的呢喃第二季12.mp4"
            },
            {
                "episode": "第13集",
                "link": "https://lzdown26.com/20250404/15127_e9c455e9/药屋少女的呢喃第二季13.mp4"
            },
            {
                "episode": "第14集",
                "link": "https://lzdown26.com/20250411/15468_ad23eecd/药屋少女的呢喃第二季14.mp4"
            },
            {
                "episode": "第15集",
                "link": "https://lzdown26.com/20250419/15800_f920fdce/药屋少女的呢喃第二季15.mp4"
            },
            {
                "episode": "第16集",
                "link": "https://lzdown26.com/20250425/16104_fd99b29b/药屋少女的呢喃第二季16.mp4"
            },
            {
                "episode": "第17集",
                "link": "https://lzdown26.com/20250503/16405_bfce67e1/药屋少女的呢喃第二季17.mp4"
            },
            {
                "episode": "第18集",
                "link": "https://lzdown26.com/20250509/16767_82ec6c42/药屋少女的呢喃第二季18.mp4"
            },
            {
                "episode": "第19集",
                "link": "https://lzdown26.com/20250524/17534_a29f2402/药屋少女的呢喃第二季19.mp4"
            }
        ]
    ],
    "descriptor": {
        "subTitle": "药师少女的独语 第2期 / The Apothecary Diaries season 2",
        "cName": "日韩动漫",
        "enName": "yaowushaonvdenenandierji",
        "initial": "Y",
        "classTag": "动画",
        "actor": "悠木碧,大塚刚央,小西克幸,种崎敦美,石川由依,木野日菜,甲斐田裕子,潘惠美,小清水亚美,七海弘希,齐藤贵美子,家中宏,赤羽根健治,名冢佳织,久野美咲,鹿糠光明,桐本拓哉,岛本须美",
        "director": "长沼范裕,笔坂明规",
        "writer": "长沼范裕",
        "blurb": "　　讲述了从玉叶妃怀孕开始后宫内势力图的变化，重镇、子昌的女儿、楼兰妃、壬氏的生命被威胁的事件，被认为是该事件主谋的翠苓的失踪等。",
        "remarks": "更新至第19集",
        "releaseDate": null,
        "area": "日本",
        "language": "日语",
        "year": "2025",
        "state": "正片",
        "updateTime": "2025-05-24 13:27:46",
        "addTime": 1736524170,
        "dbId": 36829086,
        "dbScore": "0.0",
        "hits": 0,
        "content": "<p>　　讲述了从玉叶妃怀孕开始后宫内势力图的变化，重镇、子昌的女儿、楼兰妃、壬氏的生命被威胁的事件，被认为是该事件主谋的翠苓的失踪等。</p>"
    }
}
        '''
    ))
    movie_detail_dao.upsert(movie_detail)


def test_select_movie_detail():
    vod_id = 100405
    mac_vod = MacVodDao.select_mac_vod(vod_id)
