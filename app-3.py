#Import required modules
from flask import Flask, request, jsonify
import sqlite3
import wikipediaapi
import requests

#Create a Flask web application instance
app = Flask(__name__)

#Decorator function to establish a database connection for routes
def connect_db(func):
    def db_connection(*args, **kwargs):
        # Connect to the SQLite database named "books.db"
        conn = sqlite3.connect("books.db")
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        try:
            # Execute the wrapped function with the cursor and other arguments
            result = func(cursor=cursor, *args, **kwargs)
        except Exception as e:
            # Rollback changes in case of an exception
            conn.rollback()
            # Raise the caught exception
            raise e
        else:
            # Commit changes if no exception occurred
            conn.commit()
        finally:
            # Close the database connection in any case
            conn.close()

        return result
    
    # Set the name of the wrapper function for better debugging
    db_connection.__name__ = func.__name__ + '_db_connection'

    return db_connection


#GET /books - Hämtar alla böcker i databasen med olika filter
@app.route("/books", methods=["GET"])
@connect_db
def get_books(cursor):
    # Retrieve query parameters from the request URL
    title = request.args.get("title")
    author = request.args.get("author")
    genre = request.args.get("genre")

    # Initialize the base query to select all columns from the "books" table
    query = "SELECT * FROM books WHERE 1=1"
    # Initialize an empty list to store query parameters
    params = []

    # Check if the "title" parameter is provided
    if title:
        # Add a condition to the query to filter by title
        query += " AND title LIKE ?"
        # Append the title parameter to the list of parameters
        params.append(f"%{title}%")

    # Check if the "author" parameter is provided
    if author:
        # Add a condition to the query to filter by author
        query += " AND author LIKE ?"
        # Append the author parameter to the list of parameters
        params.append(f"%{author}%")

    # Check if the "genre" parameter is provided
    if genre:
        # Add a condition to the query to filter by genre
        query += " AND genre LIKE ?"
        # Append the genre parameter to the list of parameters
        params.append(f"%{genre}%")

    # Execute the query with the specified parameters
    cursor.execute(query, params)
    # Fetch all rows (books) returned by the query
    books = cursor.fetchall()

    # Return the list of books as a JSON response
    return jsonify(books)


#POST /books - Lägger till en eller flera böcker i databasen.
@app.route("/books", methods=["POST"], endpoint="add_books_route")
@connect_db
def add_books_route(cursor):
    # Retrieve the JSON data from the request body
    new_books = request.json
    # Iterate through each book in the received JSON data
    for book in new_books:
        # Execute an SQL INSERT statement to add a new book to the "books" table
        cursor.execute(
            "INSERT INTO books (title, author, rating, genre, summary) VALUES (?, ?, ?, ?, ?)",
            (book["title"], book["author"], book["rating"], book["genre"], book["summary"])
        )
    
    # Commit the changes to the database
    return jsonify({"message": "Books added successfully"}), 201


#GET /books/{book_id} - Hämtar en enskild bok.
@app.route("/books/<int:book_id>", methods=["GET"])
@connect_db
def get_book_by_id(book_id, cursor):
    try:
        # Retrieve book details from the database using a SELECT query
        book_query = "SELECT * FROM books WHERE id = ?"
        cursor.execute(book_query, [book_id])
        selected_book = cursor.fetchone()

        # Check if the book with the given ID exists
        if not selected_book:
            return jsonify({"message": "Book not found"}), 404

        # Convert selected_book to a dictionary for easier serialization
        book_details = dict(zip(["id", "title", "author", "rating", "genre", "summary"], selected_book))

        # Return the book details in JSON format
        return jsonify({"book_details": book_details})

    except Exception as e:
        # Return an error message in case of an exception
        return jsonify({"error": str(e)}), 500  # Internal Server Error



#PUT /books/{book_id} - Uppdaterar information om en enskild bok.
@app.route("/books/<int:book_id>", methods=["PUT"])
@connect_db
def update_books(book_id, cursor):
    # Define the SQL query to update book information in the database
    query = "UPDATE books SET title = ?, author = ?, rating = ?, genre = ?, summary = ? WHERE id = ?"

    try:
        # Retrieve the updated data from the JSON request
        updated_data = request.get_json()
    except Exception as e:
        # Return an error response if the JSON format is invalid
        return jsonify({"error": "Invalid JSON format"}), 400

    # Check if any data is provided in the request
    if not updated_data:
        return jsonify({"error": "No data provided in the request"}), 400

    # Extract updated parameters from the JSON data
    params = [
        updated_data.get("title"),
        updated_data.get("author"),
        updated_data.get("rating"),
        updated_data.get("genre"),
        updated_data.get("summary"),
        book_id
    ]

    # Execute the update query with the provided parameters
    cursor.execute(query, params)

    # Check if any rows were affected (book updated successfully)
    if cursor.rowcount > 0:
        return jsonify({"message": "Book updated successfully"})
    else:
        # Return a message if the book is not found or no changes were made
        return jsonify({"message": "Book not found or no changes made"}), 404


#DELETE /books/{book_id} - Tar bort en enskild bok
@app.route("/books/<int:book_id>", methods=["DELETE"])
@connect_db
def delete_book(book_id, cursor):
    # Define the SQL query to delete a book from the database based on its ID
    query = "DELETE FROM books WHERE id = ?"
    # Set the parameters for the query, including the book ID to be deleted
    params = [book_id]

    # Execute the delete query with the provided parameters
    cursor.execute(query, params)

    # Check if any rows were affected (book deleted successfully)
    if cursor.rowcount > 0:
        return jsonify({"message": "Book deleted successfully"})
    else:
        # Return a message if the book is not found
        return jsonify({"message": "Book not found"}), 404


#POST /reviews -  Lägger till en ny recension till en bok.
@app.route("/reviews", methods=["POST"])
@connect_db
def add_review(cursor):
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract data fields from the JSON data
        book_id = data.get("book_id")
        user = data.get("user")
        rating = data.get("rating")
        review_text = data.get("review_text")

        # Check for incomplete data in the request
        if not all([book_id, user, rating, review_text]):
            return jsonify({"error": "Incomplete data in the request"}), 400

        # Check if the book exists
        cursor.execute("SELECT * FROM books WHERE id = ?", [book_id])
        book = cursor.fetchone()

        # Return an error if the book is not found
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Insert the review into the database
        cursor.execute("INSERT INTO reviews (book_id, user, rating, review_text) VALUES (?, ?, ?, ?)",
                       (book_id, user, rating, review_text))

        return jsonify({"message": "Review added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#GET /reviews - Hämtar alla recensioner som finns i databasen
@app.route("/reviews", methods=["GET"])
@connect_db
def get_all_reviews(cursor):
    try:
        # Fetch all reviews from the database
        cursor.execute("SELECT * FROM reviews")
        reviews = cursor.fetchall()

        # Return the fetched reviews in a JSON response
        return jsonify({"reviews": reviews})

    except Exception as e:
        # Return an error response if an exception occurs
        return jsonify({"error": str(e)}), 500

#GET /reviews/{book_id} - Hämtar alla recensioner för en enskild bok.
@app.route("/reviews/<int:book_id>", methods=["GET"])
@connect_db
def get_reviews_for_book(book_id, cursor):
    # SQL query to retrieve reviews for a specific book ID
    query = "SELECT * FROM reviews WHERE book_id = ?"
    params = [book_id]

    # Execute the query and fetch all reviews
    cursor.execute(query, params)
    reviews = cursor.fetchall()

    # Return a JSON response containing book ID and associated reviews
    return jsonify({"book_id": book_id, "reviews": reviews})

#GET /books/top - Hämtar de fem böckerna med högst genomsnittliga recensioner.
@app.route("/books/top", methods=["GET"])
@connect_db
def get_top_books(cursor):
    #SQL query to retrieve the top five books with the highest average ratings
    query = """
        SELECT b.id, b.title, b.author, b.rating, b.genre, b.summary, AVG(r.rating) as avg_rating
        FROM books b
        LEFT JOIN reviews r ON b.id = r.book_id
        GROUP BY b.id
        ORDER BY avg_rating DESC
        LIMIT 5
    """

    #Execute the query and fetch the top books
    cursor.execute(query)
    top_books = cursor.fetchall()

    #Return a JSON response containing the top books
    return jsonify({"top_books": top_books})


#GET /author - Hämtar en kort sammanfattning om författaren och författarens mest kända verk. Använd externa API:er för detta.

def get_author_info(author_name):
    try:
        #Make a GET request to the Wikipedia API
        response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{author_name.replace(' ', '_')}")

        #Raise an HTTPError for bad responses
        response.raise_for_status()

        #Extract relevant information from the JSON response
        summary = response.json().get('extract', '')

        #Create a dictionary with the extracted information
        author_info = {'author': author_name, 'summary': summary}

        #Return the author information as a JSON response
        return jsonify(author_info), 200

    except requests.RequestException as err:
        #Handle request exceptions
        return jsonify({"error": f"Request Exception: {err}"}), 500

#Define the route with the correct parameter name
@app.route("/author/<author_name>", methods=["GET"])
def get_author_route(author_name):
    #Call the get_author_info function and return its result
    return get_author_info(author_name)