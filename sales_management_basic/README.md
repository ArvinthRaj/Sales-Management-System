# Sales Management System - BASIC VERSION

Same project, written with simple commands only. Tools: MySQL, Python, Streamlit.

## Files and run order

| Order | File | What it does |
|---|---|---|
| 1 | `schema.sql` | Creates the database, 4 tables and 2 triggers |
| 2 | `sample_data.sql` | Loads your dataset (8 branches, 9 users, 1,000 sales, 2,011 payments) |
| 3 | `trigger_tests.sql` | Tests the triggers with manual inserts |
| 4 | `sql_queries.sql` | The 20 SQL questions |
| 5 | `app.py` | The Streamlit app (one file) |
| - | `requirements.txt` | Python libraries to install |

## How to run
1. MySQL Workbench: run `schema.sql`, then `sample_data.sql`.
2. Check: `SELECT COUNT(*) FROM customer_sales;` gives 1000 and `SELECT COUNT(*) FROM payment_splits;` gives 2011.
3. Open `app.py` and change `DB_PASSWORD = "your_mysql_password"` to your real MySQL password.
   (Put a dummy text back before uploading to GitHub.)
4. VS Code terminal: `pip install -r requirements.txt`, then `streamlit run app.py`.
5. Login: `superadmin` / `super123`, or `admin_chennai` / `admin123`.

## What is simpler in this version
| Main version | Basic version |
|---|---|
| 4 triggers (with error checks) | 2 triggers: one on `customer_sales`, one on `payment_splits` |
| CHECK rules, ENUM columns, indexes | Plain VARCHAR columns, no extra rules |
| `db.py` + `queries.py` + `app.py` | Everything in one `app.py` |
| Regex, lambda, comprehensions | Plain `if`, `for`, string `replace` |
| Overpayment blocked by a trigger | Overpayment blocked in Python (`if amount > pending`) |

Still included because the project brief asks for them: triggers, a generated column (`pending_amount`),
login with Super Admin / Admin roles, and the Customer Sales filters.

## Commands used in this version

### SQL
`CREATE DATABASE`, `USE`, `CREATE TABLE`, `DROP TABLE`, `INT / VARCHAR / DATE / DECIMAL`, `PRIMARY KEY`,
`AUTO_INCREMENT`, `NOT NULL`, `UNIQUE`, `DEFAULT`, `FOREIGN KEY`, `INSERT`, `SELECT`, `WHERE`, `ORDER BY`,
`LIMIT`, `SUM / COUNT / AVG`, `GROUP BY`, `JOIN`, `LEFT JOIN`, `UPDATE`, `DELETE`.
Two slightly advanced ones: `GENERATED ALWAYS AS (...)` (a column MySQL calculates by itself) and
`CREATE TRIGGER` (code MySQL runs by itself when a row is inserted).

### Triggers in one sentence each
* `trg_sales_before_insert`: every new sale starts with received 0 and status Open.
* `trg_payment_after_insert`: when a payment is added, add it to received_amount and set status to Close when fully paid.

### Python
`import`, variables, `def` functions, `if / elif / else`, `for` loop, lists, `try / except`,
`mysql.connector` (`connect`, `cursor`, `execute`, `fetchall`, `commit`), pandas `DataFrame`.

### Streamlit
`st.title`, `st.header`, `st.write`, `st.text_input`, `st.number_input`, `st.date_input`, `st.selectbox`,
`st.button`, `st.columns`, `st.metric`, `st.dataframe`, `st.bar_chart`, `st.line_chart`, `st.sidebar`,
`st.radio`, `st.success`, `st.error`, `st.session_state`.

## App pages
Login, Customer Sales (filters: Branch, Product, Start date, End date), Dashboard, Add Sale, Add Payment,
Pending Payments, SQL Queries (20 queries). Admins see only their own branch everywhere.

## Tested
Schema, data load (received total equals payments total), both triggers, all 20 queries for Super Admin and
Admin, login, filters, add sale, add payment (including the "amount too large" check).
