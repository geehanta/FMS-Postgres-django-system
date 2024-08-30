CREATE TABLE IF NOT EXISTS demodata (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);
INSERT INTO demodata (id, username, email) VALUES
(1, 'demodata1', 'demodata@gmail.com'),
(2, 'demodata2', 'demodata2@gmail.com'),
(3, 'demodata3', 'demodata3@gmail.com');

INSERT INTO users (userid, username) VALUES
(1, 'userdata1'),
(2, 'userdata2'),
(3, 'userdata3');

SELECT * FROM users






