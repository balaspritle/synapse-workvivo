CREATE DATABASE pierce_cqna;

USE pierce_cqna;

CREATE TABLE game_reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  time TIME DEFAULT NULL,
  user_id bigint DEFAULT NULL,
  number_of_successive_correct_score VARCHAR(255) DEFAULT NULL,
  attempt INT DEFAULT NULL
);

CREATE TABLE quiz_data (
  id INT AUTO_INCREMENT PRIMARY KEY,
  question VARCHAR(255) DEFAULT NULL,
  option_1 VARCHAR(255) DEFAULT NULL,
  option_2 VARCHAR(255) DEFAULT NULL,
  option_3 VARCHAR(255) DEFAULT NULL,
  option_4 VARCHAR(255) DEFAULT NULL,
  answer INT DEFAULT NULL
);

CREATE TABLE user_not_satisfied (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  user_id bigint DEFAULT NULL,
  message_content VARCHAR(255) DEFAULT NULL
);

CREATE TABLE user_escalations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  user_id bigint DEFAULT NULL
);

CREATE TABLE user_comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  user_id bigint DEFAULT NULL,
  rating VARCHAR(255) DEFAULT NULL,
  comments VARCHAR(255) DEFAULT NULL
);

CREATE TABLE user_cache_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  time TIME DEFAULT NULL,
  user_id bigint DEFAULT NULL,
  question VARCHAR(255) DEFAULT NULL
);

CREATE TABLE artefacts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  attachment_id VARCHAR(255) DEFAULT NULL,
  s3_uri VARCHAR(255) DEFAULT NULL
);

CREATE TABLE email_with_attachment_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  time TIME DEFAULT NULL,
  user_id bigint DEFAULT NULL,
  attachment_id VARCHAR(255) DEFAULT NULL,
  filename VARCHAR(255) DEFAULT NULL
);

INSERT INTO `artefacts` (`id`, `attachment_id`, `s3_uri`) VALUES
(2, 'b4886989338076491', 's3://ihisartefacts/Group Business Travel Insurance Form.pdf'),
(3, 'b677356030463488', 's3://ihisartefacts/Payment Requisition Form.xlsx'),
(4, 'b3562295917315600', 's3://ihisartefacts/Hospital & Surgical Claim Form.pdf'),
(5, 'b277106861605434', 's3://ihisartefacts/DP Application.xlsx'),
(6, 'b1207430493280607', 's3://ihisartefacts/Letter of Indemnity (for LOG).pdf'),
(7, 'b1206132606917580', 's3://ihisartefacts/No Pay Leave Application.docx'),
(8, 'b497766425237332', 's3://ihisartefacts/IHiS Group Check In Attendees List.xlsx'),
(9, 'b378435634146856', 's3://ihisartefacts/TalentCapability Business Partners Team Listing.pdf'),
(10, 'b630218859209162', 's3://ihisartefacts/Udemy User Guide.pdf'),
(11, 'b1432235347624488', 's3://ihisartefacts/External Engagement Application Form.xlsx'),
(12, 'b255409003945195', 's3://ihisartefacts/Secondary Employment Application Form.xlsx'),
(13, 'b263077399797550', 's3://ihisartefacts/StaRS Policy Apr 2020 V1.2.pdf'),
(15, 'b813019073665148', 's3://ihisartefacts/Interview Assessment Form.docx'),
(16, 'b255206000641803', 's3://ihisartefacts/StaRS Form.docx'),
(18, 'b944941766577465', 's3://ihisartefacts/Gift Declaration Form.xlsx'),
(19, 'b1922055144831257', 's3://ihisartefacts/SuccessFactor Mobile App Extract.pdf'),
(20, 'b606787288233113', 's3://ihisartefacts/Dependent Hospitalisation and Surgical Claim Form.xlsx'),
(21, 'b254172327387280', 's3://ihisartefacts/SF Guide (For All).pdf');