CREATE DATABASE `palimpsest`;
SHOW DATABASES;
USE `palimpsest`;

CREATE TABLE `user` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,    -- 使用者編號
    `email` VARCHAR(100) NOT NULL UNIQUE,        -- 使用者電子郵件
    `password` VARCHAR(255) NOT NULL,            -- 密碼
    `nickname` VARCHAR(50) NOT NULL,             -- 暱稱
    `photo` BLOB,                               -- 照片
    `age` INT CHECK (age > 0 AND age <= 120),    -- 年齡
    `language` VARCHAR(20) DEFAULT 'en-US',      -- 語言偏好
    `diary_visibility` VARCHAR(20) DEFAULT 'friends', -- 預設日記可見範圍
    `reminder_enabled` BOOLEAN DEFAULT TRUE,     -- 是否啟用提醒
    `reminder_time` TIME DEFAULT '08:00:00',    -- 提醒時間
    `ai_emotion_support` BOOLEAN DEFAULT TRUE,   -- AI情感支援預設值（TRUE: 開啟, FALSE: 關閉）
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP, -- 帳號創建時間
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新時間
);

CREATE TABLE `user_login` (
    `login_id` INT AUTO_INCREMENT PRIMARY KEY, -- 登錄紀錄編號，自動生成唯一值
    `user_id` INT NOT NULL,                    -- 使用者編號
    `login_timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 登入時間
    `last_login` DATETIME,                     -- 上次登入時間
    `login_attempts` INT DEFAULT 0,            -- 登入失敗次數，預設為 0
    CHECK (`login_attempts` >= 0),             -- 登入失敗次數不可為負
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) 
        ON DELETE CASCADE                      -- 刪除使用者時刪除登入紀錄
);

CREATE TABLE `diary` (
    `diary_id` INT AUTO_INCREMENT PRIMARY KEY,    -- 日記ID
    `user_id` INT NOT NULL,                       -- 外鍵關聯到用戶
    `title` VARCHAR(255),                         -- 日記標題
    `content_original` TEXT,                      -- 原始日記內容
    `image_url` VARCHAR(255),                     -- 日記相關圖片的URL
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP, -- 創建日期
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最後修改日期
    `visibility` ENUM('private', 'friends', 'public') DEFAULT 'private', -- 查看權限（預設為私人）
    `emotion_support_enabled` BOOLEAN DEFAULT TRUE, -- 是否啟用AI情感支援
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

CREATE TABLE `diary_version` (
    `version_id` INT AUTO_INCREMENT PRIMARY KEY,  -- 版本編號
    `diary_id` INT NOT NULL,                      -- 日記編號 (外鍵)
    `user_id` INT NOT NULL,                       -- 使用者編號 (外鍵)
    `group_id` INT,                              -- 分群 (外鍵)（NULL表示通用公開版）
    `content_modified` TEXT NOT NULL,            -- AI修改後的內容
    `ai_command` TEXT,                           -- 修改時的AI指令
    `emotion_support_enabled` BOOLEAN DEFAULT TRUE, -- 是否啟用AI情感支援
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP, -- 版本創建時間
    FOREIGN KEY (`diary_id`) REFERENCES `diary`(`diary_id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `friend_group`(`group_id`) ON DELETE SET NULL
);

CREATE TABLE `diary_relationship` (
    `relationship_id` INT AUTO_INCREMENT PRIMARY KEY, -- 關係ID
    `parent_diary_id` INT NOT NULL,                   -- 繼承來源的日記ID
    `child_diary_id` INT NOT NULL,                    -- 繼承目標的日記ID
    FOREIGN KEY (`parent_diary_id`) REFERENCES `diary`(`diary_id`) ON DELETE CASCADE,
    FOREIGN KEY (`child_diary_id`) REFERENCES `diary`(`diary_id`) ON DELETE CASCADE
);

CREATE TABLE `tag` (
    `tag_id` INT AUTO_INCREMENT PRIMARY KEY, -- 標籤ID
    `tag_name` VARCHAR(50) NOT NULL UNIQUE,  -- 標籤名稱（如"心情", "工作", "旅遊"等）
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP -- 創建時間
);

CREATE TABLE `diary_tag` (
    `diary_id` INT,                        -- 關聯日記
    `tag_id` INT,                          -- 關聯標籤
    PRIMARY KEY (`diary_id`, `tag_id`),    -- 組合主鍵
    FOREIGN KEY (`diary_id`) REFERENCES `diary`(`diary_id`) ON DELETE CASCADE,
    FOREIGN KEY (`tag_id`) REFERENCES `tag`(`tag_id`) ON DELETE CASCADE
);

CREATE TABLE `diary_view_log` (
    `view_id` INT AUTO_INCREMENT PRIMARY KEY, -- 自動增長的ID
    `diary_id` INT NOT NULL,                  -- 關聯日記
    `viewer_id` INT NOT NULL,                 -- 瀏覽者的用戶ID
    `viewed_at` DATETIME DEFAULT CURRENT_TIMESTAMP, -- 瀏覽時間
    FOREIGN KEY (`diary_id`) REFERENCES `diary`(`diary_id`) ON DELETE CASCADE,
    FOREIGN KEY (`viewer_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);


CREATE TABLE `friend` (
    `friendship_id` INT AUTO_INCREMENT PRIMARY KEY, -- 好友關係ID
    `user_id` INT NOT NULL,                         -- 外鍵關聯到用戶
    `friend_id` INT NOT NULL,                       -- 外鍵關聯到好友的用戶ID
    `group_id` INT NOT NULL,                        -- 外鍵關聯到好友分群
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP, -- 建立好友關係的時間
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`friend_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `friend_group`(`group_id`) ON DELETE CASCADE
);

CREATE TABLE `friend_group` (
    `group_id` INT AUTO_INCREMENT PRIMARY KEY,  -- 分群ID
    `user_id` INT NOT NULL,                     -- 外鍵關聯到用戶
    `group_name` VARCHAR(50) NOT NULL,          -- 分群名稱
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);




DESCRIBE `user`;
DESCRIBE `user_login`;
DESCRIBE `diary`;
DESCRIBE `diary_version`;
DESCRIBE `diary_relationship`;
DESCRIBE `tag`;
DESCRIBE `diary_tag`;
DESCRIBE `diary_view_log`;
DESCRIBE `friend`;
DESCRIBE `friend_group`;

SELECT * FROM `user`;
SELECT * FROM `user_login`;
SELECT * FROM `diary`;

DROP TABLE `user`;
DROP TABLE `user_login`;
DROP TABLE `diary`;
DROP DATABASE `palimpsest`;