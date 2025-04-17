# リスマ（LisMa）開発者ドキュメント

## 概要

このドキュメントは、リスマ（LisMa）アプリケーションの開発者向け技術資料です。システムアーキテクチャ、開発環境のセットアップ方法、コードの構成、および拡張方法について説明します。

## 目次

1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [技術スタック](#技術スタック)
3. [開発環境のセットアップ](#開発環境のセットアップ)
4. [プロジェクト構成](#プロジェクト構成)
5. [バックエンド実装](#バックエンド実装)
6. [フロントエンド実装](#フロントエンド実装)
7. [データベース設計](#データベース設計)
8. [認証と認可](#認証と認可)
9. [Webスクレイピング](#webスクレイピング)
10. [データ処理](#データ処理)
11. [テスト](#テスト)
12. [デプロイ](#デプロイ)
13. [拡張ガイド](#拡張ガイド)

## システムアーキテクチャ

リスマは、以下のコンポーネントで構成されています：

1. **バックエンドAPI**: FastAPIを使用したRESTful APIサーバー
2. **フロントエンドUI**: React + Next.jsを使用したシングルページアプリケーション
3. **データベース**: PostgreSQLを使用したリレーショナルデータベース
4. **スクレイピングエンジン**: 非同期処理を活用した高効率Webスクレイピングモジュール
5. **データ処理エンジン**: 企業情報の正規化、重複削除、フィルタリングを行うモジュール

アーキテクチャ図：

```
+-------------------+      +-------------------+      +-------------------+
|                   |      |                   |      |                   |
|  フロントエンドUI   |<---->|   バックエンドAPI   |<---->|    データベース    |
|  (React+Next.js)  |      |    (FastAPI)     |      |   (PostgreSQL)   |
|                   |      |                   |      |                   |
+-------------------+      +-------------------+      +-------------------+
                                    ^
                                    |
                                    v
                           +-------------------+
                           |                   |
                           | スクレイピングエンジン |
                           |                   |
                           +-------------------+
                                    ^
                                    |
                                    v
                           +-------------------+
                           |                   |
                           |  データ処理エンジン  |
                           |                   |
                           +-------------------+
```

## 技術スタック

### バックエンド
- **言語**: Python 3.9+
- **フレームワーク**: FastAPI
- **ORM**: SQLAlchemy
- **認証**: JWT (JSON Web Tokens)
- **非同期処理**: asyncio, aiohttp
- **スクレイピング**: BeautifulSoup4, Puppeteer (via pyppeteer)
- **データ処理**: pandas, numpy

### フロントエンド
- **言語**: TypeScript
- **フレームワーク**: React, Next.js
- **UIライブラリ**: Material-UI
- **状態管理**: React Context API
- **フォーム管理**: Formik, Yup
- **HTTP通信**: Axios

### データベース
- PostgreSQL

### インフラ
- Docker / Kubernetes
- CI/CD: GitHub Actions
- デプロイ: Render

## 開発環境のセットアップ

### 前提条件
- Python 3.9+
- Node.js 14+
- PostgreSQL 12+
- Docker (オプション)

### バックエンドのセットアップ

1. リポジトリをクローン:
```bash
git clone https://github.com/your-organization/risma-project.git
cd risma-project
```

2. 仮想環境を作成し有効化:
```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

4. 環境変数を設定:
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

5. データベースをマイグレーション:
```bash
alembic upgrade head
```

6. バックエンドサーバーを起動:
```bash
uvicorn app.main:app --reload
```

### フロントエンドのセットアップ

1. フロントエンドディレクトリに移動:
```bash
cd frontend
```

2. 依存関係をインストール:
```bash
npm install
```

3. 環境変数を設定:
```bash
cp .env.example .env.local
# .env.localファイルを編集して必要な設定を行う
```

4. 開発サーバーを起動:
```bash
npm run dev
```

### Dockerを使用したセットアップ

1. Dockerコンテナをビルドして起動:
```bash
docker-compose up -d
```

## プロジェクト構成

```
risma-project/
├── app/                    # バックエンドアプリケーション
│   ├── api/                # APIエンドポイント
│   │   ├── auth.py         # 認証関連API
│   │   ├── lists.py        # リスト管理API
│   │   ├── search.py       # 検索API
│   │   └── users.py        # ユーザー管理API
│   ├── core/               # コア機能
│   │   └── security.py     # 認証・認可機能
│   ├── db/                 # データベース関連
│   │   └── database.py     # DB接続設定
│   ├── models/             # データモデル
│   │   └── models.py       # SQLAlchemyモデル
│   ├── schemas/            # Pydanticスキーマ
│   │   └── schemas.py      # リクエスト/レスポンススキーマ
│   ├── services/           # ビジネスロジック
│   │   ├── scraper.py      # スクレイピングエンジン
│   │   └── data_processor.py # データ処理エンジン
│   ├── tests/              # テストコード
│   │   ├── test_api.py     # APIテスト
│   │   ├── test_services.py # サービステスト
│   │   ├── test_e2e.py     # E2Eテスト
│   │   └── test_performance.py # パフォーマンステスト
│   └── main.py             # アプリケーションエントリーポイント
├── frontend/               # フロントエンドアプリケーション
│   ├── public/             # 静的ファイル
│   ├── src/                # ソースコード
│   │   ├── components/     # Reactコンポーネント
│   │   ├── contexts/       # Contextプロバイダー
│   │   ├── hooks/          # カスタムフック
│   │   ├── pages/          # ページコンポーネント
│   │   ├── styles/         # スタイル定義
│   │   └── utils/          # ユーティリティ関数
│   ├── package.json        # npm設定
│   └── tsconfig.json       # TypeScript設定
├── docs/                   # ドキュメント
│   ├── api_specification.md # API仕様書
│   ├── user_manual.md      # ユーザーマニュアル
│   └── developer_docs.md   # 開発者ドキュメント
├── .env.example            # 環境変数サンプル
├── .gitignore              # Gitの除外設定
├── docker-compose.yml      # Docker Compose設定
├── README.md               # プロジェクト概要
├── render.yaml             # Renderデプロイ設定
└── requirements.txt        # Pythonパッケージ依存関係
```

## バックエンド実装

### メインアプリケーション (main.py)

FastAPIアプリケーションのエントリーポイントです。ミドルウェアの設定、ルーターの登録、CORSの設定などを行います。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, lists, search
from app.core.config import settings

app = FastAPI(
    title="リスマ API",
    description="BtoB営業支援のためのリスト作成アプリAPI",
    version="1.0.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(auth.router, prefix="/api/auth", tags=["認証"])
app.include_router(users.router, prefix="/api/users", tags=["ユーザー"])
app.include_router(lists.router, prefix="/api/lists", tags=["リスト"])
app.include_router(search.router, prefix="/api/search", tags=["検索"])

@app.get("/api/health", tags=["ヘルスチェック"])
async def health_check():
    return {"status": "ok"}
```

### データベース接続 (database.py)

SQLAlchemyを使用したデータベース接続の設定を行います。

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### モデル定義 (models.py)

SQLAlchemyを使用したデータベースモデルの定義を行います。

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lists = relationship("List", back_populates="owner")
    search_jobs = relationship("SearchJob", back_populates="user")

class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="lists")
    records = relationship("ListRecord", back_populates="list")
    search_jobs = relationship("SearchJob", back_populates="list")

class ListRecord(Base):
    __tablename__ = "list_records"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"))
    company_name = Column(String)
    address = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    url = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    list = relationship("List", back_populates="records")

class SearchJob(Base):
    __tablename__ = "search_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    list_id = Column(Integer, ForeignKey("lists.id"))
    job_type = Column(String)  # "keyword" or "industry_location"
    parameters = Column(JSON)
    status = Column(String)  # "pending", "processing", "completed", "failed", "cancelled"
    result_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="search_jobs")
    list = relationship("List", back_populates="search_jobs")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
    details = Column(JSON, nullable=True)

    user = relationship("User")
```

## フロントエンド実装

### APIクライアント (api.ts)

バックエンドAPIとの通信を行うクライアントモジュールです。

```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// レスポンスインターセプター
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 認証エラーの場合、リフレッシュトークンを使用して再認証
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('リフレッシュトークンがありません');
        }
        
        const response = await axios.post(`${API_URL}/api/auth/refresh-token`, {
          refresh_token: refreshToken,
        });
        
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (error) {
        // 再認証に失敗した場合はログアウト
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 認証コンテキスト (AuthContext.tsx)

ユーザー認証状態を管理するReactコンテキストです。

```typescript
import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../utils/api';
import { useRouter } from 'next/router';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // ページロード時にユーザー情報を取得
    const fetchUser = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.get('/api/users/me');
        setUser(response.data);
      } catch (error) {
        console.error('ユーザー情報の取得に失敗しました', error);
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await api.post('/api/auth/login', {
        username: email,
        password,
      });

      const { access_token, refresh_token } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);

      const userResponse = await api.get('/api/users/me');
      setUser(userResponse.data);
      router.push('/dashboard');
    } catch (error) {
      console.error('ログインに失敗しました', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

## データベース設計

リスマのデータベースは以下のテーブルで構成されています：

1. **users**: ユーザー情報
2. **lists**: リスト情報
3. **list_records**: リストに含まれる企業情報
4. **search_jobs**: 検索ジョブ情報
5. **audit_logs**: 監査ログ

ER図：

```
+---------------+       +---------------+       +---------------+
|    users      |       |    lists      |       | list_records  |
+---------------+       +---------------+       +---------------+
| id            |<----->| id            |<----->| id            |
| email         |       | name          |       | list_id       |
| hashed_password|      | description   |       | company_name  |
| full_name     |       | owner_id      |       | address       |
| role          |       | created_at    |       | tel           |
| is_active     |       | updated_at    |       | url           |
| created_at    |       +---------------+       | industry      |
+---------------+               ^               | created_at    |
        ^                       |               +---------------+
        |                       |
        |                       |
+---------------+       +---------------+
|  audit_logs   |       |  search_jobs  |
+---------------+       +---------------+
| id            |       | id            |
| user_id       |       | user_id       |
| action        |       | list_id       |
| resource_type |       | job_type      |
| resource_id   |       | parameters    |
| timestamp     |       | status        |
| ip_address    |       | result_count  |
| details       |       | created_at    |
+---------------+       | completed_at  |
                        +---------------+
```

## 認証と認可

リスマでは、JWT（JSON Web Token）を使用した認証システムを実装しています。

### 認証フロー

1. ユーザーがログインフォームからメールアドレスとパスワードを送信
2. バックエンドでパスワードを検証
3. 検証成功時、アクセストークンとリフレッシュトークンを発行
4. フロントエンドでトークンをローカルストレージに保存
5. 以降のAPIリクエストでアクセストークンを使用
6. アクセストークンの有効期限が切れた場合、リフレッシュトークンを使用して新しいアクセストークンを取得

### 認可システム

ユーザーロールに基づいた認可システムを実装しています：

- **user**: 一般ユーザー。自分のリストの作成・編集・削除が可能
- **manager**: マネージャー。チームユーザーの管理とレポート閲覧が可能
- **admin**: 管理者。全ユーザーの管理とシステム設定の変更が可能

## Webスクレイピング

リスマのWebスクレイピングエンジンは、以下の機能を提供します：

1. **キーワード検索**: 指定されたキーワードを使用してGoogle検索を行い、検索結果から企業情報を抽出
2. **業種×住所検索**: 指定された業種と住所の組み合わせで電話帳サイトを検索し、企業情報を抽出

### スクレイピングの実装

スクレイピングエンジンは、非同期処理を活用して効率的にデータを収集します：

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional

class WebScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_page(self, url: str) -> str:
        await self.init_session()
        async with self.session.get(url) as response:
            return await response.text()
    
    def parse_company_info(self, html_content: str) -> Dict:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 企業情報の抽出ロジック
        company_name = soup.select_one(".company-name")
        address = soup.select_one(".company-address")
        tel = soup.select_one(".company-tel")
        url = soup.select_one(".company-url")
        
        return {
            "company_name": company_name.text.strip() if company_name else None,
            "address": address.text.strip() if address else None,
            "tel": tel.text.strip() if tel else None,
            "url": url.get("href") if url else None,
            "industry": self.extract_industry_from_text(html_content)
        }
    
    def extract_industry_from_text(self, text: str) -> Optional[str]:
        # 業種を抽出するロジック
        industry_patterns = [
            r"業種[：:]\s*([^\n,]+)",
            r"事業内容[：:]\s*([^\n,]+)"
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def normalize_company_name(self, name: str) -> str:
        # 会社名の正規化ロジック
        patterns = [
            (r"(株式会社|（株）|㈱|\(株\))(.*)", r"株式会社\2"),
            (r"(.*)(株式会社|（株）|㈱|\(株\))", r"株式会社\1"),
        ]
        
        normalized_name = name
        for pattern, replacement in patterns:
            if re.match(pattern, name):
                normalized_name = re.sub(pattern, replacement, name)
                break
        
        return normalized_name.strip()
    
    async def search_by_keyword(self, keywords: List[str], exclude_keywords: List[str] = None, max_results: int = 100) -> List[Dict]:
        # キーワード検索の実装
        # ...
    
    async def search_by_industry_location(self, industries: List[str], prefectures: List[str], cities: List[str] = None, max_results: int = 100) -> List[Dict]:
        # 業種×住所検索の実装
        # ...
```

## データ処理

データ処理エンジンは、スクレイピングで収集したデータの正規化、重複削除、フィルタリングを行います：

```python
import pandas as pd
import numpy as np
import re
from typing import List, Dict

class DataProcessor:
    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        # 重複削除ロジック
        if data.empty:
            return data
        
        # 電話番号をキーにして重複を削除
        if 'tel' in data.columns:
            data = data.drop_duplicates(subset=['tel'], keep='first')
        
        # 会社名をキーにして重複を削除
        if 'company_name' in data.columns:
            data = data.drop_duplicates(subset=['company_name'], keep='first')
        
        return data
    
    def normalize_phone_numbers(self, data: pd.DataFrame) -> pd.DataFrame:
        # 電話番号の正規化ロジック
        if data.empty or 'tel' not in data.columns:
            return data
        
        # コピーを作成して元のデータを変更しない
        result = data.copy()
        
        # 電話番号の正規化
        def normalize_phone(phone):
            if not phone or pd.isna(phone):
                return None
            
            # 全角を半角に変換
            phone = phone.translate(str.maketrans({
                '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
                '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
                '（': '(', '）': ')', '－': '-', '　': ' '
            }))
            
            # 不要な文字を削除
            phone = re.sub(r'[^\d\-()]', '', phone)
            
            # 形式を統一 (XX-XXXX-XXXX)
            phone = re.sub(r'^\(?(\d{2,4})\)?[^\d]*(\d{2,4})[^\d]*(\d{3,4})$', r'\1-\2-\3', phone)
            
            return phone
        
        result['tel'] = result['tel'].apply(normalize_phone)
        return result
    
    def normalize_addresses(self, data: pd.DataFrame) -> pd.DataFrame:
        # 住所の正規化ロジック
        if data.empty or 'address' not in data.columns:
            return data
        
        # コピーを作成して元のデータを変更しない
        result = data.copy()
        
        # 住所の正規化
        def normalize_address(address):
            if not address or pd.isna(address):
                return None
            
            # 全角を半角に変換（数字のみ）
            address = address.translate(str.maketrans({
                '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
                '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'
            }))
            
            # 都道府県の表記を統一
            prefecture_patterns = [
                (r'東京都?', '東京都'),
                (r'大阪[府県]?', '大阪府'),
                (r'京都[府県]?', '京都府'),
                # 他の都道府県も同様に
            ]
            
            for pattern, replacement in prefecture_patterns:
                address = re.sub(pattern, replacement, address)
            
            return address
        
        result['address'] = result['address'].apply(normalize_address)
        return result
    
    def filter_by_industry(self, data: pd.DataFrame, industries: List[str]) -> pd.DataFrame:
        # 業種でフィルタリング
        if data.empty or 'industry' not in data.columns or not industries:
            return data
        
        # 業種名のパターンマッチング
        pattern = '|'.join(industries)
        mask = data['industry'].str.contains(pattern, na=False, regex=True)
        return data[mask]
    
    def filter_by_location(self, data: pd.DataFrame, prefecture: str = None, city: str = None) -> pd.DataFrame:
        # 地域でフィルタリング
        if data.empty or 'address' not in data.columns:
            return data
        
        result = data.copy()
        
        if prefecture:
            mask = result['address'].str.contains(prefecture, na=False)
            result = result[mask]
        
        if city:
            mask = result['address'].str.contains(city, na=False)
            result = result[mask]
        
        return result
    
    def process_data(self, data: List[Dict], remove_duplicates: bool = True) -> pd.DataFrame:
        # データ処理のメイン関数
        if not data:
            return pd.DataFrame()
        
        # リストをDataFrameに変換
        df = pd.DataFrame(data)
        
        # 電話番号の正規化
        df = self.normalize_phone_numbers(df)
        
        # 住所の正規化
        df = self.normalize_addresses(df)
        
        # 重複削除
        if remove_duplicates:
            df = self.remove_duplicates(df)
        
        return df
```

## テスト

リスマでは、以下の種類のテストを実装しています：

1. **ユニットテスト**: 個々のコンポーネントの機能をテスト
2. **統合テスト**: 複数のコンポーネントの連携をテスト
3. **エンドツーエンドテスト**: ユーザーの視点からシステム全体の動作をテスト
4. **パフォーマンステスト**: システムの性能と負荷耐性をテスト

### テストの実行方法

```bash
# ユニットテストの実行
pytest app/tests/test_api.py app/tests/test_services.py

# 統合テストの実行
pytest app/tests/test_e2e.py

# パフォーマンステストの実行
pytest app/tests/test_performance.py
```

## デプロイ

リスマは、Renderを使用してデプロイします。

### Renderデプロイ設定 (render.yaml)

```yaml
services:
  # バックエンドAPI
  - type: web
    name: risma-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: risma-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: 30
      - key: REFRESH_TOKEN_EXPIRE_DAYS
        value: 7
      - key: CORS_ORIGINS
        value: https://risma-app.onrender.com

  # フロントエンド
  - type: web
    name: risma-frontend
    env: node
    buildCommand: cd frontend && npm install && npm run build
    startCommand: cd frontend && npm start
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: https://risma-api.onrender.com

databases:
  - name: risma-db
    databaseName: risma
    user: risma
```

### 本番環境へのデプロイ手順

1. GitHubリポジトリにコードをプッシュ
2. Renderダッシュボードで新しいサービスを作成
3. GitHubリポジトリを連携
4. `render.yaml`を使用して設定を適用
5. デプロイを実行

## 拡張ガイド

### 新しい検索ソースの追加

新しい検索ソースを追加するには、以下の手順を実行します：

1. `app/services/scraper.py`に新しいスクレイピングメソッドを追加
2. `app/api/search.py`に新しいエンドポイントを追加
3. フロントエンドに新しい検索フォームを追加

### 新しいデータ処理機能の追加

新しいデータ処理機能を追加するには、以下の手順を実行します：

1. `app/services/data_processor.py`に新しい処理メソッドを追加
2. 必要に応じて`app/api/lists.py`にエンドポイントを追加
3. フロントエンドに新しい機能のUIを追加

### 認証プロバイダーの追加

新しい認証プロバイダー（Google、GitHub、Microsoftなど）を追加するには、以下の手順を実行します：

1. `app/core/security.py`に新しい認証ロジックを追加
2. `app/api/auth.py`に新しいエンドポイントを追加
3. フロントエンドのログインページに新しいプロバイダーのボタンを追加

### 多言語対応

多言語対応を追加するには、以下の手順を実行します：

1. バックエンドのレスポンスメッセージを多言語化
2. フロントエンドに言語切り替え機能を追加
3. 翻訳ファイルを作成し、言語ごとのテキストを定義
