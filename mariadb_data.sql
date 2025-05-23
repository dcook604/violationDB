-- MariaDB Data Migration from SQLite
-- Generated on: 2025-05-05 03:26:18
-- This script migrates data from SQLite to MariaDB

SET FOREIGN_KEY_CHECKS=0;
SET UNIQUE_CHECKS=0;
SET AUTOCOMMIT=0;

-- Table: field_definitions
-- Total rows: 29
TRUNCATE TABLE `field_definitions`;
INSERT INTO `field_definitions` (`id`, `name`, `label`, `type`, `required`, `options`, `order`, `active`, `validation`, `created_at`, `updated_at`, `grid_column`) VALUES
(1, 'Entry Date', 'Entry Date', 'date', 1, '', 0, 1, '', '2025-05-01 19:37:39', '2025-05-01 22:37:58', 3),
(2, 'Category', 'Category', 'select', 1, 'Balcony - Items Thrown, Balcony Storage, Bike/Rollerblade in Lobby/Elevator, Broken Window, Brust Pipe, Bylaw Violations, Car Break-In, Damage to Common Area, Elevator, Illegal Move, Illegal Dumping, Pet Issue, Parking Violation, Short Term Rental (AirBNB/VRBO)', 0, 1, '', '2025-05-01 19:39:39', '2025-05-02 19:18:14', 4),
(3, 'Building', 'Building', 'select', 1, 'Apartment, Townhouse', 0, 1, '', '2025-05-01 19:40:54', '2025-05-01 19:44:19', 4),
(4, 'Unit:', 'Unit', 'number', 1, '', 0, 1, '', '2025-05-01 19:42:27', '2025-05-01 22:38:12', 3),
(5, 'Incident Area:', 'Incident Area', 'text', 1, '', 0, 1, '', '2025-05-01 19:45:01', '2025-05-01 22:38:18', 6),
(6, 'Concierge Shift:', 'Concierge Shift:', 'text', 1, '', 0, 1, '', '2025-05-01 19:45:21', '2025-05-01 19:46:48', 3),
(7, 'Time:', 'Time:', 'time', 1, '', 0, 1, '', '2025-05-01 19:49:12', '2025-05-01 19:49:12', 3),
(8, 'People Involved:', 'People Involved:', 'text', 0, '', 0, 1, '', '2025-05-01 19:49:44', '2025-05-01 19:49:44', 6),
(9, 'Noticed By:', 'Noticed By:', 'text', 0, '', 0, 1, '', '2025-05-01 19:50:03', '2025-05-01 19:50:03', 3),
(10, 'People Called:', 'People Called:', 'text', 0, '', 0, 1, '', '2025-05-01 19:50:27', '2025-05-01 19:50:27', 4),
(11, 'Actioned By:', 'Name Actioned By', 'text', 1, '', 0, 1, '', '2025-05-01 19:50:36', '2025-05-02 19:21:13', 6),
(12, 'Incident Details:', 'Incident Details:', 'text', 1, '', 0, 1, '', '2025-05-01 19:51:09', '2025-05-01 19:51:09', 0),
(13, 'Initial Action Taken:', 'Initial Action Taken:', 'text', 1, '', 0, 1, '', '2025-05-01 19:51:27', '2025-05-01 19:51:27', 0),
(14, 'Owner Email:', 'Owner Email:', 'email', 0, '', 0, 1, '', '2025-05-01 19:52:03', '2025-05-01 19:52:03', 4),
(15, 'Attach Evidence:', 'Attach Evidence:', 'file', 0, '', 0, 1, '{"maxFiles":5,"maxSizePerFile":5,"allowedTypes":["image/jpeg","image/png","image/gif"]}', '2025-05-01 20:21:18', '2025-05-01 20:21:18', 0),
(16, 'Status', 'Status', 'select', 0, 'Open, Closed-No Fine Issued, Closed-Fines Issued, Pending Owner Response, Pending Council Response, Reject', 0, 1, '', '2025-05-01 22:40:25', '2025-05-02 19:24:57', 6),
(17, 'Fine', 'Fine Levied', 'select', 0, '$50.00, $100.00, $200.00, $1000.00', 0, 1, '', '2025-05-02 19:18:46', '2025-05-02 19:18:46', 0),
(18, 'Tenant Email', 'Tenant Email', 'email', 0, '', 0, 1, '', '2025-05-02 19:22:09', '2025-05-02 19:22:09', 4),
(19, '2nd Owner Email', '2nd Owner Email (Joint Owner)', 'email', 0, '', 0, 1, '', '2025-05-02 19:23:01', '2025-05-02 19:23:14', 4),
(20, '2nd Tenant Email', '2nd Tenant Email', 'email', 0, '', 0, 1, '', '2025-05-02 19:23:41', '2025-05-02 19:23:41', 4),
(21, 'Location', 'Where Did Violation Happen', 'select', 1, 'Unit, Recycle/Garbage Room, Parkade, Interior Common Area, Exterior Common Area, Garden Level, Park', 0, 1, '', '2025-05-02 19:33:27', '2025-05-02 19:33:27', 6),
(22, 'Security', 'Was Security Called', 'select', 1, 'Yes, No', 0, 1, '', '2025-05-02 19:34:09', '2025-05-02 19:34:09', 3),
(23, 'Police', 'Police Notified (Report Filed)', 'select', 0, 'Yes, No', 0, 1, '', '2025-05-02 19:34:32', '2025-05-02 19:34:32', 0),
(24, 'Police File No', 'Police File No', 'text', 0, '', 0, 1, '', '2025-05-02 19:34:59', '2025-05-02 19:34:59', 3),
(25, 'Owner Telephone', 'Owner Telephone', 'number', 0, '', 0, 1, '', '2025-05-02 19:35:38', '2025-05-02 19:35:38', 3),
(26, 'Tenant Telephone', 'Tenant Telephone', 'number', 0, '', 0, 1, '', '2025-05-02 19:35:52', '2025-05-02 19:35:52', 3),
(27, 'Preferred Contact', 'Preferred Contact', 'select', 0, 'Email, Text, Phone', 0, 1, '', '2025-05-02 19:36:35', '2025-05-02 19:36:35', 3),
(28, 'Property Management Company Contact', 'Property Management Company Contact', 'email', 0, '', 0, 1, '', '2025-05-02 19:37:18', '2025-05-02 19:37:18', 3),
(29, 'Rental Property Management Agent Name', 'Rental Property Management Agent Name', 'text', 0, '', 0, 1, '', '2025-05-02 19:37:44', '2025-05-02 19:37:44', 3);

-- Table: violation_field_values
-- Total rows: 132
TRUNCATE TABLE `violation_field_values`;
INSERT INTO `violation_field_values` (`id`, `violation_id`, `field_definition_id`, `value`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 'test@example.com', '2025-05-01 15:33:06', '2025-05-01 15:33:06'),
(2, 2, 1, 'test@example.com', '2025-05-01 15:34:12', '2025-05-01 15:34:12'),
(3, 3, 1, 'test@example.com', '2025-05-01 15:35:36', '2025-05-01 15:35:36'),
(4, 4, 1, 'test@example.com', '2025-05-01 15:42:42', '2025-05-01 15:42:42'),
(5, 5, 1, 'test@example.com', '2025-05-01 15:51:18', '2025-05-01 15:51:18'),
(6, 7, 1, '2025-05-06', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(7, 7, 2, 'Balcony Storage', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(8, 7, 3, 'Townhouse', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(9, 7, 4, '1105', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(10, 7, 5, 'test', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(11, 7, 6, 'test', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(12, 7, 7, '01:44', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(13, 7, 8, 'test', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(14, 7, 9, 'test', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(15, 7, 10, 'test', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(16, 7, 11, 'test', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(17, 7, 12, 'testtesttesttesttesttest', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(18, 7, 13, 'testtesttesttesttest', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(19, 7, 14, 'danielcook111@gmail.com', '2025-05-01 20:54:41', '2025-05-01 20:54:41'),
(20, 7, 15, 'violation_7/0412ae982dc24e3da13062e30402816b.jpg', '2025-05-01 20:54:41', '2025-05-01 20:54:42'),
(21, 8, 1, '2025-05-02', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(22, 8, 2, 'Elevator', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(23, 8, 3, 'Apartment', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(24, 8, 4, '1105', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(25, 8, 5, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(26, 8, 6, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(27, 8, 7, '19:29', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(28, 8, 8, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(29, 8, 9, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(30, 8, 10, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(31, 8, 11, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(32, 8, 12, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(33, 8, 13, 'test', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(34, 8, 14, 'dcook@spectrum4.ca', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(35, 8, 15, '', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(36, 8, 16, 'Open', '2025-05-02 13:30:05', '2025-05-02 13:30:05'),
(37, 9, 1, '2025-04-27', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(38, 9, 2, 'Balcony - Items Thrown', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(39, 9, 3, 'Apartment', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(40, 9, 4, '5005', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(41, 9, 5, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(42, 9, 6, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(43, 9, 7, '21:13', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(44, 9, 8, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(45, 9, 9, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(46, 9, 10, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(47, 9, 11, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(48, 9, 12, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(49, 9, 13, 'testing 123', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(50, 9, 14, 'danielcook111@gmail.com', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(51, 9, 15, '', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(52, 9, 16, 'Open', '2025-05-02 15:13:05', '2025-05-02 15:13:05'),
(53, 10, 1, '2025-04-29', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(54, 10, 2, 'Elevator', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(55, 10, 3, 'Apartment', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(56, 10, 4, '1111', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(57, 10, 5, 'testtesttesttest', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(58, 10, 6, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(59, 10, 7, '20:23', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(60, 10, 8, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(61, 10, 9, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(62, 10, 10, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(63, 10, 11, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(64, 10, 12, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(65, 10, 13, 'test', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(66, 10, 14, 'danielcook111@gmail.com', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(67, 10, 15, '', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(68, 10, 16, 'Open', '2025-05-02 15:22:37', '2025-05-02 15:22:37'),
(69, 11, 1, '2025-05-06', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(70, 11, 2, 'Balcony - Items Thrown', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(71, 11, 3, 'Townhouse', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(72, 11, 4, '2222', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(73, 11, 5, 'asdasdasdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(74, 11, 6, 'asdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(75, 11, 7, '00:32', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(76, 11, 8, 'asdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(77, 11, 9, '', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(78, 11, 10, 'asdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(79, 11, 11, 'asdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(80, 11, 12, 'asdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(81, 11, 13, 'asdasd', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(82, 11, 14, 'danielcook111@gmail.com', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(83, 11, 15, '', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(84, 11, 16, 'Open', '2025-05-02 15:47:26', '2025-05-02 15:47:26'),
(85, 12, 1, '2025-05-05', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(86, 12, 2, 'Balcony - Items Thrown', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(87, 12, 3, 'Apartment', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(88, 12, 4, '1111', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(89, 12, 5, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(90, 12, 6, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(91, 12, 7, '11:13', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(92, 12, 8, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(93, 12, 9, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(94, 12, 10, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(95, 12, 11, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(96, 12, 12, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(97, 12, 13, 'asdasdas', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(98, 12, 14, 'danielcook111@gmail.com', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(99, 12, 15, '', '2025-05-02 16:13:52', '2025-05-02 16:13:52'),
(100, 12, 16, 'Open', '2025-05-02 16:13:52', '2025-05-02 16:13:52');
INSERT INTO `violation_field_values` (`id`, `violation_id`, `field_definition_id`, `value`, `created_at`, `updated_at`) VALUES
(101, 13, 1, '2025-05-06', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(102, 13, 2, 'Broken Window', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(103, 13, 3, 'Townhouse', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(104, 13, 4, '2211', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(105, 13, 5, 'asdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(106, 13, 6, 'asdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(107, 13, 7, '13:13', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(108, 13, 8, 'asdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(109, 13, 9, 'asdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(110, 13, 10, 'asdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(111, 13, 11, 'asdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(112, 13, 12, 'asdasdasasdasdasasdasdasasdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(113, 13, 13, 'asdasdasasdasdasasdasdas', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(114, 13, 14, 'danielcook111@gmail.com', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(115, 13, 15, '', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(116, 13, 16, 'Open', '2025-05-02 17:13:18', '2025-05-02 17:13:18'),
(117, 14, 1, '2025-05-06', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(118, 14, 2, 'Broken Window', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(119, 14, 3, 'Townhouse', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(120, 14, 4, '2211', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(121, 14, 5, 'asdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(122, 14, 6, 'asdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(123, 14, 7, '13:13', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(124, 14, 8, 'asdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(125, 14, 9, 'asdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(126, 14, 10, 'asdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(127, 14, 11, 'asdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(128, 14, 12, 'asdasdasasdasdasasdasdasasdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(129, 14, 13, 'asdasdasasdasdasasdasdas', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(130, 14, 14, 'danielcook111@gmail.com', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(131, 14, 15, '', '2025-05-02 17:13:28', '2025-05-02 17:13:28'),
(132, 14, 16, 'Open', '2025-05-02 17:13:28', '2025-05-02 17:13:28');

-- Table: settings
-- Total rows: 1
TRUNCATE TABLE `settings`;
INSERT INTO `settings` (`id`, `smtp_server`, `smtp_port`, `smtp_username`, `smtp_password`, `smtp_use_tls`, `smtp_from_email`, `smtp_from_name`, `notification_emails`, `enable_global_notifications`, `updated_at`, `updated_by`) VALUES
(1, 'mail.smtp2go.com', 2525, 'spectrum4.ca', '1DXzEJY4XqySY55z', 0, 'noreply@spectrum4.ca', 'Spectrum 4 Violation System', 'danielcook111@gmail.com,dcook@spectrum4.ca', 0, '2025-05-01 19:56:42', 1);

-- Table: violation_replies
-- Total rows: 2
TRUNCATE TABLE `violation_replies`;
INSERT INTO `violation_replies` (`id`, `violation_id`, `email`, `response_text`, `created_at`, `ip_address`) VALUES
(1, 8, 'danielcook111@gmail.com', 'testest', '2025-05-02 13:31:30', '172.16.16.26'),
(2, 8, 'test@test.com', 'asdds', '2025-05-02 13:54:07', '172.16.16.26');

-- Table: users
-- Total rows: 3
TRUNCATE TABLE `users`;
INSERT INTO `users` (`id`, `email`, `password_hash`, `is_admin`, `is_active`, `role`, `temp_password`, `temp_password_expiry`, `created_at`, `last_login`, `failed_login_attempts`, `last_failed_login`, `account_locked_until`, `password_algorithm`, `first_name`, `last_name`) VALUES
(1, 'admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$IuKDYCjddlNMOXU+Xug+PA$ZWOKmJ8/2/OzGUxQHKVyxwzct41q+llf1tMHVSmujow', 1, 1, 'admin', NULL, NULL, '2025-05-01 15:33:05', '2025-05-04 23:49:44', 0, '2025-05-02 13:23:24', NULL, 'argon2', 'Daniel', 'Cook'),
(2, 'test@example.com', 'pbkdf2:sha256:600000$ZWkSIquPS7xxrKef$33c7193d1741070258e303839b77bde38b5da4b7819c2650507de4857c2c92dc', 1, 1, 'admin', NULL, NULL, '2025-05-01 17:05:55', NULL, 0, NULL, NULL, 'werkzeug', NULL, NULL),
(3, 'jennifer@test.com', 'pbkdf2:sha256:600000$Z5BzrKXjZFm9MDsK$b9d0ff5522e4500207bac2eebf6557d2ea6f4e882eaea8240e284048287659ce', 0, 1, 'user', NULL, NULL, '2025-05-01 17:19:00', NULL, 0, NULL, NULL, 'werkzeug', NULL, NULL);

-- Table: user_sessions
-- Total rows: 18
TRUNCATE TABLE `user_sessions`;
INSERT INTO `user_sessions` (`id`, `user_id`, `token`, `created_at`, `last_activity`, `expires_at`, `is_active`, `user_agent`, `ip_address`) VALUES
(1, 1, '117dd65c-f91e-450d-8213-7b4fcd7cc0a4', '2025-05-01 22:36:42', '2025-05-01 22:44:46', '2025-05-02 22:36:42', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '127.0.0.1'),
(2, 1, 'dfca9d29-aa57-4990-abac-8b153252940e', '2025-05-02 13:03:25', '2025-05-02 13:03:25', '2025-05-03 13:03:25', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '127.0.0.1'),
(3, 1, '0d92c199-d4f0-43a9-8579-664af7a4366f', '2025-05-02 13:07:47', '2025-05-02 13:07:47', '2025-05-03 13:07:47', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '127.0.0.1'),
(4, 1, '0f5170f4-52be-4938-a32c-5c41e3a8d210', '2025-05-02 13:17:22', '2025-05-02 13:17:22', '2025-05-03 13:17:22', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '127.0.0.1'),
(5, 1, '88894434-6f75-4b76-a7ff-c262ced5cf43', '2025-05-02 13:18:05', '2025-05-02 13:18:05', '2025-05-03 13:18:05', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '127.0.0.1'),
(6, 1, 'eca203b5-004d-4538-b1e6-b304077cccd0', '2025-05-02 13:20:30', '2025-05-02 13:20:30', '2025-05-03 13:20:30', 0, 'python-requests/2.32.3', '127.0.0.1'),
(7, 1, '692480ac-9993-4ff6-b912-a7b693d705e4', '2025-05-02 13:23:44', '2025-05-02 13:23:44', '2025-05-03 13:23:44', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0', '127.0.0.1'),
(8, 1, '7c779f52-bc7d-42d2-944c-470b65e45e1f', '2025-05-02 13:24:22', '2025-05-02 13:24:22', '2025-05-03 13:24:22', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0', '127.0.0.1'),
(9, 1, 'de1ae46b-adec-49f9-b122-f416e25c7509', '2025-05-02 13:26:53', '2025-05-02 14:08:31', '2025-05-03 13:26:53', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(10, 1, '0a5ae06d-e054-48d3-9b40-355bc546895b', '2025-05-02 14:12:34', '2025-05-02 14:42:25', '2025-05-03 14:12:34', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(11, 1, 'f54c44b9-4a38-4b9f-a851-fd69bd5af805', '2025-05-02 15:02:57', '2025-05-02 15:50:29', '2025-05-03 15:02:57', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(12, 1, 'ab5b38ee-a20d-4676-8e4c-bd436b74e3a1', '2025-05-02 16:13:23', '2025-05-02 16:37:06', '2025-05-03 16:13:23', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(13, 1, '9f701121-b93f-4ebb-bb57-fc2142ea81f7', '2025-05-02 16:42:57', '2025-05-02 16:44:13', '2025-05-03 16:42:57', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(14, 1, '183c69ad-db86-49d0-9a0c-0a74d1091b82', '2025-05-02 17:11:45', '2025-05-02 17:14:00', '2025-05-03 17:11:45', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(15, 1, '4213683c-7f60-4b64-a3d8-1ff3be128577', '2025-05-02 17:18:29', '2025-05-02 18:59:25', '2025-05-03 17:18:29', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(16, 1, '4e29e0ac-c022-4b76-b59f-a77f72fa22f2', '2025-05-02 19:02:37', '2025-05-02 19:43:52', '2025-05-03 19:02:37', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(17, 1, '70bb1873-ae6d-4862-8a6f-04ed83486040', '2025-05-04 22:46:27', '2025-05-04 23:49:14', '2025-05-05 22:46:27', 0, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26'),
(18, 1, '980b0dc4-f691-4ffd-a95d-c6653b4f64cf', '2025-05-04 23:49:44', '2025-05-05 02:24:15', '2025-05-05 23:49:44', 1, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '172.16.16.26');

-- Table: violation_access_logs
-- Total rows: 2
TRUNCATE TABLE `violation_access_logs`;
INSERT INTO `violation_access_logs` (`id`, `violation_id`, `ip_address`, `user_agent`, `accessed_at`, `token`) VALUES
(1, 13, '172.16.16.111', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/136.0.7103.56 Mobile/15E148 Safari/604.1', '2025-05-02 18:29:36', 'eyJ2aW9sYXRpb25faWQiOjEzLCJjcmVhdGVkIjoxNzQ2MjA1OTk5fQ.aBT9Lw.BLaf277oaF8xEi43btaiEduukIc'),
(2, 14, '172.16.16.26', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', '2025-05-02 19:12:59', 'eyJ2aW9sYXRpb25faWQiOjE0LCJjcmVhdGVkIjoxNzQ2MjA2MDA4fQ.aBT9OA.56W1xQbqBnzr81_Dd-fDCesargk');

COMMIT;
SET UNIQUE_CHECKS=1;
SET FOREIGN_KEY_CHECKS=1;