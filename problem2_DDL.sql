DROP DATABASE IF EXISTS library;
CREATE DATABASE library;
USE library;

-- 1. AUTHOR
CREATE TABLE author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

-- 2. PUBLISHER
CREATE TABLE publisher (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

-- 3. CATEGORY
CREATE TABLE category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- 4. BOOK
CREATE TABLE book (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    publish_year INT,
    author_id INT NOT NULL,
    publisher_id INT NOT NULL,
    category_id INT NOT NULL,

    FOREIGN KEY (author_id)
        REFERENCES author(author_id)
        ON DELETE CASCADE,

    FOREIGN KEY (publisher_id)
        REFERENCES publisher(publisher_id),

    FOREIGN KEY (category_id)
        REFERENCES category(category_id)
);

-- 5. MEMBER
CREATE TABLE member (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    join_date DATE NOT NULL
);

-- 6. LOAN
CREATE TABLE loan (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,

    FOREIGN KEY (book_id)
        REFERENCES book(book_id)
        ON DELETE CASCADE,

    FOREIGN KEY (member_id)
        REFERENCES member(member_id)
);

-- 7. REVIEW
CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    rating INT NOT NULL,
    review_date DATE NOT NULL,

    FOREIGN KEY (book_id)
        REFERENCES book(book_id)
        ON DELETE CASCADE,

    FOREIGN KEY (member_id)
        REFERENCES member(member_id)
        ON DELETE CASCADE,

    CHECK (rating BETWEEN 1 AND 5),

    UNIQUE (book_id, member_id)
);

-- BONUS: Book Details View
CREATE VIEW book_details AS
SELECT
    b.book_id,
    b.title,
    b.price,
    a.name AS author_name,
    p.name AS publisher_name,
    c.name AS category_name
FROM book b
JOIN author a ON b.author_id = a.author_id
JOIN publisher p ON b.publisher_id = p.publisher_id
JOIN category c ON b.category_id = c.category_id;

