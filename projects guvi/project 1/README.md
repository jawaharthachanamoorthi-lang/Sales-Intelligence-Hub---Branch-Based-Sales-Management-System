# 💼 Sales Intelligence Hub (Branch-Based Sales Management System)

A full-stack, enterprise-grade Sales Analytics and Financial Tracking System built using **MySQL**, **Python**, and **Streamlit**. Designed to solve multi-branch operational challenges, eliminate manual calculation errors, track split payments, automate financial balances with database triggers, and enforce strict Role-Based Access Control (RBAC).

---

## 🌟 Key Highlights & Evaluation Criteria

- **Database Normalization & Integrity**: 4 normalized tables (`branches`, `customer_sales`, `payment_splits`, `users`) with Primary Keys, Foreign Keys with cascading, and `UNIQUE` constraints on mobile number and email.
- **Automated Calculations with Generated Columns**: `pending_amount` is automatically calculated in the database via `STORED GENERATED ALWAYS AS (gross_sales - received_amount)`.
- **Database Trigger Automation**: `AFTER INSERT`, `AFTER UPDATE`, and `AFTER DELETE` triggers on `payment_splits` automatically recalculate `received_amount` and dynamically toggle order status (`Open` vs `Close`).
- **Role-Based Access Control (RBAC)**: Secure database-backed login supporting **Super Admin** (global view across all branches, create sales for any branch, query runner) and **Branch Admin** (isolated view and entry strictly for assigned branch).
- **All 20 Predefined SQL Queries**: Full implementation of all 20 capstone analytical queries across Basic, Aggregation, Join-Based, and Financial Tracking categories, executable with one click in the interactive Streamlit dashboard.
- **Python Driver Optimization**: Implemented with pure Python MySQL connector (`use_pure=True`) to guarantee rock-solid cross-platform compatibility and zero Windows C-extension crashes.

---

## 🏗️ Architecture & Table Structure

```
branches (1) ------------< (Many) customer_sales (1) ------------< (Many) payment_splits
    |                                   ^
    |                                   |
    +------------------------< (Many) users
```

### 1. `branches` Table
Stores registered branch details and designated administrator names.
- `branch_id INT PRIMARY KEY AUTO_INCREMENT`
- `branch_name VARCHAR(100) NOT NULL UNIQUE`
- `branch_admin_name VARCHAR(100) NOT NULL`

### 2. `customer_sales` Table (Main Financial Table)
Stores individual course/product sales per branch.
- `sale_id INT PRIMARY KEY AUTO_INCREMENT`
- `branch_id INT NOT NULL` (Foreign Key referencing `branches(branch_id)`)
- `date DATE NOT NULL`
- `name VARCHAR(100) NOT NULL`
- `mobile_number VARCHAR(15) NOT NULL UNIQUE` (Guarantees customer uniqueness)
- `product_name VARCHAR(30) NOT NULL` (Data Science, Data Analytics, Business Analytics, Full Stack Development)
- `gross_sales DECIMAL(12,2) NOT NULL`
- `received_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00` (Updated via triggers)
- `pending_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED`
- `status ENUM('Open', 'Close') NOT NULL DEFAULT 'Open'`

### 3. `payment_splits` Table
Tracks multiple payment installments for each customer order.
- `payment_id INT PRIMARY KEY AUTO_INCREMENT`
- `sale_id INT NOT NULL` (Foreign Key referencing `customer_sales(sale_id)`)
- `payment_date DATE NOT NULL`
- `amount_paid DECIMAL(12,2) NOT NULL CHECK (amount_paid > 0)`
- `payment_method ENUM('Cash', 'UPI', 'Card') NOT NULL`

### 4. `users` Table
Handles login credentials and authorization.
- `user_id INT PRIMARY KEY AUTO_INCREMENT`
- `username VARCHAR(100) NOT NULL UNIQUE`
- `password VARCHAR(255) NOT NULL`
- `branch_id INT NULL` (Foreign Key; NULL for Super Admin, specific branch for Admin)
- `role ENUM('Super Admin', 'Admin') NOT NULL`
- `email VARCHAR(255) NOT NULL UNIQUE`

---

## ⚡ Trigger Automation Logic

Triggers ensure zero manual calculation of financial collections:

```sql
DELIMITER //

CREATE TRIGGER trg_payment_splits_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_paid DECIMAL(12,2);
    
    -- Recalculate total amount paid for this sale
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;
    
    -- Update received_amount and dynamically toggle status
    UPDATE customer_sales
    SET received_amount = v_total_paid,
        status = CASE 
            WHEN gross_sales <= v_total_paid THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END //

DELIMITER ;
```

*Note: `AFTER UPDATE` and `AFTER DELETE` triggers are also implemented to guarantee financial integrity under all database operations.*

---

## 👥 Role-Based Access Control (RBAC) Matrix

| Feature / Permission | Super Admin 👑 | Branch Admin 🏢 |
| :--- | :---: | :---: |
| **System Access** | Requires authenticated login | Requires authenticated login |
| **Data Scope** | All Branches globally | Assigned Branch only |
| **Branch Filter** | Interactive dropdown filter | Locked to assigned branch |
| **View Sales Records** | Full system visibility | Branch-scoped visibility |
| **Add New Sales** | Can create sales for ANY branch | Can create sales for OWN branch only |
| **Record Split Payments**| Can record payments for any open sale | Can record payments for own branch sales |
| **Financial KPI Metrics**| Consolidated global & branch KPIs | Branch-specific KPIs |
| **Analytics & Charts** | Multi-branch comparisons | Branch performance analysis |
| **Execute 20 Predefined SQL Queries** | Yes (All 20 queries) | Yes (All 20 queries) |
| **Custom SQL Playground**| Yes (Interactive query runner) | Restricted |

### Demo Credentials

| Role | Username | Password | Branch Assigned | Email |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | `super_admin` | `admin123` | *Global (All Branches)* | `superadmin@saleshub.com` |
| **Branch Admin** | `chennai_admin` | `admin123` | Chennai (Branch 1) | `chennai@saleshub.com` |
| **Branch Admin** | `delhi_admin` | `admin123` | Delhi (Branch 2) | `delhi@saleshub.com` |
| **Branch Admin** | `bangalore_admin` | `admin123` | Bangalore (Branch 3) | `bangalore@saleshub.com` |
| **Branch Admin** | `mumbai_admin` | `admin123` | Mumbai (Branch 4) | `mumbai@saleshub.com` |
| **Branch Admin** | `hyderabad_admin` | `admin123` | Hyderabad (Branch 5) | `hyderabad@saleshub.com` |

---

## 📊 All 20 SQL Analytical Queries

All 20 queries are cataloged in `sql_queries.sql` and executable within the Streamlit dashboard:

### 🔹 Basic Queries (1 - 5)
1. **Retrieve all records from customer_sales**:
   ```sql
   SELECT * FROM customer_sales;
   ```
2. **Retrieve all records from branches**:
   ```sql
   SELECT * FROM branches;
   ```
3. **Retrieve all records from payment_splits**:
   ```sql
   SELECT * FROM payment_splits;
   ```
4. **Display all sales with status = 'Open'**:
   ```sql
   SELECT * FROM customer_sales WHERE status = 'Open';
   ```
5. **Retrieve all sales belonging to Chennai branch**:
   ```sql
   SELECT cs.* FROM customer_sales cs
   JOIN branches b ON cs.branch_id = b.branch_id
   WHERE b.branch_name = 'Chennai';
   ```

### 🔹 Aggregation Queries (6 - 10)
6. **Calculate total gross sales across all branches**:
   ```sql
   SELECT COALESCE(SUM(gross_sales), 0.00) AS total_gross_sales FROM customer_sales;
   ```
7. **Calculate total received amount across all sales**:
   ```sql
   SELECT COALESCE(SUM(received_amount), 0.00) AS total_received_amount FROM customer_sales;
   ```
8. **Calculate total pending amount across all sales**:
   ```sql
   SELECT COALESCE(SUM(pending_amount), 0.00) AS total_pending_amount FROM customer_sales;
   ```
9. **Count total number of sales per branch**:
   ```sql
   SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales_count
   FROM branches b
   LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
   GROUP BY b.branch_id, b.branch_name
   ORDER BY total_sales_count DESC;
   ```
10. **Find the average gross sales amount**:
    ```sql
    SELECT ROUND(AVG(gross_sales), 2) AS average_gross_sales FROM customer_sales;
    ```

### 🔹 Join-Based Queries (11 - 15)
11. **Retrieve sales details along with branch name**:
    ```sql
    SELECT cs.sale_id, b.branch_name, cs.date, cs.name AS customer_name,
           cs.product_name, cs.gross_sales, cs.pending_amount, cs.status
    FROM customer_sales cs
    INNER JOIN branches b ON cs.branch_id = b.branch_id
    ORDER BY cs.sale_id;
    ```
12. **Retrieve sales details with total payment received (using payment_splits)**:
    ```sql
    SELECT cs.sale_id, cs.name AS customer_name, cs.product_name, cs.gross_sales,
           COALESCE(SUM(ps.amount_paid), 0.00) AS total_payment_from_splits,
           cs.received_amount AS customer_sales_received_amount
    FROM customer_sales cs
    LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
    GROUP BY cs.sale_id, cs.name, cs.product_name, cs.gross_sales, cs.received_amount
    ORDER BY cs.sale_id;
    ```
13. **Show branch-wise total gross sales (using JOIN & GROUP BY)**:
    ```sql
    SELECT b.branch_name, COALESCE(SUM(cs.gross_sales), 0.00) AS branch_total_gross_sales
    FROM branches b
    JOIN customer_sales cs ON b.branch_id = cs.branch_id
    GROUP BY b.branch_id, b.branch_name
    ORDER BY branch_total_gross_sales DESC;
    ```
14. **Display sales along with payment method used**:
    ```sql
    SELECT cs.sale_id, cs.name AS customer_name, cs.product_name,
           ps.payment_id, ps.amount_paid, ps.payment_method, ps.payment_date
    FROM customer_sales cs
    JOIN payment_splits ps ON cs.sale_id = ps.sale_id
    ORDER BY cs.sale_id, ps.payment_id;
    ```
15. **Retrieve sales along with branch admin name**:
    ```sql
    SELECT cs.sale_id, b.branch_name, b.branch_admin_name, cs.name AS customer_name,
           cs.product_name, cs.gross_sales, cs.status
    FROM customer_sales cs
    JOIN branches b ON cs.branch_id = b.branch_id
    ORDER BY cs.sale_id;
    ```

### 🔹 Financial Tracking Queries (16 - 20)
16. **Find sales where pending amount is greater than 5000**:
    ```sql
    SELECT * FROM customer_sales WHERE pending_amount > 5000 ORDER BY pending_amount DESC;
    ```
17. **Retrieve top 3 highest gross sales**:
    ```sql
    SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;
    ```
18. **Find the branch with highest total gross sales**:
    ```sql
    SELECT b.branch_name, b.branch_admin_name, SUM(cs.gross_sales) AS total_gross_sales
    FROM branches b
    JOIN customer_sales cs ON b.branch_id = cs.branch_id
    GROUP BY b.branch_id, b.branch_name, b.branch_admin_name
    ORDER BY total_gross_sales DESC
    LIMIT 1;
    ```
19. **Retrieve monthly sales summary (group by month & year)**:
    ```sql
    SELECT DATE_FORMAT(date, '%Y-%m') AS sale_month,
           COUNT(sale_id) AS total_transactions,
           SUM(gross_sales) AS total_monthly_sales,
           SUM(received_amount) AS total_monthly_received,
           SUM(pending_amount) AS total_monthly_pending
    FROM customer_sales
    GROUP BY DATE_FORMAT(date, '%Y-%m')
    ORDER BY sale_month ASC;
    ```
20. **Calculate payment method-wise total collection (Cash / UPI / Card)**:
    ```sql
    SELECT payment_method,
           COUNT(payment_id) AS transaction_count,
           SUM(amount_paid) AS total_collection,
           ROUND((SUM(amount_paid) / (SELECT SUM(amount_paid) FROM payment_splits)) * 100, 2) AS percentage_share
    FROM payment_splits
    GROUP BY payment_method
    ORDER BY total_collection DESC;
    ```

---

## 🚀 Quick Setup & Run Instructions

### 1. Prerequisites
- Python 3.9+
- MySQL Server 8.0+ running locally (default port 3306)

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Initialize Database & Demo Data
Run the automated initialization script:
```powershell
python setup_database.py
```
*This automatically sets up `sales_management_db`, creates all 4 tables with constraints, installs the triggers, and seeds realistic multi-branch sample data.*

### 4. Verify All 20 SQL Queries
```powershell
python test_all_queries.py
```
*(All 20 queries execute and validate with 0 errors!)*

### 5. Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`.

---

## 📁 Project Deliverables File Manifest

| File | Purpose |
| :--- | :--- |
| [`sales_project_schema.sql`](file:///D:/jawslearn/projects%20guvi/project%201/sales_project_schema.sql) | Complete DDL schema with PK, FK, generated columns, and constraints |
| [`sales_project_trigger.sql`](file:///D:/jawslearn/projects%20guvi/project%201/sales_project_trigger.sql) | `AFTER INSERT`, `AFTER UPDATE`, `AFTER DELETE` trigger definitions |
| [`sample_data.sql`](file:///D:/jawslearn/projects%20guvi/project%201/sample_data.sql) | Seeding dataset with branches, users, sales, and payment splits |
| [`data_base_management.sql`](file:///D:/jawslearn/projects%20guvi/project%201/data_base_management.sql) | Consolidated master SQL script containing schema, triggers, and sample data |
| [`sql_queries.sql`](file:///D:/jawslearn/projects%20guvi/project%201/sql_queries.sql) | All 20 analytical SQL queries cleanly organized and documented |
| [`db_connection.py`](file:///D:/jawslearn/projects%20guvi/project%201/db_connection.py) | Python-MySQL Data Access Layer with pure python driver |
| [`setup_database.py`](file:///D:/jawslearn/projects%20guvi/project%201/setup_database.py) | Automated Python script to initialize database, triggers, and data |
| [`test_all_queries.py`](file:///D:/jawslearn/projects%20guvi/project%201/test_all_queries.py) | Automated test suite verifying all 20 queries run with 0 errors |
| [`app.py`](file:///D:/jawslearn/projects%20guvi/project%201/app.py) | Full-featured Streamlit Web Application with RBAC & visual analytics |
| [`requirements.txt`](file:///D:/jawslearn/projects%20guvi/project%201/requirements.txt) | Required Python packages |
| [`README.md`](file:///D:/jawslearn/projects%20guvi/project%201/README.md) | Comprehensive project documentation |
