
#SALES MANAGEMENT SYSTEM - BASIC VERSION (one file, simple Python)

import hashlib
from datetime import date
from decimal import Decimal

import mysql.connector
import pandas as pd
import streamlit as st

# MySQL settings 

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "sales_management_system"

PRODUCTS = ["DS", "DA", "BA", "FSD", "BI", "AI", "ML", "SQL"]
PAYMENT_METHODS = ["Cash", "UPI", "Card"]


#2. Database helper functions 
def connect():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )


def run_select(sql, values=()):
    """Run a SELECT and return the result as a table (DataFrame)."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    columns = cursor.column_names
    conn.close()
    df = pd.DataFrame(rows, columns=columns)
    # money columns come as Decimal; change them to normal numbers for charts
    for col in df.columns:
        if len(df) > 0 and isinstance(df[col].iloc[0], Decimal):
            df[col] = df[col].astype(float)
    return df


def run_change(sql, values=()):
    """Run INSERT / UPDATE and save it."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()


def branch_filter(alias, branch_id):
    """Super Admin (branch_id 0) sees all branches, Admin sees only own branch."""
    if branch_id == 0:
        return "1 = 1"
    return alias + ".branch_id = " + str(int(branch_id))


# 3. Login page 
def login_page():
    st.title("Sales Management System")
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        df = run_select(
            "SELECT u.username, u.role, u.branch_id, b.branch_name "
            "FROM users u LEFT JOIN branches b ON u.branch_id = b.branch_id "
            "WHERE u.username = %s AND u.password = %s",
            [username, hashed],
        )
        if len(df) == 0:
            st.error("Wrong username or password")
        else:
            st.session_state["logged_in"] = True
            st.session_state["username"] = df["username"][0]
            st.session_state["role"] = df["role"][0]
            if df["role"][0] == "Super Admin":
                st.session_state["branch_id"] = 0
                st.session_state["branch_name"] = "All Branches"
            else:
                st.session_state["branch_id"] = int(df["branch_id"][0])
                st.session_state["branch_name"] = df["branch_name"][0]
            st.rerun()


#  4. Customer Sales page (first page after login) 
def customer_sales_page():
    st.header("Customer Sales")
    role = st.session_state["role"]
    branch_id = st.session_state["branch_id"]

    col1, col2, col3, col4 = st.columns(4)

    # Filter 1: Branch (only Super Admin can choose)
    if role == "Super Admin":
        branches = run_select("SELECT branch_id, branch_name FROM branches ORDER BY branch_name")
        names = ["All Branches"] + branches["branch_name"].tolist()
        chosen = col1.selectbox("Branch", names)
        if chosen == "All Branches":
            branch_id = 0
        else:
            branch_id = int(branches[branches["branch_name"] == chosen]["branch_id"].iloc[0])
    else:
        col1.write("Branch: " + st.session_state["branch_name"])

    # Filter 2: Product
    products = run_select("SELECT DISTINCT product_name FROM customer_sales ORDER BY product_name")
    product = col2.selectbox("Product name", ["All"] + products["product_name"].tolist())

    # Filter 3 and 4: Start date and End date
    start_date = col3.date_input("Start date", date(2024, 1, 1))
    end_date = col4.date_input("End date", date(2024, 12, 31))

    # Build the SQL step by step
    sql = (
        "SELECT s.sale_id, b.branch_name, s.`date`, s.`name`, s.mobile_number, "
        "s.product_name, s.gross_sales, s.received_amount, s.pending_amount, s.status "
        "FROM customer_sales s JOIN branches b ON s.branch_id = b.branch_id "
        "WHERE " + branch_filter("s", branch_id)
    )
    values = []
    if product != "All":
        sql = sql + " AND s.product_name = %s"
        values.append(product)
    sql = sql + " AND s.`date` BETWEEN %s AND %s ORDER BY s.`date` DESC"
    values.append(start_date)
    values.append(end_date)

    df = run_select(sql, values)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Records", len(df))
    m2.metric("Gross sales", "Rs " + format(df["gross_sales"].sum(), ",.0f"))
    m3.metric("Received", "Rs " + format(df["received_amount"].sum(), ",.0f"))
    m4.metric("Pending", "Rs " + format(df["pending_amount"].sum(), ",.0f"))
    st.dataframe(df)


# 5. Dashboard page 
def dashboard_page():
    st.header("Dashboard")
    branch_id = st.session_state["branch_id"]
    cond_s = branch_filter("s", branch_id)
    cond_b = branch_filter("b", branch_id)

    total = run_select(
        "SELECT SUM(s.gross_sales) AS gross, SUM(s.received_amount) AS received, "
        "SUM(s.pending_amount) AS pending, COUNT(*) AS total_sales "
        "FROM customer_sales s WHERE " + cond_s
    )
    gross = total["gross"][0]
    received = total["received"][0]
    pending = total["pending"][0]
    pending_percent = pending / gross * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", "Rs " + format(gross, ",.0f"))
    c2.metric("Received", "Rs " + format(received, ",.0f"))
    c3.metric("Pending", "Rs " + format(pending, ",.0f"))
    c4.metric("Pending %", format(pending_percent, ".1f") + "%")

    st.subheader("Branch wise sales")
    df1 = run_select(
        "SELECT b.branch_name, SUM(s.gross_sales) AS gross, SUM(s.received_amount) AS received, "
        "SUM(s.pending_amount) AS pending FROM branches b JOIN customer_sales s "
        "ON b.branch_id = s.branch_id WHERE " + cond_b + " GROUP BY b.branch_name"
    )
    st.bar_chart(df1.set_index("branch_name"))

    st.subheader("Payment method summary")
    df2 = run_select(
        "SELECT p.payment_method, SUM(p.amount_paid) AS collected FROM payment_splits p "
        "JOIN customer_sales s ON p.sale_id = s.sale_id WHERE " + cond_s + " GROUP BY p.payment_method"
    )
    st.bar_chart(df2.set_index("payment_method"))

    st.subheader("Open vs Close sales")
    df3 = run_select(
        "SELECT s.status, COUNT(*) AS total FROM customer_sales s WHERE " + cond_s + " GROUP BY s.status"
    )
    st.bar_chart(df3.set_index("status"))

    st.subheader("Monthly sales")
    df4 = run_select(
        "SELECT MONTH(s.`date`) AS month, SUM(s.gross_sales) AS sales FROM customer_sales s "
        "WHERE " + cond_s + " GROUP BY MONTH(s.`date`) ORDER BY month"
    )
    st.line_chart(df4.set_index("month"))


#  6. Add Sale page 
def add_sale_page():
    st.header("Add New Sale")
    if st.session_state["role"] == "Super Admin":
        branches = run_select("SELECT branch_id, branch_name FROM branches ORDER BY branch_name")
        chosen = st.selectbox("Branch", branches["branch_name"].tolist())
        branch_id = int(branches[branches["branch_name"] == chosen]["branch_id"].iloc[0])
    else:
        branch_id = st.session_state["branch_id"]
        st.write("Branch: " + st.session_state["branch_name"])

    sale_date = st.date_input("Sale date")
    name = st.text_input("Customer name")
    mobile = st.text_input("Mobile number (10 digits)")
    product = st.selectbox("Product", PRODUCTS)
    gross = st.number_input("Gross sales (Rs)", min_value=0.0, step=1000.0)

    if st.button("Save Sale"):
        if name == "":
            st.error("Enter the customer name")
        elif len(mobile) != 10 or not mobile.isdigit():
            st.error("Mobile number must be 10 digits")
        elif gross <= 0:
            st.error("Gross sales must be more than 0")
        else:
            try:
                run_change(
                    "INSERT INTO customer_sales (branch_id, `date`, `name`, mobile_number, product_name, gross_sales) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    [branch_id, sale_date, name, mobile, product, gross],
                )
                st.success("Sale saved")
            except mysql.connector.Error as error:
                if "Duplicate" in str(error):
                    st.error("This mobile number already exists")
                else:
                    st.error(str(error))


#  7. Add Payment page 
def add_payment_page():
    st.header("Add Payment")
    cond = branch_filter("s", st.session_state["branch_id"])
    df = run_select(
        "SELECT s.sale_id, s.`name`, s.pending_amount FROM customer_sales s "
        "WHERE s.status = 'Open' AND " + cond + " ORDER BY s.sale_id"
    )
    if len(df) == 0:
        st.success("No open sales. Everything is fully paid.")
        return

    # keep the dropdown text fixed (sale id + name) so the selection does not jump after a payment
    labels = []
    for i in range(len(df)):
        labels.append(str(df["sale_id"][i]) + " - " + df["name"][i])
    chosen = st.selectbox("Select sale", labels)
    sale_id = int(chosen.split(" - ")[0])
    pending = float(df[df["sale_id"] == sale_id]["pending_amount"].iloc[0])
    st.write("Pending amount: Rs " + format(pending, ",.0f"))

    amount = st.number_input("Amount paid (Rs)", min_value=0.0, step=500.0)
    pay_date = st.date_input("Payment date")
    method = st.selectbox("Payment method", PAYMENT_METHODS)

    if st.button("Save Payment"):
        if amount <= 0:
            st.error("Enter an amount more than 0")
        elif amount > pending:
            st.error("Amount is more than the pending amount")
        else:
            run_change(
                "INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method) "
                "VALUES (%s, %s, %s, %s)",
                [sale_id, pay_date, amount, method],
            )
            st.success("Payment saved. The trigger updated received, pending and status.")


# 8. Pending Payments page 
def pending_page():
    st.header("Pending Payments")
    cond = branch_filter("s", st.session_state["branch_id"])
    df = run_select(
        "SELECT s.sale_id, b.branch_name, s.`name`, s.mobile_number, s.gross_sales, "
        "s.received_amount, s.pending_amount FROM customer_sales s "
        "JOIN branches b ON s.branch_id = b.branch_id "
        "WHERE s.pending_amount > 0 AND " + cond + " ORDER BY s.pending_amount DESC"
    )
    st.metric("Total pending", "Rs " + format(df["pending_amount"].sum(), ",.0f"))
    st.dataframe(df)


# 9. SQL Queries page 
QUERY_LIST = [
    ("Q1. All records from customer_sales", """SELECT s.* FROM customer_sales s WHERE {S} ORDER BY s.sale_id"""),
    ("Q2. All records from branches", """SELECT b.* FROM branches b WHERE {B}"""),
    ("Q3. All records from payment_splits", """SELECT p.* FROM payment_splits p JOIN customer_sales s ON s.sale_id = p.sale_id
WHERE {S} ORDER BY p.payment_id"""),
    ("Q4. Sales with status = 'Open'", """SELECT s.* FROM customer_sales s WHERE s.status = 'Open' AND {S}"""),
    ("Q5. Sales belonging to the Chennai branch", """SELECT s.* FROM customer_sales s JOIN branches b ON b.branch_id = s.branch_id
WHERE b.branch_name = 'Chennai' AND {S}"""),
    ("Q6. Total gross sales across all branches", """SELECT SUM(s.gross_sales) AS total_gross_sales FROM customer_sales s WHERE {S}"""),
    ("Q7. Total received amount", """SELECT SUM(s.received_amount) AS total_received FROM customer_sales s WHERE {S}"""),
    ("Q8. Total pending amount", """SELECT SUM(s.pending_amount) AS total_pending FROM customer_sales s WHERE {S}"""),
    ("Q9. Number of sales per branch", """SELECT b.branch_name, COUNT(s.sale_id) AS total_sales
FROM branches b LEFT JOIN customer_sales s ON s.branch_id = b.branch_id
WHERE {B}
GROUP BY b.branch_id, b.branch_name"""),
    ("Q10. Average gross sales amount", """SELECT ROUND(AVG(s.gross_sales), 2) AS avg_gross_sales FROM customer_sales s WHERE {S}"""),
    ("Q11. Sales with branch name", """SELECT s.sale_id, s.`name`, s.product_name, s.gross_sales, b.branch_name
FROM customer_sales s JOIN branches b ON b.branch_id = s.branch_id
WHERE {S}"""),
    ("Q12. Sales with total payment received (payment_splits)", """SELECT s.sale_id, s.`name`, s.gross_sales, COALESCE(SUM(p.amount_paid), 0) AS total_payment_received
FROM customer_sales s LEFT JOIN payment_splits p ON p.sale_id = s.sale_id
WHERE {S}
GROUP BY s.sale_id, s.`name`, s.gross_sales"""),
    ("Q13. Branch-wise total gross sales", """SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM branches b JOIN customer_sales s ON s.branch_id = b.branch_id
WHERE {B}
GROUP BY b.branch_name ORDER BY total_gross_sales DESC"""),
    ("Q14. Sales with payment method used", """SELECT s.sale_id, s.`name`, p.amount_paid, p.payment_method, p.payment_date
FROM customer_sales s JOIN payment_splits p ON p.sale_id = s.sale_id
WHERE {S}
ORDER BY s.sale_id, p.payment_date"""),
    ("Q15. Sales with branch admin name", """SELECT s.sale_id, s.`name`, b.branch_name, b.branch_admin_name
FROM customer_sales s JOIN branches b ON b.branch_id = s.branch_id
WHERE {S}"""),
    ("Q16. Sales where pending amount > 5000", """SELECT s.sale_id, s.`name`, s.gross_sales, s.received_amount, s.pending_amount
FROM customer_sales s WHERE s.pending_amount > 5000 AND {S}
ORDER BY s.pending_amount DESC"""),
    ("Q17. Top 3 highest gross sales", """SELECT s.sale_id, s.`name`, s.product_name, s.gross_sales
FROM customer_sales s WHERE {S}
ORDER BY s.gross_sales DESC LIMIT 3"""),
    ("Q18. Branch with the highest total gross sales", """SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM branches b JOIN customer_sales s ON s.branch_id = b.branch_id
WHERE {B}
GROUP BY b.branch_name ORDER BY total_gross_sales DESC LIMIT 1"""),
    ("Q19. Monthly sales summary (month & year)", """SELECT YEAR(s.`date`) AS sale_year, MONTH(s.`date`) AS sale_month,
       COUNT(*) AS no_of_sales, SUM(s.gross_sales) AS total_gross_sales
FROM customer_sales s WHERE {S}
GROUP BY YEAR(s.`date`), MONTH(s.`date`)
ORDER BY sale_year, sale_month"""),
    ("Q20. Payment method-wise total collection", """SELECT p.payment_method, COUNT(*) AS transactions, SUM(p.amount_paid) AS total_collected
FROM payment_splits p JOIN customer_sales s ON s.sale_id = p.sale_id
WHERE {S}
GROUP BY p.payment_method ORDER BY total_collected DESC"""),
]


def sql_queries_page():
    st.header("SQL Queries")
    titles = []
    for item in QUERY_LIST:
        titles.append(item[0])
    chosen = st.selectbox("Select a query", titles)

    sql = ""
    for item in QUERY_LIST:
        if item[0] == chosen:
            sql = item[1]

    branch_id = st.session_state["branch_id"]
    sql = sql.replace("{S}", branch_filter("s", branch_id))
    sql = sql.replace("{B}", branch_filter("b", branch_id))

    st.code(sql, language="sql")
    if st.button("Run query"):
        df = run_select(sql)
        st.dataframe(df)
        st.write(str(len(df)) + " rows")


# 10. Main program 
def main_app():
    st.sidebar.write("User: " + st.session_state["username"])
    st.sidebar.write("Role: " + st.session_state["role"])
    st.sidebar.write("Branch: " + st.session_state["branch_name"])
    page = st.sidebar.radio(
        "Menu",
        ["Customer Sales", "Dashboard", "Add Sale", "Add Payment", "Pending Payments", "SQL Queries"],
    )
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if page == "Customer Sales":
        customer_sales_page()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "Add Sale":
        add_sale_page()
    elif page == "Add Payment":
        add_payment_page()
    elif page == "Pending Payments":
        pending_page()
    else:
        sql_queries_page()


if "logged_in" not in st.session_state:
    login_page()
else:
    main_app()
