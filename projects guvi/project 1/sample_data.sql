-- =======================================================================
-- Project: Sales Intelligence Hub (Branch-Based Sales Management System)
-- Deliverable: Sample Data Insertion
-- File: sample_data.sql
-- =======================================================================

USE sales_management_db;

-- Disable foreign key checks for clean initialization
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE payment_splits;
TRUNCATE TABLE customer_sales;
TRUNCATE TABLE users;
TRUNCATE TABLE branches;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------
-- 1. Insert Branches
-- -----------------------------------------------------------------------
INSERT INTO branches (branch_id, branch_name, branch_admin_name) VALUES
(1, 'Chennai', 'Arun Kumar'),
(2, 'Delhi', 'Priya Sharma'),
(3, 'Bangalore', 'Rajesh Nair'),
(4, 'Mumbai', 'Sneha Patil'),
(5, 'Hyderabad', 'Vikram Reddy');

-- -----------------------------------------------------------------------
-- 2. Insert Users (Role-Based Access)
-- -----------------------------------------------------------------------
INSERT INTO users (user_id, username, password, branch_id, role, email) VALUES
(1, 'super_admin', 'admin123', NULL, 'Super Admin', 'superadmin@saleshub.com'),
(2, 'chennai_admin', 'admin123', 1, 'Admin', 'chennai@saleshub.com'),
(3, 'delhi_admin', 'admin123', 2, 'Admin', 'delhi@saleshub.com'),
(4, 'bangalore_admin', 'admin123', 3, 'Admin', 'bangalore@saleshub.com'),
(5, 'mumbai_admin', 'admin123', 4, 'Admin', 'mumbai@saleshub.com'),
(6, 'hyderabad_admin', 'admin123', 5, 'Admin', 'hyderabad@saleshub.com');

-- -----------------------------------------------------------------------
-- 3. Insert Customer Sales Records
-- (received_amount initialized to 0; triggers will populate it when payment_splits are inserted)
-- -----------------------------------------------------------------------
INSERT INTO customer_sales (sale_id, branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status) VALUES
(1, 1, '2026-08-10', 'Ramesh Krishnan', '9876543210', 'Data Science', 45000.00, 0.00, 'Open'),
(2, 1, '2026-08-15', 'Suresh Raina', '9876543211', 'Data Analytics', 35000.00, 0.00, 'Open'),
(3, 1, '2026-09-02', 'Meenakshi Sundaram', '9876543212', 'Full Stack Development', 60000.00, 0.00, 'Open'),
(4, 1, '2026-09-20', 'Karthik Subramanian', '9876543213', 'Business Analytics', 40000.00, 0.00, 'Open'),
(5, 2, '2026-08-18', 'Pooja Verma', '9876543214', 'Data Science', 50000.00, 0.00, 'Open'),
(6, 2, '2026-09-05', 'Amitabh Malhotra', '9876543215', 'Full Stack Development', 65000.00, 0.00, 'Open'),
(7, 2, '2026-10-01', 'Neha Kapoor', '9876543216', 'Data Analytics', 35000.00, 0.00, 'Open'),
(8, 3, '2026-08-25', 'Anand Kulkarni', '9876543217', 'Data Science', 55000.00, 0.00, 'Open'),
(9, 3, '2026-09-12', 'Deepa Iyer', '9876543218', 'Business Analytics', 42000.00, 0.00, 'Open'),
(10, 3, '2026-10-04', 'Gautam Menon', '9876543219', 'Full Stack Development', 70000.00, 0.00, 'Open'),
(11, 4, '2026-08-30', 'Rohit Deshmukh', '9876543220', 'Data Analytics', 38000.00, 0.00, 'Open'),
(12, 4, '2026-09-18', 'Tanvi Joshi', '9876543221', 'Data Science', 52000.00, 0.00, 'Open'),
(13, 4, '2026-10-08', 'Kunal Shinde', '9876543222', 'Business Analytics', 45000.00, 0.00, 'Open'),
(14, 5, '2026-09-01', 'Sravani Rao', '9876543223', 'Full Stack Development', 65000.00, 0.00, 'Open'),
(15, 5, '2026-09-22', 'Venkatesh Babu', '9876543224', 'Data Science', 48000.00, 0.00, 'Open'),
(16, 5, '2026-10-11', 'Harika Chowdary', '9876543225', 'Data Analytics', 36000.00, 0.00, 'Open'),
(17, 1, '2026-10-15', 'Divya Bharathi', '9876543226', 'Full Stack Development', 58000.00, 0.00, 'Open'),
(18, 2, '2026-10-18', 'Rahul Saxena', '9876543227', 'Business Analytics', 44000.00, 0.00, 'Open');

-- -----------------------------------------------------------------------
-- 4. Insert Payment Splits
-- (Triggers will automatically update received_amount and set status to 'Close' when paid in full)
-- -----------------------------------------------------------------------
INSERT INTO payment_splits (payment_id, sale_id, payment_date, amount_paid, payment_method) VALUES
-- Sale 1: Ramesh (Gross: 45000) -> 20000 UPI + 25000 Card = 45000 (Fully Paid -> Close)
(1, 1, '2026-08-10', 20000.00, 'UPI'),
(2, 1, '2026-08-20', 25000.00, 'Card'),

-- Sale 2: Suresh (Gross: 35000) -> 15000 Cash + 10000 UPI = 25000 (Pending: 10000 -> Open)
(3, 2, '2026-08-15', 15000.00, 'Cash'),
(4, 2, '2026-08-30', 10000.00, 'UPI'),

-- Sale 3: Meenakshi (Gross: 60000) -> 30000 Card + 30000 UPI = 60000 (Fully Paid -> Close)
(5, 3, '2026-09-02', 30000.00, 'Card'),
(6, 3, '2026-09-15', 30000.00, 'UPI'),

-- Sale 4: Karthik (Gross: 40000) -> 20000 Cash = 20000 (Pending: 20000 -> Open)
(7, 4, '2026-09-20', 20000.00, 'Cash'),

-- Sale 5: Pooja (Gross: 50000) -> 25000 UPI + 25000 Card = 50000 (Fully Paid -> Close)
(8, 5, '2026-08-18', 25000.00, 'UPI'),
(9, 5, '2026-09-01', 25000.00, 'Card'),

-- Sale 6: Amitabh (Gross: 65000) -> 35000 Card + 15000 UPI = 50000 (Pending: 15000 -> Open)
(10, 6, '2026-09-05', 35000.00, 'Card'),
(11, 6, '2026-09-25', 15000.00, 'UPI'),

-- Sale 7: Neha (Gross: 35000) -> 35000 UPI = 35000 (Fully Paid -> Close)
(12, 7, '2026-10-01', 35000.00, 'UPI'),

-- Sale 8: Anand (Gross: 55000) -> 25000 Cash + 20000 UPI = 45000 (Pending: 10000 -> Open)
(13, 8, '2026-08-25', 25000.00, 'Cash'),
(14, 8, '2026-09-10', 20000.00, 'UPI'),

-- Sale 9: Deepa (Gross: 42000) -> 42000 Card = 42000 (Fully Paid -> Close)
(15, 9, '2026-09-12', 42000.00, 'Card'),

-- Sale 10: Gautam (Gross: 70000) -> 40000 UPI + 15000 Cash = 55000 (Pending: 15000 -> Open)
(16, 10, '2026-10-04', 40000.00, 'UPI'),
(17, 10, '2026-10-12', 15000.00, 'Cash'),

-- Sale 11: Rohit (Gross: 38000) -> 38000 Cash = 38000 (Fully Paid -> Close)
(18, 11, '2026-08-30', 38000.00, 'Cash'),

-- Sale 12: Tanvi (Gross: 52000) -> 25000 Card + 20000 UPI = 45000 (Pending: 7000 -> Open)
(19, 12, '2026-09-18', 25000.00, 'Card'),
(20, 12, '2026-10-02', 20000.00, 'UPI'),

-- Sale 13: Kunal (Gross: 45000) -> 45000 Card = 45000 (Fully Paid -> Close)
(21, 13, '2026-10-08', 45000.00, 'Card'),

-- Sale 14: Sravani (Gross: 65000) -> 30000 UPI + 25000 Cash = 55000 (Pending: 10000 -> Open)
(22, 14, '2026-09-01', 30000.00, 'UPI'),
(23, 14, '2026-09-18', 25000.00, 'Cash'),

-- Sale 15: Venkatesh (Gross: 48000) -> 48000 UPI = 48000 (Fully Paid -> Close)
(24, 15, '2026-09-22', 48000.00, 'UPI'),

-- Sale 16: Harika (Gross: 36000) -> 20000 Card = 20000 (Pending: 16000 -> Open)
(25, 16, '2026-10-11', 20000.00, 'Card'),

-- Sale 17: Divya (Gross: 58000) -> 58000 UPI = 58000 (Fully Paid -> Close)
(26, 17, '2026-10-15', 58000.00, 'UPI'),

-- Sale 18: Rahul (Gross: 44000) -> 20000 Cash + 15000 Card = 35000 (Pending: 9000 -> Open)
(27, 18, '2026-10-18', 20000.00, 'Cash'),
(28, 18, '2026-10-21', 15000.00, 'Card');
