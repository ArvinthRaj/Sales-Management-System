#TEST THE TRIGGERS 
USE sales_management_system;
#test 1
INSERT INTO customer_sales (branch_id, `date`, `name`, mobile_number, product_name, gross_sales, received_amount, status)
VALUES (1, '2026-10-14', 'Trigger Test', '9000000001', 'DS', 10000, 7000, 'Close');

SET @sid = LAST_INSERT_ID();    

SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM customer_sales WHERE sale_id = @sid;


#TEST 2: first payment of 4000
INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
VALUES (@sid, '2026-10-14', 4000, 'UPI');

SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM customer_sales WHERE sale_id = @sid;

#TEST 3: second payment of 6000 (the rest)
INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
VALUES (@sid, '2026-10-15', 6000, 'Cash');

SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM customer_sales WHERE sale_id = @sid;

#CLEAN UP: delete the test rows
DELETE FROM payment_splits WHERE sale_id = @sid;
DELETE FROM customer_sales WHERE sale_id = @sid;
