from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import models
from database import SessionLocal
from services import github_service, ai_service
import json

router = APIRouter()

def process_webhook_payload(payload: dict, repo_id: int):
    # This runs in background
    db = SessionLocal()
    try:
        repo = db.query(models.Repository).filter(models.Repository.id == repo_id).first()
        if not repo or not repo.owner.access_token:
            return

        action = payload.get("action")
        pr_number = None

        if "pull_request" in payload and action in ["opened", "synchronize"]:
            pr = payload["pull_request"]
            pr_number = pr["number"]
            repo_name = pr["base"]["repo"]["full_name"]
            
            # 1. Fetch Diffs
            files_diff, title, body = github_service.get_pr_diff(repo.owner.access_token, repo.repo_name, pr_number)
            
            # Combine patches into one large string (or handle file by file to avoid limits)
            full_diff_text = ""
            for file in files_diff:
                if file["patch"]:
                    full_diff_text += f"\n--- {file['filename']} ---\n{file['patch']}\n"
                    
            if not full_diff_text:
                return

            # 2. Analyze with Gemini
            issues = ai_service.analyze_code_diff(full_diff_text)
            
            # 3. Store in DB
            review = models.Review(repo_id=repo.id, pr_id=pr_number, result_json=issues)
            db.add(review)
            db.commit()
            db.refresh(review)

            for issue_data in issues:
                db_issue = models.Issue(
                    review_id=review.id,
                    issue_type=issue_data.get("issue_type", "style"),
                    severity=issue_data.get("severity", "low"),
                    message=issue_data.get("message"),
                    file_path=issue_data.get("file_path")
                )
                db.add(db_issue)
            db.commit()

            # 4. Post Summary to GitHub PR
            if issues:
                high_count = len([i for i in issues if i["severity"] == "high"])
                med_count = len([i for i in issues if i["severity"] == "medium"])
                
                comment_body = f"## 🤖 CodeGuard AI Review Complete\n\nFound **{len(issues)}** total issues ({high_count} High, {med_count} Medium).\n\n"
                for i in issues:
                    emoji = "🐞" if i["issue_type"] == "bug" else "🔐" if i["issue_type"] == "security" else "🎨"
                    comment_body += f"- {emoji} **{i['severity'].upper()}** in `{i['file_path']}`: {i['message']}\n"
                    
                comment_body += "\n*[View full details on the CodeGuard Dashboard]*"
                
                github_service.post_pr_comment(
                    repo.owner.access_token, repo.repo_name, pr_number, comment_body
                )

    finally:
        db.close()


@router.post("/")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Listens for GitHub Push/PR events."""
    # Check if we should ignore (e.g., verify signature)
    # For now, simplistic approach
    payload = await request.json()
    
    # Identify which repo this belongs to
    repo_data = payload.get("repository")
    if not repo_data:
         return {"status": "ignored"}
         
    repo_name = repo_data.get("full_name")
    
    db = SessionLocal()
    repo = db.query(models.Repository).filter(models.Repository.repo_name == repo_name).first()
    if repo:
        background_tasks.add_task(process_webhook_payload, payload, repo.id)
    db.close()

    return {"status": "accepted"}
