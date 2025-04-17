from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.api.auth import get_current_user, get_current_active_superuser
from app.core.security import get_password_hash, verify_password

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    ユーザー一覧を取得する（管理者のみ）
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=schemas.User)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    新しいユーザーを作成する（管理者のみ）
    """
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
        role=user_in.role,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 監査ログを記録
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="create",
        resource_type="user",
        resource_id=user.id,
        details={"created_by": current_user.id}
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    現在のユーザー情報を取得する
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    現在のユーザー情報を更新する
    """
    if user_in.email and user_in.email != current_user.email:
        user = db.query(models.User).filter(models.User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="このメールアドレスは既に登録されています"
            )
    
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # 監査ログを記録
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="update",
        resource_type="user",
        resource_id=current_user.id,
        details={"self_update": True}
    )
    db.add(audit_log)
    db.commit()
    
    return current_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    特定のユーザー情報を取得する（管理者のみ）
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="ユーザーが見つかりません"
        )
    return user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    特定のユーザー情報を更新する（管理者のみ）
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="ユーザーが見つかりません"
        )
    
    if user_in.email and user_in.email != user.email:
        existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="このメールアドレスは既に登録されています"
            )
    
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 監査ログを記録
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="update",
        resource_type="user",
        resource_id=user.id,
        details={"updated_by": current_user.id}
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    特定のユーザーを削除する（管理者のみ）
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="ユーザーが見つかりません"
        )
    
    # 自分自身は削除できない
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="自分自身を削除することはできません"
        )
    
    # 監査ログを記録
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="delete",
        resource_type="user",
        resource_id=user.id,
        details={"deleted_by": current_user.id}
    )
    db.add(audit_log)
    
    db.delete(user)
    db.commit()
    
    return user
