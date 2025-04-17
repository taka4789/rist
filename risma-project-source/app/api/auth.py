from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.core.security import create_access_token, verify_password, SECRET_KEY, ALGORITHM
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from jose import jwt, JWTError

router = APIRouter()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(OAuth2PasswordRequestForm)
) -> models.User:
    """
    現在のユーザーを取得する
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="ユーザーが無効です")
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    現在のアクティブユーザーを取得する
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="ユーザーが無効です")
    return current_user

def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    現在のスーパーユーザーを取得する
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="権限が不足しています"
        )
    return current_user

def get_current_manager_or_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    現在のマネージャーまたはスーパーユーザーを取得する
    """
    if current_user.role != "manager" and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="権限が不足しています"
        )
    return current_user

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 互換のトークンログインを取得する
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="メールアドレスまたはパスワードが正しくありません")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="ユーザーが無効です")
    
    access_token_expires = timedelta(minutes=60)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(get_current_user)) -> Any:
    """
    トークンをテストする
    """
    return current_user

@router.post("/register", response_model=schemas.User)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    新規ユーザー登録（オープン登録が許可されている場合）
    """
    # 本番環境では無効化するか、管理者承認プロセスを追加する
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="このメールアドレスは既に登録されています"
        )
    
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role="user",  # デフォルトは一般ユーザー
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 監査ログを記録
    audit_log = models.AuditLog(
        user_id=user.id,
        action="register",
        resource_type="user",
        resource_id=user.id,
        details={"method": "self_registration"}
    )
    db.add(audit_log)
    db.commit()
    
    return user
