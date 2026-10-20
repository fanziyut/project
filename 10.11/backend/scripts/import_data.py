"""将 111.csv 全量导入 SQLite 数据库。

用法（在 backend 目录下执行）：
    python scripts/import_data.py
"""
import os
import sys

# 让脚本能导入 backend 根目录下的模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import func

from app import create_app
from config import Config
from extensions import db
from models import Job
from services.cleaning import (classify_salary, clean_industry, clean_list_str,
                               extract_city, parse_salary)

BATCH_SIZE = 2000

COLUMNS = {
    '岗位名称': 'title',
    '公司名称': 'company',
    '城市': 'city',
    '薪资': 'salary',
    '发布日期': 'publish_date',
    '详情': 'detail',
    '公司类型': 'company_type',
    '公司规模': 'company_size',
    '行业': 'industry',
    '岗位描述': 'description',
}


def _text(value):
    """统一把空值/NaN 转成 None。"""
    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    text = str(value).strip()
    return text or None


def build_records(df):
    """把原始 DataFrame 转换成可直接入库的行记录。"""
    records = []
    for row in df.itertuples(index=False):
        salary_min, salary_max = parse_salary(row.salary)
        salary_avg = (salary_min + salary_max) / 2 \
            if salary_min is not None and salary_max is not None else None

        records.append({
            'title': _text(row.title) or '未知岗位',
            'company': _text(row.company),
            'city': extract_city(row.city),
            'city_raw': _text(row.city),
            'salary': _text(row.salary),
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_avg': salary_avg,
            'salary_range': classify_salary(salary_avg),
            'publish_date': _text(row.publish_date),
            'detail': _text(row.detail),
            'company_type': _text(row.company_type),
            'company_type_clean': clean_list_str(row.company_type),
            'company_size': _text(row.company_size),
            'company_size_clean': clean_list_str(row.company_size),
            'industry': _text(row.industry),
            'industry_clean': clean_industry(row.industry),
            'description': _text(row.description),
        })
    return records


def main():
    csv_path = Config.CSV_PATH
    if not os.path.exists(csv_path):
        raise SystemExit(f'找不到数据文件: {csv_path}')

    print(f'[1/3] 读取 CSV: {csv_path}')
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    df = df.rename(columns=COLUMNS)
    print(f'      原始数据形状: {df.shape}')

    print('[2/3] 清洗并构造入库记录 ...')
    records = build_records(df)

    app = create_app()
    with app.app_context():
        print('[3/3] 写入数据库 ...')
        db.drop_all()
        db.create_all()
        for start in range(0, len(records), BATCH_SIZE):
            db.session.execute(Job.__table__.insert(), records[start:start + BATCH_SIZE])
            db.session.commit()

        total = db.session.query(func.count(Job.id)).scalar()
        valid_salary = db.session.query(func.count(Job.id)) \
            .filter(Job.salary_avg.isnot(None)).scalar()
        cities = db.session.query(func.count(func.distinct(Job.city))).scalar()

    print(f'导入完成: 共 {total} 条岗位, {valid_salary} 条含薪资, {cities} 个城市')
    print(f'数据库文件: {Config.SQLALCHEMY_DATABASE_URI}')


if __name__ == '__main__':
    main()
