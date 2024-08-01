from sqlalchemy.orm import Session
from fastapi import HTTPException
from .auth import pwd_context
from . import model, schema, auth
from datetime import datetime
import sqlalchemy
from sqlalchemy import func

# User Crud start
def create_user(db: Session, user: schema.UserCreate, hashed_password: str):
    db_user = model.User(
        full_name = user.full_name,
        username = user.username,
        hashed_password = hashed_password,
        email = user.email        
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(model.User).filter(model.User.email == email).first()

def get_user_by_username(db: Session, username:str):
    return db.query(model.User).filter(model.User.username == username).first()

def update_user_password(db: Session, email: str, new_password: str):
    user = db.query(model.User).filter(model.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the new password is the same as the old one
    if pwd_context.verify(new_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different from the old password")

    # Hash the new password
    new_hashed_password = pwd_context.hash(new_password)
    
    # Update the password in the database
    user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(user)
    
    return user

# User CRUD End

# Movie Crud start

# 1. List a Movie
def Upload_new_movie(db: Session, movie: schema.MovieUpload, user_id: str = None):
    db_movie = model.Movies(
        title = movie.title,
        genre = movie.genre,
        description = movie.description,
        release_date = movie.release_date,
        user_id = user_id       
        
    
        
        )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# View all Movie (Public)

def view_all_movies(db: Session):
    return db.query(model.Movies).all()

def get_movie_by_title(db: Session, title: str):
    return db.query(model.Movies).filter(model.Movies.title == title).first()

def update_movie(db: Session, title: str, updateMovie: schema.MovieUpdate):
    movie = db.query(model.Movies).filter(model.Movies.title == title).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie.title = updateMovie.title
    movie.genre = updateMovie.genre
    movie.description = updateMovie.description
    # Set updated_at to current time if not provided
    movie.updated_at = updateMovie.updated_at if updateMovie.updated_at else datetime.utcnow()
    

    db.commit()
    db.refresh(movie)
    
    return movie

#Authorized delete a movie

def delete_movie(db: Session, title: str, user_id: str):
    movie = db.query(model.Movies).filter(model.Movies.title == title, model.Movies.user_id == user_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(movie)
    db.commit()
    
    return {"detail": "Movie deleted successfully"}

# Movie Crud End
 
# Rating a movie 

def rate_movie(db: Session, movie_id, rating: int, user_id: str):
    existing_rating = db.query(model.Rating).filter(model.Rating.movie_id == movie_id, model.Rating.user_id == user_id).first()
    if existing_rating:
        raise HTTPException(status_code=400, detail="User has already rated this movie")
    # Create a new rating
    new_rating = model.Rating(
        movie_id = movie_id,
        user_id = user_id,
        rating = rating
        )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return {"detail": "Rating added successfully"}

# Get Ratings for a movie

def get_ratings_for_movie(db: Session, movie_id: str):
    ratings = db.query(
        func.avg(model.Rating.rating).label('rating'),
        model.Movies.title
        ).join(
            model.Movies, model.Rating.movie_id == model.Movies.movie_id
    ).filter(
    model.Movies.movie_id == movie_id
    ).group_by(
        model.Movies.title
    ).first()
    return (ratings)
    # return db.query(model.Rating).filter(model.Rating.movie_id == movie_id).all()

# Rating a movie End

# Comment on a movie CRUD 

def create_comment(db: Session, comment: schema.PostComment, movie_id: str, user_id: str):
    new_comment = model.ParentComment(

        movie_id = movie_id,
        user_id = user_id,
        content = comment.content
        )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    user = db.query(model.User).filter(model.User.user_id == user_id).first()
    movie = db.query(model.Movies).filter(model.Movies.movie_id == movie_id).first()
   
    return {
        "username": user.username,
        "movie_title": movie.title,
        "content": new_comment.content
    }

# Get all comments for a movie

def get_comments_for_movie(db: Session, movie_id: str):
    comments = db.query(
        model.User.username,
        model.ParentComment.content,
        model.Movies.title
    ).join(
        model.ParentComment, model.ParentComment.user_id == model.User.user_id
    ).join(
        model.Movies, model.ParentComment.movie_id == model.Movies.movie_id
    ).filter(
        model.ParentComment.movie_id == movie_id
    ).distinct().all()
    
    return [{"movie_title": comment.title, "username": comment.username, "comment": comment.content} for comment in comments]
    
# Reply to comments (Nested Comment)

def reply_to_comment(db: Session, comment_id: str, reply: schema.PostReply, user_id: str):
    parent_comment = db.query(model.ParentComment).filter(model.ParentComment.parent_comment_id == comment_id).first()
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    new_reply = model.CommentReply(
        parent_comment_id = parent_comment.parent_comment_id,
        user_id = user_id,
        content = reply.content
    )
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)
    
    user = db.query(model.User).filter(model.User.user_id == user_id).first()
    return {
        "username": user.username,
        "Comment": parent_comment.content,
        "reply": new_reply.content
    }

def get_reply(db: Session, parent_comment_id: int):
    replies = db.query(model.CommentReply).filter(model.CommentReply.parent_comment_id == parent_comment_id).all()
    return [{"reply": reply.content} for reply in replies]

# Comment on a movie CRUD End
     