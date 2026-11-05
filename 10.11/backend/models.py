"""数据模型：招聘岗位明细表、登录用户表。"""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class Job(db.Model):
    """招聘岗位明细，一行对应 CSV 中的一条招聘信息。"""

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 原始字段
    title = db.Column(db.String(300), nullable=False, index=True)   # 岗位名称
    company = db.Column(db.String(300), index=True)                 # 公司名称
    city = db.Column(db.String(100), index=True)                    # 城市（已清洗，如 广州）
    salary = db.Column(db.String(100))                              # 薪资原文，如 5-8千/月
    publish_date = db.Column(db.String(50))                         # 发布日期
    detail = db.Column(db.Text)                                     # 详情
    company_type = db.Column(db.String(300))                        # 公司类型原文
    company_size = db.Column(db.String(300))                        # 公司规模原文
    industry = db.Column(db.String(500))                            # 行业原文
    description = db.Column(db.Text)                                # 岗位描述
    city_raw = db.Column(db.String(100))                            # 城市原文

    # 派生字段
    salary_min = db.Column(db.Float)                                # 最低薪资（元）
    salary_max = db.Column(db.Float)                                # 最高薪资（元）
    salary_avg = db.Column(db.Float, index=True)                    # 平均薪资（元）
    salary_range = db.Column(db.String(50), index=True)              # 薪资区间
    company_type_clean = db.Column(db.String(100), index=True)      # 公司类型清洗值
    company_size_clean = db.Column(db.String(50), index=True)       # 公司规模清洗值
    industry_clean = db.Column(db.String(200), index=True)          # 行业清洗值

    def to_dict(self, detail=False):
        data = {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'city': self.city,
            'salary': self.salary,
            'salaryMin': self.salary_min,
            'salaryMax': self.salary_max,
            'salaryAvg': self.salary_avg,
            'salaryRange': self.salary_range,
            'publishDate': self.publish_date,
            'companyType': self.company_type_clean,
            'companySize': self.company_size_clean,
            'industry': self.industry_clean,
        }
        if detail:
            data['detail'] = self.detail
            data['description'] = self.description
            data['cityRaw'] = self.city_raw
            data['companyTypeRaw'] = self.company_type
            data['companySizeRaw'] = self.company_size
            data['industryRaw'] = self.industry
        return data


class User(db.Model):
    """登录用户。"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'displayName': self.display_name or self.username,
        }
