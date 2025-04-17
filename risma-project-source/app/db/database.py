from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 開発環境用のSQLite設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./risma.db"

# PostgreSQL設定（本番環境用）
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/risma"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB接続用のDependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
