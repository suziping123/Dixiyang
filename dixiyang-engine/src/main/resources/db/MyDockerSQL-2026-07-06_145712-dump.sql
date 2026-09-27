/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-12.3.2-MariaDB, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: dixiyang
-- ------------------------------------------------------
-- Server version	5.7.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `app_user`
--

DROP TABLE IF EXISTS `app_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `bg_config` longtext COLLATE utf8mb4_unicode_ci COMMENT '用户背景配置JSON',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_user`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `app_user` WRITE;
/*!40000 ALTER TABLE `app_user` DISABLE KEYS */;
INSERT INTO `app_user` (`id`, `username`, `password`, `nickname`, `email`, `create_time`, `bg_config`) VALUES (1,'admin','$2a$10$8HXhYyBUjUx5zC/OLwyAtOi6Kc/YiHxe//AdpJLBBa2k5pCE0xQiy','admin','suziping123@outlook.com','2026-03-18 16:51:16',NULL),
(2,'Alaa','$2a$10$s//94x00ftwfCalR9Tdnk.vqiCB7/pPEUozQZDXzbUj0oUxoixJoG','张三','suziping123@outlook.com','2026-03-18 18:10:03',NULL),
(3,'11111','$2a$10$s//94x00ftwfCalR9Tdnk.vqiCB7/pPEUozQZDXzbUj0oUxoixJoG','111','suziping123@outlook.com','2026-03-18 18:10:03',NULL),
(4,'admin123','$2a$10$8HXhYyBUjUx5zC/OLwyAtOi6Kc/YiHxe//AdpJLBBa2k5pCE0xQiy','admin123','suziping123@QQ.com','2026-07-01 13:10:44',NULL);
/*!40000 ALTER TABLE `app_user` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `chat_session`
--

DROP TABLE IF EXISTS `chat_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_session` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `novel_id` bigint(20) DEFAULT NULL COMMENT '关联小说ID',
  `session_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会话UUID(由前端生成)',
  `head_path` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '链式JSON头文件路径',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对话标题(首条消息AI生成或截取)',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '会话创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后消息时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_session` (`user_id`,`session_id`) USING BTREE,
  KEY `idx_user_novel` (`user_id`,`novel_id`) USING BTREE,
  KEY `idx_update_time` (`update_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_session`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `chat_session` WRITE;
/*!40000 ALTER TABLE `chat_session` DISABLE KEYS */;
INSERT INTO `chat_session` (`id`, `user_id`, `novel_id`, `session_id`, `head_path`, `title`, `create_time`, `update_time`) VALUES (20,1,2,'62f1b716-fdfb-4841-9117-f4c4d86ffafb',NULL,'陈诚故事方向','2026-06-29 06:03:18','2026-06-29 14:05:19'),
(28,1,55,'c5b28e24-37e9-4d3b-9fd7-a5731be0e7cc','__file__:chat/1/c5b28e24-37e9-4d3b-9fd7-a5731be0e7cc/1782925956112_1535.json','仙蛊虫术体系设计','2026-07-02 01:12:36','2026-07-05 16:14:44'),
(29,1,55,'f283ef6a-e1b9-4981-9120-733ee965659a','__file__:chat/1/f283ef6a-e1b9-4981-9120-733ee965659a/1782974243224_4383.json','蝶衣羽化之术优化','2026-07-02 14:37:23','2026-07-05 16:14:44'),
(31,1,1,'9ea79301-43a4-4417-ae10-d3e27de66c58','__file__:chat/1/9ea79301-43a4-4417-ae10-d3e27de66c58/1783007296544_389.json','测评流程标准化','2026-07-02 23:48:17','2026-07-05 16:14:44'),
(33,1,NULL,'1354deb06b6445d5a399b4d75269a93d',NULL,'新对话','2026-07-05 09:40:42','2026-07-05 09:40:42'),
(34,1,NULL,'7e9db70ecbd24fc59b0995269ca76981',NULL,'新对话','2026-07-05 09:41:01','2026-07-05 09:41:01'),
(35,1,NULL,'98019c880cea41f9b5d8bb71801c7437',NULL,'新对话','2026-07-05 09:41:02','2026-07-05 09:41:02'),
(36,1,55,'89b4cd66a840462cafe6d4c59107bff2','__file__:chat/1/89b4cd66a840462cafe6d4c59107bff2/1783265800132_9ce9aa66.json','角色对话冲突','2026-07-05 09:41:06','2026-07-05 23:36:40'),
(38,1,1,'cb10083f-229c-4313-9b92-1807b42635aa','__file__:chat/1/cb10083f-229c-4313-9b92-1807b42635aa/1783260409189_ece21562.json','测试恢复功能','2026-07-05 14:06:49','2026-07-05 16:16:08'),
(39,1,1,'0a3a46d5-9554-4a46-a97f-923a7de80809','__file__:chat/1/0a3a46d5-9554-4a46-a97f-923a7de80809/1783260432679_edf70d66.json','测试回复限制','2026-07-05 14:07:12','2026-07-05 16:16:08'),
(40,1,1,'ae0ab21c-5c83-4ac5-b8d9-1f21eebac812','__file__:chat/1/ae0ab21c-5c83-4ac5-b8d9-1f21eebac812/1783260502261_3907d95a.json','测试回复生成','2026-07-05 14:07:23','2026-07-05 16:16:08'),
(41,1,1,'2989ad54-0a63-4876-b0fe-cfc91158a538','__file__:chat/1/2989ad54-0a63-4876-b0fe-cfc91158a538/1783300498644_caede83b.json','西装与故乡情','2026-07-05 14:09:34','2026-07-06 09:14:59'),
(42,1,56,'eb18044477ca431c9161d41fda14d0d2','__file__:chat/1/eb18044477ca431c9161d41fda14d0d2/1783318126671_798bd2d2.json','测试消息回复','2026-07-05 15:24:47','2026-07-06 06:08:49'),
(44,1,55,'a7290843-755a-4c81-9ae7-9af456ccc9ef','__file__:chat/1/a7290843-755a-4c81-9ae7-9af456ccc9ef/1783302630048_6355d9db.json','仙虫体系设计','2026-07-05 16:38:02','2026-07-06 10:57:33'),
(45,1,55,'27c55b4a-c37e-46d4-b5fc-dbd7237c16af','__file__:chat/1/27c55b4a-c37e-46d4-b5fc-dbd7237c16af/1783311504954_a5d708c1.json','姐妹私密时刻','2026-07-05 17:06:14','2026-07-06 12:18:26');
/*!40000 ALTER TABLE `chat_session` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `file`
--

DROP TABLE IF EXISTS `file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `file` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `file`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `file` WRITE;
/*!40000 ALTER TABLE `file` DISABLE KEYS */;
/*!40000 ALTER TABLE `file` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `novel`
--

DROP TABLE IF EXISTS `novel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `novel` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pen_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `cover_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_title` (`user_id`,`title`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  CONSTRAINT `fk_novel_user` FOREIGN KEY (`user_id`) REFERENCES `app_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `novel`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `novel` WRITE;
/*!40000 ALTER TABLE `novel` DISABLE KEYS */;
INSERT INTO `novel` (`id`, `user_id`, `title`, `pen_name`, `description`, `cover_url`, `create_time`, `update_time`) VALUES (1,1,'人间一梦','舞江月','多年以后，面对行刑队的枪口，蔡同林会想起那个因错失奖学金而心灰意冷的下午，班长的关切、死党伯越轻哼着匆匆的小曲，去那座隐匿在荒烟蔓草间的古寺。彼时的他尚未知晓，一次随兴的散心之旅，竟会让他们撞破元世界的疮痍，让他踏上一场漫长如梦的奇幻旅途。那是他们命运的开端，亦是终局：这个世界在此时尚未被权利与虚幻完全吞噬，万物未有名号，而这个曾在草丛间渴望未来的少年与单纯的白纸的萍水相逢，最终都将在枪声响起前，于孤独的归途中看清那被欲望写定的宿命。',NULL,'2026-03-19 20:07:33','2026-06-29 09:02:41'),
(2,1,'硅基时代','舞江月','我叫陈诚，一个富安城的汽修工，这行在这个机器人遍地走的年代，没什么前途，于是我只好兼职做……枪支走私，我真没想到我会走到这一步……','preset:silicon-age','2026-03-20 18:58:46','2026-05-31 22:06:38'),
(55,1,'火影：从油女开始的忍界之旅','舞江月','基于火影忍者世界观的小说，记录木叶村从建村到鸣人时代的完整时间线。','/api/uploads/covers/d3fa487ff37e433db6f10817249be0b6.jpg','2026-06-27 05:51:20','2026-07-06 05:24:47'),
(56,1,'纯情蟑螂屎臭臭','舞江月','纯情蟑螂屎臭臭','/api/uploads/covers/6bb666f643e54aa79a1b1ff670856a8b.jpg','2026-07-06 06:02:15','2026-07-06 06:02:15'),
(57,3,'test','111','test','/api/uploads/covers/1743f709ecd9444dbbe63115a419ada0.gif','2026-07-06 06:13:55','2026-07-06 06:13:55');
/*!40000 ALTER TABLE `novel` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `novel_character`
--

DROP TABLE IF EXISTS `novel_character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `novel_character` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `novel_id` bigint(20) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `appearance` text COLLATE utf8mb4_unicode_ci,
  `background` text COLLATE utf8mb4_unicode_ci,
  `personality` text COLLATE utf8mb4_unicode_ci,
  `extra` text COLLATE utf8mb4_unicode_ci COMMENT 'è§’è‰²æ‰©å±•è®¾å®šï¼ˆJSON æˆ–æ–‡ä»¶è·¯å¾„å¼•ç”¨ï¼‰',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_novel_name` (`novel_id`,`name`) USING BTREE,
  KEY `idx_novel_id` (`novel_id`) USING BTREE,
  CONSTRAINT `fk_character_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `novel_character`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `novel_character` WRITE;
/*!40000 ALTER TABLE `novel_character` DISABLE KEYS */;
INSERT INTO `novel_character` (`id`, `novel_id`, `name`, `gender`, `age`, `appearance`, `background`, `personality`, `extra`, `create_time`) VALUES (1,1,'蔡同林','男',17,'有些胖，但经过五天的界外流转探索，已经瘦下来了','父亲（张真司）：大厂高薪程序员;母亲（蔡菜籽）:检察官;六年前母亲死于一场车祸，五年前父亲被裁员，母亲死后父亲变得早出晚归，不知道在忙些什么',NULL,'{}','2026-03-19 20:56:13'),
(3,1,'明','男',5100,'看起来瘦削，但事实上很身体很结实，但这是蒙君的身体，他具体长什么样子已经不可考了。','在这片天地的文明伊始这个四处流浪的弃儿怎么也想不到他会有这么波澜壮阔的一生，游侠时代第一批游侠之一，经历过游侠时代的浪漫、宗门的分化、王朝的建立、梁朝的腐朽。曾目睹理想的堕落，也曾亲身参与过无数战斗、逃亡、背叛。因害怕死亡，通过残破圣器签订契约，开始了不断更换身体的“续命”生涯。每次更换身体都需要吞噬另一个意识——许愿者或实现者，最终总有一个人消失，一个人留下。\n\n他经历过无数契约，吞噬过无数人，也偶尔被反噬过。与蒙君的契约已持续十几年，是时间最长的一次。圣器裁决功能受损导致两人陷入平局，谁也无法彻底吞噬谁。明目前处于“等待”状态——等待蒙君崩溃、等待圣器故障、等待某个意外打破平衡。他不急于获胜，因为他已经等了太久了。\n\n他曾在庆功宴上发现并救了齐莲儿，给她带去了食物，并给她取名“齐莲儿”。','沉稳','__file__:character/3.json','2026-03-23 14:56:34'),
(5,1,'齐莲儿','女',16,'很健康很完美的身材，容貌几乎从任何角度都跳不出毛病来，170的身高在近现代世界不算矮，甚至比绝大多数男性要高','在一个古代修仙世界中，因为经受梁朝动乱影响，在军妓营中出生，母亲是富延城周边小地主家的掌上千金，身材姣好，能说会道，面若朱玉，眼似水波，但被叛军攻破后，母亲被军人掳掠到营中，献给叛军中的军官，但因为母亲的刚烈咬下了军官某个器官，被军官气急败坏地赏给手下士兵，在被侵犯了一整天后果不其然怀孕了生下了她，任何人都不知道她的父亲具体是谁，但此时的母亲也已经完全精神失常，只能在军妓营中苦难度日，她也被军妓营中的大龄军妓抚养长大，看着她的母亲被迫终日接客，最终生下了三个孩子，一个弟弟，两个妹妹；5岁那年在季子舟的军队占领富延城之后混入溃军逃走，但最终被明捡到并抚养,','温婉、坚定、训练有素','{}','2026-03-23 16:37:54'),
(7,2,'陈诚','男',35,'结实，矮壮','当兵，在军队中见识了开山炸洞，战友被炸死','敦厚，但喜欢冒险','{}','2026-03-23 16:37:54'),
(8,2,'低洼','男',10,'低洼','大王','大王','__file__:character/8.json','2026-03-23 16:37:54'),
(9,55,'油女志明','男',16,'白绿色带兜帽冲锋衣常年不离身。浅灰色护目镜的镜片经他亲手改良——单面透光结构（结合仙虫的体系制成），外人看去只见暗色镜面，完全看不到镜片后瞳孔的细微变化（在发现自己觉醒写轮眼后，更是加强了镜片对于红光的单向过滤能力）。护目带在脑后系得随意，总有几缕黑发从中漏出来。脸部线条轮廓清晰，颧骨微高，下颌弧线利落，是不算惊艳但也并不丑陋，看着稍显冷淡，但嘴角略微向下压的习惯让他显得比实际年龄更老成。\n\n十六七岁那阵子身形还有些少年人的单薄178cm，两年后被仙虫查克拉滋养开，肩背厚实了几分，行动间却依然透着油女族人那种“存在感偏低”的沉默气质183cm。因为长期低头观察虫子，脖子略微前倾，走路步子不大，落脚稳当。','穿越者云志明，意识进入一个被“三眼母体”吞噬精神后的油女族婴儿体内，原主人是团藏中年时期的心腹代号为村的油女家族族长油女志茂的二儿子的第四个孩子，前三个姐姐和哥哥因为被志茂给村种下的超剂量仙虫保护住了身体能量的流失（因为原本仙虫会汲取母体和孩子的身体能量，但三眼宇智波的身体能量太香了，所以光顾着吸取三眼宇智波的能量了），却没有抵挡住三眼宇智波也就是母亲写轮眼的吞噬能力，被吞噬了精神，虽暂时未继承额头上的第三只写轮眼，却天生携带极亲和虫子的查克拉，并被种下隐蔽版舌祸根绝之印，被不知内情的团藏因为嫌弃前三个智力有缺的孩子并且也觉得三个实验体够进行写轮眼实验了，还因为志茂对村“催婚”（实际上知道被仙虫寄生后没有生育的希望，所以只是想让“村”回到家族）而把志明给送回去了。\n在根部间谍任务执行完毕后归来的孤儿院教师兼“妈妈”药师堇乃（忍冬）和志茂安排的仆人的抚养下于木叶成长，忍校时期开始展露虫术天赋。经历峡谷虫群隼人与岩忍爆破班同归于尽事件、雷影战中识破四重杀局并协助悠香杀死三代雷影任务，获得“木叶黑潮”称号。\n战后逐步掌控仙虫之力，扎根木叶、调查真相、控制团藏（面对日斩），由真一、大和、卡卡西共管新根部。与悠香关系从忍校互生情愫，在日差替死事件后协助悠香（批量制造在峡谷事件中获得的爆破虫，配合悠香的成名组合技：狮冲咬绝+互乘引爆符（为了防止被发现，所以用的是爆破虫，所以这招严格说来应该叫互乘爆破虫））……','谨慎、好奇心强、沉默寡言，有显著的社恐倾向，在多数社交场合容易结巴。但他习惯于周密计划之后，能表演出截然不同的一面——或许是因为以前作为一名计算机系学生跨考科学技术史研究生时练出来的叙述与伪装能力。嘴笨心软，从不擅长甜言蜜语，却会在凌晨四点泡好豆子、在灶台前守着滤浆。对历史、文化、科学与文学都有浓厚兴趣，有时会盯着生物聚落出神，像在翻阅一本活着的典籍。','__file__:character/9.json','2026-03-23 16:37:54'),
(10,55,'日向悠香','女',16,'黑色长发，常穿白色训练服，外套一件深灰色裙装短褂，左手腕常年缠着绷带（用于掩盖狮冲咬绝留下的经络灼痕）。16岁时167cm，18岁时169cm。后来因为油女志明喜欢，所以时不时会在私下穿高开叉旗袍，搭配不同颜色的丝袜——她不会主动提起这件事。','月光很淡，训练森林里的空气还带着白天的余温。\n\n兔子面具是她在木叶村外的杂货铺买的，花了三十两。她记得那个价格，因为那是她攒了三个月的零用钱——宗家给分家的月例少得可怜，母亲死后就更少了。\n\n她站在那棵老橡树的横枝上，看着对面那个油女家的少年从训练场走出来。\n\n“你比我想象中来得晚。”\n\n志明停下脚步，抬头看向声音传来的方向。月光下，一个戴着兔子面具的人影从树枝上跃下，落地时几乎没有声响。\n\n“你是……”\n\n“打一场。”兔子面具人说，“我听说你今天用火球赢了那场比赛。我要看看你到底是不是真有那么强。”\n\n志明沉默了几息，然后说：“我认识你。”\n\n兔子面具人的动作顿了一瞬。\n\n“学校里……对练课的时候，你的手型……”志明的声音不大，语速也不快，“你不是第一次和我打。”\n\n兔子面具人没有回答。她站了一会儿，然后转身走进了树影里。\n\n志明没有追上去。\n\n但第二天早上，他在自己的课桌上看到一张字条，纸上只有一句话：“下次我会赢回来。”\n\n字迹很工整，但最后一笔拖得有些长，像是写完之后犹豫了一下。\n\n志明把字条收进衣兜里。他没有告诉任何人这件事，也没有问她是谁。\n\n日子照常过。白天的班级里，她坐在他斜后方，他偶尔会在她的方向停驻片刻目光，但她从来没有在白天的时候回应过。\n\n后来，她被刻上了笼中鸟的印记。宗家的仪式在族内进行，分家的孩子不能参加。\n\n第二天她来学校的时候，额头上多了白色的头带。她换到最后一排，坐在窗边。\n\n有人说她“变了”，不是能力变了，而是姿态变了。\n\n志明在午休的时候走到她旁边，递给她一个小布袋。她打开看，里面是一层透明的、几乎看不出厚度的薄膜状物体，触感像是活的，轻轻附着在她的皮肤上。\n\n“变色虫。”志明说，“很扁……能模拟周围环境的颜色。贴上去之后，远处看不太出来。”\n\n她没有立刻回答，手按在额头上，停了一会儿。\n\n“……为什么要给我这个？”\n\n志明没有回答这个问题。他只是说：“你先用着吧。”\n\n她用了。但在试过几次之后，她觉得不舒服。贴在皮肤上的触感，时时刻刻在提醒她“你正在被注视”。她后来告诉志明：“我不需要一直遮着。”\n\n志明点了点头，说：“那就不用。”\n\n她后来才知道，那个动作意味着“他可以接受她不需要伪装的样子”。而在那之后不久，她在一个没有月亮的夜晚去了训练森林，站在那棵老橡树的横枝上，等了很久。\n\n志明来了。\n\n“我知道是你。”他说。\n\n她摘下了面具。\n\n“我是兔子面具人。”\n\n她手里握着的面具，在月光下映出一道浅淡的白色。她没有立刻解释，也不需要解释太多，因为她已经确信眼前的人在她摘下面具之后，仍然会留在原地。这是她逐渐确认的事实之一。后来的许多年里，她持续确认这个事实，并且每次确认的结论都没有改变。','内敛、自尊心强、占有欲强、好胜、行动先于言语。习惯用行动来表达立场，而不是通过语言。不轻易信任别人，但一旦信任就不会轻易撤回。对“被看见”这件事有复杂的感受——她不想被看见（因为被看见意味着被评价、被控制），但她又渴望被一个人真正地看见。','__file__:character/10.json','2026-03-23 16:37:54'),
(11,55,'日向宗太','男',14,'14岁时165cm，16岁168cm，18岁时170cm','日向宗家一位权势很大的长老的的唯一孙子，觊觎悠香的美貌。','好色，权利欲强，控制欲强','{}','2026-06-29 03:57:09'),
(12,55,'秋道次步美','女',16,'深棕色短发，常穿宽松的红色训练服，腰间系有秋道家的纹章腰带。12岁时身高约152cm，体态偏圆润但仍在发育期；17岁时身高约165cm，体型丰满，面部线条开始显出成年女性的轮廓。因为她改良了秋道一族的修炼方法，可以让脂肪储存在自己想要储存地方，甚至可以在战场上依靠这个封印术转移脂肪，防止致命伤。','秋道家的孩子从小就被期望“能吃东西、能长胖、能打”。但作为女生的她拒绝“成为家族标准模板”，她羡慕那些身材姣好的女性她也从未放弃过靠近她们，即便从小她就被喂得胖胖的，长过胖的都知道，长胖并不只是身材的变化，如果你从小就很胖，身体会自动适应你的体重和体态，减肥从来不是下定决心后的事，你能感觉到减肥的时候，你正在与自己为敌，而她从来不想话化茧成蝶，她想要的是像她的名字一样身矫如燕，用曼妙的身姿，自由翱翔在这片天空。\n……\n猪鹿蝶三族联谊赛的最后一场是作为蝶的秋道家的大胃王比赛，她盯着碗里堆成山的食物，没有动筷。族人和父母以及猪鹿另外两家的长辈小孩的议论身此起彼伏。而她脑中似乎只有一根绷紧的弦在颤动的声音，她逃跑了！逃跑并不能解决问题，但似乎这次格外有用……，在火影岩上，晚风胡乱地吹动发丝拍打着四个油女志明、山中真一、奈良鹿野的脸，志明的巧思、鹿野的建议、真一没心没肺的笑脸，为她打开了另外一条——羽化之路。','嘴硬，要强，行动力强，习惯用自己的方式解决问题。是真一眼中的“暴力女”\n对“被期待”这件事有强烈的排斥感。她认为秋道家“只有增肥这一条路”的叙述是错误的。\n说话直接，有时显得很冲。但她冲的时候通常是在保护自己，或者保护她认为需要保护的人。','__file__:character/12.json','2026-03-23 16:37:54'),
(13,55,'山中真一','男',16,'棕色短发，略带卷曲，常穿山中家的灰绿色训练服，但衣角和袖口常有颜料痕迹。手指和指甲缝里有洗不掉的颜料残留。12岁时身高约155cm，身形偏瘦，站姿松散，但画画时会突然坐直。13岁时身高约158cm。','','','__file__:character/13.json','2026-07-03 06:50:48'),
(14,1,'季子舟（落魄还乡）','男',24,'身高约180cm，因长期穿布鞋，看起来比实际身高稍矮。身形挺拔匀称，肩宽腰窄，是天然的衣架子，穿短打、长衫、元服都很精神。手指修长，掌心与指节处生有厚茧，部分茧子因长期接触水而泛白、起皮。皮肤因常年户外奔走，呈浅麦色。五官轮廓分明，眉骨较高，眼神沉静，平时不笑时略显得冷淡，但嘴型微微上扬，带一种天然的温和。三川道口音，说话时尾音略拖。头发平常束得利落，偶尔有碎发垂落。','三川道小地主季伯仲之子。季伯仲早年当兵，退伍后倒买倒卖、放贷营生，因放贷逼死了自己的亲弟弟和亲妹妹（即季子舟的叔姑），季子舟知情后与其父关系彻底断裂。\n\n幼时在程都府随舅舅学习纺织、缝纫、剪裁，与管家的女儿孙文慧同窗数年，两人自小相识，情谊深厚，但季子舟待她如妹妹，并未产生男女之情。\n\n少年时在程都府读了许多书，舅舅为他取名“子舟”，寄望他如舟般能够远行。父亲季伯仲不喜他读书，希望他回乡练武、从商、守业，断其零用钱。赴京赶考的盘缠由在程都府当差的舅舅资助。\n\n到京城后，入新式学堂，成绩优异，恩师为自强派自动化大师。因恩师卷入大皇子一系的派系斗争，季子舟受牵连，毕业后未被重用，被发配至铎天司做底层工人。期间与何家嫡长女何玉琢相识并恋爱，后元界助教出现，何玉琢选择与助教在一起，两人分手。\n\n大皇子倒台后，二皇子裁撤铎天司，季子舟失业，被迫返回三川道。回家后父亲季伯仲与母亲田氏强行安排他与孙文慧成亲，季子舟不愿，但未反抗。洞房夜，孙文慧看出他不想结，两人共同逃婚，离开三川道。','好读书，尤喜琢磨事理，对底层人有天然的亲近与敬佩。\n\n温和但不软弱，有自己的判断，不轻易受人左右。\n\n不与父亲正面冲突，但一旦做出选择便不再回头。\n\n对在意的人（如孙文慧）有种近乎固执的“不回应”——他知道她的心意，但从不主动回应，也不切断联系。\n\n有手艺人的耐心和实际操作能力，善于用行动代替言语。\n\n内心有很深的自卑，这种自卑不是源于出身，而是源于“自己始终无法成为父亲期望的样子”，以及“曾经输给了元界助教那样的存在”。','__file__:character/14.json','2026-07-05 13:36:06'),
(15,1,'甲落（亦可写作贾洛，随父亲姓时）','男',16,'个子比同龄人矮小。肤色苍白，常随意扎着或散落。眼睛在脸上占比小，瞳孔颜色偏浅，指甲边缘常有倒刺。','祭祀族后裔。祭祀族曾是元界原住民中的一支，因诅咒“疾病=力量”而被元界殖民者圈养、实验、清洗。甲落是该族幸存者之一，自幼在元界底层长大，与母亲生活。母亲拥有某种“不被发现”的能力，但在甲落成长过程中家庭逐渐不和睦，母亲保护失效。父亲是底层平民，与甲落关系疏远。\n\n甲落从小患有多种病症——认知障碍、幽闭恐惧、皮肤病等，这些疾病同时也是他能力的来源。他无意识地运用认知扭曲能力，创造出幻觉实体以缓解病痛与孤独。他身边存在“清水正义医生”（实际是一窝老鼠/死鼠）和“妹妹”（实际是一窝鸟/死鸟），但他本人无法意识到这些是他自己创造的，只能模糊感觉到“有些人与其他人不同”。\n\n他不了解自己的出身，也不清楚自己的能力。元界宣传机器与自身底层处境之间的矛盾，使他在成长过程中不断进行认知上的自我篡改：将“我和别人不一样”扭曲为“我和别人一样”。追捕、霸凌、母亲的离开，都被他的能力逐渐合理化。随着病情恶化，他的能力在增强，但寿命也在加速缩短。\n\n他不知道自己是祭祀族幸存者，不知道自己被面组织盯上，不知道自己是一颗潜在的炸弹。他只是活着，和自己的医生与妹妹一起。','自卑且内向，习惯性回避他人目光。\n\n对外界信任度低，但对“清水医生”和“妹妹”有完全的依赖。\n\n性情温和，几乎没有攻击性。即使能力本质上是极强的认知扭曲和暗影系力量，他也从未主动用于伤害任何人。\n\n有强烈的“被人需要”的需求——他需要照顾妹妹、被医生治疗，这些虚构的关系是他维持生存的锚点。\n\n在正常交流中显得迟钝、走神、反应偏慢，但在自己的认知世界里他有完整的逻辑系统。\n\n潜意识里极其恐惧“被发现”——他分不清什么是真实的，但他隐约知道，“真相”会摧毁他所拥有的一切。','__file__:character/15.json','2026-07-05 13:41:19'),
(16,1,'蒙君','男',37,'中等身材，偏胖，以前是典型的纨绔，身体协调性较差，动作偶尔出现不自然的停顿或错位。面容原本端正，但因长期紧张与焦虑，眉间有深刻的竖纹，眼下有暗色。头发散乱，衣服常穿不合身或搭配奇怪，因两个意识会轮流选择不同的穿着风格。手指有时会无意识地蜷缩或抽搐，像是想抓住什么。','传统家族出身，渴望复兴家族往日的荣光。其家族曾是巫术家族之一，垄断灵的觉醒权与修炼权，但游侠时代后逐渐衰落。蒙君自小被灌输“家族高于一切”的理念，成年后为了获取复兴家族的力量，暗害了父亲雇来的师傅，夺走了师傅手中与“明”签订圣器（竹书纪年）契约的机会。\n\n他通过圣器与明签订契约，期望明能帮助他复兴家族。根据契约规则：若未实现愿望，许愿者（蒙君）将获得一切（即完全占据身体）；若实现愿望，则实现者（明）逐渐获得一切。由于圣器裁决功能受损，两人未能分出胜负，而是陷入了长达十余年的身体控制权争夺。目前两人共用一个身体，不同部位、不同时段由不同意识控制。','执念极深，对“家族复兴”有近乎偏执的坚持。\n\n在正常状态下有一定世故和算计能力，但焦虑和绝望时常让他做出冲动决定。\n\n对明既恨又依赖——恨他占据自己的身体，依赖他可能带来的能力与知识。\n\n内心深处怀疑自己永远无法实现愿望，但不愿承认，只能继续争夺。\n\n有强烈的孤独感——他不能告诉任何人自己正在经历什么，因为没人会相信。','__file__:character/16.json','2026-07-05 13:44:02'),
(17,55,'奈良鹿野','男',16,'黑色短发，常穿浅灰色奈良家服饰，外罩一件深色外套。站姿松散，走路速度偏慢，倾向于用最少的动作完成最多的事。12岁时身高约160cm，17岁时身高约178cm。手指修长，常放在身侧或插在口袋里。','生物解剖课是他在忍校期间唯一不躺着的课。\n\n他不喜欢站着，也不喜欢走动。大多数时候他靠在窗边，或者趴在后排的课桌上，看窗外树影晃动。但解剖课的桌子一拉出来，他会坐直，俯身观察，目光落在标本的切开面上，看组织结构的分布走向。\n\n“你是奈良家的孩子，为什么总是不练习影子术？”有一次老师这样问他。\n\n鹿野：“我在练。”\n\n“你在练什么？”\n\n“我在看影子怎么动。”\n\n老师说他有潜力，但用错了方向。鹿野没有反驳。他继续看影子在不同光照条件下的形态变化，记录它们在不同距离、不同角度下的速度差异，然后想：影子能不能在不被察觉的情况下靠近目标？\n\n后来他找到了一种用法——影子可以做手术。\n\n不需要接触，不需要器械，不留下切口。它可以直接伸入伤口内部，剥离坏死组织，重建断裂的经络。','安静、观察型、倾向于用最小行动获取最大信息。不主动向人解释自己的选择，但如果有人问，会用最简单的语言作答。他说话少，是因为他并不觉得所有事都需要解释。\n\n对大多数事情保持“嫌麻烦”的态度，但生物解剖课和忍术原理课会打起十二分精神。他感兴趣的领域和奈良家期望他走的路径之间存在明显差异，但他选择用更安静的坚持来维持自己的方向，而不是通过言辞来表达不满。','__file__:character/17.json','2026-07-05 14:05:47'),
(18,1,'孙文慧','女',24,'身高约164cm，身材丰腴，骨架结实，属于长辈眼中“好生养”的体态，前凸后翘。因常年劳作，皮肤偏黑黄且粗糙，但掩盖不住她的秀气，手掌宽厚，指节有力，但是把自己收拾得很干净。五官端正，眉眼舒展，笑起来时眼角有细纹，不笑时有一种沉静的踏实感。头发乌黑浓密，常编成一条粗辫盘在脑后，干活时利落，不拖沓。穿三川道常见的粗布衣，袖口习惯性卷到肘部以上。','三川道季家管家的女儿，自幼在季家长大，与季子舟青梅竹马。两人曾在程都府跟随季子舟的舅舅学习纺织、缝纫、剪裁，是同窗，也是手艺上的搭档。她自小对季子舟有情意，但季子舟待她如妹妹，未曾回应。\n季子舟赴京求学后，她留在三川道，与季子舟保持书信往来。信中她协助传递季子舟与革命组织之间的消息，同时负责保管和转寄各种物品（如季子舟从京城寄回的醪糟与小吃）。她亲眼看着季子舟在京城与何玉琢恋爱、受挫、被发配铎天司、失业、回乡。\n季子舟回乡后，父母季伯仲与田氏强行安排两人成亲。洞房夜，孙文慧看出季子舟不愿，主动提出一起逃婚。两人共同翻墙离开三川道，此后她时不时回三川道看望父母，季子舟则终身未归。','勤劳朴实，做事踏实，不夸海口，不怨天尤人。\n\n善于观察，能准确判断他人的情绪与意愿——尤其对季子舟，她总能看透他嘴上不说的事。\n\n主动但不张扬。她不是“等”的人，但她选择“等”季子舟。这是她的选择，不是被动接受。\n\n有极强的忍耐力，对艰苦环境适应迅速——随军后能立刻转入随军医生与文工部的工作。\n\n情感深沉但不外露。她不会说我爱你，但她会做一身衣服、寄一封信、等一辈子、养一个孩子。','__file__:character/18.json','2026-07-05 14:18:33'),
(20,55,'西宫爱子','女',19,'黑色长发，发尾微卷，常梳理整齐，偶尔会盘起或编成侧编发。面容柔和，眉眼温润，整体气质偏向淑女。长期坐轮椅，腿部肌肉不如正常人结实，触感偏软，有轻微的赘肉感，但不影响整体仪态。坐姿端正，上半身保持挺直，手部动作流畅。激动时能站起来走两步，但步履不稳，需要依靠支撑物才能保持平衡。\n因长期坐轮椅，双腿形状比起经常站立的人更放松，没有明显的肌肉线条。靠近膝盖处有时能看到轻微的压痕或按摩痕迹，因为不能站起来走虽然有在堇乃的指导下进行康复锻炼能走几步但是因为实在没有太多锻炼看起来虽然小腿不胖但肉感十足，足部也相对娇小，视觉上十分秀气，也许是因为堇乃的调理，身材气色其实不算太差，只是残疾人的身份，让她显得有些较弱。\n看起来让人很有保护欲与一种贤妻良母的人妻感，但其实背地里很毒舌，特别是对志明。','西宫家长女，父亲是火之国国都的商人，母亲是木叶出身的忍具制造商，与天天家世代交好。父母因理念不合离婚后，爱子由母亲和家庭教师抚养长大，同时承担了部分家族产业的管理工作——包括参与母亲和父亲的产业经营。她是妹妹惠子童年时期的主要照料者和稳定来源。\n爱子出生时家庭和睦，名字寄予“被爱”的期望。但实际上，她承担了作为长女的一切责任，并未获得与之匹配的回报。后因父亲的政治利益安排，她差点被嫁予王都贵族作为结盟筹码，后被志明救下。\n由于母亲与堇乃的熟人关系，以及西宫家长期资助孤儿院、福利院和养老院，堇乃经常来给姐妹俩讲课，也偶尔会带志明一同前来。正是在这些访问中，志明初次见到了爱子和惠子，并注意到爱子的外貌与云志明穿越前认识的某人极为相似。','表面符合“贤内助”的培养方向——举止得体、言语有度、善于察言观色。但内心实际上更轻松、更放松，有时会带有一点调侃他人的兴致，因为一些初见时的误会与志明在她心中特殊的感觉尤其喜欢打趣、揶揄志明。她能观察到别人的情绪变化并做出回应，但不会过度主动介入。\n但其实内心很脆弱，只是因为家庭原因不得不坚强，因为初见时志明一直盯着她看（她不知道，志明也没说，他长得很像志明穿越前的一个同学），而又因为堇乃阿姨让她不得不了解志明，所以经常用自己的残疾和志明的各种做得不好的地方挖苦他，但其实只有在志明或者惠子面前才这样。\n她对妹妹既关心也关注，在妹妹面前较为稳定，在母亲面前则更谨慎，在父亲面前带着明显的距离感。她对志明的态度经历了从怀疑到关注，再到信任的过程，转折点发生在王都篇她被救出之后。她不是不会表达情绪，而是环境使她需要选择特定的方式来表达。','__file__:character/20.json','2026-07-05 16:56:02'),
(21,55,'西宫惠子','女',16,'常将头发扎成单短马尾或留短发，以便工作，较少披散，和志明见面时时常会扎狼尾。面容清秀但气色干练，整体给人利落、不拖沓的印象。成年后身形偏瘦，因长期从事制图与工程劳动，手指有茧。日常衣着以实用为主，颜色偏深，较少穿裙装。\n与姐姐爱子的淑女气质不同，惠子的形象更偏向“假小子”风格，行动迅速，不刻意修饰外表。','西宫家次女，出生时家庭氛围已不如爱子出生时融洽，父母分歧逐渐扩大。本名“惠子”，名字寄托“贤惠、富足”的期望。但她实际上走向了完全不同的方向——她没有成为传统意义上的“贤惠女性”，而是成为了一名工程师和制图师，专注于制造和设计。\n因家庭变故和姐姐的残疾，她从小就习惯于承担更多行动上的责任。后来在志明的影响下，她逐渐放弃了成为忍者的愿望，转而专注技术路线。她开始画图纸、参与制造工作，并在此领域逐渐获得立足之处。\n她与姐姐爱子关系亲密，但青春期时因一些原因受到姐姐的限制（因为惠子拿着志明的东西在床上夹腿，床单湿了，被门缝隙外的爱子看到了。也因此爱子对待志明的态度有点不满），导致两人之间曾在较长时间内存在一定的距离感。','行动力强、有主见、不墨守成规。外表看起来有些粗枝大叶，但实际工作时细致专注。说话直来直去，不擅长绕弯子，也不喜欢被安排。在熟悉的人面前会比较放得开，但在陌生人面前会有明显的距离感。\n小时候很依赖姐姐，但长大后因为对于志明的态度对姐姐有时会表现出不服气的态度。随着年龄增长和自身境遇的变化，她对姐姐的依赖逐渐转为相互理解。','__file__:character/21.json','2026-07-05 17:05:44');
/*!40000 ALTER TABLE `novel_character` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `novel_relation`
--

DROP TABLE IF EXISTS `novel_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `novel_relation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `novel_id` bigint(20) NOT NULL,
  `related_novel_id` bigint(20) NOT NULL,
  `relation_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_novel_id` (`novel_id`) USING BTREE,
  KEY `fk_nr_related` (`related_novel_id`) USING BTREE,
  CONSTRAINT `fk_nr_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel` (`id`),
  CONSTRAINT `fk_nr_related` FOREIGN KEY (`related_novel_id`) REFERENCES `novel` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `novel_relation`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `novel_relation` WRITE;
/*!40000 ALTER TABLE `novel_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `novel_relation` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `story_node`
--

DROP TABLE IF EXISTS `story_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `story_node` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `novel_id` bigint(20) NOT NULL,
  `timeline_id` bigint(20) DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `vector_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_date` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'äº‹ä»¶æ—¥æœŸ(å¦‚: æœ¨å¶1å¹´)',
  `event_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'äº‹ä»¶ç±»åž‹: birth(å‡ºç”Ÿ), war(æˆ˜äº‰), politics(æ”¿æ²»), major(é‡å¤§è½¬æŠ˜)',
  `importance` int(11) DEFAULT '3' COMMENT 'é‡è¦æ€§: 1-5, 5æœ€é‡è¦',
  `character_names` json DEFAULT NULL COMMENT 'ç›¸å…³è§’è‰²åç§°åˆ—è¡¨',
  `tags` json DEFAULT NULL COMMENT 'æ ‡ç­¾åˆ—è¡¨',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_timeline_id` (`timeline_id`) USING BTREE,
  KEY `fk_story_novel` (`novel_id`) USING BTREE,
  KEY `idx_event_date` (`event_date`),
  KEY `idx_event_type` (`event_type`),
  KEY `idx_importance` (`importance`),
  CONSTRAINT `fk_story_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel` (`id`),
  CONSTRAINT `fk_story_timeline` FOREIGN KEY (`timeline_id`) REFERENCES `timeline` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `story_node`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `story_node` WRITE;
/*!40000 ALTER TABLE `story_node` DISABLE KEYS */;
INSERT INTO `story_node` (`id`, `novel_id`, `timeline_id`, `title`, `content`, `create_time`, `vector_id`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES (94,55,4,'建村；五影会谈','木叶建村，五影会谈确立忍村制度。','2026-06-27 06:34:25',NULL,'木叶1年','politics',5,'[]','[]'),
(95,55,4,'各国争夺尾兽','各国争夺尾兽。','2026-06-27 06:34:25',NULL,'木叶1-5年','politics',4,'[]','[]'),
(96,55,4,'终结谷之战；柱间病倒；第一次忍界大战爆发','终结谷之战，柱间病倒，第一次忍界大战爆发。','2026-06-27 06:34:25',NULL,'木叶10年前后','major',5,'[\"柱间\"]','[]'),
(97,55,4,'加藤断出生','加藤断出生。','2026-06-27 06:34:25',NULL,'木叶12-13年','birth',2,'[\"加藤断\"]','[]'),
(98,55,4,'自来也、大蛇丸、纲手出生','自来也、大蛇丸、纲手出生。','2026-06-27 06:34:25',NULL,'木叶16-18年','birth',3,'[\"自来也\", \"大蛇丸\", \"纲手\"]','[]'),
(99,55,4,'绳树出生（纲手弟弟）','绳树出生，纲手的弟弟。','2026-06-27 06:34:25',NULL,'木叶24-25年','birth',2,'[\"绳树\", \"纲手\"]','[]'),
(100,55,4,'波风水门、漩涡玖辛奈出生','波风水门、漩涡玖辛奈出生。','2026-06-27 06:34:25',NULL,'木叶27年','birth',3,'[\"波风水门\", \"漩涡玖辛奈\"]','[]'),
(101,55,4,'志明、悠香、真一、鹿野、次步美出生；第二次忍界大战爆发','主角团成员出生。第二次忍界大战爆发。','2026-06-27 06:34:25',NULL,'木叶31-32年','major',3,'[\"志明\", \"悠香\", \"真一\", \"鹿野\", \"次步美\"]','[]'),
(102,55,4,'卡卡西、带土、琳、凯、红、阿斯玛出生；代理人战争','卡卡西、带土、琳、凯、红、阿斯玛出生。木叶、砂隐、岩隐等势力在雨之国打代理人战争。','2026-06-27 06:34:25',NULL,'木叶33-34年','birth',4,'[\"卡卡西\", \"带土\", \"琳\", \"凯\", \"红\", \"阿斯玛\"]','[]'),
(103,55,4,'惠比寿、不知火玄间等出生','惠比寿、不知火玄间等出生。','2026-06-27 06:34:25',NULL,'木叶34年','birth',2,'[\"惠比寿\", \"不知火玄间\"]','[]'),
(104,55,4,'根部疯狂扩张','根部疯狂扩张。','2026-06-27 06:34:25',NULL,'木叶35年','politics',3,'[]','[]'),
(105,55,4,'绳树阵亡；加藤断阵亡；三忍获封','绳树（12岁）阵亡，加藤断（约23-24岁）阵亡。三忍获封。','2026-06-27 06:34:25',NULL,'木叶36年','major',5,'[\"绳树\", \"加藤断\", \"自来也\", \"大蛇丸\", \"纲手\"]','[]'),
(106,55,4,'大蛇丸开始研究禁术','受到绳树死亡的刺激，大蛇丸开始研究禁术、柱间细胞、永生、血继限界。','2026-06-27 06:34:25',NULL,'木叶36年','major',4,'[\"大蛇丸\"]','[]'),
(107,55,4,'大和出生；第二次忍界大战结束','大和出生。第二次忍界大战结束。','2026-06-27 06:34:25',NULL,'木叶36-37年','major',3,'[\"大和\"]','[]'),
(108,55,4,'自来也收徒；纲手患恐血症','自来也收长门、弥彦、小南为徒。纲手患恐血症。','2026-06-27 06:34:25',NULL,'木叶38年','major',4,'[\"自来也\", \"长门\", \"弥彦\", \"小南\", \"纲手\"]','[]'),
(109,55,4,'卡卡西毕业；自来也离村','卡卡西毕业。自来也离村。','2026-06-27 06:34:25',NULL,'木叶39年','major',3,'[\"卡卡西\", \"自来也\"]','[]'),
(110,55,4,'隼人班成立；第三次忍界大战开始','隼人班成立，新之助班成立，卡卡西晋升中忍。纲手离村漂泊。第三次忍界大战正式开始。','2026-06-27 06:34:25',NULL,'木叶40年','war',5,'[\"隼人\", \"新之助\", \"卡卡西\", \"纲手\"]','[]'),
(111,55,4,'山中风、油女取根出生','山中风、油女取根出生。','2026-06-27 06:34:25',NULL,'木叶40-41年','birth',2,'[\"山中风\", \"油女取根\"]','[]'),
(112,55,4,'白牙自杀；宇智波止水出生；水门开发螺旋丸','白牙自杀。宇智波止水出生。水门开始开发螺旋丸。','2026-06-27 06:34:25',NULL,'木叶43年','major',4,'[\"白牙\", \"止水\", \"水门\"]','[]'),
(113,55,4,'宇智波鼬出生；水门班成立','宇智波鼬出生。水门班成立。','2026-06-27 06:34:25',NULL,'木叶44年','birth',3,'[\"宇智波鼬\", \"水门\"]','[]'),
(114,55,4,'第三次忍界大战最惨烈阶段','第三次忍界大战最惨烈阶段。','2026-06-27 06:34:25',NULL,'木叶45-46年','war',5,'[]','[]'),
(115,55,4,'卡卡西升上忍；神无毗桥之战','卡卡西13岁升上忍。主角团15岁已是有经验的忍者。神无毗桥之战。带土被斑救走。','2026-06-27 06:34:25',NULL,'木叶46年','major',5,'[\"卡卡西\", \"带土\"]','[]'),
(116,55,4,'琳死亡；水门迎战AB组合','琳死亡。水门用螺旋丸迎战AB组合。','2026-06-27 06:34:25',NULL,'木叶46-47年','major',5,'[\"琳\", \"水门\"]','[]'),
(117,55,4,'水门就任四代目；三战结束','水门就任四代目火影。水门与玖辛奈结婚。三战结束。大蛇丸选举失败心灰意冷。','2026-06-27 06:34:25',NULL,'木叶48年','major',5,'[\"水门\", \"玖辛奈\", \"大蛇丸\"]','[]'),
(118,55,4,'水门、玖辛奈牺牲；鸣人出生；九尾之乱','水门、玖辛奈牺牲。鸣人出生。雏田出生。九尾之乱。','2026-06-27 06:34:25',NULL,'木叶49年','major',5,'[\"水门\", \"玖辛奈\", \"鸣人\", \"雏田\"]','[]'),
(119,55,4,'大蛇丸叛逃','大蛇丸叛逃。','2026-06-27 06:34:25',NULL,'木叶49年','major',4,'[\"大蛇丸\"]','[]'),
(120,55,4,'鸣人、佐助等新一代出生','鸣人、佐助等新一代出生。','2026-06-27 06:34:25',NULL,'木叶50-51年','birth',3,'[\"鸣人\", \"佐助\"]','[]'),
(121,55,4,'日向花火出生','日向花火出生。','2026-06-27 06:34:25',NULL,'木叶53年','birth',2,'[\"日向花火\"]','[]'),
(122,55,4,'宇智波灭族','宇智波灭族。','2026-06-27 06:34:25',NULL,'木叶55年','major',5,'[]','[]'),
(123,55,4,'鸣人12岁，主线开始','鸣人12岁，主线开始。','2026-06-27 06:34:25',NULL,'木叶60年','major',5,'[\"鸣人\"]','[]');
/*!40000 ALTER TABLE `story_node` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `timeline`
--

DROP TABLE IF EXISTS `timeline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `timeline` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `novel_id` bigint(20) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_novel_id` (`novel_id`) USING BTREE,
  KEY `fk_timeline_parent` (`parent_id`) USING BTREE,
  CONSTRAINT `fk_timeline_novel` FOREIGN KEY (`novel_id`) REFERENCES `novel` (`id`),
  CONSTRAINT `fk_timeline_parent` FOREIGN KEY (`parent_id`) REFERENCES `timeline` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timeline`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `timeline` WRITE;
/*!40000 ALTER TABLE `timeline` DISABLE KEYS */;
INSERT INTO `timeline` (`id`, `novel_id`, `name`, `parent_id`, `description`, `create_time`) VALUES (4,55,'木叶纪年时间线',NULL,'火影：从油女开始的忍界之旅 - 木叶纪年历史时间线','2026-06-27 05:52:56');
/*!40000 ALTER TABLE `timeline` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `user_config`
--

DROP TABLE IF EXISTS `user_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_config` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `preset` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `anim_enabled` tinyint(1) DEFAULT NULL,
  `intensity` int(11) DEFAULT NULL,
  `color_theme` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `custom_image_url` longtext COLLATE utf8mb4_unicode_ci,
  `background_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `custom_bgs` text COLLATE utf8mb4_unicode_ci COMMENT 'è‡ªå®šä¹‰èƒŒæ™¯å›¾åˆ—è¡¨ï¼ˆæ–‡ä»¶è·¯å¾„å¼•ç”¨ï¼‰',
  `font_colors_json` text COLLATE utf8mb4_unicode_ci COMMENT 'å­—ä½“é¢œè‰²é…ç½®ï¼ˆæ–‡ä»¶è·¯å¾„å¼•ç”¨ï¼‰',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2072311361793200131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_config`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `user_config` WRITE;
/*!40000 ALTER TABLE `user_config` DISABLE KEYS */;
INSERT INTO `user_config` (`id`, `user_id`, `preset`, `anim_enabled`, `intensity`, `color_theme`, `custom_image_url`, `background_id`, `custom_bgs`, `font_colors_json`, `created_at`, `updated_at`) VALUES (2071100620398424066,1,NULL,NULL,NULL,NULL,NULL,'custom_1783300391733','__file__:user/customBgs/1.json','__file__:user/fontColors/1.json','2026-06-28 05:17:21','2026-07-06 05:24:34'),
(2071100898644357122,3,NULL,NULL,NULL,NULL,NULL,'【哲风壁纸】五角星-国徽-庄严','__file__:user/customBgs/3.json',NULL,'2026-06-28 05:18:28','2026-07-06 06:11:17'),
(2072311361793200129,4,NULL,NULL,NULL,NULL,NULL,'【哲风壁纸】五角星-国徽-庄严','[]',NULL,'2026-07-01 13:28:24','2026-07-01 13:28:49'),
(2072311361793200130,2,NULL,1,50,NULL,NULL,'【哲风壁纸】丘陵-乡村-公路','__file__:user/customBgs/2.json',NULL,'2026-07-06 06:12:59','2026-07-06 06:15:09');
/*!40000 ALTER TABLE `user_config` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Dumping routines for database 'dixiyang'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-07-06 14:57:12
