from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, List
import asyncio
import datetime  # ← 修正ポイント！

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.api.auth import get_current_user
from app.services.scraper import WebScraper
from app.services.data_processor import DataProcessor

router = APIRouter()
scraper = WebScraper()
data_processor = DataProcessor()

@router.post("/keyword", response_model=schemas.SearchJob)
async def create_keyword_search(
    search_params: schemas.KeywordSearchParams,
    list_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")

    search_job = models.SearchJob(
        list_id=list_id,
        user_id=current_user.id,
        job_type="keyword",
        params={
            "keywords": search_params.keywords,
            "exclude_keywords": search_params.exclude_keywords,
            "max_results": search_params.max_results
        },
        status="pending"
    )
    db.add(search_job)
    db.commit()
    db.refresh(search_job)

    background_tasks.add_task(
        process_keyword_search,
        search_job.id,
        search_params.keywords,
        search_params.exclude_keywords,
        search_params.max_results,
        list_id,
        db
    )

    return search_job

@router.post("/industry-location", response_model=schemas.SearchJob)
async def create_industry_location_search(
    search_params: schemas.IndustryLocationSearchParams,
    list_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="リストが見つかりません")
    if list_obj.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")

    search_job = models.SearchJob(
        list_id=list_id,
        user_id=current_user.id,
        job_type="industry_location",
        params={
            "industry_codes": search_params.industry_codes,
            "prefectures": search_params.prefectures,
            "cities": search_params.cities,
            "max_results": search_params.max_results
        },
        status="pending"
    )
    db.add(search_job)
    db.commit()
    db.refresh(search_job)

    background_tasks.add_task(
        process_industry_location_search,
        search_job.id,
        search_params.industry_codes,
        search_params.prefectures,
        search_params.cities,
        search_params.max_results,
        list_id,
        db
    )

    return search_job

@router.get("/jobs", response_model=List[schemas.SearchJob])
def read_search_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    if current_user.is_superuser:
        jobs = db.query(models.SearchJob).offset(skip).limit(limit).all()
    else:
        jobs = db.query(models.SearchJob).filter(models.SearchJob.user_id == current_user.id).offset(skip).limit(limit).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=schemas.SearchJob)
def read_search_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    job = db.query(models.SearchJob).filter(models.SearchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="検索ジョブが見つかりません")
    if job.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="権限がありません")
    return job

async def process_keyword_search(
    job_id: int,
    keywords: List[str],
    exclude_keywords: List[str] = None,
    max_results: int = 1000,
    list_id: int = None,
    db: Session = None
) -> None:
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()

    try:
        job = db.query(models.SearchJob).filter(models.SearchJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        db.add(job)
        db.commit()

        try:
            results = await scraper.search_by_keyword(keywords, max_results)

            if exclude_keywords:
                results = [
                    r for r in results
                    if not any(
                        k.lower() in r.get("name", "").lower() or k.lower() in r.get("description", "").lower()
                        for k in exclude_keywords
                    )
                ]

            normalized = data_processor.normalize_company_data(results)
            unique = data_processor.remove_duplicates(normalized)

            for company_data in unique:
                company = models.Company(
                    list_id=list_id,
                    name=company_data.get("name", ""),
                    address=company_data.get("address", ""),
                    phone=company_data.get("phone", ""),
                    email=company_data.get("email", ""),
                    website=company_data.get("website", ""),
                    industry=company_data.get("industry", ""),
                    industry_code=company_data.get("industry_code", ""),
                    prefecture=company_data.get("prefecture", ""),
                    city=company_data.get("city", ""),
                    representative=company_data.get("representative", ""),
                    has_fax=company_data.get("has_fax", False),
                    has_contact_form=company_data.get("has_contact_form", False),
                    source_url=company_data.get("source_url", "")
                )
                db.add(company)

            list_obj = db.query(models.List).filter(models.List.id == list_id).first()
            if list_obj:
                list_obj.total_records = db.query(models.Company).filter(models.Company.list_id == list_id).count()
                db.add(list_obj)

            job.status = "completed"
            job.result_count = len(unique)
            job.completed_at = datetime.datetime.utcnow()  # ← 修正ポイント！
            db.add(job)
            db.commit()

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            db.add(job)
            db.commit()

    finally:
        db.close()

async def process_industry_location_search(
    job_id: int,
    industry_codes: List[str],
    prefectures: List[str] = None,
    cities: List[str] = None,
    max_results: int = 1000,
    list_id: int = None,
    db: Session = None
) -> None:
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()

    try:
        job = db.query(models.SearchJob).filter(models.SearchJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        db.add(job)
        db.commit()

        try:
            results = await scraper.search_by_industry_location(industry_codes, prefectures, cities, max_results)
            normalized = data_processor.normalize_company_data(results)
            filtered = data_processor.filter_by_location(
                data_processor.filter_by_industry(normalized, industry_codes),
                prefectures, cities
            )
            unique = data_processor.remove_duplicates(filtered)

            for company_data in unique:
                company = models.Company(
                    list_id=list_id,
                    name=company_data.get("name", ""),
                    address=company_data.get("address", ""),
                    phone=company_data.get("phone", ""),
                    email=company_data.get("email", ""),
                    website=company_data.get("website", ""),
                    industry=company_data.get("industry", ""),
                    industry_code=company_data.get("industry_code", ""),
                    prefecture=company_data.get("prefecture", ""),
                    city=company_data.get("city", ""),
                    representative=company_data.get("representative", ""),
                    has_fax=company_data.get("has_fax", False),
                    has_contact_form=company_data.get("has_contact_form", False),
                    source_url=company_data.get("source_url", "")
                )
                db.add(company)

            list_obj = db.query(models.List).filter(models.List.id == list_id).first()
            if list_obj:
                list_obj.total_records = db.query(models.Company).filter(models.Company.list_id == list_id).count()
                db.add(list_obj)

            job.status = "completed"
            job.result_count = len(unique)
            job.completed_at = datetime.datetime.utcnow()  # ← 修正ポイント！
            db.add(job)
            db.commit()

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            db.add(job)
            db.commit()

    finally:
        db.close()
