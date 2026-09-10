CREATE DATABASE IF NOT EXISTS smart_queue_database;

USE smart_queue_database;

CREATE TABLE IF NOT EXISTS queue (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    service VARCHAR(100) NOT NULL,
    priority INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);



USE smart_queue_database;

CREATE TABLE IF NOT EXISTS current_serving (
    id INT PRIMARY KEY,
    token_id INT,
    counter_number INT DEFAULT 1
);

INSERT INTO current_serving (id, token_id, counter_number)
VALUES (1, NULL, 1);

SELECT * FROM current_serving;
SELECT * FROM queue;
SHOW TABLES;
