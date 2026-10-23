"""Database connection and Data Access Layer for Sales Intelligence Hub.

Provides reliable MySQL connectivity using pure Python driver,
schema initialization, user authentication, queries, and transaction helpers.
"""

from decimal import Decimal
import os
from typing import Any, Dict, List, Optional
import mysql.connector
import pandas as pd

# Default Database Configuration
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Jawsaadhu@07"),
    "database": os.getenv("MYSQL_DATABASE", "sales_management_db"),
    "use_pure": True,
    "connection_timeout": 10,
}


def get_connection(with_db: bool = True):
    """Get a MySQL database connection with pure python driver."""
    config = DB_CONFIG.copy()
    if not with_db:
        config.pop("database", None)
    conn = mysql.connector.connect(**config)
    conn.autocommit = True
    return conn


def execute_query(sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Execute a SELECT query and return results as a pandas DataFrame."""
    conn = get_connection(with_db=True)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        if not rows:
            # Return empty dataframe with column names if available
            cols = [d[0] for d in cursor.description] if cursor.description else []
            return pd.DataFrame(columns=cols)
        df = pd.DataFrame(rows)
        # Convert Decimals to float for clean Streamlit display and plotting
        for col in df.columns:
            if df[col].dtype == object and len(df) > 0 and isinstance(df[col].iloc[0], Decimal):
                df[col] = df[col].astype(float)
        return df
    finally:
        cursor.close()
        conn.close()


def execute_dml(sql: str, params: Optional[tuple] = None) -> int:
    """Execute INSERT, UPDATE, or DELETE query and return lastrowid."""
    conn = get_connection(with_db=True)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        last_id = cursor.lastrowid
        return last_id
    finally:
        cursor.close()
        conn.close()


def authenticate_user(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate user credentials against the users table.

    Returns user dict if valid, else None.
    """
    sql = """
        SELECT u.user_id, u.username, u.role, u.branch_id, u.email, b.branch_name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.branch_id
        WHERE (u.username = %s OR u.email = %s) AND u.password = %s
    """
    conn = get_connection(with_db=True)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (username_or_email.strip(), username_or_email.strip(), password))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()


def get_all_branches() -> pd.DataFrame:
    """Fetch all branches."""
    return execute_query("SELECT branch_id, branch_name, branch_admin_name FROM branches ORDER BY branch_id;")


def get_sales_records(branch_id: Optional[int] = None, status: Optional[str] = None) -> pd.DataFrame:
    """Retrieve customer sales records with joined branch information."""
    sql = """
        SELECT 
            cs.sale_id,
            cs.branch_id,
            b.branch_name,
            b.branch_admin_name,
            cs.date,
            cs.name AS customer_name,
            cs.mobile_number,
            cs.product_name,
            cs.gross_sales,
            cs.received_amount,
            cs.pending_amount,
            cs.status
        FROM customer_sales cs
        JOIN branches b ON cs.branch_id = b.branch_id
        WHERE 1=1
    """
    params = []
    if branch_id is not None:
        sql += " AND cs.branch_id = %s"
        params.append(branch_id)
    if status and status != "All":
        sql += " AND cs.status = %s"
        params.append(status)
    sql += " ORDER BY cs.sale_id DESC;"
    return execute_query(sql, tuple(params) if params else None)


def get_payment_splits_records(branch_id: Optional[int] = None) -> pd.DataFrame:
    """Retrieve payment split records joined with sales and branches."""
    sql = """
        SELECT 
            ps.payment_id,
            ps.sale_id,
            b.branch_name,
            cs.name AS customer_name,
            cs.product_name,
            ps.payment_date,
            ps.amount_paid,
            ps.payment_method,
            cs.gross_sales,
            cs.received_amount,
            cs.pending_amount,
            cs.status
        FROM payment_splits ps
        JOIN customer_sales cs ON ps.sale_id = cs.sale_id
        JOIN branches b ON cs.branch_id = b.branch_id
        WHERE 1=1
    """
    params = []
    if branch_id is not None:
        sql += " AND cs.branch_id = %s"
        params.append(branch_id)
    sql += " ORDER BY ps.payment_id DESC;"
    return execute_query(sql, tuple(params) if params else None)


def add_sale_record(branch_id: int, date: str, name: str, mobile_number: str, product_name: str, gross_sales: float) -> int:
    """Insert a new sales record."""
    sql = """
        INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
        VALUES (%s, %s, %s, %s, %s, %s, 0.00, 'Open');
    """
    return execute_dml(sql, (branch_id, date, name.strip(), mobile_number.strip(), product_name, gross_sales))


def add_payment_split_record(sale_id: int, payment_date: str, amount_paid: float, payment_method: str) -> int:
    """Insert a payment split record. The MySQL trigger will automatically
    update received_amount and status in customer_sales.
    """
    sql = """
        INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
        VALUES (%s, %s, %s, %s);
    """
    return execute_dml(sql, (sale_id, payment_date, amount_paid, payment_method))


def get_kpis(branch_id: Optional[int] = None) -> Dict[str, Any]:
    """Calculate core Financial KPIs."""
    sql = """
        SELECT 
            COUNT(sale_id) AS total_orders,
            COALESCE(SUM(gross_sales), 0.00) AS total_gross_sales,
            COALESCE(SUM(received_amount), 0.00) AS total_received_amount,
            COALESCE(SUM(pending_amount), 0.00) AS total_pending_amount,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_orders,
            SUM(CASE WHEN status = 'Close' THEN 1 ELSE 0 END) AS closed_orders
        FROM customer_sales
        WHERE 1=1
    """
    params = []
    if branch_id is not None:
        sql += " AND branch_id = %s"
        params.append(branch_id)
    
    df = execute_query(sql, tuple(params) if params else None)
    if not df.empty:
        row = df.iloc[0]
        total_gross = float(row["total_gross_sales"])
        total_received = float(row["total_received_amount"])
        total_pending = float(row["total_pending_amount"])
        collection_pct = (total_received / total_gross * 100) if total_gross > 0 else 0.0
        pending_pct = (total_pending / total_gross * 100) if total_gross > 0 else 0.0
        return {
            "total_orders": int(row["total_orders"]),
            "total_gross_sales": total_gross,
            "total_received_amount": total_received,
            "total_pending_amount": total_pending,
            "collection_pct": collection_pct,
            "pending_pct": pending_pct,
            "open_orders": int(row["open_orders"] or 0),
            "closed_orders": int(row["closed_orders"] or 0),
        }
    return {
        "total_orders": 0,
        "total_gross_sales": 0.0,
        "total_received_amount": 0.0,
        "total_pending_amount": 0.0,
        "collection_pct": 0.0,
        "pending_pct": 0.0,
        "open_orders": 0,
        "closed_orders": 0,
    }


# All 20 Predefined SQL Queries categorized
PREDEFINED_QUERIES = [
    # ---------------- Basic Queries (1-5) ----------------
    {
        "id": 1,
        "category": "Basic Queries",
        "title": "1. Retrieve all records from customer_sales",
        "description": "Fetches all sales transaction records stored in the database.",
        "sql": "SELECT * FROM customer_sales;"
    },
    {
        "id": 2,
        "category": "Basic Queries",
        "title": "2. Retrieve all records from branches",
        "description": "Fetches all branch locations and their assigned administrators.",
        "sql": "SELECT * FROM branches;"
    },
    {
        "id": 3,
        "category": "Basic Queries",
        "title": "3. Retrieve all records from payment_splits",
        "description": "Lists all payment installments and payment modes recorded.",
        "sql": "SELECT * FROM payment_splits;"
    },
    {
        "id": 4,
        "category": "Basic Queries",
        "title": "4. Display all sales with status = 'Open'",
        "description": "Filters sales that have remaining outstanding balance.",
        "sql": "SELECT * FROM customer_sales WHERE status = 'Open';"
    },
    {
        "id": 5,
        "category": "Basic Queries",
        "title": "5. Retrieve all sales belonging to Chennai branch",
        "description": "Fetches sales records associated specifically with the Chennai branch.",
        "sql": """SELECT cs.sale_id, b.branch_name, cs.date, cs.name AS customer_name,
       cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount, cs.status
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';"""
    },

    # ---------------- Aggregation Queries (6-10) ----------------
    {
        "id": 6,
        "category": "Aggregation Queries",
        "title": "6. Calculate total gross sales across all branches",
        "description": "Computes the grand total revenue across all branches.",
        "sql": "SELECT COALESCE(SUM(gross_sales), 0.00) AS total_gross_sales FROM customer_sales;"
    },
    {
        "id": 7,
        "category": "Aggregation Queries",
        "title": "7. Calculate total received amount across all sales",
        "description": "Calculates the total payments received across all customer orders.",
        "sql": "SELECT COALESCE(SUM(received_amount), 0.00) AS total_received_amount FROM customer_sales;"
    },
    {
        "id": 8,
        "category": "Aggregation Queries",
        "title": "8. Calculate total pending amount across all sales",
        "description": "Computes the total outstanding pending amount awaiting collection.",
        "sql": "SELECT COALESCE(SUM(pending_amount), 0.00) AS total_pending_amount FROM customer_sales;"
    },
    {
        "id": 9,
        "category": "Aggregation Queries",
        "title": "9. Count the total number of sales per branch",
        "description": "Determines the total sales volume (number of transactions) for each branch.",
        "sql": """SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales_count
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_sales_count DESC;"""
    },
    {
        "id": 10,
        "category": "Aggregation Queries",
        "title": "10. Find the average gross sales amount",
        "description": "Calculates the overall average transaction value per sale.",
        "sql": "SELECT ROUND(AVG(gross_sales), 2) AS average_gross_sales FROM customer_sales;"
    },

    # ---------------- Join-Based Queries (11-15) ----------------
    {
        "id": 11,
        "category": "Join-Based Queries",
        "title": "11. Retrieve sales details along with branch name",
        "description": "Performs an INNER JOIN to show customer sales with their branch name.",
        "sql": """SELECT cs.sale_id, b.branch_name, cs.date, cs.name AS customer_name,
       cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount, cs.status
FROM customer_sales cs
INNER JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;"""
    },
    {
        "id": 12,
        "category": "Join-Based Queries",
        "title": "12. Retrieve sales details along with total payment received (using payment_splits)",
        "description": "Sums payments from payment_splits and joins with customer_sales.",
        "sql": """SELECT cs.sale_id, cs.name AS customer_name, cs.product_name, cs.gross_sales,
       COALESCE(SUM(ps.amount_paid), 0.00) AS total_payment_from_splits,
       cs.received_amount AS customer_sales_received_amount
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.product_name, cs.gross_sales, cs.received_amount
ORDER BY cs.sale_id;"""
    },
    {
        "id": 13,
        "category": "Join-Based Queries",
        "title": "13. Show branch-wise total gross sales (using JOIN & GROUP BY)",
        "description": "Calculates the total revenue generated by each branch using JOIN and GROUP BY.",
        "sql": """SELECT b.branch_name, COALESCE(SUM(cs.gross_sales), 0.00) AS branch_total_gross_sales
FROM branches b
JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY branch_total_gross_sales DESC;"""
    },
    {
        "id": 14,
        "category": "Join-Based Queries",
        "title": "14. Display sales along with payment method used",
        "description": "Lists customer sales transactions paired with each payment split method.",
        "sql": """SELECT cs.sale_id, cs.name AS customer_name, cs.product_name,
       ps.payment_id, ps.amount_paid, ps.payment_method, ps.payment_date
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_id;"""
    },
    {
        "id": 15,
        "category": "Join-Based Queries",
        "title": "15. Retrieve sales along with branch admin name",
        "description": "Associates each sale with the responsible branch administrator.",
        "sql": """SELECT cs.sale_id, b.branch_name, b.branch_admin_name, cs.name AS customer_name,
       cs.product_name, cs.gross_sales, cs.status
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;"""
    },

    # ---------------- Financial Tracking Queries (16-20) ----------------
    {
        "id": 16,
        "category": "Financial Tracking Queries",
        "title": "16. Find sales where pending amount is greater than 5000",
        "description": "Identifies customer sales accounts with high outstanding amounts (> ₹5,000).",
        "sql": "SELECT * FROM customer_sales WHERE pending_amount > 5000 ORDER BY pending_amount DESC;"
    },
    {
        "id": 17,
        "category": "Financial Tracking Queries",
        "title": "17. Retrieve top 3 highest gross sales",
        "description": "Finds the 3 highest value transactions recorded in the system.",
        "sql": "SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;"
    },
    {
        "id": 18,
        "category": "Financial Tracking Queries",
        "title": "18. Find the branch with highest total gross sales",
        "description": "Identifies the highest revenue grossing branch overall.",
        "sql": """SELECT b.branch_name, b.branch_admin_name, SUM(cs.gross_sales) AS total_gross_sales
FROM branches b
JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name, b.branch_admin_name
ORDER BY total_gross_sales DESC
LIMIT 1;"""
    },
    {
        "id": 19,
        "category": "Financial Tracking Queries",
        "title": "19. Retrieve monthly sales summary (group by month & year)",
        "description": "Aggregates revenue, received collections, and pending balances by month.",
        "sql": """SELECT DATE_FORMAT(date, '%Y-%m') AS sale_month,
       COUNT(sale_id) AS total_transactions,
       SUM(gross_sales) AS total_monthly_sales,
       SUM(received_amount) AS total_monthly_received,
       SUM(pending_amount) AS total_monthly_pending
FROM customer_sales
GROUP BY DATE_FORMAT(date, '%Y-%m')
ORDER BY sale_month ASC;"""
    },
    {
        "id": 20,
        "category": "Financial Tracking Queries",
        "title": "20. Calculate payment method-wise total collection (Cash / UPI / Card)",
        "description": "Analyzes the total payment amounts collected per payment modality.",
        "sql": """SELECT payment_method,
       COUNT(payment_id) AS transaction_count,
       SUM(amount_paid) AS total_collection,
       ROUND((SUM(amount_paid) / (SELECT SUM(amount_paid) FROM payment_splits)) * 100, 2) AS percentage_share
FROM payment_splits
GROUP BY payment_method
ORDER BY total_collection DESC;"""
    },
]
