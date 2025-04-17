from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, lists, search
from app.db.database import Base, engine

# データベーステーブルの作成
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="リスマ (LisMa)",
    description="見込み客創出アプリ - BtoB営業支援のためのリスト作成・管理システム",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの設定
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])
api_router.include_router(lists.router, prefix="/lists", tags=["リスト"])
api_router.include_router(search.router, prefix="/search", tags=["検索"])

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "リスマ (LisMa) API",
        "version": "0.1.0",
        "status": "開発中"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
