# flask-book-management-api

Flask Book Management API is a lightweight RESTful API for managing books and reviews. Built with Flask and SQLite, it offers simple endpoints for CRUD operations on book data. The API has been rigorously tested using Postman for reliability.

## Installation

To install and run the API, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/khaledahmed2023/flask-book-management-api.git

2. **Install Dependencies:**

  ```bash
    pip install -r requirements.txt


3. **Run the Flask application:**
  
   ```bash
      python app.py

## Endpoints

Explore the following endpoints for interacting with the API:

- **GET /books:** Retrieve all books in the database with optional filters for title, author, and genre.
- **POST /books:** Add one or more books to the database.
- **GET /books/{book_id}:** Retrieve details of a single book by its ID.
- **PUT /books/{book_id}:** Update information about a book.
- **DELETE /books/{book_id}:** Delete a book by its ID.
- **POST /reviews:** Add a review for a book.
- **GET /reviews:** Retrieve all reviews in the database.
- **GET /reviews/{book_id}:** Retrieve all reviews for a specific book.
- **GET /books/top:** Retrieve the top five books with the highest average ratings.
- **GET /author/{author_name}:** Retrieve a summary of an author and their most famous works using external APIs.

## Database

The application uses SQLite as its database backend. The database file is `books.db`, which stores information about books and reviews.

## External APIs

The API integrates with the Wikipedia API to fetch information about authors and their notable works.

## Usage

Once the application is running, you can interact with it using any HTTP client (e.g., cURL, Postman). Here's an example using cURL:


