from pydantic import BaseModel
from typing import List, Optional
import datetime

class IssueBase(BaseModel):
    issue_type: str
    severity: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

class IssueModel(IssueBase):
    id: int
    review_id: int

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    pr_id: int
    result_json: Optional[dict] = None

class ReviewModel(ReviewBase):
    id: int
    repo_id: int
    created_at: datetime.datetime
    issues: List[IssueModel] = []

    class Config:
        orm_mode = True

class RepositoryBase(BaseModel):
    repo_name: str

class RepositoryModel(RepositoryBase):
    id: int
    user_id: int
    webhook_url: Optional[str] = None
    
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserModel(UserBase):
    id: int
    github_id: str
    repositories: List[RepositoryModel] = []

    class Config:
        orm_mode = True
