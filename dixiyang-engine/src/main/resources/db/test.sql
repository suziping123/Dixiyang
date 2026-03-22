CREATE TABLE user_config (
                             id BIGINT AUTO_INCREMENT PRIMARY KEY,
                             user_id BIGINT NOT NULL,
                             preset VARCHAR(50),
                             anim_enabled BOOLEAN,
                             intensity INT,
                             color_theme VARCHAR(50),
                             custom_image_url LONGTEXT,
                             font_colors_json JSON,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                             KEY idx_user_id (user_id)
);
