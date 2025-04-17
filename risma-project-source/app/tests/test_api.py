import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db, Base, engine
from sqlalchemy.orm import Session
from app.models.models import User
import os
import sys

# テスト用のクライアント
client = TestClient(app)

# テスト用のデータベースセットアップ
@pytest.fixture(scope="function")
def test_db():
    # テスト用のデータベースを作成
    Base.metadata.create_all(bind=engine)
    
    # テスト用のデータを追加
    db = next(get_db())
    
    # テスト用ユーザーの作成
    from app.core.security import get_password_hash
    test_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        role="user",
        is_active=True
    )
    db.add(test_user)
    db.commit()
    
    yield db
    
    # テスト後にデータベースをクリーンアップ
    Base.metadata.drop_all(bind=engine)

# 認証済みユーザーのトークンを生成
@pytest.fixture
def token():
    return create_access_token({"sub": "test@example.com"})

# 認証ヘッダー
@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

# テスト: ユーザー認証
def test_login(test_db):
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# テスト: 無効なログイン
def test_invalid_login(test_db):
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

# テスト: ユーザープロファイル取得
def test_get_user_profile(test_db, auth_headers):
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

# テスト: 認証なしでのアクセス拒否
def test_unauthorized_access(test_db):
    response = client.get("/api/users/me")
    assert response.status_code == 401

# テスト: リスト作成
def test_create_list(test_db, auth_headers):
    response = client.post(
        "/api/lists",
        headers=auth_headers,
        json={"name": "Test List", "description": "Test Description"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test List"
    assert response.json()["description"] == "Test Description"

# テスト: リスト取得
def test_get_lists(test_db, auth_headers):
    # まずリストを作成
    client.post(
        "/api/lists",
        headers=auth_headers,
        json={"name": "Test List", "description": "Test Description"}
    )
    
    # リスト一覧を取得
    response = client.get("/api/lists", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Test List"

# テスト: キーワード検索ジョブの作成
def test_create_keyword_search_job(test_db, auth_headers):
    # まずリストを作成
    list_response = client.post(
        "/api/lists",
        headers=auth_headers,
        json={"name": "Search List", "description": "For search testing"}
    )
    list_id = list_response.json()["id"]
    
    # 検索ジョブを作成
    response = client.post(
        f"/api/search/keyword?list_id={list_id}",
        headers=auth_headers,
        json={
            "keywords": ["test", "example"],
            "exclude_keywords": [],
            "max_results": 100
        }
    )
    assert response.status_code == 201
    assert response.json()["job_type"] == "keyword"
    assert response.json()["status"] in ["pending", "processing"]

# テスト: 業種×住所検索ジョブの作成
def test_create_industry_location_search_job(test_db, auth_headers):
    # まずリストを作成
    list_response = client.post(
        "/api/lists",
        headers=auth_headers,
        json={"name": "Industry Location List", "description": "For industry-location testing"}
    )
    list_id = list_response.json()["id"]
    
    # 検索ジョブを作成
    response = client.post(
        f"/api/search/industry-location?list_id={list_id}",
        headers=auth_headers,
        json={
            "industries": ["IT", "情報通信"],
            "prefectures": ["東京都"],
            "cities": ["千代田区"],
            "max_results": 100
        }
    )
    assert response.status_code == 201
    assert response.json()["job_type"] == "industry_location"
    assert response.json()["status"] in ["pending", "processing"]

# テスト: 検索ジョブのステータス取得
def test_get_search_job_status(test_db, auth_headers):
    # まずリストを作成
    list_response = client.post(
        "/api/lists",
        headers=auth_headers,
        json={"name": "Job Status List", "description": "For job status testing"}
    )
    list_id = list_response.json()["id"]
    
    # 検索ジョブを作成
    job_response = client.post(
        f"/api/search/keyword?list_id={list_id}",
        headers=auth_headers,
        json={
            "keywords": ["test"],
            "exclude_keywords": [],
            "max_results": 10
        }
    )
    job_id = job_response.json()["id"]
    
    # ジョブのステータスを取得
    response = client.get(f"/api/search/jobs/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert "status" in response.json()

if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"])
