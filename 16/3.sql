CREATE DATABASE flask_db;
USE flask_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    content TEXT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Datos de prueba
INSERT INTO users (username, password) VALUES ("admin", "1234"), ("juan", "5678");
INSERT INTO posts (title, content, user_id) VALUES ("Primer post", "Hola Flask", 1);
