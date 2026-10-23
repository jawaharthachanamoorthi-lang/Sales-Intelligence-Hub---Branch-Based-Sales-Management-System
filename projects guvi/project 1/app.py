"""Sales Intelligence Hub - Branch-Based Sales Management System.

A comprehensive Streamlit Web Application with MySQL integration,
Role-Based Access Control (Super Admin & Branch Admin), database triggers,
split payment tracking, KPI analytics, and interactive SQL query runner.
"""

from datetime import date
import io
import pandas as pd
import streamlit as st

import db_connection

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern enterprise look
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-super {
        background-color: #EDE9FE;
        color: #6D28D9;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-admin {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-open {
        color: #D97706;
        font-weight: bold;
    }
    .status-close {
        color: #059669;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. SESSION STATE & AUTHENTICATION
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None


def login(username_or_email: str, password: str):
    """Attempt user authentication."""
    user = db_connection.authenticate_user(username_or_email, password)
    if user:
        st.session_state["authenticated"] = True
        st.session_state["user"] = user
        st.success(f"Welcome back, {user['username']}!")
        st.rerun()
    else:
        st.error("Invalid username/email or password. Please try again.")


def logout():
    """Clear session state and log out."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()


# -----------------------------------------------------------------------------
# 3. LOGIN SCREEN (MANDATORY REQUIREMENT)
# -----------------------------------------------------------------------------
if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>💼 Sales Intelligence Hub</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Branch-Based Sales & Financial Tracking System</p>", unsafe_allow_html=True)
        st.markdown("---")

        st.subheader("🔐 System Login")
        with st.form("login_form"):
            username_input = st.text_input("Username or Email", placeholder="e.g. super_admin or chennai_admin")
            password_input = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                if username_input.strip() and password_input.strip():
                    login(username_input, password_input)
                else:
                    st.warning("Please enter both username and password.")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔑 Quick Demo Credentials (Click to inspect or quick fill)", expanded=True):
            st.markdown(
                """
                | Role | Username | Password | Branch Assigned |
                | :--- | :--- | :--- | :--- |
                | **Super Admin** | `super_admin` | `admin123` | *All Branches (Full Access)* |
                | **Branch Admin** | `chennai_admin` | `admin123` | Chennai (Branch ID: 1) |
                | **Branch Admin** | `delhi_admin` | `admin123` | Delhi (Branch ID: 2) |
                | **Branch Admin** | `bangalore_admin` | `admin123` | Bangalore (Branch ID: 3) |
                | **Branch Admin** | `mumbai_admin` | `admin123` | Mumbai (Branch ID: 4) |
                | **Branch Admin** | `hyderabad_admin` | `admin123` | Hyderabad (Branch ID: 5) |
                """
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⚡ Quick Login as Super Admin", use_container_width=True):
                    login("super_admin", "admin123")
            with col_b:
                if st.button("⚡ Quick Login as Chennai Admin", use_container_width=True):
                    login("chennai_admin", "admin123")
    st.stop()


# -----------------------------------------------------------------------------
# 4. AUTHENTICATED USER CONTEXT & SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
user = st.session_state["user"]
is_super_admin = user["role"] == "Super Admin"
assigned_branch_id = user["branch_id"]

with st.sidebar:
    st.markdown("### 👤 User Profile")
    role_badge = (
        f"<span class='badge-super'>👑 {user['role']}</span>"
        if is_super_admin
        else f"<span class='badge-admin'>🏢 {user['role']}</span>"
    )
    st.markdown(role_badge, unsafe_allow_html=True)
    st.write(f"**Username:** `{user['username']}`")
    st.write(f"**Email:** `{user['email']}`")
    if not is_super_admin:
        st.write(f"**Branch:** {user.get('branch_name', f'Branch #{assigned_branch_id}')} (ID: {assigned_branch_id})")
    else:
        st.write("**Access Scope:** Global (All Branches)")

    if st.button("🚪 Logout", use_container_width=True):
        logout()

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    menu = st.radio(
        "Go to",
        [
            "📊 Executive Dashboard",
            "📋 Sales Records & Entry",
            "💳 Payment Splits & Tracking",
            "🔍 Predefined SQL Analytics",
            "⚙️ Database & Trigger Status",
        ],
    )

    # Branch Filtering for Super Admin
    selected_branch_id = None
    if is_super_admin:
        st.markdown("---")
        st.markdown("### 🏢 Branch Filter")
        branches_df = db_connection.get_all_branches()
        branch_options = {"All Branches (Consolidated)": None}
        for _, b in branches_df.iterrows():
            branch_options[f"{b['branch_name']} (ID: {b['branch_id']})"] = int(b["branch_id"])
        selected_branch_name = st.selectbox("Select Branch View", list(branch_options.keys()))
        selected_branch_id = branch_options[selected_branch_name]
    else:
        selected_branch_id = assigned_branch_id


# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD (KPIs & VISUAL ANALYTICS)
# -----------------------------------------------------------------------------
if menu == "📊 Executive Dashboard":
    header_title = "Global Sales & Analytics Dashboard" if is_super_admin else f"{user.get('branch_name', 'Branch')} Performance Dashboard"
    st.markdown(f"<div class='main-header'>📊 {header_title}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-header'>Real-time tracking of branch performance, revenue collections, and pending dues.</div>",
        unsafe_allow_html=True,
    )

    # 1. Fetch KPI metrics
    kpis = db_connection.get_kpis(selected_branch_id)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Gross Sales", f"₹ {kpis['total_gross_sales']:,.2f}", help="Total value of recorded sales")
    with col2:
        st.metric(
            "Total Received",
            f"₹ {kpis['total_received_amount']:,.2f}",
            delta=f"{kpis['collection_pct']:.1f}% collected",
            delta_color="normal",
            help="Total payments confirmed via triggers",
        )
    with col3:
        st.metric(
            "Total Pending",
            f"₹ {kpis['total_pending_amount']:,.2f}",
            delta=f"-{kpis['pending_pct']:.1f}% pending",
            delta_color="inverse",
            help="Calculated by MySQL generated column (gross_sales - received_amount)",
        )
    with col4:
        st.metric(
            "Order Transactions",
            f"{kpis['total_orders']}",
            f"{kpis['closed_orders']} Closed / {kpis['open_orders']} Open",
            delta_color="off",
            help="Total customer orders and completion status",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Visual Analytics
    sales_df = db_connection.get_sales_records(selected_branch_id)

    if sales_df.empty:
        st.info("No sales records found for this branch selection.")
    else:
        tab_a, tab_b = st.columns([1, 1])

        with tab_a:
            st.subheader("🏢 Branch-Wise Gross Sales Comparison")
            if is_super_admin and selected_branch_id is None:
                branch_chart_df = (
                    sales_df.groupby("branch_name")["gross_sales"]
                    .sum()
                    .reset_index()
                    .rename(columns={"gross_sales": "Gross Sales (₹)", "branch_name": "Branch"})
                )
                st.bar_chart(branch_chart_df, x="Branch", y="Gross Sales (₹)", color="#2563EB")
            else:
                branch_chart_df = (
                    sales_df.groupby("product_name")["gross_sales"]
                    .sum()
                    .reset_index()
                    .rename(columns={"gross_sales": "Gross Sales (₹)", "product_name": "Course/Product"})
                )
                st.bar_chart(branch_chart_df, x="Course/Product", y="Gross Sales (₹)", color="#2563EB")

        with tab_b:
            st.subheader("💰 Payment Collection Status")
            collection_summary = pd.DataFrame(
                {
                    "Metric": ["Received Amount", "Pending Balance"],
                    "Amount (₹)": [kpis["total_received_amount"], kpis["total_pending_amount"]],
                }
            )
            st.bar_chart(collection_summary, x="Metric", y="Amount (₹)", color="#10B981")

        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_d = st.columns([1, 1])

        with col_c:
            st.subheader("💳 Collections by Payment Method")
            splits_df = db_connection.get_payment_splits_records(selected_branch_id)
            if not splits_df.empty:
                method_df = (
                    splits_df.groupby("payment_method")["amount_paid"]
                    .sum()
                    .reset_index()
                    .rename(columns={"amount_paid": "Total Collected (₹)", "payment_method": "Method"})
                )
                st.bar_chart(method_df, x="Method", y="Total Collected (₹)", color="#8B5CF6")
            else:
                st.info("No split payments recorded yet.")

        with col_d:
            st.subheader("📚 Product / Course Sales Distribution")
            prod_df = (
                sales_df.groupby("product_name")["sale_id"]
                .count()
                .reset_index()
                .rename(columns={"sale_id": "Number of Enrollments", "product_name": "Product"})
            )
            st.bar_chart(prod_df, x="Product", y="Number of Enrollments", color="#F59E0B")

        # High Pending Alerts
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("⚠️ High Pending Accounts (> ₹5,000)")
        high_pending = sales_df[sales_df["pending_amount"] > 5000][
            ["sale_id", "branch_name", "date", "customer_name", "mobile_number", "product_name", "gross_sales", "received_amount", "pending_amount"]
        ]
        if not high_pending.empty:
            st.dataframe(high_pending, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Excellent! No accounts have pending balances greater than ₹5,000.")


# -----------------------------------------------------------------------------
# TAB 2: SALES RECORDS & ENTRY (ROLE-BASED PERMISSIONS)
# -----------------------------------------------------------------------------
elif menu == "📋 Sales Records & Entry":
    st.markdown("<div class='main-header'>📋 Sales Management & Data Entry</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>View, filter, search, and register new customer sales transactions.</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📑 View Sales Records", "➕ Add New Sales Entry"])

    # 1. View Records Tab
    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1:
            search_query = st.text_input("🔍 Search by Customer Name or Mobile", placeholder="Type name or phone...")
        with c2:
            status_filter = st.selectbox("Status Filter", ["All", "Open", "Close"])

        sales = db_connection.get_sales_records(selected_branch_id, status_filter)

        if search_query.strip():
            sales = sales[
                sales["customer_name"].str.contains(search_query, case=False, na=False)
                | sales["mobile_number"].str.contains(search_query, case=False, na=False)
            ]

        st.markdown(f"**Displaying {len(sales)} sales records:**")
        if not sales.empty:
            st.dataframe(
                sales,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "gross_sales": st.column_config.NumberColumn("Gross Sales", format="₹ %,.2f"),
                    "received_amount": st.column_config.NumberColumn("Received", format="₹ %,.2f"),
                    "pending_amount": st.column_config.NumberColumn("Pending (Generated)", format="₹ %,.2f"),
                    "status": st.column_config.TextColumn("Status"),
                },
            )
            # CSV Download
            csv_data = sales.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Sales Report (CSV)", csv_data, "sales_report.csv", "text/csv")
        else:
            st.info("No matching sales transactions found.")

    # 2. Add New Sales Entry Tab
    with tab2:
        st.subheader("➕ Create New Sales Entry")
        st.markdown(
            "Enter customer details and enrollment sales amount. **Received amount will default to 0.00** and **Pending amount will be auto-calculated**."
        )

        branches_df = db_connection.get_all_branches()

        with st.form("new_sale_form", clear_on_submit=True):
            col_s1, col_s2 = st.columns(2)

            with col_s1:
                # Branch selection logic based on Role
                if is_super_admin:
                    branch_map = {f"{row['branch_name']} (ID: {row['branch_id']})": int(row["branch_id"]) for _, row in branches_df.iterrows()}
                    selected_b_str = st.selectbox("Branch Name *", list(branch_map.keys()))
                    form_branch_id = branch_map[selected_b_str]
                else:
                    form_branch_id = assigned_branch_id
                    branch_name_display = user.get("branch_name", f"Branch ID: {form_branch_id}")
                    st.text_input("Assigned Branch (Locked)", value=f"{branch_name_display} (ID: {form_branch_id})", disabled=True)

                sale_date = st.date_input("Sale Date *", value=date.today())
                customer_name = st.text_input("Customer Name *", placeholder="e.g. Anand Sharma")

            with col_s2:
                mobile = st.text_input("Customer Mobile Number (UNIQUE) *", placeholder="e.g. 9876543299", max_chars=15)
                product = st.selectbox(
                    "Product / Course *",
                    [
                        "Data Science",
                        "Data Analytics",
                        "Business Analytics",
                        "Full Stack Development",
                    ],
                )
                gross_sales = st.number_input("Gross Sales Amount (₹) *", min_value=1000.0, step=1000.0, format="%.2f")

            sale_submit = st.form_submit_button("💾 Save Sales Entry", use_container_width=True)

            if sale_submit:
                if not customer_name.strip():
                    st.error("Please enter a valid customer name.")
                elif len(mobile.strip()) < 10:
                    st.error("Please enter a valid 10-digit mobile number.")
                else:
                    try:
                        new_id = db_connection.add_sale_record(
                            branch_id=form_branch_id,
                            date=str(sale_date),
                            name=customer_name.strip(),
                            mobile_number=mobile.strip(),
                            product_name=product,
                            gross_sales=float(gross_sales),
                        )
                        st.success(f"✅ Sale #{new_id} successfully created! Initial Status: 'Open', Pending: ₹{gross_sales:,.2f}")
                        st.rerun()
                    except Exception as e:
                        if "Duplicate entry" in str(e) and "mobile_number" in str(e):
                            st.error("❌ Mobile Number constraint error: A customer with this mobile number already exists in the database.")
                        else:
                            st.error(f"❌ Database error: {e}")


# -----------------------------------------------------------------------------
# TAB 3: PAYMENT SPLITS & TRACKING (TRIGGERS IN ACTION)
# -----------------------------------------------------------------------------
elif menu == "💳 Payment Splits & Tracking":
    st.markdown("<div class='main-header'>💳 Payment Splits & Automated Tracking</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-header'>Record split payments. The <b>MySQL AFTER INSERT trigger</b> will automatically calculate total received and update pending amount!</div>",
        unsafe_allow_html=True,
    )

    tab_split1, tab_split2 = st.tabs(["📑 Payment Splits History", "➕ Record Split Payment"])

    # 1. View Splits
    with tab_split1:
        splits = db_connection.get_payment_splits_records(selected_branch_id)
        st.markdown(f"**Total Payments Recorded: {len(splits)}**")
        if not splits.empty:
            st.dataframe(
                splits,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "amount_paid": st.column_config.NumberColumn("Amount Paid", format="₹ %,.2f"),
                    "gross_sales": st.column_config.NumberColumn("Sale Gross", format="₹ %,.2f"),
                    "received_amount": st.column_config.NumberColumn("Total Received", format="₹ %,.2f"),
                    "pending_amount": st.column_config.NumberColumn("Remaining Pending", format="₹ %,.2f"),
                },
            )
        else:
            st.info("No payment splits recorded for this branch view.")

    # 2. Record New Split Tab
    with tab_split2:
        st.subheader("➕ Record Split Payment for a Sale")

        # Fetch eligible sales (where pending_amount > 0 or status = 'Open')
        eligible_sales = db_connection.get_sales_records(selected_branch_id, status="Open")

        if eligible_sales.empty:
            st.success("🎉 All sales under this view are fully paid! No open sales require payment.")
        else:
            sales_dropdown_map = {}
            for _, r in eligible_sales.iterrows():
                label = f"Sale #{r['sale_id']} - {r['customer_name']} ({r['branch_name']}) | Gross: ₹{r['gross_sales']:,.2f} | Pending: ₹{r['pending_amount']:,.2f}"
                sales_dropdown_map[label] = {
                    "sale_id": int(r["sale_id"]),
                    "pending_amount": float(r["pending_amount"]),
                    "customer_name": r["customer_name"],
                    "branch_name": r["branch_name"],
                }

            with st.form("split_payment_form", clear_on_submit=True):
                selected_sale_label = st.selectbox("Select Sale Transaction *", list(sales_dropdown_map.keys()))
                target_sale = sales_dropdown_map[selected_sale_label]

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    pay_date = st.date_input("Payment Date *", value=date.today())
                    pay_method = st.selectbox("Payment Method *", ["UPI", "Card", "Cash"])
                with col_p2:
                    current_pending = target_sale["pending_amount"]
                    pay_amount = st.number_input(
                        f"Amount to Pay (Current Outstanding: ₹{current_pending:,.2f}) *",
                        min_value=100.0,
                        max_value=max(100.0, current_pending),
                        value=float(min(10000.0, current_pending)),
                        step=500.0,
                        format="%.2f",
                    )

                submit_pay = st.form_submit_button("🚀 Submit Split Payment (Execute Trigger)", use_container_width=True)

                if submit_pay:
                    try:
                        p_id = db_connection.add_payment_split_record(
                            sale_id=target_sale["sale_id"],
                            payment_date=str(pay_date),
                            amount_paid=float(pay_amount),
                            payment_method=pay_method,
                        )
                        st.success(
                            f"✅ Payment #{p_id} of ₹{pay_amount:,.2f} recorded via {pay_method} for Sale #{target_sale['sale_id']}! "
                            f"MySQL trigger executed: `received_amount` updated and `pending_amount` recalculated."
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding payment split: {e}")


# -----------------------------------------------------------------------------
# TAB 4: PREDEFINED SQL ANALYTICS (ALL 20 QUERIES - MANDATORY)
# -----------------------------------------------------------------------------
elif menu == "🔍 Predefined SQL Analytics":
    st.markdown("<div class='main-header'>🔍 Interactive SQL Analytics Explorer</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-header'>Mandatory project deliverable: Execute and verify all <b>20 SQL Capstone Questions</b> with live output.</div>",
        unsafe_allow_html=True,
    )

    categories = [
        "All Categories",
        "Basic Queries",
        "Aggregation Queries",
        "Join-Based Queries",
        "Financial Tracking Queries",
    ]
    selected_cat = st.selectbox("Filter Questions by Category", categories)

    all_queries = db_connection.PREDEFINED_QUERIES
    if selected_cat != "All Categories":
        filtered_queries = [q for q in all_queries if q["category"] == selected_cat]
    else:
        filtered_queries = all_queries

    query_options = {f"{q['id']}. {q['title']}": q for q in filtered_queries}
    selected_q_label = st.selectbox("Select SQL Question to Inspect & Run", list(query_options.keys()))
    q_data = query_options[selected_q_label]

    st.markdown("---")
    st.markdown(f"### ❓ Question #{q_data['id']}: {q_data['title']}")
    st.markdown(f"**Category:** `{q_data['category']}` &nbsp;|&nbsp; **Description:** {q_data['description']}")

    # Display Query Code Box
    st.code(q_data["sql"], language="sql")

    col_btn, col_down = st.columns([1, 4])
    with col_btn:
        run_clicked = st.button("▶️ Execute Query", use_container_width=True)

    # Automatically run on selection or when clicked
    try:
        result_df = db_connection.execute_query(q_data["sql"])
        st.markdown(f"**Query Results ({len(result_df)} rows returned):**")
        st.dataframe(result_df, use_container_width=True, hide_index=True)

        csv_result = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Query Result (CSV)",
            data=csv_result,
            file_name=f"query_{q_data['id']}_results.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"❌ Error executing query: {e}")

    # Optional: Super Admin Custom Query Runner
    if is_super_admin:
        st.markdown("---")
        with st.expander("🛠️ Super Admin Custom SQL Query Runner (SELECT only)"):
            custom_sql = st.text_area("Enter Custom SQL Query", value="SELECT branch_name, COUNT(*) AS count FROM branches GROUP BY branch_name;")
            if st.button("Run Custom Query"):
                if not custom_sql.strip().lower().startswith("select"):
                    st.error("Only SELECT queries are permitted in the playground.")
                else:
                    try:
                        c_df = db_connection.execute_query(custom_sql)
                        st.dataframe(c_df, use_container_width=True)
                    except Exception as err:
                        st.error(f"Query Error: {err}")


# -----------------------------------------------------------------------------
# TAB 5: DATABASE & TRIGGER STATUS
# -----------------------------------------------------------------------------
elif menu == "⚙️ Database & Trigger Status":
    st.markdown("<div class='main-header'>⚙️ Database Architecture & Trigger Inspector</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-header'>Verify table structures, foreign keys, triggers, and generated columns.</div>",
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["🗂️ Tables & Schemas", "⚡ Active Triggers", "👥 Registered Users"])

    with t1:
        st.subheader("Database Tables in `sales_management_db`")
        for table in ["branches", "customer_sales", "payment_splits", "users"]:
            st.markdown(f"#### Table: `{table}`")
            desc_df = db_connection.execute_query(f"DESCRIBE {table};")
            st.dataframe(desc_df, use_container_width=True, hide_index=True)

    with t2:
        st.subheader("Triggers on `payment_splits` Table")
        trig_df = db_connection.execute_query("SHOW TRIGGERS FROM sales_management_db;")
        if not trig_df.empty:
            st.dataframe(trig_df[["Trigger", "Event", "Table", "Timing"]], use_container_width=True, hide_index=True)
        else:
            st.warning("No triggers found.")

        st.info(
            "💡 **Automation Logic**: When a payment split is recorded, the trigger automatically recalculates `SUM(amount_paid)` "
            "for that `sale_id`, updates `received_amount` in `customer_sales`, and MySQL's stored generated column "
            "`pending_amount = (gross_sales - received_amount)` instantly reflects the outstanding balance without manual intervention."
        )

    with t3:
        st.subheader("Users & Access Control Table")
        users_df = db_connection.execute_query("SELECT user_id, username, role, branch_id, email FROM users;")
        st.dataframe(users_df, use_container_width=True, hide_index=True)
