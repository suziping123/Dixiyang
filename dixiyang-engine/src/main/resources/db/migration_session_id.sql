-- 单点登录（顶号踢出）+ 登录风控（多次被踢后强制验证码登录）
-- 执行方式：mysql -uroot -p123321 dixiyang < migration_session_id.sql

ALTER TABLE `app_user`
  ADD COLUMN `session_id` varchar(64) NULL COMMENT '当前登录会话ID（单点登录顶号，登录时覆盖）',
  ADD COLUMN `login_count` int NOT NULL DEFAULT 0 COMMENT '风控窗口内成功登录次数',
  ADD COLUMN `login_window_start` datetime NULL COMMENT '风控窗口起点',
  ADD COLUMN `require_code` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否强制邮箱验证码登录(0/1)';

-- 邮箱验证码表（与 DixyangFast models/email_verification.py 一致；已存在则跳过）
CREATE TABLE IF NOT EXISTS `email_verification_code` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `code` varchar(6) NOT NULL,
  `purpose` varchar(10) NOT NULL COMMENT 'LOGIN/REGISTER/CHG_EMAIL',
  `expire_time` datetime NOT NULL,
  `used` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_email_purpose` (`email`, `purpose`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 回滚：
-- ALTER TABLE `app_user`
--   DROP COLUMN `session_id`, DROP COLUMN `login_count`,
--   DROP COLUMN `login_window_start`, DROP COLUMN `require_code`;
