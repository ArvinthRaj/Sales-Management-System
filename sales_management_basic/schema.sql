 #SALES MANAGEMENT SYSTEM  
CREATE DATABASE  sales_management_system;

USE sales_management_system;

#Table 1: branches
CREATE TABLE branches (
    branch_id         INT AUTO_INCREMENT PRIMARY KEY,
    branch_name       VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

# Table 2: customer_sales
CREATE TABLE customer_sales (
    sale_id         INT AUTO_INCREMENT PRIMARY KEY,
    branch_id       INT NOT NULL,
    `date`          DATE NOT NULL,
    `name`          VARCHAR(100) NOT NULL,
    mobile_number   VARCHAR(15) NOT NULL UNIQUE,
    product_name    VARCHAR(30) NOT NULL,
    gross_sales     DECIMAL(12,2) NOT NULL,
    received_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    pending_amount  DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status          VARCHAR(10) NOT NULL DEFAULT 'Open',
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
# Table 3: users
CREATE TABLE users (
    user_id   INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(100) NOT NULL UNIQUE,
    password  VARCHAR(255) NOT NULL,
    branch_id INT NULL,
    role      VARCHAR(20) NOT NULL,
    email     VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
#Table 4: payment_splits
CREATE TABLE payment_splits (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    sale_id        INT NOT NULL,
    payment_date   DATE NOT NULL,
    amount_paid    DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
);
# TRIGGERS  

DELIMITER $$
#Trigger 1 (customer_sales)
CREATE TRIGGER trg_sales_before_insert
BEFORE INSERT ON customer_sales
FOR EACH ROW
BEGIN
    SET NEW.received_amount = 0;
    SET NEW.status = 'Open';
END$$

#Trigger 2 (payment_splits): when a payment is added,
CREATE TRIGGER trg_payment_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = received_amount + NEW.amount_paid,
        status = IF(received_amount >= gross_sales, 'Close', 'Open')
    WHERE sale_id = NEW.sale_id;
END$$

DELIMITER ;
