-- 火影忍者时间线数据导入脚本
-- 小说: 火影：从油女开始的忍界之旅
-- 数据来源: 用户提供的木叶纪年时间线表格

-- 假设小说ID为1，如果不同请修改

-- ==================== 时间线 ====================
INSERT INTO `timeline` (`novel_id`, `name`, `description`) VALUES
(10, '木叶纪年时间线', '火影：从油女开始的忍界之旅 - 木叶纪年历史时间线');

SET @timeline_id = LAST_INSERT_ID();

-- ==================== 故事节点 ====================

-- 木叶1年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '建村；五影会谈', '木叶建村，五影会谈确立忍村制度。', '木叶1年', 'politics', 5, '[]', '["建村", "政治"]');

-- 木叶1-5年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '各国争夺尾兽', '各国争夺尾兽。', '木叶1-5年', 'politics', 4, '[]', '["尾兽"]');

-- 木叶10年前后
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '终结谷之战；柱间病倒；第一次忍界大战爆发', '终结谷之战，柱间病倒，第一次忍界大战爆发。', '木叶10年', 'major', 5, '["柱间"]', '["终结谷", "第一次忍界大战"]');

-- 木叶12-13年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '加藤断出生', '加藤断出生。', '木叶12年', 'birth', 2, '["加藤断"]', '["出生"]');

-- 木叶16-18年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '自来也、大蛇丸、纲手出生', '自来也、大蛇丸、纲手出生。', '木叶16年', 'birth', 3, '["自来也", "大蛇丸", "纲手"]', '["三忍"]');

-- 木叶24-25年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '绳树出生（纲手弟弟）', '绳树出生，纲手的弟弟。', '木叶24年', 'birth', 2, '["绳树", "纲手"]', '["出生"]');

-- 木叶27年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '波风水门、漩涡玖辛奈出生', '波风水门、漩涡玖辛奈出生。', '木叶27年', 'birth', 3, '["波风水门", "漩涡玖辛奈"]', '["出生"]');

-- 木叶31-32年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '志明、悠香、真一、鹿野、次步美出生', '志明、悠香、真一、鹿野、次步美出生。第二次忍界大战爆发。', '木叶31年', 'birth', 3, '["志明", "悠香", "真一", "鹿野", "次步美"]', '["主角团", "第二次忍界大战"]');

-- 木叶33-34年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '卡卡西、带土、琳、凯、红、阿斯玛出生', '卡卡西、带土、琳、凯、红、阿斯玛出生。木叶、砂隐、岩隐等势力都在雨之国活动。打代理人战争。', '木叶33年', 'birth', 4, '["卡卡西", "带土", "琳", "凯", "红", "阿斯玛"]', '["雨之国", "代理人战争"]');

-- 木叶34年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '惠比寿、不知火玄间等出生', '惠比寿、不知火玄间等出生。', '木叶34年', 'birth', 2, '["惠比寿", "不知火玄间"]', '["出生"]');

-- 木叶35年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '根部疯狂扩张', '根部疯狂扩张。', '木叶35年', 'politics', 3, '[]', '["根部"]');

-- 木叶36年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '绳树（12岁）阵亡；加藤断（约23-24岁）阵亡', '绳树阵亡，加藤断阵亡。三忍获封。', '木叶36年', 'major', 5, '["绳树", "加藤断", "自来也", "大蛇丸", "纲手"]', '["阵亡", "三忍"]'),
(1, @timeline_id, '大蛇丸开始研究禁术', '受到绳树死亡的刺激，以及思考的深入，大蛇丸开始研究禁术、柱间细胞、永生、血继限界。', '木叶36年', 'major', 4, '["大蛇丸"]', '["禁术", "研究"]');

-- 木叶36-37年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '大和出生；第二次忍界大战结束', '大和出生。第二次忍界大战结束。', '木叶36年', 'major', 3, '["大和"]', '["第二次忍界大战结束"]');

-- 木叶38年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '自来也收长门、弥彦、小南为徒；纲手患恐血症', '自来也收长门、弥彦、小南为徒。纲手患恐血症。', '木叶38年', 'major', 4, '["自来也", "长门", "弥彦", "小南", "纲手"]', '["师徒", "恐血症"]');

-- 木叶39年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '卡卡西毕业；自来也离村', '卡卡西毕业。自来也离村。', '木叶39年', 'major', 3, '["卡卡西", "自来也"]', '["毕业", "离村"]');

-- 木叶40年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '隼人班成立；新之助班成立；卡卡西晋升中忍', '隼人班成立，新之助班成立，卡卡西晋升中忍。纲手离村漂泊。第三次忍界大战正式开始。山中真一被根部带走。', '木叶40年', 'war', 5, '["隼人", "新之助", "卡卡西", "纲手", "山中真一"]', '["第三次忍界大战", "根部"]');

-- 木叶40-41年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '山中风、油女取根出生', '山中风、油女取根出生。', '木叶40年', 'birth', 2, '["山中风", "油女取根"]', '["出生"]');

-- 木叶43年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '白牙自杀；宇智波止水出生', '白牙自杀。宇智波止水出生。水门开始开发螺旋丸。隼人班等被直接投入战场。晋升中忍。', '木叶43年', 'major', 4, '["白牙", "止水", "水门"]', '["白牙", "螺旋丸"]');

-- 木叶44年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '宇智波鼬出生；水门班成立', '宇智波鼬出生。水门班成立。', '木叶44年', 'birth', 3, '["宇智波鼬", "水门"]', '["水门班"]');

-- 木叶45-46年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '第三次忍界大战最惨烈阶段', '第三次忍界大战最惨烈阶段。', '木叶45年', 'war', 5, '[]', '["第三次忍界大战"]');

-- 木叶46年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '卡卡西13岁升上忍；主角团15岁已是有经验的忍者', '卡卡西13岁升上忍。主角团15岁已是有经验的忍者。神无毗桥之战。带土被斑救走。', '木叶46年', 'major', 5, '["卡卡西", "带土"]', '["神无毗桥", "斑"]');

-- 木叶46-47年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '琳死亡/地狱乱；水门用螺旋丸迎战AB组合', '琳死亡，地狱乱。水门用螺旋丸迎战AB组合。', '木叶46年', 'major', 5, '["琳", "水门"]', '["琳死亡", "螺旋丸"]');

-- 木叶47年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '木叶47年', '（无重大事件记录）', '木叶47年', 'politics', 1, '[]', '[]');

-- 木叶48年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '水门就任四代目火影；水门与玖辛奈结婚与庆功宴', '水门就任四代目火影。水门与玖辛奈结婚与庆功宴。三战结束。大蛇丸选举失败彻底心灰意冷。', '木叶48年', 'major', 5, '["水门", "玖辛奈", "大蛇丸"]', '["四代目", "三战结束"]');

-- 木叶49年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '水门、玖辛奈牺牲；鸣人出生；雏田出生', '水门、玖辛奈牺牲。鸣人出生。雏田出生。九尾之乱。', '木叶49年', 'major', 5, '["水门", "玖辛奈", "鸣人", "雏田"]', '["九尾之乱", "牺牲"]'),
(1, @timeline_id, '大蛇丸叛逃', '大蛇丸叛逃。', '木叶49年', 'major', 4, '["大蛇丸"]', '["叛逃"]');

-- 木叶50-51年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '鸣人、佐助等新一代出生', '鸣人、佐助等新一代出生。', '木叶50年', 'birth', 3, '["鸣人", "佐助"]', '["出生"]');

-- 木叶53年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '日向花火出生', '日向花火出生。', '木叶53年', 'birth', 2, '["日向花火"]', '["出生"]');

-- 木叶55年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '宇智波灭族', '宇智波灭族。', '木叶55年', 'major', 5, '[]', '["宇智波灭族"]');

-- 木叶60年
INSERT INTO `story_node` (`novel_id`, `timeline_id`, `title`, `content`, `event_date`, `event_type`, `importance`, `character_names`, `tags`) VALUES
(1, @timeline_id, '鸣人12岁，主线开始', '鸣人12岁，主线开始。', '木叶60年', 'major', 5, '["鸣人"]', '["主线开始"]');

-- 完成
SELECT '火影忍者时间线数据导入完成！' AS message;
SELECT COUNT(*) AS total_events FROM story_node WHERE novel_id = 1;
