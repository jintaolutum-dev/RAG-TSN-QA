-- ============================================
-- Enterprise knowledge base QA system - database initialization script
-- Database name: db_enterprise_qa
-- MySQL port: 3306
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS db_enterprise_qa DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE db_enterprise_qa;

-- ============================================
-- User table
-- ============================================
DROP TABLE IF EXISTS t_chat_history;
DROP TABLE IF EXISTS t_document;
DROP TABLE IF EXISTS t_knowledge_base;
DROP TABLE IF EXISTS t_user;

CREATE TABLE t_user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'User ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Username',
    password VARCHAR(64) NOT NULL COMMENT 'Password (MD5 hashed)',
    nickname VARCHAR(50) DEFAULT '' COMMENT 'Nickname',
    role VARCHAR(10) NOT NULL DEFAULT 'user' COMMENT 'Role: admin-administrator, user-regular user',
    avatar VARCHAR(255) DEFAULT '' COMMENT 'Avatar URL',
    status TINYINT NOT NULL DEFAULT 1 COMMENT 'Status: 1-enabled, 0-disabled',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User table';

-- ============================================
-- Knowledge base table
-- ============================================
CREATE TABLE t_knowledge_base (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Knowledge base ID',
    kb_name VARCHAR(100) NOT NULL COMMENT 'Knowledge base name',
    description VARCHAR(500) DEFAULT '' COMMENT 'Knowledge base description',
    creator_id INT NOT NULL COMMENT 'Creator ID',
    doc_count INT NOT NULL DEFAULT 0 COMMENT 'Document count',
    status TINYINT NOT NULL DEFAULT 1 COMMENT 'Status: 1-active, 0-disabled',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    FOREIGN KEY (creator_id) REFERENCES t_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Knowledge base table';

-- ============================================
-- Document table
-- ============================================
CREATE TABLE t_document (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Document ID',
    kb_id INT NOT NULL COMMENT 'Knowledge base ID',
    file_name VARCHAR(255) NOT NULL COMMENT 'File name',
    file_path VARCHAR(500) NOT NULL COMMENT 'File storage path',
    file_size BIGINT NOT NULL DEFAULT 0 COMMENT 'File size (bytes)',
    file_type VARCHAR(20) NOT NULL COMMENT 'File type: txt/pdf/md/docx',
    chunk_count INT NOT NULL DEFAULT 0 COMMENT 'Chunk count',
    status VARCHAR(20) NOT NULL DEFAULT 'uploading' COMMENT 'Status: uploading-in progress, vectorized-vectorized, failed-failed',
    creator_id INT NOT NULL COMMENT 'Uploader ID',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    FOREIGN KEY (kb_id) REFERENCES t_knowledge_base(id),
    FOREIGN KEY (creator_id) REFERENCES t_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Document table';

-- ============================================
-- Chat history table
-- ============================================
CREATE TABLE t_chat_history (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Record ID',
    user_id INT NOT NULL COMMENT 'User ID',
    kb_id INT NOT NULL COMMENT 'Knowledge base ID',
    session_id VARCHAR(64) NOT NULL COMMENT 'Session ID',
    question TEXT NOT NULL COMMENT 'User question',
    answer TEXT NOT NULL COMMENT 'AI answer',
    source_docs TEXT DEFAULT NULL COMMENT 'Reference sources (JSON)',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    FOREIGN KEY (user_id) REFERENCES t_user(id),
    FOREIGN KEY (kb_id) REFERENCES t_knowledge_base(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chat history table';

-- ============================================
-- Insert test data
-- ============================================

-- Admin account: admin / 123456 (MD5 hashed)
-- Regular users: user1 / 123456, user2 / 123456
INSERT INTO t_user (username, password, nickname, role, status) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'Document Administrator', 'admin', 1),
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'Stefan', 'user', 1),
('user2', 'e10adc3949ba59abbe56e057f20f883e', 'Jintao', 'user', 1);



