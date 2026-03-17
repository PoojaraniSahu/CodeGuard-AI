from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from routers import auth, github_webhook, repos

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeGuard AI", description="AI-powered code review platform.")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
import os
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(auth.router, prefix="/auth/github", tags=["auth"])
app.include_router(auth.router, tags=["auth_ui"]) # to get logout route without prefix
app.include_router(github_webhook.router, prefix="/webhook/github", tags=["webhook"])
app.include_router(repos.router, prefix="/repos", tags=["repos"])

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if user_id:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/")
        
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        from fastapi.responses import RedirectResponse
        response = RedirectResponse(url="/")
        response.delete_cookie("user_id")
        return response
        
    connected_repos = user.repositories
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "connected_repos": connected_repos
    })

@app.get("/repo/{repo_id}", response_class=HTMLResponse)
def repo_detail(request: Request, repo_id: int, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/")
        
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    repo = db.query(models.Repository).filter(models.Repository.id == repo_id, models.Repository.user_id == user.id).first()
    
    if not repo:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard")

    # Fetch reviews ordered by newest first
    reviews = db.query(models.Review).filter(models.Review.repo_id == repo.id).order_by(models.Review.created_at.desc()).all()
    
    return templates.TemplateResponse("repo_detail.html", {
        "request": request,
        "user": user,
        "repo": repo,
        "reviews": reviews
    })
