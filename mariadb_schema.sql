-- MariaDB Schema Generated from SQLite
-- Generated on: 2025-05-05 03:26:11
-- This script creates MariaDB-compatible versions of all tables

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `field_definitions`;
CREATE TABLE `field_definitions` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(64) NOT NULL,
  `label` VARCHAR(128) NOT NULL,
  `type` VARCHAR(32) NOT NULL,
  `required` TINYINT(1),
  `options` TEXT,
  `order` INT,
  `active` TINYINT(1),
  `validation` TEXT,
  `created_at` DATETIME,
  `updated_at` DATETIME,
  `grid_column` INT DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Creating index on name since it's likely meant to be unique
CREATE UNIQUE INDEX `idx_field_def_name` ON `field_definitions` (`name`);

DROP TABLE IF EXISTS `violation_field_values`;
CREATE TABLE `violation_field_values` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `violation_id` INT NOT NULL,
  `field_definition_id` INT NOT NULL,
  `value` TEXT,
  `created_at` DATETIME,
  `updated_at` DATETIME,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`field_definition_id`) REFERENCES `field_definitions` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  FOREIGN KEY (`violation_id`) REFERENCES `violations` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings` (
  `id` INT AUTO_INCREMENT,
  `smtp_server` VARCHAR(255),
  `smtp_port` INT,
  `smtp_username` VARCHAR(255),
  `smtp_password` VARCHAR(255),
  `smtp_use_tls` TINYINT(1) DEFAULT 1,
  `smtp_from_email` VARCHAR(255),
  `smtp_from_name` VARCHAR(255),
  `notification_emails` TEXT,
  `enable_global_notifications` TINYINT(1) DEFAULT 0,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_by` INT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `violation_replies`;
CREATE TABLE `violation_replies` (
  `id` INT AUTO_INCREMENT,
  `violation_id` INT NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `response_text` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `ip_address` VARCHAR(50),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`violation_id`) REFERENCES `violations` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Creating index on violation_id and email combination
CREATE UNIQUE INDEX `idx_reply_violation_email` ON `violation_replies` (`violation_id`, `email`);

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT,
  `email` VARCHAR(120) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `is_admin` TINYINT(1) DEFAULT 0,
  `is_active` TINYINT(1) DEFAULT 0,
  `role` VARCHAR(50) DEFAULT 'user',
  `temp_password` VARCHAR(255),
  `temp_password_expiry` DATETIME,
  `created_at` DATETIME,
  `last_login` DATETIME,
  `failed_login_attempts` INT DEFAULT 0,
  `last_failed_login` DATETIME,
  `account_locked_until` DATETIME,
  `password_algorithm` VARCHAR(20) DEFAULT 'werkzeug',
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adding unique index for email
CREATE UNIQUE INDEX `idx_user_email` ON `users` (`email`);

DROP TABLE IF EXISTS `user_sessions`;
CREATE TABLE `user_sessions` (
  `id` INT AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `token` VARCHAR(64) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_activity` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` DATETIME NOT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `user_agent` VARCHAR(255),
  `ip_address` VARCHAR(45),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Creating meaningful indices for user sessions
CREATE UNIQUE INDEX `idx_session_token` ON `user_sessions` (`token`);
CREATE INDEX `idx_session_user_id` ON `user_sessions` (`user_id`);
CREATE INDEX `idx_session_expires` ON `user_sessions` (`expires_at`);

DROP TABLE IF EXISTS `violation_access_logs`;
CREATE TABLE `violation_access_logs` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `violation_id` INT NOT NULL,
  `ip_address` VARCHAR(50),
  `user_agent` VARCHAR(255),
  `accessed_at` DATETIME,
  `token` VARCHAR(255),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`violation_id`) REFERENCES `violations` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adding index on violation_id and token
CREATE INDEX `idx_access_log_violation` ON `violation_access_logs` (`violation_id`);
CREATE INDEX `idx_access_log_token` ON `violation_access_logs` (`token`);

DROP TABLE IF EXISTS `violations`;
CREATE TABLE `violations` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `public_id` VARCHAR(36),
  `reference` VARCHAR(50),
  `category` VARCHAR(255),
  `building` VARCHAR(255),
  `unit_number` VARCHAR(50),
  `incident_date` DATE,
  `incident_time` VARCHAR(20),
  `subject` VARCHAR(255),
  `details` TEXT,
  `created_at` DATETIME,
  `created_by` INT,
  `html_path` VARCHAR(255),
  `pdf_path` VARCHAR(255),
  `status` VARCHAR(64) NOT NULL,
  `resolved_at` DATETIME,
  `resolved_by` INT,
  `owner_property_manager_first_name` VARCHAR(100),
  `owner_property_manager_last_name` VARCHAR(100),
  `owner_property_manager_email` VARCHAR(255),
  `owner_property_manager_telephone` VARCHAR(50),
  `where_did` VARCHAR(100),
  `was_security_or_police_called` VARCHAR(100),
  `fine_levied` VARCHAR(100),
  `action_taken` TEXT,
  `tenant_first_name` VARCHAR(100),
  `tenant_last_name` VARCHAR(100),
  `tenant_email` VARCHAR(255),
  `tenant_phone` VARCHAR(50),
  `concierge_shift` VARCHAR(100),
  `noticed_by` VARCHAR(100),
  `people_called` VARCHAR(255),
  `actioned_by` VARCHAR(100),
  `people_involved` VARCHAR(255),
  `incident_details` TEXT,
  `attach_evidence` TEXT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`resolved_by`) REFERENCES `users` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Creating unique index on public_id
CREATE UNIQUE INDEX `idx_violation_public_id` ON `violations` (`public_id`);

DROP TABLE IF EXISTS `violation_status_log`;
CREATE TABLE `violation_status_log` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `violation_id` INT NOT NULL,
  `old_status` VARCHAR(64) NOT NULL,
  `new_status` VARCHAR(64) NOT NULL,
  `changed_by` VARCHAR(128) NOT NULL,
  `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`violation_id`) REFERENCES `violations` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adding index on violation_id for faster status log lookup
CREATE INDEX `idx_status_log_violation` ON `violation_status_log` (`violation_id`);

SET FOREIGN_KEY_CHECKS=1;