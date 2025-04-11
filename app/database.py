from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost/mydb")

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)


# 创建数据库表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 获取数据库会话
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
