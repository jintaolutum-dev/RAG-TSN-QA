/*
SQLyog Community v13.2.0 (64 bit)
MySQL - 8.1.0 : Database - db_enterprise_qa
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`db_enterprise_qa` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `db_enterprise_qa`;

/*Table structure for table `t_chat_history` */

DROP TABLE IF EXISTS `t_chat_history`;

CREATE TABLE `t_chat_history` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Record ID',
  `user_id` int NOT NULL COMMENT 'User ID',
  `kb_id` int NOT NULL COMMENT 'Knowledge base ID',
  `session_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Session ID',
  `question` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'User question',
  `answer` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'AI answer',
  `source_docs` text COLLATE utf8mb4_unicode_ci COMMENT 'Reference sources (JSON)',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `kb_id` (`kb_id`),
  CONSTRAINT `t_chat_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`),
  CONSTRAINT `t_chat_history_ibfk_2` FOREIGN KEY (`kb_id`) REFERENCES `t_knowledge_base` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chat history table';

/*Data for the table `t_chat_history` */


/*Table structure for table `t_document` */

DROP TABLE IF EXISTS `t_document`;

CREATE TABLE `t_document` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Document ID',
  `kb_id` int NOT NULL COMMENT 'Knowledge base ID',
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'File name',
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'File storage path',
  `file_size` bigint NOT NULL DEFAULT '0' COMMENT 'File size (bytes)',
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'File type: txt/pdf/md/docx',
  `chunk_count` int NOT NULL DEFAULT '0' COMMENT 'Chunk count',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'uploading' COMMENT 'Status: uploading-in progress, vectorized-vectorized, failed-failed',
  `creator_id` int NOT NULL COMMENT 'Uploader ID',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`id`),
  KEY `kb_id` (`kb_id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `t_document_ibfk_1` FOREIGN KEY (`kb_id`) REFERENCES `t_knowledge_base` (`id`),
  CONSTRAINT `t_document_ibfk_2` FOREIGN KEY (`creator_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Document table';

/*Data for the table `t_document` */



/*Table structure for table `t_knowledge_base` */

DROP TABLE IF EXISTS `t_knowledge_base`;

CREATE TABLE `t_knowledge_base` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Knowledge base ID',
  `kb_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Knowledge base name',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT 'Knowledge base description',
  `creator_id` int NOT NULL COMMENT 'Creator ID',
  `doc_count` int NOT NULL DEFAULT '0' COMMENT 'Document count',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT 'Status: 1-active, 0-disabled',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `t_knowledge_base_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Knowledge base table';

/*Data for the table `t_knowledge_base` */



/*Table structure for table `t_user` */

DROP TABLE IF EXISTS `t_user`;

CREATE TABLE `t_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Username',
  `password` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Password (MD5 hashed)',
  `nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT 'Nickname',
  `role` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user' COMMENT 'Role: admin-administrator, user-regular user',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT 'Avatar URL',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT 'Status: 1-enabled, 0-disabled',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User table';

/*Data for the table `t_user` */

insert  into `t_user`(`id`,`username`,`password`,`nickname`,`role`,`avatar`,`status`,`create_time`,`update_time`) values 
(1,'admin','e10adc3949ba59abbe56e057f20f883e','Document Administrator','admin','',1,'2026-03-21 18:20:17','2026-03-21 18:20:17'),
(2,'user1','e10adc3949ba59abbe56e057f20f883e','Stefan','user','',1,'2026-03-21 18:20:17','2026-03-21 18:20:17'),
(3,'user2','e10adc3949ba59abbe56e057f20f883e','Jintao','user','',1,'2026-03-21 18:20:17','2026-03-21 18:20:17');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

