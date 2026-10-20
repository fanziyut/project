"""岗位明细接口：分页列表、筛选条件、详情。"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_

from extensions import db
from models import Job
from services.cleaning import SALARY_RANGE_ORDER

jobs_bp = Blueprint('jobs', __name__)


def _top_values(column, limit=30):
    """取出某列出现次数最多的取值，用于筛选下拉框。"""
    count = func.count(Job.id)
    rows = db.session.query(column, count) \
        .filter(column != '') \
        .group_by(column).order_by(count.desc()).limit(limit).all()
    return [value for value, _ in rows]


@jobs_bp.get('/filters')
def filters():
    """返回可用的筛选条件。"""
    return jsonify({
        'cities': _top_values(Job.city, 40),
        'industries': _top_values(Job.industry_clean, 40),
        'companyTypes': _top_values(Job.company_type_clean, 20),
        'companySizes': _top_values(Job.company_size_clean, 20),
        'salaryRanges': SALARY_RANGE_ORDER,
    })


@jobs_bp.get('')
@jobs_bp.get('/')
def list_jobs():
    """分页查询岗位列表，支持多条件筛选与排序。"""
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 20, type=int), 1), 100)

    query = Job.query

    city = request.args.get('city')
    industry = request.args.get('industry')
    company_type = request.args.get('company_type')
    company_size = request.args.get('company_size')
    salary_range = request.args.get('salary_range')
    keyword = request.args.get('keyword')

    if city:
        query = query.filter(Job.city == city)
    if industry:
        query = query.filter(Job.industry_clean == industry)
    if company_type:
        query = query.filter(Job.company_type_clean == company_type)
    if company_size:
        query = query.filter(Job.company_size_clean == company_size)
    if salary_range:
        query = query.filter(Job.salary_range == salary_range)
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(or_(Job.title.like(like), Job.company.like(like)))

    sort = request.args.get('sort', 'default')
    if sort == 'salary_desc':
        query = query.order_by(Job.salary_avg.is_(None), Job.salary_avg.desc())
    elif sort == 'salary_asc':
        query = query.order_by(Job.salary_avg.is_(None), Job.salary_avg.asc())
    else:
        query = query.order_by(Job.id.asc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'total': pagination.total,
        'page': pagination.page,
        'pageSize': pagination.per_page,
        'pages': pagination.pages,
        'items': [job.to_dict() for job in pagination.items],
    })


@jobs_bp.get('/<int:job_id>')
def job_detail(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({'message': '岗位不存在'}), 404
    return jsonify(job.to_dict(detail=True))
