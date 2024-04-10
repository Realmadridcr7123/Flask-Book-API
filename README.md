Flask Book Management API

Welcome to the Flask Book Management API! This API provides a lightweight and efficient solution for managing books and reviews. Developed using Flask and SQLite, it offers straightforward endpoints for performing CRUD operations on book data.

Installation

Clone the repository:
bash
Copy code
[git clone https://github.com/khaledahmed2023/flask-book-management-api.git]
Install dependencies:
Copy code
pip install -r requirements.txt
Run the Flask application:
Copy code
python app.py
Endpoints

GET /books: Retrieve all books from the database, with optional filters for title, author, and genre.
POST /books: Add one or more books to the database.
GET /books/{book_id}: Retrieve details of a specific book by its ID.
PUT /books/{book_id}: Update information about a book.
DELETE /books/{book_id}: Delete a book from the database.
POST /reviews: Add a review for a book.
GET /reviews: Retrieve all reviews stored in the database.
GET /reviews/{book_id}: Retrieve reviews for a specific book.
GET /books/top: Retrieve the top five books with the highest average ratings.
GET /author/{author_name}: Fetch a summary of an author and their notable works using external APIs.
Database

The API utilizes SQLite as its database backend. The database file books.db stores information about books and reviews.

External APIs

Wikipedia API: Utilized to fetch information about authors and their notable works.
Usage

Once the application is running, interact with it using any HTTP client (e.g., cURL, Postman). Here's an example using cURL:

bash
Copy code
curl http://localhost:5000/books
Testing

The API endpoints have been rigorously tested using Postman to ensure functionality and reliability.

To run tests using pytest, execute the following command:

bash
Copy code
pytest test_app.py
Contributors

