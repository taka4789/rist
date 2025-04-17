# リスマ（LisMa）API仕様書

## 概要
このドキュメントでは、リスマ（LisMa）アプリケーションのAPI仕様について説明します。リスマAPIはRESTfulなインターフェースを提供し、JSONフォーマットでデータをやり取りします。

## ベースURL
```
https://api.risma-app.example.com
```

## 認証
APIへのアクセスにはJWTトークンによる認証が必要です。認証トークンは`Authorization`ヘッダーに`Bearer {token}`の形式で指定します。

### 認証エンドポイント

#### ログイン
```
POST /api/auth/login
```

**リクエスト**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**レスポンス**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

#### トークンリフレッシュ
```
POST /api/auth/refresh-token
```

**リクエスト**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**レスポンス**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## ユーザー管理

### ユーザープロファイル取得
```
GET /api/users/me
```

**レスポンス**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "テストユーザー",
  "role": "user",
  "is_active": true,
  "created_at": "2025-04-01T00:00:00Z"
}
```

### ユーザー一覧取得（管理者のみ）
```
GET /api/users
```

**クエリパラメータ**
- `limit`: 取得する最大件数（デフォルト: 100）
- `offset`: スキップする件数（デフォルト: 0）

**レスポンス**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "テストユーザー",
    "role": "user",
    "is_active": true,
    "created_at": "2025-04-01T00:00:00Z"
  },
  ...
]
```

### ユーザー作成（管理者のみ）
```
POST /api/users
```

**リクエスト**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "新規ユーザー",
  "role": "user"
}
```

**レスポンス**
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "full_name": "新規ユーザー",
  "role": "user",
  "is_active": true,
  "created_at": "2025-04-17T10:00:00Z"
}
```

## リスト管理

### リスト一覧取得
```
GET /api/lists
```

**クエリパラメータ**
- `limit`: 取得する最大件数（デフォルト: 100）
- `offset`: スキップする件数（デフォルト: 0）

**レスポンス**
```json
[
  {
    "id": 1,
    "name": "IT企業リスト",
    "description": "東京都内のIT企業リスト",
    "total_records": 150,
    "created_at": "2025-04-15T09:30:00Z",
    "updated_at": "2025-04-15T09:30:00Z"
  },
  ...
]
```

### リスト詳細取得
```
GET /api/lists/{list_id}
```

**レスポンス**
```json
{
  "id": 1,
  "name": "IT企業リスト",
  "description": "東京都内のIT企業リスト",
  "total_records": 150,
  "created_at": "2025-04-15T09:30:00Z",
  "updated_at": "2025-04-15T09:30:00Z",
  "records": [
    {
      "id": 1,
      "company_name": "株式会社テスト",
      "address": "東京都千代田区1-1-1",
      "tel": "03-1234-5678",
      "url": "https://example.com",
      "industry": "IT・情報通信"
    },
    ...
  ]
}
```

### リスト作成
```
POST /api/lists
```

**リクエスト**
```json
{
  "name": "新規リスト",
  "description": "新しく作成するリスト"
}
```

**レスポンス**
```json
{
  "id": 2,
  "name": "新規リスト",
  "description": "新しく作成するリスト",
  "total_records": 0,
  "created_at": "2025-04-17T10:05:00Z",
  "updated_at": "2025-04-17T10:05:00Z"
}
```

### リスト更新
```
PUT /api/lists/{list_id}
```

**リクエスト**
```json
{
  "name": "更新リスト",
  "description": "更新された説明"
}
```

**レスポンス**
```json
{
  "id": 2,
  "name": "更新リスト",
  "description": "更新された説明",
  "total_records": 0,
  "created_at": "2025-04-17T10:05:00Z",
  "updated_at": "2025-04-17T10:10:00Z"
}
```

### リスト削除
```
DELETE /api/lists/{list_id}
```

**レスポンス**
```
204 No Content
```

### リストエクスポート
```
GET /api/lists/{list_id}/export
```

**レスポンス**
CSVファイルがダウンロードされます。

## 検索機能

### キーワード検索
```
POST /api/search/keyword
```

**クエリパラメータ**
- `list_id`: 結果を保存するリストID

**リクエスト**
```json
{
  "keywords": ["IT", "システム開発"],
  "exclude_keywords": ["個人", "フリーランス"],
  "max_results": 1000
}
```

**レスポンス**
```json
{
  "id": 1,
  "job_type": "keyword",
  "status": "processing",
  "created_at": "2025-04-17T10:15:00Z"
}
```

### 業種×住所検索
```
POST /api/search/industry-location
```

**クエリパラメータ**
- `list_id`: 結果を保存するリストID

**リクエスト**
```json
{
  "industries": ["IT・情報通信"],
  "prefectures": ["東京都"],
  "cities": ["千代田区", "新宿区"],
  "max_results": 1000
}
```

**レスポンス**
```json
{
  "id": 2,
  "job_type": "industry_location",
  "status": "processing",
  "created_at": "2025-04-17T10:20:00Z"
}
```

### 検索ジョブ一覧取得
```
GET /api/search/jobs
```

**クエリパラメータ**
- `limit`: 取得する最大件数（デフォルト: 100）
- `offset`: スキップする件数（デフォルト: 0）

**レスポンス**
```json
[
  {
    "id": 1,
    "job_type": "keyword",
    "status": "completed",
    "created_at": "2025-04-17T10:15:00Z",
    "completed_at": "2025-04-17T10:25:00Z",
    "result_count": 150
  },
  {
    "id": 2,
    "job_type": "industry_location",
    "status": "processing",
    "created_at": "2025-04-17T10:20:00Z",
    "completed_at": null,
    "result_count": null
  }
]
```

### 検索ジョブ詳細取得
```
GET /api/search/jobs/{job_id}
```

**レスポンス**
```json
{
  "id": 1,
  "job_type": "keyword",
  "status": "completed",
  "created_at": "2025-04-17T10:15:00Z",
  "completed_at": "2025-04-17T10:25:00Z",
  "result_count": 150,
  "list_id": 1,
  "parameters": {
    "keywords": ["IT", "システム開発"],
    "exclude_keywords": ["個人", "フリーランス"],
    "max_results": 1000
  }
}
```

### 検索ジョブキャンセル
```
POST /api/search/jobs/{job_id}/cancel
```

**レスポンス**
```json
{
  "id": 2,
  "job_type": "industry_location",
  "status": "cancelled",
  "created_at": "2025-04-17T10:20:00Z",
  "completed_at": "2025-04-17T10:22:00Z",
  "result_count": null
}
```

## 監査ログ

### 監査ログ取得（管理者のみ）
```
GET /api/audit/logs
```

**クエリパラメータ**
- `limit`: 取得する最大件数（デフォルト: 100）
- `offset`: スキップする件数（デフォルト: 0）
- `user_id`: ユーザーIDでフィルタリング
- `action`: アクション種別でフィルタリング
- `from_date`: 開始日時
- `to_date`: 終了日時

**レスポンス**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "action": "login",
    "resource_type": "user",
    "resource_id": 1,
    "timestamp": "2025-04-17T09:00:00Z",
    "ip_address": "192.168.1.1",
    "details": {}
  },
  {
    "id": 2,
    "user_id": 1,
    "action": "create",
    "resource_type": "list",
    "resource_id": 1,
    "timestamp": "2025-04-17T09:05:00Z",
    "ip_address": "192.168.1.1",
    "details": {
      "name": "IT企業リスト",
      "description": "東京都内のIT企業リスト"
    }
  }
]
```

## エラーレスポンス

### 認証エラー
```
401 Unauthorized
```
```json
{
  "detail": "認証情報が無効です"
}
```

### 権限エラー
```
403 Forbidden
```
```json
{
  "detail": "このリソースにアクセスする権限がありません"
}
```

### リソース未検出
```
404 Not Found
```
```json
{
  "detail": "指定されたリソースが見つかりません"
}
```

### バリデーションエラー
```
422 Unprocessable Entity
```
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "フィールドは必須です",
      "type": "value_error.missing"
    }
  ]
}
```

### サーバーエラー
```
500 Internal Server Error
```
```json
{
  "detail": "内部サーバーエラーが発生しました"
}
```

## レート制限
APIには1分あたり100リクエストのレート制限があります。制限を超えた場合は429 Too Many Requestsレスポンスが返されます。

```
429 Too Many Requests
```
```json
{
  "detail": "リクエスト数が制限を超えました。しばらく待ってから再試行してください。"
}
```

## バージョン管理
APIのバージョンはURLパスに含まれます。現在のバージョンはv1です。

```
https://api.risma-app.example.com/v1/...
```

将来的なバージョンアップデートの際には、新しいバージョン番号が使用されます。
