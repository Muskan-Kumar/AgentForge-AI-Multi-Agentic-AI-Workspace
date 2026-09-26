from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from src.auth.dependencies import get_current_user

from src.auth.security import (
    create_access_token,
    verify_password,
)

from src.auth.user_service import (
    create_user,
    get_user_by_email,
    update_password
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )



@router.post("/register")
def register(request: RegisterRequest):

    try:
        user = create_user(
            email=request.email,
            password=request.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return {
        "message": "User registered successfully",
        "user_id": user.user_id,
        "email": user.email,
    }


@router.post("/login")
def login(request: LoginRequest):

    user = get_user_by_email(
        request.email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "email": user.email,
    }


@router.get("/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
):
    return current_user



@router.put("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
):
    user = get_user_by_email(
        current_user["email"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if not verify_password(
        request.current_password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    if request.current_password == request.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password",
        )

    update_password(
        email=current_user["email"],
        new_password=request.new_password,
    )

    return {
        "message": "Password changed successfully"
    }