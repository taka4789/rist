from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any, List, Optional
import datetime

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.api.auth import get_current_user, get_current_active_superuser

router = APIRouter()

@router.get("/", response_model=List[schemas.AuditLog])
def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    監査ログ一覧を取得する（管理者のみ）
    """
    query = db.query(models.AuditLog)
    
    # フィルタリング
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    if action:
        query = query.filter(models.AuditLog.action == action)
    if resource_type:
        query = query.filter(models.AuditLog.resource_type == resource_type)
    if start_date:
        query = query.filter(models.AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(models.AuditLog.created_at <= end_date)
    
    # ソートと制限
    query = query.order_by(models.AuditLog.created_at.desc()).offset(skip).limit(limit)
    
    return query.all()

@router.post("/", response_model=schemas.AuditLog)
def create_audit_log(
    log_in: schemas.AuditLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    監査ログを作成する
    """
    # IPアドレスを取得
    client_ip = request.client.host if request.client else None
    
    # 監査ログを作成
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action=log_in.action,
        resource_type=log_in.resource_type,
        resource_id=log_in.resource_id,
        details=log_in.details,
        ip_address=client_ip
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

@router.get("/{log_id}", response_model=schemas.AuditLog)
def read_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """
    特定の監査ログを取得する（管理者のみ）
    """
    log = db.query(models.AuditLog).filter(models.AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=404,
            detail="監査ログが見つかりません"
        )
    return log
