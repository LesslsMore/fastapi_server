/*
 Navicat Premium Data Transfer

 Source Server         : localhost_5432
 Source Server Type    : PostgreSQL
 Source Server Version : 160008 (160008)
 Source Host           : localhost:5432
 Source Catalog        : film_site_py
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 160008 (160008)
 File Encoding         : 65001

 Date: 08/06/2025 16:38:07
*/


-- ----------------------------
-- Table structure for mac_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."mac_type";
CREATE TABLE "public"."mac_type" (
  "type_name" varchar(60) COLLATE "pg_catalog"."default" NOT NULL,
  "type_en" varchar(60) COLLATE "pg_catalog"."default" NOT NULL,
  "type_sort" int4 NOT NULL,
  "type_mid" int4 NOT NULL,
  "type_pid" int4 NOT NULL,
  "type_status" int4 NOT NULL,
  "type_tpl" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "type_tpl_list" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "type_tpl_detail" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "type_tpl_play" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "type_tpl_down" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "type_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "type_des" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "type_title" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "type_union" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "type_extend" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "type_logo" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "type_pic" varchar(1024) COLLATE "pg_catalog"."default" NOT NULL,
  "type_jumpurl" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "type_id" int4 NOT NULL DEFAULT nextval('mac_type_type_id_seq'::regclass)
)
;

-- ----------------------------
-- Records of mac_type
-- ----------------------------
INSERT INTO "public"."mac_type" VALUES ('分类1', 'fenlei1', 1, 1, 0, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"\u559c\u5267,\u7231\u60c5,\u6050\u6016,\u52a8\u4f5c,\u79d1\u5e7b,\u5267\u60c5,\u6218\u4e89,\u8b66\u532a,\u72af\u7f6a,\u52a8\u753b,\u5947\u5e7b,\u6b66\u4fa0,\u5192\u9669,\u67aa\u6218,\u6050\u6016,\u60ac\u7591,\u60ca\u609a,\u7ecf\u5178,\u9752\u6625,\u6587\u827a,\u5fae\u7535\u5f71,\u53e4\u88c5,\u5386\u53f2,\u8fd0\u52a8,\u519c\u6751,\u513f\u7ae5,\u7f51\u7edc\u7535\u5f71","area":"\u5927\u9646,\u9999\u6e2f,\u53f0\u6e7e,\u7f8e\u56fd,\u6cd5\u56fd,\u82f1\u56fd,\u65e5\u672c,\u97e9\u56fd,\u5fb7\u56fd,\u6cf0\u56fd,\u5370\u5ea6,\u610f\u5927\u5229,\u897f\u73ed\u7259,\u52a0\u62ff\u5927,\u5176\u4ed6","lang":"\u56fd\u8bed,\u82f1\u8bed,\u7ca4\u8bed,\u95fd\u5357\u8bed,\u97e9\u8bed,\u65e5\u8bed,\u6cd5\u8bed,\u5fb7\u8bed,\u5176\u5b83","year":"2018,2017,2016,2015,2014,2013,2012,2011,2010","star":"\u738b\u5b9d\u5f3a,\u9ec4\u6e24,\u5468\u8fc5,\u5468\u51ac\u96e8,\u8303\u51b0\u51b0,\u9648\u5b66\u51ac,\u9648\u4f1f\u9706,\u90ed\u91c7\u6d01,\u9093\u8d85,\u6210\u9f99,\u845b\u4f18,\u6797\u6b63\u82f1,\u5f20\u5bb6\u8f89,\u6881\u671d\u4f1f,\u5f90\u5ce5,\u90d1\u607a,\u5434\u5f66\u7956,\u5218\u5fb7\u534e,\u5468\u661f\u9a70,\u6797\u9752\u971e,\u5468\u6da6\u53d1,\u674e\u8fde\u6770,\u7504\u5b50\u4e39,\u53e4\u5929\u4e50,\u6d2a\u91d1\u5b9d,\u59da\u6668,\u502a\u59ae,\u9ec4\u6653\u660e,\u5f6d\u4e8e\u664f,\u6c64\u552f,\u9648\u5c0f\u6625","director":"\u51af\u5c0f\u521a,\u5f20\u827a\u8c0b,\u5434\u5b87\u68ee,\u9648\u51ef\u6b4c,\u5f90\u514b,\u738b\u5bb6\u536b,\u59dc\u6587,\u5468\u661f\u9a70,\u674e\u5b89","state":"\u6b63\u7247,\u9884\u544a\u7247,\u82b1\u7d6e","version":"\u9ad8\u6e05\u7248,\u5267\u573a\u7248,\u62a2\u5148\u7248,OVA,TV,\u5f71\u9662\u7248"}', '', '', '', 1);
INSERT INTO "public"."mac_type" VALUES ('日韩动漫', 'rihandongman', 2, 1, 0, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"\u53e4\u88c5,\u6218\u4e89,\u9752\u6625\u5076\u50cf,\u559c\u5267,\u5bb6\u5ead,\u72af\u7f6a,\u52a8\u4f5c,\u5947\u5e7b,\u5267\u60c5,\u5386\u53f2,\u7ecf\u5178,\u4e61\u6751,\u60c5\u666f,\u5546\u6218,\u7f51\u5267,\u5176\u4ed6","area":"\u5185\u5730,\u97e9\u56fd,\u9999\u6e2f,\u53f0\u6e7e,\u65e5\u672c,\u7f8e\u56fd,\u6cf0\u56fd,\u82f1\u56fd,\u65b0\u52a0\u5761,\u5176\u4ed6","lang":"\u56fd\u8bed,\u82f1\u8bed,\u7ca4\u8bed,\u95fd\u5357\u8bed,\u97e9\u8bed,\u65e5\u8bed,\u5176\u5b83","year":"2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2006,2005,2004","star":"\u738b\u5b9d\u5f3a,\u80e1\u6b4c,\u970d\u5efa\u534e,\u8d75\u4e3d\u9896,\u5218\u6d9b,\u5218\u8bd7\u8bd7,\u9648\u4f1f\u9706,\u5434\u5947\u9686,\u9646\u6bc5,\u5510\u5ae3,\u5173\u6653\u5f64,\u5b59\u4fea,\u674e\u6613\u5cf0,\u5f20\u7ff0,\u674e\u6668,\u8303\u51b0\u51b0,\u6797\u5fc3\u5982,\u6587\u7ae0,\u9a6c\u4f0a\u740d,\u4f5f\u5927\u4e3a,\u5b59\u7ea2\u96f7,\u9648\u5efa\u658c,\u674e\u5c0f\u7490","director":"\u5f20\u7eaa\u4e2d,\u674e\u5c11\u7ea2,\u5218\u6c5f,\u5b54\u7b19,\u5f20\u9ece,\u5eb7\u6d2a\u96f7,\u9ad8\u5e0c\u5e0c,\u80e1\u73ab,\u8d75\u5b9d\u521a,\u90d1\u6653\u9f99","state":"\u6b63\u7247,\u9884\u544a\u7247,\u82b1\u7d6e","version":"\u9ad8\u6e05\u7248,\u5267\u573a\u7248,\u62a2\u5148\u7248,OVA,TV,\u5f71\u9662\u7248"}', '', '', '', 2);
INSERT INTO "public"."mac_type" VALUES ('分类3', 'fenlei3', 3, 1, 0, 0, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"\u9009\u79c0,\u60c5\u611f,\u8bbf\u8c08,\u64ad\u62a5,\u65c5\u6e38,\u97f3\u4e50,\u7f8e\u98df,\u7eaa\u5b9e,\u66f2\u827a,\u751f\u6d3b,\u6e38\u620f\u4e92\u52a8,\u8d22\u7ecf,\u6c42\u804c","area":"\u5185\u5730,\u6e2f\u53f0,\u65e5\u97e9,\u6b27\u7f8e","lang":"\u56fd\u8bed,\u82f1\u8bed,\u7ca4\u8bed,\u95fd\u5357\u8bed,\u97e9\u8bed,\u65e5\u8bed,\u5176\u5b83","year":"2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2007,2006,2005,2004","star":"\u4f55\u7085,\u6c6a\u6db5,\u8c22\u5a1c,\u5468\u7acb\u6ce2,\u9648\u9c81\u8c6b,\u5b5f\u975e,\u674e\u9759,\u6731\u519b,\u6731\u4e39,\u534e\u5c11,\u90ed\u5fb7\u7eb2,\u6768\u6f9c","director":"","state":"","version":""}', '', '', '', 3);
INSERT INTO "public"."mac_type" VALUES ('动漫', 'dongman', 0, 1, 0, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"\u60c5\u611f,\u79d1\u5e7b,\u70ed\u8840,\u63a8\u7406,\u641e\u7b11,\u5192\u9669,\u841d\u8389,\u6821\u56ed,\u52a8\u4f5c,\u673a\u6218,\u8fd0\u52a8,\u6218\u4e89,\u5c11\u5e74,\u5c11\u5973,\u793e\u4f1a,\u539f\u521b,\u4eb2\u5b50,\u76ca\u667a,\u52b1\u5fd7,\u5176\u4ed6","area":"\u56fd\u4ea7,\u65e5\u672c,\u6b27\u7f8e,\u5176\u4ed6","lang":"\u56fd\u8bed,\u82f1\u8bed,\u7ca4\u8bed,\u95fd\u5357\u8bed,\u97e9\u8bed,\u65e5\u8bed,\u5176\u5b83","year":"2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2007,2006,2005,2004","star":"","director":"","state":"","version":"TV\u7248,\u7535\u5f71\u7248,OVA\u7248,\u771f\u4eba\u7248"}', '', '', '', 4);
INSERT INTO "public"."mac_type" VALUES ('分类5', 'fenlei5', 5, 2, 0, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 5);
INSERT INTO "public"."mac_type" VALUES ('子类2', 'zilei2', 2, 1, 1, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 7);
INSERT INTO "public"."mac_type" VALUES ('里番动漫', 'lifandongman', 0, 1, 0, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 6);
INSERT INTO "public"."mac_type" VALUES ('子类3', 'zilei3', 3, 1, 1, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 8);
INSERT INTO "public"."mac_type" VALUES ('子类4', 'zilei4', 4, 1, 1, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 9);
INSERT INTO "public"."mac_type" VALUES ('子类5', 'zilei5', 5, 1, 1, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 10);
INSERT INTO "public"."mac_type" VALUES ('子类6', 'zilei6', 6, 1, 1, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 11);
INSERT INTO "public"."mac_type" VALUES ('子类7', 'zilei7', 7, 1, 1, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 12);
INSERT INTO "public"."mac_type" VALUES ('子类8', 'zilei8', 1, 1, 2, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 13);
INSERT INTO "public"."mac_type" VALUES ('子类9', 'zilei9', 2, 1, 2, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 14);
INSERT INTO "public"."mac_type" VALUES ('子类10', 'zilei10', 3, 1, 2, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 15);
INSERT INTO "public"."mac_type" VALUES ('子类11', 'zilei11', 4, 1, 2, 1, 'type.html', 'show.html', 'detail.html', 'play.html', 'down.html', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 16);
INSERT INTO "public"."mac_type" VALUES ('子类12', 'zilei12', 1, 2, 5, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 17);
INSERT INTO "public"."mac_type" VALUES ('子类113', 'zilei13', 2, 2, 5, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '', '', '', '', 18);
INSERT INTO "public"."mac_type" VALUES ('日本动漫', 'ribendongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 20);
INSERT INTO "public"."mac_type" VALUES ('海外动漫', 'haiwaidongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 21);
INSERT INTO "public"."mac_type" VALUES ('国产动漫', 'guochandongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 22);
INSERT INTO "public"."mac_type" VALUES ('欧美动漫', 'oumeidongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 23);
INSERT INTO "public"."mac_type" VALUES ('日韩动漫', 'rihandongman', 0, 1, 4, 0, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 24);
INSERT INTO "public"."mac_type" VALUES ('港台动漫', 'gangtaidongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 25);
INSERT INTO "public"."mac_type" VALUES ('有声动漫', 'youshengdongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 26);
INSERT INTO "public"."mac_type" VALUES ('动画片', 'donghuapian', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 27);
INSERT INTO "public"."mac_type" VALUES ('动漫电影', 'dongmandianying', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 28);
INSERT INTO "public"."mac_type" VALUES ('日韩动漫', 'rihandongman', 0, 1, 4, 1, 'type.html', 'show.html', 'detail.html', '', '', '', '', '', '', '{"class":"","area":"","lang":"","year":"","star":"","director":"","state":"","version":""}', '', '', '', 30);

-- ----------------------------
-- Primary Key structure for table mac_type
-- ----------------------------
ALTER TABLE "public"."mac_type" ADD CONSTRAINT "mac_type_pkey" PRIMARY KEY ("type_id");
