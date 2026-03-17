from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    access_token = Column(String, nullable=True) # To store the GitHub token securely

    repositories = relationship("Repository", back_populates="owner")

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    repo_name = Column(String, index=True)
    webhook_url = Column(String, nullable=True)
    webhook_id = Column(String, nullable=True)

    owner = relationship("User", back_populates="repositories")
    reviews = relationship("Review", back_populates="repository")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    pr_id = Column(Integer, index=True)
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    repository = relationship("Repository", back_populates="reviews")
    issues = relationship("Issue", back_populates="review")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    issue_type = Column(String) # error/security/style
    severity = Column(String)   # high/medium/low
    message = Column(Text)
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)

    review = relationship("Review", back_populates="issues")
