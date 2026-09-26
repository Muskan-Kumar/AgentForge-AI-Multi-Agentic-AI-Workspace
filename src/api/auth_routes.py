from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from src.auth.dependencies import get_current_user
from src.auth.email_service import send_password_reset_email
from src.core.rate_limiter import RateLimiter

from src.auth.security import (
    create_access_token,
    verify_password,
)

from src.auth.user_service import (
    create_user,
    get_user_by_email,
    update_password,
    create_password_reset_request,
    reset_password,
    increment_token_version,
)




router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


login_limiter = RateLimiter(
    max_requests=5,
    window_seconds=300,
)

forgot_password_limiter = RateLimiter(
    max_requests=3,
    window_seconds=900,
)

reset_password_limiter = RateLimiter(
    max_requests=5,
    window_seconds=900,
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20)
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

    client_key = request.email.lower().strip()

    if not login_limiter.is_allowed(client_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

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
        token_version=user.token_version,
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

    increment_token_version(
        user_id=current_user["user_id"]
    )

    return {
        "message": "Password changed successfully"
    }





@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
):

    client_key = request.email.lower().strip()

    if not forgot_password_limiter.is_allowed(client_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again later.",
        )
    
    token = create_password_reset_request(
        email=request.email
    )

    if token:
        send_password_reset_email(
            email=request.email,
            reset_token=token,
        )

    return {
        "message": (
            "If an account exists for this email, "
            "a password reset link has been sent."
        )
    }




@router.post("/reset-password")
def reset_password_route(
    request: ResetPasswordRequest,
):

    client_key = request.token

    if not reset_password_limiter.is_allowed(client_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reset attempts. Please try again later.",
        )

    success = reset_password(
        token=request.token,
        new_password=request.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {
        "message": "Password reset successfully"
    }
