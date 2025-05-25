
from model.system.manage import BasicConfig, Banner
from service.system.manage import save_site_basic, save_banners


def basic_config_init():
    # Initialize website basic configuration
    basic_config = BasicConfig(
        siteName="GoFilm",
        domain="http://127.0.0.1:3600",
        logo="https://s2.loli.net/2023/12/05/O2SEiUcMx5aWlv4.jpg",
        keyword="在线视频, 免费观影",
        describe="自动采集, 多播放源集成,在线观影网站",
        state=True,
        hint="网站升级中, 暂时无法访问 !!!"
    )
    save_site_basic(basic_config)


def banners_init():
    # Initialize banners
    banners = [
        Banner(id="1", mid=1, name="樱花庄的宠物女孩", year=2020, cName="日韩动漫",
               poster="https://s2.loli.net/2024/02/21/Wt1QDhabdEI7HcL.jpg",
               picture="https://img.bfzypic.com/upload/vod/20230424-43/06e79232a4650aea00f7476356a49847.jpg",
               remark="已完结", sort=1),
        Banner(id="2", mid=2, name="从零开始的异世界生活", year=2020, cName="日韩动漫",
               poster="https://s2.loli.net/2024/02/21/UkpdhIRO12fsy6C.jpg",
               picture="https://img.bfzypic.com/upload/vod/20230424-43/06e79232a4650aea00f7476356a49847.jpg",
               remark="已完结", sort=2),
        Banner(id="3", mid=3, name="五等分的花嫁", year=2020, cName="日韩动漫",
               poster="https://s2.loli.net/2024/02/21/wXJr59Zuv4tcKNp.jpg",
               picture="https://img.bfzypic.com/upload/vod/20230424-43/06e79232a4650aea00f7476356a49847.jpg",
               remark="已完结", sort=3),
        Banner(id="4", mid=4, name="我的青春恋爱物语果然有问题", year=2020, cName="日韩动漫",
               poster="https://s2.loli.net/2024/02/21/oMAGzSliK2YbhRu.jpg",
               picture="https://img.bfzypic.com/upload/vod/20230424-43/06e79232a4650aea00f7476356a49847.jpg",
               remark="已完结", sort=4)
    ]
    save_banners(banners)
