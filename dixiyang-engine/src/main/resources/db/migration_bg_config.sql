-- 添加背景配置字段到app_user表
ALTER TABLE `app_user` ADD COLUMN `bg_config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '用户背景配置JSON';

-- 如果需要回滚，运行：
-- ALTER TABLE `app_user` DROP COLUMN `bg_config`;
