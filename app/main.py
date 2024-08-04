from fastapi import Depends, FastAPI, File, UploadFile, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app import crud, schema, model, auth, database
from app.auth import pwd_context, oauth2_scheme, authenticate_user, create_access_token, get_current_user
import sqlalchemy
from datetime import date
from io import BytesIO
import base64
from app.database import SessionLocal, engine, Base, get_db
from typing import Optional
from passlib.context import CryptContext
from my_logging.logger import get_logger



Base.metadata.create_all(bind=engine)

app = FastAPI()
logger = get_logger(__name__)

@app.get("/")
async def root():
    logger.info("App accessed")
    return {"message": "Welcome to my Movie Listing API"}

# User EndPoint Start
@app.post("/signup/", response_model=schema.UserResponse)
async def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    logger.info("Creating User....")
    check_email = crud.get_user_by_email(db, email=user.email)
    if check_email:
        logger.warning(f'email:{user.email} already exists')
        raise HTTPException(status_code=400, detail="Email already registered")
    check_username = crud.get_user_by_username(db, username=user.username)
    if check_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = pwd_context.hash(user.password)
    new_user = crud.create_user(db, user=user, hashed_password=hashed_password)
    logger.info(f"Created a new user {user.username}")
    return new_user

@app.post('/login/')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info("Generating authentication token...")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Token generated for {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.put("/reset_password/{email}")
async def reset_password(email: str, new_password: schema.PasswordReset, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    get_user = crud.get_user_by_email(db, email)
    if not get_user:
        logger.warning(f'user with the email {email} is not found')
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.email != get_user.email:
        logger.warning('User with the email {email} is not authorized')
        raise HTTPException(status_code=401, detail="Unauthorized user")
    hashed_password = pwd_context.hash(new_password.password)
    updated_user = crud.update_user_password(db, email=email, new_password=new_password.password)
    logger.info(f"Updated user {current_user.username} password successfully")
    return {"message": "Password reset successfully"}

# User EndPoint End

# Movie EndPoint Start

@app.post("/List_a_Movie/", response_model=schema.MovieResponse)
async def list_a_movie(
    
    title: str = Form(...),
    genre: str = Form(...),
    description: str = Form(...),
    videofile: UploadFile = File(...),
    coverfile: UploadFile = File(...),
    release_date: str = Form(...),
    db: Session = Depends(get_db),
    posted_by: schema.User = Depends(get_current_user)
    ):
    if videofile.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Invalid file type. Only MP4 files are allowed.")
    if coverfile.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only jpeg or png files are allowed.")
    
    videofile_data = await videofile.read()
    coverfile_data = await coverfile.read()

    movie_upload = schema.MovieUpload(
        title=title,
        genre=genre,
        description=description,
        video_data=videofile_data,
        coverimage_data=coverfile_data,
        release_date=release_date,
        user_id=posted_by.user_id,

    )

    new_movie = crud.upload_new_movie (db, movie= movie_upload, user_id = posted_by.user_id )
    logger.info(f'{posted_by.username} listed a new movie {new_movie.title}')
    return new_movie

# @app.post("/List_a_Movie/", response_model=schema.MovieResponse)
# async def list_a_movie(movie: schema.MovieUpload, db: Session = Depends(get_db), posted_by: schema.User = Depends(get_current_user)):
#     new_movie = crud.Upload_new_movie (db, movie= movie, user_id = posted_by.user_id )
#     logger.info(f'{posted_by.username} listed a new movie')
#     return new_movie

@app.get("/movies/", response_model=List[schema.MovieResponse])
async def get_all_movies(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    all_movies = crud.view_all_movies(db, offset=offset, limit=limit)
    logger.info("All movies Generated by a user")
    return all_movies

@app.get("/movie/{title}", response_model=schema.MovieResponse)
async def get_movie_by_title(title: str, db: Session = Depends(get_db)):
    movie = crud.get_movie_by_title(db, title=title)
    if not movie:
        logger.warning(f'Movie {title} not found')
        raise HTTPException(status_code=404, detail="Movie not found")
    logger.info(f'Movie {title} fetched')
    return movie






# Movie Update Endpoint

@app.put("/update_movie/{movie_title}", response_model=schema.MovieResponse)
async def update_movie_by_title(movie_title: str, updated_movie: schema.MovieUpdate, db: Session = Depends(get_db), updated_by: schema.User = Depends(get_current_user)):
    get_movie = crud.get_movie_by_title(db, title=movie_title)
    if not get_movie:
        logger.warning(f"Movie {movie_title} not found")
        raise HTTPException(status_code=404, detail="Movie not found")
    if updated_by.user_id != get_movie.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    updated_movie = crud.update_movie(db, title=movie_title, updateMovie=updated_movie)
    logger.info(f"{updated_by.user_id} Updated movie '{movie_title}' successfully")
    return updated_movie

# Movie Delete Endpoint

@app.delete("/delete_movie/{movie_title}")
async def delete_movie_by_title(movie_title: str, db: Session = Depends(get_db), deleted_by: schema.User = Depends(get_current_user)):
    get_movie = crud.get_movie_by_title(db, title=movie_title)
    if not get_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if deleted_by.user_id != get_movie.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized To delete this movie")
    deleted_movie = crud.delete_movie(db, title=movie_title, user_id=deleted_by.user_id)
    logger.info(f"{deleted_by.user_id} deleted movie '{movie_title}' successfully")
    return {"detail": f"Movie '{movie_title}' deleted successfully"}


# Rate a movie (authenticated access)
@app.post('/rating/')

async def rate_movie(rating: schema.RatingCreate, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    movie_rated = db.query(model.Movies).filter(model.Movies.title == rating.movie_title).first()
    if not movie_rated:
        raise HTTPException(status_code=404, detail="Movie not found")
    new_rating = crud.rate_movie(db, movie_id= movie_rated.movie_id, rating=rating.rating, user_id=current_user.user_id)
    logger.info(f"{current_user.username} rated movie '{rating.movie_title}' with {rating.rating}")
    return new_rating

# Get all ratings for a movie

@app.get('/ratings/{movie_title}', response_model=schema.RatingResponse)
async def get_movie_ratings(movie_title: str, db: Session = Depends(get_db)):
    movie_rated = db.query(model.Movies).filter(model.Movies.title == movie_title).first()
    if movie_rated is None:
        logger.warning(f"Movie {movie_title} not found")
        raise HTTPException(status_code=404, detail="Movie not found")
    movie_ratings = crud.get_ratings_for_movie(db, movie_id = movie_rated.movie_id)
    if not movie_ratings:
        logger.warning(f"No ratings found for movie '{movie_title}'")
        raise HTTPException(status_code=404, detail="No ratings found for this movie")
    logger.info(f"All ratings for movie '{movie_title}' fetched successfully")
    return movie_ratings

# Comment on a movie (authenticated access)

@app.post('/comment/{movie_title}', response_model = schema.ParentCommentResponse)
async def comment_on_movie(movie_title: str, comment: schema.PostComment, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    movie_commented = db.query(model.Movies).filter(model.Movies.title == movie_title).first()
    if not movie_commented:
        logger.warning("Movie %s not found in database")
        raise HTTPException(status_code=404, detail="Movie not found")

    new_comment = crud.create_comment(db, comment = comment, movie_id=movie_commented.movie_id, user_id=current_user.user_id)
    logger.info(f"{current_user.user_id} commented on movie '{movie_title}'")
    return new_comment

# Get all comments for a movie
@app.get("/comments/{movie_title}")

async def get_movie_comments(movie_title: str, db: Session = Depends(get_db)):
    movie_commented = db.query(model.Movies).filter(model.Movies.title == movie_title).first()
    if not movie_commented:
        logger.warning("Movie %s not found in database")
        raise HTTPException(status_code=404, detail="Movie not found")
    movie_comments = crud.get_comments_for_movie(db, movie_id=movie_commented.movie_id)
    if not movie_comments:
        logger.warning("No comments found for movie %s")
        raise HTTPException(status_code=404, detail="No comments found for this movie")
    logger.info(f"comment for {movie_title} checked")
    return movie_comments

# Reply to a comment on a movie

@app.post("/reply/",  #response_model=schema.ChildCommentResponse
)
async def reply_to_comment(parent_comment_id: int, reply: schema.PostReply, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    parent_comment = db.query(model.ParentComment).filter(model.ParentComment.parent_comment_id == parent_comment_id).first()
    if not parent_comment:
        return None
    new_reply = crud.reply_to_comment(db, comment_id=parent_comment_id, reply=reply,user_id=current_user.user_id)
    logger.info(f"{current_user.user_id} replied to comment {parent_comment_id}") 
    return new_reply

@app.get("/replies/{parent_comment_id}")
async def get_replies(parent_comment_id: int, db: Session = Depends(get_db)):
    replies = crud.get_reply(db, parent_comment_id)
    if not replies:
        raise HTTPException(status_code=404, detail="No replies found for the given comment")
    logger.info(f"Replies for comment {parent_comment_id} fetched")
    return replies