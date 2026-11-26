from multiprocessing import connection
import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv(override=True)
print("DATABASE LOADED:", os.getenv("DB_NAME"))

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

app.secret_key = os.getenv("SESSION_SECRET")

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("todo_list"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required", "register_error")
            return render_template("register.html")
        if password != confirm_password:
            flash("Passwords do not match", "register_error")
            return render_template("register.html")

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s);"
                cursor.execute(query, (email, name, hashed_pw))
                connection.commit()
                session["user_id"] = cursor.lastrowid
                session["user_name"] = name
                return redirect(url_for("todo_list"))
        except pymysql.err.IntegrityError:
            flash("Email Already Exists", "register_error")
            return render_template("register.html")
        finally:
            connection.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required", "login_error")
            return render_template("login.html")

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "SELECT user_id, name, password_hash FROM users WHERE email = %s;"
                cursor.execute(query, (email,))
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                    session["user_id"] = user["user_id"]
                    session["user_name"] = user["name"]
                    return redirect(url_for("todo_list"))
                else:
                    flash("Invalid email or password", "login_error")
        finally:
            connection.close()
        return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/todos")
def todo_list():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT todo_id, title, is_done, created_at
                FROM todos
                WHERE user_id = %s
                ORDER BY todo_id DESC;
            """
            cursor.execute(query, (session["user_id"],))
            todos = cursor.fetchall()
    finally:
        connection.close()

    open_count = sum(1 for todo in todos if not todo["is_done"])
    completed_count = sum(1 for todo in todos if todo["is_done"])

    return render_template(
        "todos.html",
        todos=todos,
        name=session["user_name"],
        open_count=open_count,
        completed_count=completed_count
    )

@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()

    if not title:
        flash("Title is required", "todo_error")
    elif len(title) > 200:
        flash("Title is too long (200 characters at most)", "todo_error")
    else:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO todos (user_id, title) VALUES (%s, %s);"
                cursor.execute(query, (session["user_id"], title))
                connection.commit()
        finally:
            connection.close()

    return redirect(url_for("todo_list"))





@app.route("/todos/update/<int:todo_id>", methods=["POST"])
def update_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form.get("title", "").strip()
    is_done = 1 if request.form.get("is_done") == "on" else 0
    if not title:
        flash("Title is required", "todo_error")
    elif len(title) > 200:
        flash("Title is too long (200 characters at most)", "todo_error")
    else:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "UPDATE todos SET title = %s, is_done = %s WHERE todo_id = %s AND user_id = %s;"
                cursor.execute(query, (title, is_done, todo_id, session["user_id"]))
                connection.commit()
        finally:
            connection.close()
    return redirect(url_for("todo_list"))

@app.route("/todos/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM todos WHERE todo_id = %s AND user_id = %s;"
            cursor.execute(query, (todo_id, session["user_id"]))
            connection.commit()
    finally:
        connection.close()
    return redirect(url_for("todo_list"))



@app.route("/library")
def library():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT author_id, name, country, photo FROM author ORDER BY author_id"
            )
            authors = cursor.fetchall()

            cursor.execute(
                "SELECT book_id, title, price, author_id, cover FROM book ORDER BY book_id"
            )
            books = cursor.fetchall()

            cursor.execute(
                "SELECT publisher_id, name FROM publisher ORDER BY name"
            )
            publishers = cursor.fetchall()

            cursor.execute(
                "SELECT category_id, name FROM category ORDER BY name"
            )
            categories = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "library.html",
        authors=authors,
        books=books,
        publishers=publishers,
        categories=categories
    )





@app.route("/library/author/add", methods=["POST"])
def add_author():
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("photo")
    photo_filename = None

    if not name or not country:
        flash("Please enter the author's name and country.")
        return redirect(url_for("library"))

    if image and image.filename:
        if not allowed_file(image.filename):
            flash("Please upload a valid image file.")
            return redirect(url_for("library"))

        photo_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO author (name, country, photo) VALUES (%s, %s, %s)",
                (name, country, photo_filename)
            )
        connection.commit()
        flash("Author added successfully!")
    except Exception:
        connection.rollback()
        app.logger.exception("Could not add author")
        flash("Could not add author. Please check the application log.")
    finally:
        connection.close()

    return redirect(url_for("library"))




@app.route("/library/book/add", methods=["POST"])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_id = request.form.get("author_id", "").strip()
    publisher_id = request.form.get("publisher_id", "").strip()
    category_id = request.form.get("category_id", "").strip()
    cover = request.files.get("cover")

    if not all([title, price_text, author_id, publisher_id, category_id]):
        flash("Please complete all book fields.")
        return redirect(url_for("library"))

    try:
        price = float(price_text)
        author_id = int(author_id)
        publisher_id = int(publisher_id)
        category_id = int(category_id)

        if price < 0:
            raise ValueError

    except (ValueError, TypeError):
        flash("Please enter valid book information.")
        return redirect(url_for("library"))

    cover_filename = None

    if cover and cover.filename:
        if not allowed_file(cover.filename):
            flash("Please upload a valid image file.")
            return redirect(url_for("library"))

        import uuid
        cover_filename = (
            str(uuid.uuid4()) + "_" + secure_filename(cover.filename)
        )

        cover.save(
            os.path.join(app.config["UPLOAD_FOLDER"], cover_filename)
        )

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO book
                   (title, price, author_id, publisher_id, category_id, cover)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (title, price, author_id, publisher_id,
                 category_id, cover_filename)
            )

        connection.commit()
        flash("Book added successfully!")

    except Exception:
        connection.rollback()
        app.logger.exception("Could not add book")
        flash("Could not add book. Check the application log.")

    finally:
        connection.close()

    return redirect(url_for("library"))




@app.route("/library/author/edit/<int:author_id>", methods=["GET", "POST"])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            if request.method == "POST":
                name = request.form.get("name", "").strip()
                country = request.form.get("country", "").strip()
                photo = request.files.get("photo")

                if not name or not country:
                    flash("Please enter the author's name and country.")
                    return redirect(
                        url_for("edit_author", author_id=author_id)
                    )

                cursor.execute(
                    "SELECT photo FROM author WHERE author_id = %s",
                    (author_id,)
                )
                current_author = cursor.fetchone()

                if current_author is None:
                    flash("Author not found.")
                    return redirect(url_for("library"))

                photo_filename = current_author["photo"]

                if photo and photo.filename:
                    from werkzeug.utils import secure_filename
                    import uuid

                    photo_filename = (
                        str(uuid.uuid4()) + "_"
                        + secure_filename(photo.filename)
                    )

                    upload_folder = os.path.join(
                        app.static_folder, "uploads"
                    )
                    os.makedirs(upload_folder, exist_ok=True)

                    photo.save(
                        os.path.join(upload_folder, photo_filename)
                    )

                cursor.execute(
                    "UPDATE author SET name = %s, country = %s, "
                    "photo = %s WHERE author_id = %s",
                    (name, country, photo_filename, author_id)
                )

                connection.commit()
                flash("Author updated successfully!")
                return redirect(url_for("library"))

            cursor.execute(
                "SELECT * FROM author WHERE author_id = %s",
                (author_id,)
            )
            author = cursor.fetchone()

            if author is None:
                flash("Author not found.")
                return redirect(url_for("library"))

            return render_template("edit_author.html", author=author)

    except Exception:
        connection.rollback()
        app.logger.exception("Could not update author")
        flash("Could not update author. Check the application log.")
        return redirect(url_for("library"))

    finally:
        connection.close()





@app.route("/library/book/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            if request.method == "POST":
                title = request.form.get("title", "").strip()
                price_text = request.form.get("price", "").strip()
                author_text = request.form.get("author_id", "").strip()
                cover = request.files.get("cover")

                try:
                    price = float(price_text)
                    author_id = int(author_text)

                    if price < 0:
                        raise ValueError

                except (ValueError, TypeError):
                    flash("Enter a valid price and author.")
                    return redirect(url_for("edit_book", book_id=book_id))

                if not title:
                    flash("Please enter a book title.")
                    return redirect(url_for("edit_book", book_id=book_id))

                cursor.execute(
                    "SELECT cover FROM book WHERE book_id = %s",
                    (book_id,)
                )
                existing_book = cursor.fetchone()

                if existing_book is None:
                    flash("Book not found.")
                    return redirect(url_for("library"))

                cover_filename = existing_book["cover"]

                if cover and cover.filename:
                    from werkzeug.utils import secure_filename

                    cover_filename = secure_filename(cover.filename)
                    upload_folder = os.path.join(
                        app.static_folder, "uploads"
                    )
                    os.makedirs(upload_folder, exist_ok=True)
                    cover.save(os.path.join(upload_folder, cover_filename))

                cursor.execute(
                    """UPDATE book
                       SET title = %s, price = %s,
                           author_id = %s, cover = %s
                       WHERE book_id = %s""",
                    (title, price, author_id, cover_filename, book_id)
                )

                connection.commit()
                flash("Book updated successfully!")
                return redirect(url_for("library"))

            cursor.execute(
                """SELECT book_id, title, price, author_id, cover
                   FROM book WHERE book_id = %s""",
                (book_id,)
            )
            book = cursor.fetchone()

            if book is None:
                flash("Book not found.")
                return redirect(url_for("library"))

            cursor.execute(
                "SELECT author_id, name FROM author ORDER BY name"
            )
            author = cursor.fetchall()

            return render_template(
                "edit_book.html",
                book=book,
                authors=author
            )

    except Exception:
        connection.rollback()
        app.logger.exception("Could not edit book")
        flash("Could not update book. Please check the application log.")
        return redirect(url_for("library"))

    finally:
        connection.close()



@app.route("/library/book/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM book WHERE book_id = %s",
                (book_id,)
            )
        connection.commit()
        flash("Book deleted successfully!")
    except Exception:
        connection.rollback()
        app.logger.exception("Could not delete book")
        flash("Could not delete book.")
    finally:
        connection.close()

    return redirect(url_for("library"))


@app.route("/delete_author/<int:author_id>", methods=["POST"])
def delete_author(author_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM author WHERE author_id = %s",
                (author_id,)
            )
        connection.commit()
        flash("Author deleted successfully.", "success")
    finally:
        connection.close()

    return redirect(url_for("library"))



# F2.1 - Search Books (Prepared Statement)

@app.route("/library/search", methods=["GET", "POST"])
def search_books():
    if "user_id" not in session:
        return redirect(url_for("login"))

    books = []
    keyword = ""
    min_price = 15
    max_price = 30
    selected_categories = []

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Get all categories for the search form
            cursor.execute(
                "SELECT category_id, name FROM category ORDER BY name"
            )
            categories = cursor.fetchall()

            if request.method == "POST":
                keyword = request.form.get("keyword", "").strip()

                min_price = float(request.form.get("min_price", 15))
                max_price = float(request.form.get("max_price", 30))

                if min_price > max_price:
                    raise ValueError

                selected_categories = request.form.getlist("categories")

                query = """
                    SELECT
                        b.book_id,
                        b.title,
                        b.price,
                        b.publish_year,
                        c.name AS category
                    FROM book b
                    JOIN category c
                        ON b.category_id = c.category_id
                    WHERE
                        b.title LIKE %s
                        AND b.price BETWEEN %s AND %s
                """

                parameters = [f"%{keyword}%", min_price, max_price]

                if selected_categories:
                    category_ids = [int(x) for x in selected_categories]
                    placeholders = ", ".join(["%s"] * len(category_ids))
                    query += f" AND b.category_id IN ({placeholders})"
                    parameters.extend(category_ids)

                query += " ORDER BY b.price ASC"

                cursor.execute(query, parameters)
                books = cursor.fetchall()

    except ValueError:
        flash("Please enter a valid price range.")

    finally:
        connection.close()

    return render_template(
        "search_books.html",
        books=books,
        keyword=keyword,
        min_price=min_price,
        max_price=max_price,
        categories=categories,
        selected_categories=selected_categories
    )

# F2.2 - Catalogue (JOIN)

@app.route("/library/catalogue")
def catalogue():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    b.book_id,
                    b.title,
                    b.price,
                    b.publish_year,
                    a.name AS author,
                    p.name AS publisher,
                    c.name AS category
                FROM book b
                JOIN author a ON b.author_id = a.author_id
                JOIN publisher p ON b.publisher_id = p.publisher_id
                JOIN category c ON b.category_id = c.category_id
                ORDER BY b.title
            """

            cursor.execute(query)
            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template("catalogue.html", books=books)

# F2.3 - Reports (GROUP BY and HAVING)

@app.route("/library/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Book count and average price per category
            cursor.execute("""
                SELECT
                    c.name AS category,
                    COUNT(b.book_id) AS book_count,
                    AVG(b.price) AS average_price
                FROM category c
                LEFT JOIN book b ON c.category_id = b.category_id
                GROUP BY c.category_id, c.name
            """)
            category_reports = cursor.fetchall()

            # 2. Authors with at least 2 books
            cursor.execute("""
                SELECT
                    a.name AS author,
                    COUNT(b.book_id) AS book_count
                FROM author a
                JOIN book b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name
                HAVING COUNT(b.book_id) >= 2
            """)
            author_reports = cursor.fetchall()

            # 3. Total, minimum, and maximum book prices
            cursor.execute("""
                SELECT
                    SUM(price) AS total_price,
                    MIN(price) AS min_price,
                    MAX(price) AS max_price
                FROM book
            """)
            price_report = cursor.fetchone()

    finally:
        connection.close()

    return render_template(
        "reports.html",
        category_reports=category_reports,
        author_reports=author_reports,
        price_report=price_report
    )

# F2.4 - Loans (JOIN and LEFT JOIN)

@app.route("/library/loans")
def loans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Unreturned loans
            cursor.execute("""
                SELECT
                    l.loan_id,
                    b.title AS book_title,
                    m.name AS member_name,
                    l.loan_date
                FROM loan l
                JOIN book b ON l.book_id = b.book_id
                JOIN member m ON l.member_id = m.member_id
                WHERE l.return_date IS NULL
                ORDER BY l.loan_date
            """)
            unreturned_loans = cursor.fetchall()

            # 2. Members who never borrowed a book
            cursor.execute("""
                SELECT
                    m.member_id,
                    m.name,
                    m.email
                FROM member m
                LEFT JOIN loan l ON m.member_id = l.member_id
                WHERE l.loan_id IS NULL
            """)
            members_never_borrowed = cursor.fetchall()

            # 3. Books that were never borrowed
            cursor.execute("""
                SELECT
                    b.book_id,
                    b.title
                FROM book b
                LEFT JOIN loan l ON b.book_id = l.book_id
                WHERE l.loan_id IS NULL
            """)
            books_never_borrowed = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "loans.html",
        unreturned_loans=unreturned_loans,
        members_never_borrowed=members_never_borrowed,
        books_never_borrowed=books_never_borrowed
    )


# F2.5 - Most Borrowed (GROUP BY, ORDER BY, LIMIT)

@app.route("/library/most-borrowed")
def most_borrowed():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Top 3 most borrowed books
            cursor.execute("""
                SELECT
                    b.book_id,
                    b.title,
                    COUNT(l.loan_id) AS loan_count
                FROM book b
                JOIN loan l ON b.book_id = l.book_id
                GROUP BY b.book_id, b.title
                ORDER BY loan_count DESC
                LIMIT 3
            """)
            top_books = cursor.fetchall()

            # 2. Member who borrowed the most
            cursor.execute("""
                SELECT
                    m.member_id,
                    m.name,
                    COUNT(l.loan_id) AS loan_count
                FROM member m
                JOIN loan l ON m.member_id = l.member_id
                GROUP BY m.member_id, m.name
                ORDER BY loan_count DESC
                LIMIT 1
            """)
            top_member = cursor.fetchone()

    finally:
        connection.close()

    return render_template(
        "most_borrowed.html",
        top_books=top_books,
        top_member=top_member
    )


# F2.6 - Authors and Books

@app.route("/library/authors-books")
def authors_books():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Every author with their number of books, including zero
            cursor.execute("""
                SELECT
                    a.author_id,
                    a.name,
                    COUNT(b.book_id) AS book_count
                FROM author a
                LEFT JOIN book b
                    ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name
                ORDER BY a.name
            """)
            authors = cursor.fetchall()

            # 2. Books whose author and publisher are from the same country
            cursor.execute("""
                SELECT
                    b.book_id,
                    b.title,
                    a.name AS author_name,
                    a.country AS author_country,
                    p.name AS publisher_name,
                    p.country AS publisher_country
                FROM book b
                JOIN author a
                    ON b.author_id = a.author_id
                JOIN publisher p
                    ON b.publisher_id = p.publisher_id
                WHERE a.country = p.country
                ORDER BY b.title
            """)
            matching_books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "authors_books.html",
        authors=authors,
        matching_books=matching_books
    )


# F2.1 - Above the Average (Scalar Subquery)

@app.route("/library/above-average")
def above_average():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    title,
                    price,
                    (SELECT AVG(price) FROM book_details) AS average_price
                FROM book_details
                WHERE price > (SELECT AVG(price) FROM book_details)
                ORDER BY price DESC;
            """

            cursor.execute(query)
            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template("above_average.html", books=books)



# F2.2 - Never Borrowed Books (NOT EXISTS)

@app.route("/library/never-borrowed")
def never_borrowed():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            books_query = """
    SELECT book_id, title
    FROM book_details
    WHERE NOT EXISTS (
        SELECT 1
        FROM loan
        WHERE loan.book_id = book_details.book_id
    );
"""

            cursor.execute(books_query)
            books = cursor.fetchall()

            # Query 2: Members who have never borrowed
            members_query = """
                SELECT member_id, name
                FROM member
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM loan
                    WHERE loan.member_id = member.member_id
                );
            """

            cursor.execute(members_query)
            members = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "never_borrowed.html",
        books=books,
        members=members
    )


# F2.3 - Best of Category (Correlated Subquery)

@app.route("/library/best-category")
def best_category():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Query 1: Most expensive book in each category
            query1 = """
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
            """

            cursor.execute(query1)
            best_books = cursor.fetchall()

            # Query 2: Books priced above their category average
            query2 = """
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
            """

            cursor.execute(query2)
            above_category_average = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "best_category.html",
        best_books=best_books,
        above_category_average=above_category_average
    )



# F2.4 - Active Members (Derived Table + EXISTS)

@app.route("/library/active-members")
def active_members_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Query 1: Members whose loans are above the average
            # The average includes all members, even those with zero loans
            active_query = """
                SELECT
                    m.member_id,
                    m.name,
                    loan_counts.loan_count,
                    loan_counts.average_loans
                FROM member m
                JOIN (
                    SELECT
                        m2.member_id,
                        COUNT(l.loan_id) AS loan_count,
                        averages.average_loans
                    FROM member m2
                    LEFT JOIN loan l ON m2.member_id = l.member_id
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
                ) AS loan_counts
                ON m.member_id = loan_counts.member_id
                WHERE loan_counts.loan_count > loan_counts.average_loans
                ORDER BY loan_counts.loan_count DESC;
            """

            cursor.execute(active_query)
            active_members = cursor.fetchall()

            # Query 2: Authors who have at least one borrowed book
            authors_query = """
                SELECT DISTINCT
                    a.author_id,
                    a.name
                FROM author a
                WHERE EXISTS (
                    SELECT 1
                    FROM book b
                    JOIN loan l ON l.book_id = b.book_id
                    WHERE b.author_id = a.author_id
                )
                ORDER BY a.name;
            """

            cursor.execute(authors_query)
            borrowed_authors = cursor.fetchall()

            # Query 3: Average loans per member
            # Includes members who have zero loans
            average_query = """
                SELECT AVG(member_loan_count) AS average_loans
                FROM (
                    SELECT
                        m.member_id,
                        COUNT(l.loan_id) AS member_loan_count
                    FROM member m
                    LEFT JOIN loan l ON m.member_id = l.member_id
                    GROUP BY m.member_id
                ) AS member_counts;
            """

            cursor.execute(average_query)
            average_result = cursor.fetchone()
            average_loans = average_result["average_loans"]

    finally:
        connection.close()

    return render_template(
        "active_members.html",
        active_members=active_members,
        borrowed_authors=borrowed_authors,
        average_loans=average_loans
    )




# F2.5 - Reviews (LEFT JOIN, CASE, COALESCE, HAVING)

@app.route("/library/reviews")
def reviews_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Query 1: All books with review count, average, and rating status
            reviews_query = """
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
                    END AS rating_status
                FROM book b
                LEFT JOIN review r ON b.book_id = r.book_id
                GROUP BY b.book_id, b.title
                ORDER BY b.title;
            """

            cursor.execute(reviews_query)
            book_reviews = cursor.fetchall()

            # Query 2: Books above the overall average rating
            above_average_query = """
                SELECT
                    b.title,
                    AVG(r.rating) AS average_rating
                FROM book b
                JOIN review r ON b.book_id = r.book_id
                GROUP BY b.book_id, b.title
                HAVING AVG(r.rating) > (
                    SELECT AVG(r2.rating)
                    FROM review r2
                )
                ORDER BY average_rating DESC;
            """

            cursor.execute(above_average_query)
            above_average_reviews = cursor.fetchall()

            # Query 3: Overall average rating
            overall_query = """
                SELECT COALESCE(AVG(rating), 0) AS overall_average
                FROM review;
            """

            cursor.execute(overall_query)
            overall_result = cursor.fetchone()
            overall_average = overall_result["overall_average"]

    finally:
        connection.close()

    return render_template(
        "reviews.html",
        book_reviews=book_reviews,
        above_average_reviews=above_average_reviews,
        overall_average=overall_average
    )

# F2.6 - Countries and People (UNION, INTERSECT, EXCEPT)

@app.route("/library/countries-people")
def countries_people():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Countries of authors
            author_countries_query = """
                SELECT DISTINCT country
                FROM author
                WHERE country IS NOT NULL;
            """
            cursor.execute(author_countries_query)
            author_countries = cursor.fetchall()

            # Countries of publishers
            publisher_countries_query = """
                SELECT DISTINCT country
                FROM publisher
                WHERE country IS NOT NULL;
            """
            cursor.execute(publisher_countries_query)
            publisher_countries = cursor.fetchall()

            # Countries shared by authors and publishers (INTERSECT)
            common_countries_query = """
                SELECT country FROM author WHERE country IS NOT NULL
                INTERSECT
                SELECT country FROM publisher WHERE country IS NOT NULL;
            """
            cursor.execute(common_countries_query)
            common_countries = cursor.fetchall()

            # Author countries that do not exist among publisher countries (EXCEPT)
            author_only_countries_query = """
                SELECT DISTINCT country FROM author WHERE country IS NOT NULL
                EXCEPT
                SELECT DISTINCT country FROM publisher WHERE country IS NOT NULL;
            """
            cursor.execute(author_only_countries_query)
            author_only_countries = cursor.fetchall()

            people_query = """
    SELECT name, 'Author' AS person_type
    FROM author

    UNION

    SELECT name, 'Member' AS person_type
    FROM member

    ORDER BY name;
"""
            cursor.execute(people_query)
            people = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "countries_people.html",
        author_countries=author_countries,
        publisher_countries=publisher_countries,
        common_countries=common_countries,
        author_only_countries=author_only_countries,
        people=people
    )

if __name__ == "__main__":
    app.run(debug=True)
