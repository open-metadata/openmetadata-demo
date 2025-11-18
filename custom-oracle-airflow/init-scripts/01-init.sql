-- Create sample schema and tables for OpenMetadata ingestion testing

-- Create a sample user/schema
CREATE USER openmetadata_demo IDENTIFIED BY demo123;
GRANT CONNECT, RESOURCE TO openmetadata_demo;
GRANT CREATE SESSION TO openmetadata_demo;
GRANT CREATE TABLE TO openmetadata_demo;
GRANT CREATE VIEW TO openmetadata_demo;
GRANT UNLIMITED TABLESPACE TO openmetadata_demo;

-- Switch to the demo schema
ALTER SESSION SET CURRENT_SCHEMA = openmetadata_demo;

-- Create sample tables
CREATE TABLE customers (
    customer_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(50),
    last_name VARCHAR2(50),
    email VARCHAR2(100),
    phone VARCHAR2(20),
    created_date DATE DEFAULT SYSDATE
);

CREATE TABLE orders (
    order_id NUMBER PRIMARY KEY,
    customer_id NUMBER,
    order_date DATE DEFAULT SYSDATE,
    total_amount NUMBER(10,2),
    status VARCHAR2(20),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id NUMBER PRIMARY KEY,
    product_name VARCHAR2(100),
    description CLOB,
    price NUMBER(10,2),
    category VARCHAR2(50),
    created_date DATE DEFAULT SYSDATE
);

-- Insert sample data
INSERT INTO customers VALUES (1, 'John', 'Doe', 'john.doe@email.com', '555-0001', SYSDATE-30);
INSERT INTO customers VALUES (2, 'Jane', 'Smith', 'jane.smith@email.com', '555-0002', SYSDATE-25);
INSERT INTO customers VALUES (3, 'Bob', 'Johnson', 'bob.johnson@email.com', '555-0003', SYSDATE-20);

INSERT INTO products VALUES (1, 'Laptop', 'High-performance laptop', 999.99, 'Electronics', SYSDATE-10);
INSERT INTO products VALUES (2, 'Mouse', 'Wireless optical mouse', 29.99, 'Electronics', SYSDATE-8);
INSERT INTO products VALUES (3, 'Keyboard', 'Mechanical keyboard', 79.99, 'Electronics', SYSDATE-5);

INSERT INTO orders VALUES (1, 1, SYSDATE-7, 999.99, 'COMPLETED');
INSERT INTO orders VALUES (2, 2, SYSDATE-5, 109.98, 'COMPLETED');
INSERT INTO orders VALUES (3, 3, SYSDATE-3, 29.99, 'PENDING');

-- Create a view for testing
CREATE VIEW customer_orders AS
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    o.order_id,
    o.order_date,
    o.total_amount,
    o.status
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

COMMIT;