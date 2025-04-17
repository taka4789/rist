from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.api.auth import get_current_user
from app.services.data_processor import DataProcessor

router = APIRouter()
data_processor = DataProcessor()

@router.post("/", response_model=schemas.List)
def create_list(
    list_in: schemas.ListCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    新しいリストを作成する
    """
    list_obj = models.List(
        title=list_in.title,
        description=list_in.description,
        search_params=list_in.search_params,
        owner_id=current_user.id
    )
    db.add(list_obj)
    db.commit()
    db.refresh(list_obj)
    return list_obj

@router.get("/", response_model=List[schemas.List])
def read_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    ユーザーのリスト一覧を取得する
    """
    if current_user.is_superuser:
        lists = db.query(models.List).offset(skip).limit(limit).all()
    else:
        lists = db.query(models.List).filter(models.List.owner_id == current_user.id).offset(skip).limit(limit).all()
    return lists

@router.get("/{list_id}", response_model=schemas.List)
def read_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    特定のリストを取得する
    """
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")
    return list_obj

@router.put("/{list_id}", response_model=schemas.List)
def update_list(
    list_id: int,
    list_in: schemas.ListUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    リストを更新する
    """
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")
    
    update_data = list_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(list_obj, field, value)
    
    db.add(list_obj)
    db.commit()
    db.refresh(list_obj)
    return list_obj

@router.delete("/{list_id}", response_model=schemas.List)
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    リストを削除する
    """
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")
    
    db.delete(list_obj)
    db.commit()
    return list_obj

@router.get("/{list_id}/companies", response_model=List[schemas.Company])
def read_list_companies(
    list_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    リストに含まれる企業一覧を取得する
    """
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")
    
    companies = db.query(models.Company).filter(models.Company.list_id == list_id).offset(skip).limit(limit).all()
    return companies

@router.post("/{list_id}/export", response_model=dict)
def export_list(
    list_id: int,
    export_format: schemas.ExportFormat,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    リストをエクスポートする
    """
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")
    
    companies = db.query(models.Company).filter(models.Company.list_id == list_id).all()
    company_data = [company.__dict__ for company in companies]
    
    # SQLAlchemyの内部属性を削除
    for company in company_data:
        if "_sa_instance_state" in company:
            del company["_sa_instance_state"]
    
    # CSVエクスポート
    if export_format.format == "csv":
        file_path = f"/tmp/list_{list_id}.csv"
        data_processor.export_to_csv(
            company_data, 
            file_path, 
            include_fields=export_format.include_fields,
            exclude_fields=export_format.exclude_fields
        )
        return {"file_path": file_path, "format": "csv", "count": len(companies)}
    
    # その他のフォーマット（将来の拡張用）
    return {"data": company_data, "format": export_format.format, "count": len(companies)}
