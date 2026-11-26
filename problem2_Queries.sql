
-- =====================================================
-- LAB 5 PART II - F2.1 TO F2.6
-- =====================================================

USE library;


-- =====================================================
-- F2.1 - ABOVE THE AVERAGE (SCALAR SUBQUERY)
-- Books whose price is above the overall average
-- =====================================================

SELECT
    title,
    price,
    (SELECT AVG(price) FROM book_details) AS average_price
FROM book_details
WHERE price > (SELECT AVG(price) FROM book_details)
ORDER BY price DESC;


-- =====================================================
-- F2.2 - NEVER BORROWED (NOT EXISTS)
-- =====================================================

-- (a) Books that have never been borrowed

SELECT
    book_id,
    title
FROM book_details b
WHERE NOT EXISTS (
    SELECT 1
    FROM loan l
    WHERE l.book_id = b.book_id
);


-- (b) Members who have never borrowed a book

SELECT
    m.member_id,
    m.name
FROM member m
WHERE NOT EXISTS (
    SELECT 1
    FROM loan l
    WHERE l.member_id = m.member_id
);


-- =====================================================
-- F2.3 - BEST OF CATEGORY (CORRELATED SUBQUERY)
-- =====================================================

-- (a) Most expensive book in each category

SELECT
    category_name,
    title,
    price
FROM book_details b
WHERE price = (
    SELECT MAX(b2.price)
    FROM book_details b2
    WHERE b2.category_name = b.category_name
)
ORDER BY category_name;


-- (b) Books above their own category average

SELECT
    category_name,
    title,
    price,
    (
        SELECT AVG(b2.price)
        FROM book_details b2
        WHERE b2.category_name = b.category_name
    ) AS category_average
FROM book_details b
WHERE price > (
    SELECT AVG(b2.price)
    FROM book_details b2
    WHERE b2.category_name = b.category_name
)
ORDER BY category_name, price DESC;


-- =====================================================
-- F2.4 - ACTIVE MEMBERS (DERIVED TABLE + EXISTS)
-- =====================================================

-- (a) Members whose number of loans is above the average
-- The average includes members with zero loans

SELECT
    m.member_id,
    m.name,
    member_counts.loan_count,
    member_counts.average_loans
FROM member m
JOIN (
    SELECT
        m2.member_id,
        COUNT(l2.loan_id) AS loan_count,
        averages.average_loans
    FROM member m2
    LEFT JOIN loan l2
        ON m2.member_id = l2.member_id
    CROSS JOIN (
        SELECT AVG(member_loan_count) AS average_loans
        FROM (
            SELECT
                m3.member_id,
                COUNT(l3.loan_id) AS member_loan_count
            FROM member m3
            LEFT JOIN loan l3
                ON m3.member_id = l3.member_id
            GROUP BY m3.member_id
        ) AS member_averages
    ) AS averages
    GROUP BY m2.member_id, averages.average_loans
) AS member_counts
    ON m.member_id = member_counts.member_id
WHERE member_counts.loan_count > member_counts.average_loans
ORDER BY member_counts.loan_count DESC;


-- (b) Authors who have at least one borrowed book (EXISTS)

SELECT DISTINCT
    a.author_id,
    a.name
FROM author a
WHERE EXISTS (
    SELECT 1
    FROM book b
    JOIN loan l
        ON b.book_id = l.book_id
    WHERE b.author_id = a.author_id
)
ORDER BY a.name;


-- (c) Average loans per member including zero-loan members

SELECT AVG(member_loan_count) AS average_loans
FROM (
    SELECT
        m.member_id,
        COUNT(l.loan_id) AS member_loan_count
    FROM member m
    LEFT JOIN loan l
        ON m.member_id = l.member_id
    GROUP BY m.member_id
) AS member_counts;


-- =====================================================
-- F2.5 - REVIEWS
-- LEFT JOIN, CASE, COALESCE, HAVING
-- =====================================================

-- (a) Every book with review count, average rating,
-- and rating classification

SELECT
    b.book_id,
    b.title,
    COUNT(r.review_id) AS review_count,
    COALESCE(AVG(r.rating), 0) AS average_rating,
    CASE
        WHEN COUNT(r.review_id) = 0 THEN 'No review'
        WHEN AVG(r.rating) >= 4.5 THEN 'Excellent'
        WHEN AVG(r.rating) >= 3.5 THEN 'Good'
        ELSE 'Fair'
    END AS review_category
FROM book_details b
LEFT JOIN review r
    ON b.book_id = r.book_id
GROUP BY b.book_id, b.title
ORDER BY b.title;


-- (b) Books whose average rating is above the overall
-- average rating of all reviews

SELECT
    b.book_id,
    b.title,
    AVG(r.rating) AS average_rating
FROM book_details b
JOIN review r
    ON b.book_id = r.book_id
GROUP BY b.book_id, b.title
HAVING AVG(r.rating) > (
    SELECT AVG(r2.rating)
    FROM review r2
)
ORDER BY average_rating DESC;


-- =====================================================
-- F2.6 - COUNTRIES AND PEOPLE
-- UNION, INTERSECT, EXCEPT
-- =====================================================

-- (a) Countries of authors and publishers combined

SELECT country
FROM author

UNION

SELECT country
FROM publisher
ORDER BY country;


-- (b) Countries shared by authors and publishers

SELECT country
FROM author

INTERSECT

SELECT country
FROM publisher;


-- (c) Countries where authors exist but publishers do not

SELECT country
FROM author

EXCEPT

SELECT country
FROM publisher;


-- (d) Authors and members combined into one list

SELECT
    name,
    'Author' AS person_type
FROM author

UNION

SELECT
    name,
    'Member' AS person_type
FROM member

ORDER BY name, person_type;



