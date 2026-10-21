   USE sales_management_system;
   SELECT COUNT(*) FROM customer_sales;
   SELECT COUNT(*) FROM payment_splits;
   SELECT
    (SELECT COUNT(*) FROM customer_sales) AS total_customer_sales,
    (SELECT COUNT(*) FROM payment_splits) AS total_payment_splits;