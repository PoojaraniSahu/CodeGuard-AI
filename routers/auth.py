from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session
from database import get_db
import models
from config import settings

router = APIRouter()

GITHUB_OAUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API = "https://api.github.com/user"

@router.get("/login")
def github_login():
    """Redirects to GitHub OAuth page."""
    redirect_uri = f"{settings.WEBHOOK_BASE_URL}/auth/github/callback"
    url = f"{GITHUB_OAUTH_URL}?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}&scope=repo,user"
    return RedirectResponse(url)

@router.get("/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """Handles GitHub callback, exchanges code for token, and creates/updates user."""
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for access token
        headers = {'Accept': 'application/json'}
        data = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code
        }
        token_res = await client.post(GITHUB_TOKEN_URL, data=data, headers=headers)
        token_data = token_res.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token from GitHub")
            
        access_token = token_data["access_token"]
        
        # 2. Fetch user profile from GitHub
        user_headers = {"Authorization": f"Bearer {access_token}"}
        user_res = await client.get(GITHUB_USER_API, headers=user_headers)
        user_profile = user_res.json()
        
        github_id = str(user_profile.get("id"))
        username = user_profile.get("login")
        
        if not github_id or not username:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info from GitHub")

        # 3. Store user in database
        user = db.query(models.User).filter(models.User.github_id == github_id).first()
        if not user:
            user = models.User(github_id=github_id, username=username, access_token=access_token)
            db.add(user)
        else:
            user.username = username
            user.access_token = access_token
        
        db.commit()
        db.refresh(user)

        response = RedirectResponse(url="/dashboard")
        response.set_cookie(key="user_id", value=str(user.id), httponly=True)
        return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    return response
