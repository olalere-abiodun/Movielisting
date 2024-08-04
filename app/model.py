from sqlalchemy import Column, Boolean, String,LargeBinary, Integer, ForeignKey, TIMESTAMP, Date, Text, CheckConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base 

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    movies = relationship('Movies', back_populates='posted_by')
    ratings = relationship('Rating', back_populates='user')
    parent_comments = relationship('ParentComment', back_populates='user')
    comment_replies = relationship('CommentReply', back_populates='user')


class Movies(Base):
    __tablename__ ='movies'

    movie_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    # addition
    video_data = Column(LargeBinary)
    coverimage_data = Column(LargeBinary)
    release_date = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.user_id'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    posted_by = relationship('User', back_populates='movies')
    ratings = relationship('Rating', back_populates='movie')
    parent_comments = relationship('ParentComment', back_populates='movie')
    
    
class Rating(Base):
    __tablename__ = "ratings"
    
    rating_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship('User', back_populates='ratings')
    movie = relationship('Movies', back_populates='ratings')

class ParentComment(Base):
    __tablename__ = "parent_comments"
    
    parent_comment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship('User', back_populates='parent_comments')
    movie = relationship('Movies', back_populates='parent_comments')
    comment_replies = relationship('CommentReply', back_populates='parent_comment')

class CommentReply(Base):
    __tablename__ = "comment_replies"
    
    reply_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('parent_comments.parent_comment_id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship('User', back_populates='comment_replies')
    parent_comment = relationship('ParentComment', back_populates='comment_replies')