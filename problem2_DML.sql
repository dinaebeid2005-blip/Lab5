

USE library;

-- =================================
-- 1. AUTHORS
-- =================================

INSERT INTO author (author_id, name, country) VALUES
(1, 'J.K. Rowling', 'United Kingdom'),
(2, 'George Orwell', 'United Kingdom'),
(3, 'Naguib Mahfouz', 'Egypt'),
(4, 'Agatha Christie', 'United Kingdom'),
(5, 'Paulo Coelho', 'Brazil'),
(6, 'Test Author', 'Egypt');


-- =================================
-- 2. PUBLISHERS
-- =================================

INSERT INTO publisher (publisher_id, name, country) VALUES
(1, 'Penguin Books', 'United Kingdom'),
(2, 'Dar El Shorouk', 'Egypt'),
(3, 'HarperCollins', 'United States');


-- =================================
-- 3. CATEGORIES
-- =================================

INSERT INTO category (category_id, name) VALUES
(1, 'Fantasy'),
(2, 'Mystery'),
(3, 'Literature');


-- =================================
-- 4. BOOKS
-- =================================

INSERT INTO book
(book_id, title, price, publish_year,
 author_id, publisher_id, category_id)
VALUES
(1, 'Harry Potter', 25.00, 1997, 1, 1, 1),
(2, 'The Casual Vacancy', 30.00, 2012, 1, 1, 3),
(3, '1984', 20.00, 1949, 2, 1, 3),
(4, 'Animal Farm', 15.00, 1945, 2, 1, 3),
(5, 'Palace Walk', 22.00, 1956, 3, 2, 3),
(6, 'Miramar', 18.00, 1967, 3, 2, 3),
(7, 'Murder on the Orient Express', 28.00, 1934, 4, 1, 2),
(8, 'And Then There Were None', 24.00, 1939, 4, 3, 2),
(9, 'The Alchemist', 27.00, 1988, 5, 3, 1),
(10, 'Brida', 21.00, 1990, 5, 3, 1);


-- =================================
-- 5. MEMBERS
-- =================================

INSERT INTO member
(member_id, name, email, join_date)
VALUES
(1, 'Ahmed Ali', 'ahmed@gmail.com', '2025-01-10'),
(2, 'Sara Mohamed', 'sara@gmail.com', '2025-02-15'),
(3, 'Omar Hassan', 'omar@gmail.com', '2025-03-20'),
(4, 'Mariam Adel', 'mariam@gmail.com', '2025-04-05'),
(5, 'Youssef Samir', 'youssef@gmail.com', '2025-05-12');


-- =================================
-- 6. LOANS
-- =================================

INSERT INTO loan
(loan_id, book_id, member_id, loan_date, return_date)
VALUES
(1, 1, 1, '2025-06-01', '2025-06-10'),
(2, 1, 2, '2025-07-01', '2025-07-12'),
(3, 1, 3, '2025-08-01', NULL),
(4, 2, 1, '2025-06-05', '2025-06-15'),
(5, 2, 2, '2025-07-10', '2025-07-20'),
(6, 3, 3, '2025-06-12', '2025-06-22'),
(7, 3, 4, '2025-07-15', NULL),
(8, 4, 1, '2025-08-05', '2025-08-15'),
(9, 5, 2, '2025-08-10', '2025-08-20'),
(10, 6, 3, '2025-09-01', '2025-09-10'),
(11, 7, 4, '2025-09-05', '2025-09-15'),
(12, 8, 1, '2025-09-10', '2025-09-20');

-- =================================
-- 7. REVIEWS (LAB 5)
-- =================================

INSERT INTO review
(review_id, book_id, member_id, rating, review_date)
VALUES
(1, 1, 1, 5, '2025-10-01'),
(2, 1, 2, 4, '2025-10-03'),
(3, 1, 3, 5, '2025-10-05'),
(4, 2, 4, 3, '2025-10-07'),
(5, 3, 1, 4, '2025-10-10'),
(6, 5, 2, 2, '2025-10-12'),
(7, 7, 3, 1, '2025-10-15'),
(8, 9, 4, 3, '2025-10-18');
