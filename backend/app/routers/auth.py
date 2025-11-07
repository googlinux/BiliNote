"""
Authentication router for user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.engine import get_db
from app.db.user_dao import UserDAO
from app.db.models.user import User
from app.models.auth_model import (
    UserRegister, UserLogin, Token, UserResponse,
    UserUpdate, PasswordChange, PasswordResetRequest,
    PasswordReset, EmailVerification
)
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    create_email_verification_token, create_password_reset_token,
    verify_email_token, verify_password_reset_token, verify_password
)
from app.core.dependencies import get_current_user, get_current_active_user
from app.utils.response import ResponseWrapper

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=ResponseWrapper[UserResponse])
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - **email**: Valid email address
    - **password**: Password (min 8 chars, must contain letter and digit)
    - **full_name**: Optional full name
    - **username**: Optional username (min 3 chars)

    Returns user data and verification email is sent (in production)
    """
    # Check if user already exists
    existing_user = UserDAO.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check username if provided
    if user_data.username:
        existing_username = UserDAO.get_user_by_username(db, user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create user
    user = UserDAO.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        username=user_data.username,
    )

    # In production, send verification email here
    # verification_token = create_email_verification_token(user.email)
    # await send_verification_email(user.email, verification_token)

    return ResponseWrapper.success(
        data=UserResponse.model_validate(user),
        msg="Registration successful. Please check your email for verification link."
    )


@router.post("/login", response_model=ResponseWrapper[Token])
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login with email and password

    Returns access token and refresh token
    """
    user = UserDAO.authenticate_user(db, user_data.email, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return ResponseWrapper.success(
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        ),
        msg="Login successful"
    )


@router.post("/refresh", response_model=ResponseWrapper[Token])
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Returns new access token and refresh token
    """
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Verify user still exists
    user = UserDAO.get_user_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return ResponseWrapper.success(
        data=Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        ),
        msg="Token refreshed"
    )


@router.post("/verify-email", response_model=ResponseWrapper[dict])
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """
    Verify user email with verification token
    """
    email = verify_email_token(verification_data.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    success = UserDAO.verify_email(db, email)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ResponseWrapper.success(
        data={"email": email},
        msg="Email verified successfully"
    )


@router.post("/forgot-password", response_model=ResponseWrapper[dict])
async def forgot_password(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset

    Sends password reset email (in production)
    """
    user = UserDAO.get_user_by_email(db, request_data.email)

    # Don't reveal if user exists or not (security best practice)
    if user:
        # In production, send reset email here
        # reset_token = create_password_reset_token(user.email)
        # await send_password_reset_email(user.email, reset_token)
        pass

    return ResponseWrapper.success(
        data={},
        msg="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=ResponseWrapper[dict])
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset password with token
    """
    email = verify_password_reset_token(reset_data.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    user = UserDAO.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    success = UserDAO.update_password(db, user.id, reset_data.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

    return ResponseWrapper.success(
        data={},
        msg="Password reset successful"
    )


@router.get("/me", response_model=ResponseWrapper[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information

    Requires authentication
    """
    return ResponseWrapper.success(
        data=UserResponse.model_validate(current_user),
        msg="User retrieved"
    )


@router.put("/me", response_model=ResponseWrapper[UserResponse])
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile

    Requires authentication
    """
    # Check if username is being changed and already taken
    if user_update.username and user_update.username != current_user.username:
        existing = UserDAO.get_user_by_username(db, user_update.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    updated_user = UserDAO.update_user(
        db=db,
        user_id=current_user.id,
        full_name=user_update.full_name,
        username=user_update.username,
        avatar_url=user_update.avatar_url,
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update failed"
        )

    return ResponseWrapper.success(
        data=UserResponse.model_validate(updated_user),
        msg="Profile updated"
    )


@router.post("/change-password", response_model=ResponseWrapper[dict])
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user

    Requires current password for verification
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    success = UserDAO.update_password(db, current_user.id, password_data.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

    return ResponseWrapper.success(
        data={},
        msg="Password changed successfully"
    )
