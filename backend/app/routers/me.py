from fastapi import APIRouter, Depends

from app.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/me")
def me(user: CurrentUser = Depends(get_current_user)):
    return {"email": user.email, "full_name": user.full_name, "role": user.role}
