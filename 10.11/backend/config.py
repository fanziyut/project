"""项目配置：数据库地址、CSV 数据源路径等。"""
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')


class Config:
    # 默认使用 SQLite 单文件数据库，可用环境变量 DATABASE_URL 覆盖（例如切换到 MySQL）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_DIR, 'recruitment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    JSON_AS_ASCII = False

    # 登录会话配置，生产环境请通过环境变量 SECRET_KEY 覆盖
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'recruitment-dev-secret-key'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 原始招聘数据 CSV
    CSV_PATH = os.environ.get('CSV_PATH') or os.path.join(PROJECT_DIR, '111.csv')
