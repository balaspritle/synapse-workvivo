CREATE DATABASE workvivo_cqna_iris;

USE workvivo_cqna_iris;

CREATE TABLE game_reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  time TIME DEFAULT NULL,
  user_id VARCHAR(255) DEFAULT NULL,
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
  user_id VARCHAR(255) DEFAULT NULL,
  message_content VARCHAR(255) DEFAULT NULL
);

CREATE TABLE user_escalations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  user_id VARCHAR(255) DEFAULT NULL
);

CREATE TABLE user_comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  user_id VARCHAR(255) DEFAULT NULL,
  rating VARCHAR(255) DEFAULT NULL,
  comments VARCHAR(255) DEFAULT NULL
);

CREATE TABLE user_cache_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE DEFAULT NULL,
  time TIME DEFAULT NULL,
  user_id VARCHAR(255) DEFAULT NULL,
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
  user_id VARCHAR(255) DEFAULT NULL,
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


INSERT INTO `quiz_data` (`id`, `question`, `option_1`, `option_2`, `option_3`, `option_4`, `answer`) VALUES
(1, 'How do I submit claims for mobile phone expenses?', 'I receive it in the form of fixed allowance in my payroll', 'I should submit Payment Requisition form before month end', NULL, NULL, 1),
(2, 'What does NHG stand for?', 'National Healthcare Group', 'National Health Group', 'National Human Group', 'National Hospital Group', 1),
(3, 'What purposes can I use my flexible benefits on?', 'For dental, health check and health related matters only ', 'For professional and recreational memberships only', 'For excess of medical expenses beyond my outpatient claim limit', 'It\'s flexible for my use on any benefits', 4),
(4, 'What is the official working hours in IHiS?', 'Mon-Thur: 8:30am to 6:00pm, Fri : 8.30am to 5.30pm', 'Mon-Thur: 8:30am to 6:00pm, Fri : 9am to 5.30pm', 'Mon-Thur: 9am to 6:30pm, Fri : 9am to 6.00pm', 'Mon-Fri: 9am to 6:00pm', 1),
(5, 'How do I setup my account with Udemy?', 'Access Udemy link from IHiS Academy portal', 'Contact HCM HRBP', 'Contact HCM Learning Partner', 'Request RO for access', 1),
(6, 'Where is the company shuttle bus waiting area at Serangoon North office?', 'Level 1 East lobby loading bay', 'Level 1 West lobby main entrance', 'Level 1 South lobby loading bay', 'Level 1 North lobby loading bay', 1),
(7, 'What is the name of the mobile application to submit our outpatient medical claims?', 'AON iCare app', 'Alliance iCare app', 'AIA iCare app', 'Healthway iCare app', 2),
(8, 'What is the name of IHiS CFO?', 'Ms Lee Kai Nee', 'Ms May Chew', 'Ms May Wee', 'Ms Carol Seah', 1),
(9, 'What is the name of IHiS CIO?', 'Mr Kevin Tay', 'Mr Seah Han Yong', 'Mr Rick Tan', 'Mr Huan Boon Kean', 3),
(10, 'What is Ms Ngiam Siew Ying\'s designation in IHiS?', 'CIO', 'CEO', 'GCEO', 'CTO', 2),
(11, 'Where can I find the IHiS Employee Handbook?', 'Via IHiS website on Internet', 'Via IHiS HCM site on Intranet', 'Via SuccessFactors portal', 'Via GRMS site on intranet', 2),
(12, 'How can I access the iLMS portal?', 'Via IHiS website on Internet', 'Via IHiS HCM site on Intranet', 'Via SuccessFactors portal', 'Via GRMS site on intranet', 2),
(13, 'How can I apply leave of absence?', 'Use Leave Application Form', 'Apply via SuccessFactors', 'Apply via SAP Employee Self Service', NULL, 2),
(14, 'How can I submit my GP clinic medical claims?', 'Submit via AON site', 'Submit via Alliance iCare app', 'Complete medical reimbursement form  and submit to HCM', NULL, 2),
(15, 'What is IHiS full-time employment work hours in a week?', '40hrs', '42hrs', '42.5hrs', '44hrs', 2),
(16, 'What does HCM stand for?', 'Human Change Management', 'Human Capital Management', 'Home Capital Management', 'Hope for Change Management', 2),
(17, 'What does NUHS stand for?', 'National Universal Healthcare System', 'National University Health System', 'National University Heathcare System', 'National Universal Health System', 2),
(18, 'What is the cap for IHiS outpatient medical claims per calendar year?', 'S$1,500', 'S$1,600', 'S$1,800', 'S$2,000', 2),
(19, 'When does iBallot open for application of Zoo passes?', 'Between 1st to 10th of the month', 'Between 8th to 14th of the month', 'On 1st week of the month', 'On last week of the month', 2),
(20, 'Where can I find the security PIN for door access at Serangoon North office?', 'Via SuccessFactors Authenticator app', 'On my employee ID card', 'Contact Corporate Admin', 'Contact HCM', 2),
(21, 'How can I obtain a locker in the SN office?', 'Contact HCM', 'Contact my department admin', 'Contact Corporate Admin', 'Contact my HOD', 3),
(22, 'How can I submit my transport claims?', 'Complete transport claim form and submit to HCM', 'Complete payment request form and submit to HCM', 'Submit via SAP Concur', NULL, 3),
(23, 'Who can I get my timelog code from?', 'HCM', 'Corporate Admin', 'My Project Manager', 'Corporate IT', 3),
(24, 'What does HRBP stand for?', 'Human Resource Business Panel', 'Headcount Reporting Business Programme', 'Human Resource Business Partner', 'Huge Rasberry Baked Pastry', 3),
(25, 'What does SingHealth stand for?', 'Singapore Healthcare Services', 'Singapore Healthcare System', 'Singapore Health Services', 'Singapore Health System', 3),
(26, 'What does FCL leave type stand for?', 'Future Computed Leave', 'Flexible Company Care Leave', 'Family Care Leave', 'Forward Carry Leave', 3),
(27, 'When was IHiS incepted?', 'Year 2000', 'Year 2004', 'Year 2008', 'Year 2012', 3),
(28, 'Where can I find my security PIN number to SuccessFactors portal?', 'On my employee ID card', 'Via Microsoft Authenticator app', 'Via SuccessFactors Authenticator app', 'Via SMS', 3),
(29, 'How many Assistant Chief Executives (ACE) do we have?', '2', '3', '4', '5', 3),
(30, 'Am I eligible to half day work on eve of all public holidays?', 'Only employees celebrating the festive will be eligible for half-day. ', 'Yes, as long as my RO approves it.', 'It is a default arrangement for all public holidays. ', 'It is not a default arrangement. I should wait for formal HCM announcements.', 4),
(31, 'How can I request for an extra monitor?', 'Contact HCM', 'Contact my department admin', 'Contact Corporate Admin', 'Create request via ITSM portal', 4),
(32, 'What are the 3 pick-up/drop-off locations for our company shuttle bus?', 'Buona Vista, Clementi and Dhoby Ghaut MRT stations', 'Yio Chu Kang, Choa Chu Kang and Serangoon MRT stations ', 'Yio Chu Kang, Serangoon and Commonwealth MRT stations', 'Yio Chu Kang, Serangoon and Outram MRT stations', 4),
(33, 'What is MVC in my payslip?', 'Maximum Value Component', 'Monthly Value Cash', 'Maximum Variable Component', 'Monthly Variable Component', 4),
(34, 'What is IHiS Financial Year period?', '1st Jan to 31st Dec', '1st Feb to 31st Jan', '1st Mar to 28th Feb', '1st Apr to 31st Mar', 4),
(35, 'Where can I update my vaccination status?', 'Inform HCM to update on behalf', 'Inform department admin to update on behalf', 'Update in SAP Employee Self Service', 'Update in SuccessFactors', 4),
(36, 'Where can I find my payslips?', 'Contact HCM Payroll', 'Contact HCM O&T team', 'Contact Finance', 'Login to SuccessFactors', 4),
(37, 'What is the general guideline to be eligible for a transfer of department/team?', 'I must have at least 12 months of service in my current team', 'I should have completed 24 months of service in my current team', 'I must have at least 2 rating in the last 2 years', 'My HOD must approve before I can apply', 2),
(38, 'When is IHiS regular payday?', 'on 10th of the month', 'on 1st of following month', 'on 25th of the month', 'on 1st of the month', 3),
(39, 'How can I apply for annual leave?', 'Via SuccessFactors app on my mobile', 'Via ESS', 'Fill in a form to apply with HCM', NULL, 1),
(40, 'What should I do to apply for medical/sick leave?', 'Inform my RO and apply medical leave through SuccessFactors.', 'Inform my department admin and apply medical leave through SuccessFactors.', 'Apply Medical Leave on SAP ESS and my RO will be informed.', NULL, 1),
(41, 'Can I claim for medical consultation while overseas?', 'Overseas outpatient medical claims is only applicable for General Practitioner in Johor Bahru, Malaysia.', 'Yes, as long is paid in cash.', 'Yes, I can claim under IHiS Hospitalisation insurance when warded overseas. ', NULL, 1),
(42, 'Does IHiS have a social media policy?', 'Yes', 'No', NULL, NULL, 1),
(43, 'What is the gift value for 3 years\' Long Service award recipients?', 'S$200', 'S$300', 'S$400', 'S$600', 1),
(44, 'What should I do if I want to take on a part time role outside of IHiS?', 'I should write an email to my RO for approval', 'I should declare any external employment or engagement to HCM and HOD', 'I should declare to HCM and HOD if my engagement are on weekdays', 'I do not need to declare as it is after office hours', 2),
(45, 'In our insurance coverage context, dependents are defined as:', 'Parents and siblings', 'Legally married spouse and children', 'Parents, siblings, legally married spouse and children', NULL, 2),
(46, 'What is the retirement age in Singapore as of Year 2022?', '62 years old', '63 years old', '65 years old', '55 years old', 2),
(47, 'Can I apply for Hospitalisation Leave when I\'m overseas?', 'Yes when with doctor\'s discharge summary', 'Yes but I must inform HCM before admission', 'No, foreign hospitalisation leave certification is not recognised', NULL, 3),
(48, 'What leave type should I use if I exhausted my Sick Leave due to Covid re-infection? ', 'Medical Leave only', 'Hospitalisation Leave if I have exhausted my Medical Leave quota', 'Unpaid Leave if I have exhausted my Medical Leave quota', 'Family Care Leave if I have exhausted my Medical Leave quota', 2),
(49, 'What is the gift value for 5 years\' Long Service award recipients?', 'S$200', 'S$300', 'S$400', 'S$600', 3),
(50, 'What is the gift value for 10 years\' Long Service award recipients?', 'S$200', 'S$300', 'S$400', 'S$600', 4),
(51, 'IHiS employee benefits are refreshed every 1 January of the year', 'True ', 'False', NULL, NULL, 1),
(52, 'What is IHiS Mission statement?', 'We digitise, connect and analyse Singapore’s health ecosystem.', 'We define, connect and analyse Singapore\'s health ecosystem.', 'We digitise, collaborate and analyse Singapore’s health ecosystem.', 'We integrate, connect and analyse Singapore’s health ecosystem.', 1),
(53, 'IHiS employee benefits are refreshed every 1 April of the year (financial year)', 'True ', 'False', NULL, NULL, 2),
(54, 'Which of these is one of IHiS new core values?', 'Innovation Through Teamwork', 'Agility with Speed', 'Mastery and Advocacy', 'Agility with Integrity', 4),
(55, 'How can I order a get well hamper for a colleague?', 'I should inform HCM to send the token on behalf.', 'I can purchase and claim at S$150 per gift.', 'I should inform Finance to send the token on behalf.', 'I can purchase and claim from department welfare fund.', 1),
(56, 'Is TCM medical certificate valid?', 'Yes as long is the TCM clinic and physicians are registered with the Singapore TCM Council', 'No TCM is not recognised', NULL, NULL, 1),
(57, 'How do I enrol my new born for IHiS medical coverage?', 'Contact my HRBP to enrol', 'Inform my department admin to trigger for enrolment', 'Update dependant\'s details in SuccessFactors to trigger enrolment', 'My dependants are not eligible for medical cover', 3),
(58, 'Who can I contact for issues in timelogging?', 'HCM HRBP', 'My RO', 'Corporate Admin', 'BSG Planning - PMR team', 4),
(59, 'Can I claim for my regular dental visit (e.g. polishing, scaling)?', 'Yes, under Outpatient Visit', 'Yes, by using the payment requisition form.', 'I don\'t have to claim as it\'s covered by the monthly flexi-benefit allowance', NULL, 3),
(60, 'Does IHiS medical benefits cover TCM treatment?', 'Yes', 'No', NULL, NULL, 1),
(61, 'What is the criteria to claim transport expenses as part of overtime claim?', 'After 6pm on weekdays', 'After 8pm on Mon to Thurs and after 7.30pm on Fri', 'After 9pm on Mon to Thurs and after 8.30pm on Fri', 'We can\'t claim transport as part of overtime', 3),
(62, 'What is the maximum annual leave each staff can carry forward to next year?', 'Max of 5 days', 'Max of 8 days', 'Max of 10 days', 'Max of 15 days', 3),
(63, 'Am I eligible for overtime payment if I work extra hours during weekdays?', 'Yes, all employees are eligible for Overtime Pay', 'Yes, because I am  under the non-exempt job grade', 'Yes, because I am on exempt job grade', NULL, 2),
(64, 'Where can I find a general directory of different department\'s contact point?', 'Iris - the IHiS chatbot', '\"IHiS Ask Me\" on the Intranet or Workplace', 'IHiS Receptionist', 'Outlook Address Book', 2),
(65, 'I joined IHiS in October 2022 and will be eligible for Corporate Bonus in December 2022. ', 'True ', 'False', NULL, NULL, 2),
(66, 'I can apply for Family Care Leave…', 'when I want to travel overseas', 'when I am accompanying my parents for their medical appointment', 'when I am given a medical certificate', 'when I don\'t feel like working', 2),
(67, 'Which of these is a milestone for Long Service Award?', 'After my 3 months probation', 'After 3 years of service', 'Only after 5 years of service', 'Only after 7 years of service', 2),
(68, 'Are my dependents eligible for IHiS medical coverage?', 'No, it\'s only for self', 'Yes, my parents are covered', 'Yes, my spouse and children are covered', NULL, 3),
(69, 'Can I claim transport expenses from home to external work locations?', 'Yes, only when I need to reach office before 8am.', 'No, we cannot claim for transport from home', 'Yes, I can claim if I am travelling to a site', 'We can only claim transport expenses when I have prior approval from my RO', 3),
(70, 'Can I post work related information on my personal social media accounts?', 'Yes', 'No', NULL, NULL, 2),
(71, 'How can I update my bank account details?', 'Via PPMS portal', 'Via SAP Employee Self Service portal', 'Via SuccessFactors', 'No self-service allowed. I should inform HCM O&T team', 3),
(72, 'Which of the following is not an insurance covered under IHiS benefits scheme?', 'Personal Accident Insurance ', 'Hospitalisation Insurance', 'Workmen Compensation', 'Dental Insurance', 4),
(73, 'When is IHiS Corporate Variable Bonus payout period?', 'On 15th of June each year', 'On 25th of June of each year', 'On 15th of December each year', 'On 25th of December each year', 3),
(74, 'When is IHiS Performance Bonus payout period?', '1st June of the year', '1st July of the year', 'Payroll date in June', 'Payroll date in July', 3),
(75, 'I have received a Chinese New Year gift from a vendor. I should…', 'Declare to HOD and keep the gift', 'Declare to HOD and HCM only if it\'s above $50 in value', 'Declare to HOD and HCM if it\'s above $1,000 in value', 'Declare to HCM and HOD regardless of value', 4),
(76, 'When is the annual IHiS salary increment held?', 'On 1st April each year', 'On 1st May each year', 'On 1st June each year', 'On 1st July each year', 4),
(77, 'Who should I contact when I need help with SuccessFactors Login?', 'Email to ihis.sfactors.enquiries@ihis.com.sg', 'Email to IHIS_SAP_Support@ihis1.com.sg', 'Email to ihis.hcmconnect@ihis.com.sg', 'Log a ticket with ITSM', 1),
(78, 'Who should I contact if my leave balance is incorrect?', 'Email to ihis.sfactors.enquiries@ihis.com.sg', 'Email to IHIS_SAP_Support@ihis1.com.sg', 'Email to ihis.hcmconnect@ihis.com.sg', 'Log a ticket with ITSM', 1),
(79, 'Which of the following is not a criteria for STaRS Bonus eligibility?', 'My referral must be hired for direct employment with IHIS.', 'My referral should stay in service for 6 months upon hire.', 'The scheme excludes part-time or contract positions of less than 1 year duration.', 'I can refer ex-IHiS staff who have left IHIS more than 2 years ago, under the scheme.', 1),
(80, 'Which of the following is a criteria for STaRS Bonus eligibility?', 'My referral must be hired for direct employment with IHIS.', 'My referral should stay in service for 3 months upon hire.', 'The scheme excludes part-time or contract positions of less than 1 year duration.', 'I can refer ex-IHiS staff who have left IHIS less than 2 years ago, under the scheme.', 3),
(81, 'Which of the following mode of transportation cannot be claimed under transport claims?', 'Strides Taxi', 'Comfort Taxi', 'GrabCar', 'Grab Hitch', 4),
(82, 'How do I update the reporting line of my team?', 'Raise request through HCM O&T team', 'Raise request through SuccessFactors', 'Raise request through Department Admin', 'Raise request through GRMS > CRO', 4),
(83, 'What is the mileage rate for   motorcyles in transport claims?', '$0.15/km', '$0.25/km', '$0.60/km', '$0.70/km', 1),
(84, 'Which of the following is not part of the welfare / staff benefits offered by IHiS?', 'Microsoft Employee Purchase Program', 'Fitness First Membership', 'Corporate Health Screening Rates', 'SCS Corporate Membership', 2),
(85, 'Which of the following is not the criteria for mandatory Compulsory Leave?', 'Employees nominated by HOD due to involvement in procurement activities.', 'All members of Finance and Payroll team.', 'All members of Legal & Procurement.', 'All employees who are Job Grade 8 and above.', 4),
(86, 'Which of the following leave types cannot be considered as part of Compliance Leave?', 'Annual Leave', 'Medical Leave', 'Training Leave', 'Examnation Leave', 3),
(87, 'Who is the external party providing the independant Whistle-blowing channel for IHiS?', 'Accenture', 'Deloitte', 'PWC', 'KPMG', 2),
(88, 'Which of the following does not constitute our flexi-work arrangements?', 'Work from Home', 'Bring-Your-Own-Device', 'Flexi Work Hours', 'Part-Time Work', 2),
(89, 'My Annual Leave entitlement for the year is …', '..prorated by the calendar year from my join date if it\'s the same year.', '..prorated by the financial year from my join date if it\'s the same year.', '..awarded in full regardless of when my join date is, in the same year.', NULL, 1),
(90, 'My Sick Leave entitlement for the year is…', '..prorated by the calendar year from my join date if it\'s the same year.', '..prorated by the calendar year from my join date if I have less than 6 months service in the year.', '..awarded in full regardless of when my join date is, in the same year.', NULL, 2),
(91, 'How many days of Family Care Leave does IHiS offer?', 'None', '3', '4', '5', 3),
(92, 'How many days of Family Care Leave can I take for parent-care purposes?', 'None', '2', '3', '4', 4),
(93, 'How do I claim for my birthday leave?', 'I can apply as Annual Leave and indicate as \"Birthday Leave\".', 'I can apply under Family Care Leave category for Birthday Leave.', 'I have to request HCM to grant me the quota on my birthday month.', 'I can make arrangement with my RO to clear a day as Birthday Leave.', 2),
(94, 'Mid-term No Pay Leave is defined as…', '..unpaid leave of less than 15 consecutive calendar days.', '..unpaid leave of more than 15 consecutive calendar days.', '..unpaid leave between 15 consecutive days to 3 months.', '..unpaid leave of more than 3 months.', 2);