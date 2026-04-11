import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.config import settings
from app.crud.user import get_user_by_email, create_user
from app.core.security import create_access_token
from app.schemas.user import UserCreate, TokenResponse

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.get("/login")
def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }

    query_string = "&".join(f"{k}={v}" for k,v in params.items())
    google_url = f"{GOOGLE_AUTH_URL}?{query_string}"

    return {"url": google_url}

@router.get("/callback", response_model=TokenResponse)
def google_callback(code: str, db: Session = Depends(get_db)):
    with httpx.Client() as client:
        token_response = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
        )
    
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token with Google."
        )
    
    token_data = token_response.json()
    google_access_token = token_data.get("access_token")

    if not google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token received from Google."
        )
    

    with httpx.Client() as client:
        userinfo_response = client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"}
        )

    if userinfo_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch user data from Google."
        )
    
    userinfo = userinfo_response.json()
    email = userinfo.get("email")
    full_name = userinfo.get("name", "")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from Google account."
        )

    user = get_user_by_email(db, email=email)

    if not user:
        user = create_user(
            db=db,
            user_in=UserCreate(
                email=email,
                full_name=full_name,
                password=f"google_oauth_{email}"
            )
        )
    

    access_token = create_access_token(subject=user.email)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )