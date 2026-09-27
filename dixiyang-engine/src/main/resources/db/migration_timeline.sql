-- 时间线功能扩展迁移脚本
-- 扩展story_node表字段

-- 添加事件日期字段
ALTER TABLE `story_node` ADD COLUMN `event_date` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '事件日期(如: 木叶1年)';

-- 添加事件类型字段
ALTER TABLE `story_node` ADD COLUMN `event_type` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '事件类型: birth(出生), war(战争), politics(政治), major(重大转折)';

-- 添加重要性字段
ALTER TABLE `story_node` ADD COLUMN `importance` INT NULL DEFAULT 3 COMMENT '重要性: 1-5, 5最重要';

-- 添加相关角色字段(JSON数组)
ALTER TABLE `story_node` ADD COLUMN `character_names` JSON NULL COMMENT '相关角色名称列表';

-- 添加标签字段(JSON数组)
ALTER TABLE `story_node` ADD COLUMN `tags` JSON NULL COMMENT '标签列表';

-- 添加索引
ALTER TABLE `story_node` ADD INDEX `idx_event_date`(`event_date`);
ALTER TABLE `story_node` ADD INDEX `idx_event_type`(`event_type`);
ALTER TABLE `story_node` ADD INDEX `idx_importance`(`importance`);
