# Movie Listing App

This project is a movie listing application built with FastAPI. It includes endpoints for listing, creating, and managing movies, using SQLAlchemy for database interactions and Pydantic for request and response validation. The API documentation is auto-generated using FastAPI's built-in OpenAPI/Swagger documentation.


## 1. Setting Up the Application

### 1.1. Install Dependencies

Install the dependencies using pip:

```bash```
pip install -r requirements.txt


### 1.2. Database Specification

Database Used in the application is MongoDB

### 1.3. Environment Variables

Create a `.env` file and add the required environment variables (e.g., database URL, secret key).

## 2.  Endpoints

### User Endpoints:

* POST /signup/: Creates a new user (signup functionality).
* POST /login/: Authenticates a user and generates an access token (login functionality).
* PUT /reset_password/{email}: Resets the password for a user with the provided email (requires current user to be logged in and the email to match).

### Movie Endpoints:

* POST /List_a_Movie/: Uploads a new movie (requires user to be logged in).
* GET /movies/: Retrieves all movies (public endpoint).
* GET /movie/{title}: Retrieves a movie by its title (public endpoint).
* PUT /update_movie/{movie_title}: Updates a movie by its title (requires user to be logged in and the movie to be uploaded by the same user).
* DELETE /delete_movie/{movie_title}: Deletes a movie by its title (requires user to be logged in and the movie to be uploaded by the same user).

### Movie Rating Endpoints:

* POST /rating/: Rates a movie (requires user to be logged in).
* GET /ratings/{movie_title}: Retrieves all ratings for a movie (public endpoint).

### Movie Comment Endpoints:
* POST /comment/{movie_title}: Creates a comment for a movie (requires user to be logged in).
* GET /comments/{movie_title}: Retrieves all comments for a movie (public endpoint).
* POST /reply/: Replies to a comment on a movie (requires user to be logged in).
* GET /replies/{parent_comment_id}: Retrieves all replies for a comment (public endpoint).

##  3. Running the application

To run the application, use uvicorn

```bash```
uvicorn app.main:app --reload

##  4. Testting the application

```bash```
pytest


## 5. API Documentation

* FastAPI automatically generates interactive API documentation using OpenAPI/Swagger. Once the server is running, you can access:

* **Swagger UI:** Navigate to http://127.0.0.1:8000/docs to view the interactive API documentation.
* **ReDoc:** Navigate to http://127.0.0.1:8000/redoc for an alternative documentation style.

## 6. Technologies Used

FastAPI
SQLAlchemy
Pydantic
MongoDB
Uvicorn
Pytest

## 7. Contributing

If you wish to contribute to this project, please fork the repository and create a pull request with your changes. Ensure that your code follows the project's coding standards and passes all tests.

## Summary

This project is a movie listing application built with FastAPI, which includes endpoints for listing, managing movies, rating and commenting on movies. It uses SQLAlchemy for database interactions and Pydantic for request and response validation. The API documentation is auto-generated using FastAPI's built-in OpenAPI/Swagger documentation. The application is set up with MongoDB as the database, and includes detailed instructions for installation, setup, running, testing, and contribution.








