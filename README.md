# Library Management Website – Lab 5

## 1. Team Members

| Name | Student ID | Responsibilities |
|---|---|---|
| Dina Ibrahim Ebeid | 2304144 | Backend development, user authentication, database integration, implementing SQL queries, and application integration. |
| Mohab Mohamed | 2304077 | Database design, frontend development, interface styling, testing, and project documentation. |

---

## 2. Project Overview

This project is a web-based Library Management Website developed using Python, Flask, MySQL, HTML, and CSS.

Lab 5 extends the previous library application by introducing advanced SQL queries and additional database features. It focuses on using subqueries, correlated subqueries, derived tables, EXISTS, NOT EXISTS, UNION, INTERSECT, EXCEPT, and aggregate functions.

The website provides different functionalities for analyzing book prices, identifying books and members with no borrowing activity, comparing books within categories, analyzing active members, evaluating book reviews, and exploring relationships between authors, publishers, and members.

---

## 3. Features

### Existing Features

- User registration and login.
- Book management.
- Author management.
- MySQL database integration.
- Frontend styling using CSS.

### Lab 5 Features

- **F2.1 – Above the Average:** Retrieve books whose prices are higher than the overall average book price using a scalar subquery.
- **F2.2 – Never Borrowed:** Identify books that have never been borrowed and members who have never borrowed a book using NOT EXISTS.
- **F2.3 – Best of Category:** Find the most expensive books in each category and books whose prices are above their category average using correlated subqueries.
- **F2.4 – Active Members:** Identify members whose borrowing activity is above the average number of loans, find authors who have at least one borrowed book, and calculate the average loans per member, including members with zero loans.
- **F2.5 – Reviews:** Analyze book reviews by displaying review counts, average ratings, review classifications, and books with average ratings above the overall review average.
- **F2.6 – Countries and People:** Explore relationships between authors and publishers using UNION, INTERSECT, and EXCEPT, and combine author and member information.

### Bonus Feature

- **Book Details View:** Create a SQL view named `book_details` that combines book, author, publisher, and category information to simplify book-related queries.

---

## 4. Technologies Used

- Python 3
- Flask
- MySQL
- PyMySQL
- HTML
- CSS
- bcrypt
- python-dotenv
- Werkzeug

---

## 5. Database Design

The project uses a MySQL database named `library`.

The database contains the following tables:

1. **AUTHOR** – Stores author information.
2. **PUBLISHER** – Stores publisher information.
3. **CATEGORY** – Stores book categories.
4. **BOOK** – Stores book details and references its author, publisher, and category.
5. **MEMBER** – Stores library member information.
6. **LOAN** – Stores book borrowing and return information.
7. **REVIEW** – Stores members' ratings and reviews of books.

Foreign keys are used to maintain relationships between tables and ensure data integrity.

The REVIEW table connects books and members and stores ratings and review dates. It also includes constraints to ensure valid ratings and prevent a member from reviewing the same book more than once.

### Bonus View

The `book_details` view combines information from the BOOK, AUTHOR, PUBLISHER, and CATEGORY tables.

It provides:

- Book ID
- Book title
- Book price
- Author name
- Publisher name
- Category name

This view simplifies queries that require information from multiple related tables.

---

## 6. Project Structure

```text
LAB5/
│
├── static/
│   ├── style.css
│   ├── background.jpg
│   └── uploads/
│
├── templates/
│   ├── above_average.html
│   ├── never_borrowed.html
│   ├── best_category.html
│   ├── active_members.html
│   ├── reviews.html
│   ├── countries_people.html
│   └── other application templates
│
├── app.py
├── problem2_DDL.sql
├── problem2_DML.sql
├── problem2_Queries.sql
├── requirements.txt
├── .env.example
└── README.md
```

*Note: The project structure should match the actual files included in the submitted folder.*

---

## 7. Requirements

Before running the project, install or prepare:

- Python 3
- MySQL Server
- pip (Python package installer)
- Visual Studio Code (recommended)

---

## 8. Installation and Setup

### Step 1: Open the Project

Download or clone the project and open its folder in Visual Studio Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

On Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create or update the `.env` file with your MySQL connection settings.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library
```

Replace `your_mysql_password` with your actual MySQL password.

**Security Note:** Do not upload your real `.env` file or database password to a public GitHub repository.

### Step 6: Set Up the Database

1. Start MySQL Server.
2. Connect to MySQL.
3. Execute `problem2_DDL.sql` to create the database, tables, constraints, and the `book_details` view.
4. Execute `problem2_DML.sql` to insert the sample data.

**Important:** The DDL file contains `DROP DATABASE IF EXISTS library`. Run it only when creating or intentionally resetting the database because it deletes the existing database and its data.

### Step 7: Run the Application

From the project directory, run:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

---

## 9. How to Use the Website

1. Open the website in your browser.
2. Register an account if required.
3. Log in using your credentials.
4. Navigate through the available Lab 5 features.
5. Open **Above the Average** to view books priced above the overall average.
6. Open **Never Borrowed** to identify books that have never been borrowed and members who have never borrowed a book.
7. Open **Best of Category** to compare book prices within categories.
8. Open **Active Members** to analyze borrowing activity and authors with borrowed books.
9. Open **Reviews** to analyze book ratings and review statistics.
10. Open **Countries and People** to explore country relationships and combine author and member information.

---

## 10. SQL Queries

The file `problem2_Queries.sql` contains the SQL statements implemented for Lab 5.

The queries demonstrate the following SQL concepts:

- Scalar subqueries.
- Subqueries using aggregate functions.
- NOT EXISTS.
- EXISTS.
- Correlated subqueries.
- Derived tables.
- LEFT JOIN.
- GROUP BY.
- HAVING.
- AVG, COUNT, and MAX.
- CASE statements.
- COALESCE.
- UNION.
- INTERSECT.
- EXCEPT.

The queries are used to retrieve information, analyze library activity, compare book prices, evaluate ratings, and identify relationships between different database entities.

The `book_details` view is also used to simplify queries involving book information and related author, publisher, and category data.

---

## 11. Security Considerations

- Store database credentials in environment variables.
- Do not commit passwords or secret keys to version control.
- Use parameterized SQL queries to handle user inputs safely.
- Use secure password hashing for user authentication.
- Validate user inputs before processing them.

---

## 12. Screenshots

This section presents screenshots of the Library Management Website and its Lab 5 features.

### 12.1 Above the Average (F2.1)

*Insert screenshot here.*

### 12.2 Never Borrowed (F2.2)

*Insert screenshot here.*

### 12.3 Best of Category (F2.3)

*Insert screenshot here.*

### 12.4 Active Members (F2.4)

*Insert screenshot here.*

### 12.5 Reviews (F2.5)

*Insert screenshot here.*

### 12.6 Countries and People (F2.6)

*Insert screenshot here.*

### 12.7 Bonus – Book Details View

*Insert screenshot of the `book_details` view or its results here.*

---

## 13. Conclusion

Lab 5 extends the Library Management Website by applying advanced SQL concepts to a practical web-based database application.

The project demonstrates how subqueries, correlated subqueries, derived tables, EXISTS, NOT EXISTS, aggregate functions, set operations, and SQL views can be used to retrieve, analyze, and organize database information.

Through the implementation of these features, the project provides practical experience in database querying, relational data analysis, MySQL integration, and full-stack web development using Flask.
