-- 会话索引表：替代 chat_history，每行一个会话，消息体存链式 JSON 文件
DROP TABLE IF EXISTS `chat_history`;

CREATE TABLE IF NOT EXISTS `chat_session` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `novel_id` BIGINT NULL DEFAULT NULL COMMENT '关联小说ID',
    `session_id` VARCHAR(64) NOT NULL COMMENT '会话UUID(由前端生成)',
    `head_path` VARCHAR(512) NULL DEFAULT NULL COMMENT '链式JSON头文件路径',
    `title` VARCHAR(200) NULL DEFAULT NULL COMMENT '对话标题(首条消息AI生成或截取)',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '会话创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后消息时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY `uk_user_session` (`user_id`, `session_id`) USING BTREE,
    INDEX `idx_user_novel` (`user_id`, `novel_id`) USING BTREE,
    INDEX `idx_update_time` (`update_time`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;
