-- =======================================================================
-- Project: Sales Intelligence Hub (Branch-Based Sales Management System)
-- Deliverable: Complete MySQL Database Schema
-- File: sales_project_schema.sql
-- =======================================================================

CREATE DATABASE IF NOT EXISTS sales_management_db;
USE sales_management_db;

-- 1. Branches Table
-- Stores information about business branches and their administrators
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    branch_admin_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Customer Sales Table (Main Financial Table)
-- Stores individual sales transactions per branch with auto-calculated pending amount
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
-- Handles multiple split payments for a single customer sale transaction
CREATE TABLE IF NOT EXISTS payment_splits (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL CHECK (amount_paid > 0),
    payment_method ENUM('Cash', 'UPI', 'Card') NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Users Table
-- Supports Role-Based Access Control (Super Admin and Branch Admin)
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    branch_id INT NULL,
    role ENUM('Super Admin', 'Admin') NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
