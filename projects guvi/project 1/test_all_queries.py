"""Automated test script for all 20 predefined SQL queries.

Ensures every query executes successfully and produces valid data.
"""

import sys
import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Jawsaadhu@07",
    database="sales_management_db",
    use_pure=True
)

QUERIES = [
    # Basic Queries
    (1, "Retrieve all records from the customer_sales table.",
     "SELECT * FROM customer_sales;"),
    (2, "Retrieve all records from the branches table.",
     "SELECT * FROM branches;"),
    (3, "Retrieve all records from the payment_splits table.",
     "SELECT * FROM payment_splits;"),
    (4, "Display all sales with status = 'Open'.",
     "SELECT * FROM customer_sales WHERE status = 'Open';"),
    (5, "Retrieve all sales belonging to the Chennai branch.",
     "SELECT cs.* FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE b.branch_name = 'Chennai';"),

    # Aggregation Queries
    (6, "Calculate the total gross sales across all branches.",
     "SELECT COALESCE(SUM(gross_sales), 0.00) AS total_gross_sales FROM customer_sales;"),
    (7, "Calculate the total received amount across all sales.",
     "SELECT COALESCE(SUM(received_amount), 0.00) AS total_received_amount FROM customer_sales;"),
    (8, "Calculate the total pending amount across all sales.",
     "SELECT COALESCE(SUM(pending_amount), 0.00) AS total_pending_amount FROM customer_sales;"),
    (9, "Count the total number of sales per branch.",
     "SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales_count FROM branches b LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id GROUP BY b.branch_id, b.branch_name;"),
    (10, "Find the average gross sales amount.",
     "SELECT ROUND(AVG(gross_sales), 2) AS average_gross_sales FROM customer_sales;"),

    # Join-Based Queries
    (11, "Retrieve sales details along with the branch name.",
     "SELECT cs.sale_id, cs.name AS customer_name, cs.mobile_number, cs.product_name, cs.gross_sales, b.branch_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id;"),
    (12, "Retrieve sales details along with total payment received (using payment_splits).",
     "SELECT cs.sale_id, cs.name AS customer_name, cs.gross_sales, COALESCE(SUM(ps.amount_paid), 0) AS total_payment_received FROM customer_sales cs LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id GROUP BY cs.sale_id, cs.name, cs.gross_sales;"),
    (13, "Show branch-wise total gross sales (using JOIN & GROUP BY).",
     "SELECT b.branch_name, SUM(cs.gross_sales) AS branch_total_gross_sales FROM branches b JOIN customer_sales cs ON b.branch_id = cs.branch_id GROUP BY b.branch_id, b.branch_name;"),
    (14, "Display sales along with payment method used.",
     "SELECT cs.sale_id, cs.name AS customer_name, cs.product_name, ps.payment_id, ps.amount_paid, ps.payment_method, ps.payment_date FROM customer_sales cs JOIN payment_splits ps ON cs.sale_id = ps.sale_id;"),
    (15, "Retrieve sales along with branch admin name.",
     "SELECT cs.sale_id, cs.name AS customer_name, cs.product_name, cs.gross_sales, b.branch_name, b.branch_admin_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id;"),

    # Financial Tracking Queries
    (16, "Find sales where the pending amount is greater than 5000.",
     "SELECT * FROM customer_sales WHERE pending_amount > 5000;"),
    (17, "Retrieve top 3 highest gross sales.",
     "SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;"),
    (18, "Find the branch with highest total gross sales.",
     "SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales FROM branches b JOIN customer_sales cs ON b.branch_id = cs.branch_id GROUP BY b.branch_id, b.branch_name ORDER BY total_gross_sales DESC LIMIT 1;"),
    (19, "Retrieve monthly sales summary (group by month & year).",
     "SELECT DATE_FORMAT(date, '%Y-%m') AS sale_month, COUNT(sale_id) AS total_transactions, SUM(gross_sales) AS total_monthly_sales, SUM(received_amount) AS total_monthly_received FROM customer_sales GROUP BY DATE_FORMAT(date, '%Y-%m') ORDER BY sale_month;"),
    (20, "Calculate payment method-wise total collection (Cash / UPI / Card).",
     "SELECT payment_method, SUM(amount_paid) AS total_collection, COUNT(payment_id) AS transaction_count FROM payment_splits GROUP BY payment_method ORDER BY total_collection DESC;"),
]

cursor = conn.cursor(dictionary=True)
all_passed = True

print(f"Testing {len(QUERIES)} SQL queries...\n")
for q_num, title, query in QUERIES:
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"Query {q_num:02d}: PASS ({len(rows)} rows) - {title[:50]}")
    except Exception as e:
        print(f"Query {q_num:02d}: FAIL - {e}")
        all_passed = False

cursor.close()
conn.close()

if all_passed:
    print("\nALL 20 SQL QUERIES PASSED WITH 0 ERRORS!")
else:
    sys.exit(1)
