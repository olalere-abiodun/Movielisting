import sys
from pathlib import Path

# Add the root directory to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))


import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.auth import pwd_context
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup the test database and test client

SQLALCHEMY_DATABASE_URL = os.environ.get('DB_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Create a test database session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create the test database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    """Yield a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()

    # Use the connection with a transaction
    session = TestingSessionLocal(bind=connection)

    yield session  

    # Rollback - clean up the session
    session.close()
    transaction.rollback()
    connection.close()
# 1
def test_root():
   response = client.get("/")
   assert response.status_code == 200
   assert response.json() == {"message": "Welcome to my ALTSCHOOL Capstone project"}
# 2
def test_signup(test_db):
    response = client.post("/signup", json={
        "full_name": "User Test",
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com"
    })
    
    if response.status_code != 200:
        print("User Already Registered")
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser",  f"Key 'User has already Signed Up'"
        assert "created_at" in data
# 3
def test_login(test_db):
    response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

# 4
def test_list_a_movie(test_db):
    # Login to get the token
    login_response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/List_a_Movie/", json={
        "title": "Test Movie",
        "genre": "Sci - Fi",
        "description": "A test movie description2",
        "release_date": "2024-07-27"
    }, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Movie"
    assert data["genre"] == "Sci - Fi"

    assert "coverimage_data" in data, f"Cover image is empty"


# Get movie 5

def test_get_all_movie (test_db):
    response = client.get("/movies/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Movie"
    assert data[0]["genre"] == "Drama"
    assert data[0]["description"] == "A test movie description"
    assert data[0]["release_date"] == "2024-07-23"

    assert "coverimage_data" in data, f"Cover image is empty"

# 6
def test_get_movie_by_title (test_db):

    response = client.get("/movie/Test%20Movie")

    assert response.status_code == 200
    data = response.json()
    assert data["movie_id"] == 1
    assert data["title"] == "Test Movie"
    assert data["genre"] == "Drama"
    assert data["description"] == "A test movie description"
    assert data["release_date"] == "2024-07-23"

    assert "coverimage_data" in data, f"Cover image is empty"

# 7
def test_update_movie_by_title(test_db):
    login_response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a movie
    client.post("/List_a_Movie/", json={
        "title": "Test Movie To Update",
        "genre": "Drama",
        "description": "A test movie description",
        "release_date": "2024-07-27"
    }, headers=headers)

    response = client.put("/update_movie/Test%20Deleted%Movie", json={
        "title": "Updated Movie",
        "genre": "Action",
        "description": "Updated description",
        "updated_at": "2024-07-27"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Movie"
    assert data["genre"] == "Action"
    assert data["description"] == "Updated description"
#  8   
def delete_movie(test_db):
    login_response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a movie
    client.post("/List_a_Movie/", json={
        "title": "Deleted Movie",
        "genre": "Deleted Drama",
        "description": "A deleted test movie description",
        "release_date": "2024-07-23"
    }, headers=headers)
    
    client.delete("/delete_movie/Deleted%20Movie", headers=headers)
    response = client.get("/movies/Updated%20Movie")
    assert response.status_code == 404
# 9
def test_rate_movie(test_db):
    login_response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/movie/Teste%20Movie")
    assert response.status_code == 200
    data = response.json()
    assert data["movie_id"] == 1

    # Rate a movie 
    rate_response = client.post("/rating/", json={
        "movie_title": "Test Movie",
        "rating": 5,
        "created_at": "2024-07-27"
    }, headers=headers)

    if rate_response.status_code == 200:
        data = rate_response.json()
        print (f"Response: {data}")
        assert data["detail"] == "Rating added successfully", f"Key 'User has already rated this movie'"

    else:
        print("User already rated this movie")
        
       
# 10
def test_get_movie_ratings(test_db):
    response = client.get("/ratings/Test%20Movie")
    assert response.status_code == 200
    data = response.json()
    print(f"Ratings data: {data}")


# Comment starts here 11

def test_comment_on_movie(test_db):
    # Create user and login
    login_response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/movie/Test%20Movie")
    assert response.status_code == 200
    data = response.json()
    assert data["movie_id"] == 1

    # Comment on a movie
    comment_response = client.post("/comment/Test%20Movie", json={
        "content": "Another Great movie! Comment",
        "created_at": "2024-07-23"
    }, headers=headers)
    assert comment_response.status_code == 200
    data = comment_response.json()
    assert data["content"] == "Another Great movie! Comment"
    assert "username" in data
    assert "movie_title" in data


# test on get movie comments 12

def test_get_movie_comments(test_db):
    response = client.get("/comments/Test%20Movie")
    assert response.status_code == 200
    data = response.json()
    print(f"Comments data: {data}")


# Test reply to comment 13

def test_reply_to_comment(test_db):
    # Create user and login
    login_response = client.post("/login/", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    parent_comment_id = 1  

    # Reply to a comment
    response = client.post(f"/reply/?parent_comment_id={parent_comment_id}", json={
        "content": "Great reply!"
    }, headers=headers)
    
    assert response.status_code == 200, f"Reply failed: {response.text}"
    data = response.json()
    print(f"Response data: {data}")

    assert "reply" in data, f"Key 'content' not found in response: {data}"
    assert data["reply"] == "Great reply!", f"Unexpected content in response: {data['content']}"
    assert "username" in data, f"Key 'parent_comment_id' not found in response: {data}"

# Get all replies to a comment 14
def test_get_replies_to_comment(test_db):
    response = client.get("/replies/1")
    assert response.status_code == 200
    data = response.json()
    print(f"Replies data: {data}")