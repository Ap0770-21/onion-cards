from fastapi import APIRouter, Header, HTTPException, Depends
from supabase_client import supabase

router = APIRouter()


def get_current_user(authorization: str = Header(None)):
    """
    Frontend sends the Supabase session access token as:
    Authorization: Bearer <token>
    Returns the user dict, or None for anonymous (free, prompt-only) requests.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        user_resp = supabase.auth.get_user(token)
        return user_resp.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session")


def require_user(user=Depends(get_current_user)):
    """Use this dependency on routes that must not be anonymous (e.g. upload, cards, billing)."""
    if user is None:
        raise HTTPException(status_code=401, detail="Sign in required")
    return user


@router.get("/me")
def me(user=Depends(require_user)):
    return {"id": user.id, "email": user.email}
