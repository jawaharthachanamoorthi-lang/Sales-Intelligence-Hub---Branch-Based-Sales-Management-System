-- =======================================================================
-- Project Title: Sales Intelligence Hub (Sales Analytics & Financial Tracking)
-- Deliverable: Master Database Management Script
-- File: data_base_management.sql
-- =======================================================================

-- -----------------------------------------------------------------------
-- STEP 1: CREATE DATABASE
-- -----------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS sales_management_db;
USE sales_management_db;

-- -----------------------------------------------------------------------
-- STEP 2: CREATE RELATIONAL TABLES WITH CONSTRAINTS
-- -----------------------------------------------------------------------

-- 1. Branches Table
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    branch_admin_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Customer Sales Table (Main Financial Table)
CREATE TABLE IF NOT EXISTS customer_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT NOT NULL,
    date DATE NOT NULL,
    name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15) NOT NULL UNIQUE,
    product_name VARCHAR(30) NOT NULL,
    gross_sales DECIMAL(12,2) NOT NULL CHECK (gross_sales >= 0),
    received_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK (received_amount >= 0),
    pending_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('Open', 'Close') NOT NULL DEFAULT 'Open',
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Payment Splits Table
CREATE TABLE IF NOT EXISTS payment_splits (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL CHECK (amount_paid > 0),
    payment_method ENUM('Cash', 'UPI', 'Card') NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Users Table (Role-Based Access)
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    branch_id INT NULL,
    role ENUM('Super Admin', 'Admin') NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------
-- STEP 3: AUTOMATION LOGIC (TRIGGERS)
-- -----------------------------------------------------------------------
DELIMITER //

DROP TRIGGER IF EXISTS trg_payment_splits_after_insert //
DROP TRIGGER IF EXISTS trg_payment_splits_after_update //
DROP TRIGGER IF EXISTS trg_payment_splits_after_delete //
DROP TRIGGER IF EXISTS update_received_amount //

-- Trigger 1: AFTER INSERT on payment_splits
CREATE TRIGGER trg_payment_splits_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_paid DECIMAL(12,2);
    
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;
    
    UPDATE customer_sales
    SET received_amount = v_total_paid,
        status = CASE 
            WHEN gross_sales <= v_total_paid THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END //

-- Trigger 2: AFTER UPDATE on payment_splits
CREATE TRIGGER trg_payment_splits_after_update
AFTER UPDATE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_new DECIMAL(12,2);
    DECLARE v_total_old DECIMAL(12,2);
    
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_new
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;
    
    UPDATE customer_sales
    SET received_amount = v_total_new,
        status = CASE 
            WHEN gross_sales <= v_total_new THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
    
    IF OLD.sale_id <> NEW.sale_id THEN
        SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_old
        FROM payment_splits
        WHERE sale_id = OLD.sale_id;
        
        UPDATE customer_sales
        SET received_amount = v_total_old,
            status = CASE 
                WHEN gross_sales <= v_total_old THEN 'Close'
                ELSE 'Open'
            END
        WHERE sale_id = OLD.sale_id;
    END IF;
END //

-- Trigger 3: AFTER DELETE on payment_splits
CREATE TRIGGER trg_payment_splits_after_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_paid DECIMAL(12,2);
    
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM payment_splits
    WHERE sale_id = OLD.sale_id;
    
    UPDATE customer_sales
    SET received_amount = v_total_paid,
        status = CASE 
            WHEN gross_sales <= v_total_paid THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = OLD.sale_id;
END //

DELIMITER ;


-- -----------------------------------------------------------------------
-- STEP 4: SAMPLE DATA INSERTION
-- -----------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE payment_splits;
TRUNCATE TABLE customer_sales;
TRUNCATE TABLE users;
TRUNCATE TABLE branches;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Branches
INSERT INTO branches (branch_id, branch_name, branch_admin_name) VALUES
(1, 'Chennai', 'Arun Kumar'),
(2, 'Delhi', 'Priya Sharma'),
(3, 'Bangalore', 'Rajesh Nair'),
(4, 'Mumbai', 'Sneha Patil'),
(5, 'Hyderabad', 'Vikram Reddy');

-- 2. Users
INSERT INTO users (user_id, username, password, branch_id, role, email) VALUES
(1, 'super_admin', 'admin123', NULL, 'Super Admin', 'superadmin@saleshub.com'),
(2, 'chennai_admin', 'admin123', 1, 'Admin', 'chennai@saleshub.com'),
(3, 'delhi_admin', 'admin123', 2, 'Admin', 'delhi@saleshub.com'),
(4, 'bangalore_admin', 'admin123', 3, 'Admin', 'bangalore@saleshub.com'),
(5, 'mumbai_admin', 'admin123', 4, 'Admin', 'mumbai@saleshub.com'),
(6, 'hyderabad_admin', 'admin123', 5, 'Admin', 'hyderabad@saleshub.com');

-- 3. Customer Sales
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

-- 4. Payment Splits (Auto-triggers recalculation of received_amount & status)
INSERT INTO payment_splits (payment_id, sale_id, payment_date, amount_paid, payment_method) VALUES
(1, 1, '2026-08-10', 20000.00, 'UPI'),
(2, 1, '2026-08-20', 25000.00, 'Card'),
(3, 2, '2026-08-15', 15000.00, 'Cash'),
(4, 2, '2026-08-30', 10000.00, 'UPI'),
(5, 3, '2026-09-02', 30000.00, 'Card'),
(6, 3, '2026-09-15', 30000.00, 'UPI'),
(7, 4, '2026-09-20', 20000.00, 'Cash'),
(8, 5, '2026-08-18', 25000.00, 'UPI'),
(9, 5, '2026-09-01', 25000.00, 'Card'),
(10, 6, '2026-09-05', 35000.00, 'Card'),
(11, 6, '2026-09-25', 15000.00, 'UPI'),
(12, 7, '2026-10-01', 35000.00, 'UPI'),
(13, 8, '2026-08-25', 25000.00, 'Cash'),
(14, 8, '2026-09-10', 20000.00, 'UPI'),
(15, 9, '2026-09-12', 42000.00, 'Card'),
(16, 10, '2026-10-04', 40000.00, 'UPI'),
(17, 10, '2026-10-12', 15000.00, 'Cash'),
(18, 11, '2026-08-30', 38000.00, 'Cash'),
(19, 12, '2026-09-18', 25000.00, 'Card'),
(20, 12, '2026-10-02', 20000.00, 'UPI'),
(21, 13, '2026-10-08', 45000.00, 'Card'),
(22, 14, '2026-09-01', 30000.00, 'UPI'),
(23, 14, '2026-09-18', 25000.00, 'Cash'),
(24, 15, '2026-09-22', 48000.00, 'UPI'),
(25, 16, '2026-10-11', 20000.00, 'Card'),
(26, 17, '2026-10-15', 58000.00, 'UPI'),
(27, 18, '2026-10-18', 20000.00, 'Cash'),
(28, 18, '2026-10-21', 15000.00, 'Card');
