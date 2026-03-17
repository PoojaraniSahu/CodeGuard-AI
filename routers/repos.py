from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db, SessionLocal
from services import github_service, ai_service
from config import settings
from typing import List

router = APIRouter()

def get_current_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[schemas.RepositoryModel])
def list_connected_repos(user_id: int, db: Session = Depends(get_db)):
    """List repositories connected to CodeGuard AI."""
    user = get_current_user(user_id, db)
    return user.repositories

@router.get("/available")
def list_github_repos(user_id: int, db: Session = Depends(get_db)):
    """Fetch all repositories the user has access to on GitHub."""
    user = get_current_user(user_id, db)
    if not user.access_token:
         raise HTTPException(status_code=401, detail="GitHub access token missing. Please re-authenticate.")
         
    return github_service.fetch_user_repos(user.access_token)

@router.post("/connect", response_model=schemas.RepositoryModel)
def connect_repo(repo: schemas.RepositoryBase, user_id: int, db: Session = Depends(get_db)):
    """Connect a repository and set up GitHub Webhook."""
    user = get_current_user(user_id, db)
    if not user.access_token:
         raise HTTPException(status_code=401, detail="GitHub access token missing. Please re-authenticate.")
         
    existing = db.query(models.Repository).filter(
        models.Repository.repo_name == repo.repo_name,
        models.Repository.user_id == user.id
    ).first()
    
    if existing:
        return existing

    webhook_url = f"{settings.WEBHOOK_BASE_URL}/webhook/github"
    
    try:
        webhook_id = github_service.setup_repo_webhook(
            access_token=user.access_token,
            repo_name=repo.repo_name,
            webhook_url=webhook_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup webhook on GitHub: {str(e)}")

    new_repo = models.Repository(
        user_id=user.id,
        repo_name=repo.repo_name,
        webhook_url=webhook_url,
        webhook_id=str(webhook_id)
    )
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)
    return new_repo

def process_full_repo_scan(repo_id: int):
    # This runs in background
    db = SessionLocal()
    try:
        repo = db.query(models.Repository).filter(models.Repository.id == repo_id).first()
        if not repo or not repo.owner.access_token:
            return

        # 1. Fetch all important files
        files_content = github_service.get_all_repo_files(repo.owner.access_token, repo.repo_name)
        
        # 2. Setup a unified review object
        # Since it's a full repo review, we'll set pr_id to 0 to indicate a manual full scan
        review = models.Review(repo_id=repo.id, pr_id=0, result_json=[])
        db.add(review)
        db.commit()
        db.refresh(review)

        total_issues = []

        # 3. Analyze each file sequentially (or we could batch, but sequential is safer for quota)
        for file_obj in files_content:
            issues = ai_service.analyze_full_file(file_obj["filename"], file_obj["content"])
            if issues:
                total_issues.extend(issues)
                
                # Store immediately
                for issue_data in issues:
                    db_issue = models.Issue(
                        review_id=review.id,
                        issue_type=issue_data.get("issue_type", "style"),
                        severity=issue_data.get("severity", "low"),
                        message=issue_data.get("message"),
                        file_path=issue_data.get("file_path", file_obj["filename"]),
                        line_number=issue_data.get("line_number")
                    )
                    db.add(db_issue)
                db.commit()
                
        # 4. Update the review JSON with all issues combined
        review.result_json = total_issues
        db.commit()

    finally:
        db.close()

@router.post("/{repo_id}/scan")
def trigger_repo_scan(repo_id: int, user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers a full codebase AI review in the background."""
    user = get_current_user(user_id, db)
    repo = db.query(models.Repository).filter(
        models.Repository.id == repo_id,
        models.Repository.user_id == user.id
    ).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    background_tasks.add_task(process_full_repo_scan, repo.id)
    return {"status": "scanning", "message": "Full repository scan started in the background."}
