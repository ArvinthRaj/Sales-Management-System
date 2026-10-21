USE sales_management_system;
-- 20 SQL questions (brief asks: any 4 basic, 4 aggregation, 4 join, 3 financial)

-- ======== Basic Queries ========
-- Q1. All records from customer_sales
SELECT s.* FROM customer_sales s ORDER BY s.sale_id;

-- Q2. All records from branches
SELECT b.* FROM branches b;

-- Q3. All records from payment_splits
SELECT p.* FROM payment_splits p JOIN customer_sales s ON s.sale_id = p.sale_id ORDER BY p.payment_id;

-- Q4. Sales with status = 'Open'
SELECT s.* FROM customer_sales s WHERE s.status = 'Open';

-- Q5. Sales belonging to the Chennai branch
SELECT s.* FROM customer_sales s JOIN branches b ON b.branch_id = s.branch_id
WHERE b.branch_name = 'Chennai';


-- ======== Aggregation Queries ========
-- Q6. Total gross sales across all branches
SELECT SUM(s.gross_sales) AS total_gross_sales FROM customer_sales s;

-- Q7. Total received amount
SELECT SUM(s.received_amount) AS total_received FROM customer_sales s;

-- Q8. Total pending amount
SELECT SUM(s.pending_amount) AS total_pending FROM customer_sales s;

-- Q9. Number of sales per branch
SELECT b.branch_name, COUNT(s.sale_id) AS total_sales
FROM branches b LEFT JOIN customer_sales s ON s.branch_id = b.branch_id
GROUP BY b.branch_id, b.branch_name;

-- Q10. Average gross sales amount
SELECT ROUND(AVG(s.gross_sales), 2) AS avg_gross_sales FROM customer_sales s;


-- ======== Join-Based Queries ========
-- Q11. Sales with branch name
SELECT s.sale_id, s.`name`, s.product_name, s.gross_sales, b.branch_name
FROM customer_sales s JOIN branches b ON b.branch_id = s.branch_id;

-- Q12. Sales with total payment received (payment_splits)
SELECT s.sale_id, s.`name`, s.gross_sales, COALESCE(SUM(p.amount_paid), 0) AS total_payment_received
FROM customer_sales s LEFT JOIN payment_splits p ON p.sale_id = s.sale_id
GROUP BY s.sale_id, s.`name`, s.gross_sales;

-- Q13. Branch-wise total gross sales
SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM branches b JOIN customer_sales s ON s.branch_id = b.branch_id
GROUP BY b.branch_name ORDER BY total_gross_sales DESC;

-- Q14. Sales with payment method used
SELECT s.sale_id, s.`name`, p.amount_paid, p.payment_method, p.payment_date
FROM customer_sales s JOIN payment_splits p ON p.sale_id = s.sale_id
ORDER BY s.sale_id, p.payment_date;

-- Q15. Sales with branch admin name
SELECT s.sale_id, s.`name`, b.branch_name, b.branch_admin_name
FROM customer_sales s JOIN branches b ON b.branch_id = s.branch_id;


-- ======== Financial Tracking Queries ========
-- Q16. Sales where pending amount > 5000
SELECT s.sale_id, s.`name`, s.gross_sales, s.received_amount, s.pending_amount
FROM customer_sales s WHERE s.pending_amount > 5000
ORDER BY s.pending_amount DESC;

-- Q17. Top 3 highest gross sales
SELECT s.sale_id, s.`name`, s.product_name, s.gross_sales
FROM customer_sales s
ORDER BY s.gross_sales DESC LIMIT 3;

-- Q18. Branch with the highest total gross sales
SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM branches b JOIN customer_sales s ON s.branch_id = b.branch_id
GROUP BY b.branch_name ORDER BY total_gross_sales DESC LIMIT 1;

-- Q19. Monthly sales summary (month & year)
SELECT YEAR(s.`date`) AS sale_year, MONTH(s.`date`) AS sale_month,
       COUNT(*) AS no_of_sales, SUM(s.gross_sales) AS total_gross_sales
FROM customer_sales s
GROUP BY YEAR(s.`date`), MONTH(s.`date`)
ORDER BY sale_year, sale_month;

-- Q20. Payment method-wise total collection
SELECT p.payment_method, COUNT(*) AS transactions, SUM(p.amount_paid) AS total_collected
FROM payment_splits p JOIN customer_sales s ON s.sale_id = p.sale_id
GROUP BY p.payment_method ORDER BY total_collected DESC;

