"""统计类接口：为前端图表提供聚合数据。"""
from flask import Blueprint, jsonify, request

from services import analysis

stats_bp = Blueprint('stats', __name__)


@stats_bp.get('/dashboard')
def dashboard():
    """一次性返回仪表盘全部数据。"""
    return jsonify(analysis.dashboard())


@stats_bp.get('/overview')
def overview():
    return jsonify(analysis.overview())


@stats_bp.get('/city-count')
def city_count():
    return jsonify(analysis.city_count(request.args.get('limit', 15, type=int)))


@stats_bp.get('/industry-count')
def industry_count():
    return jsonify(analysis.industry_count(request.args.get('limit', 15, type=int)))


@stats_bp.get('/salary-range')
def salary_range_count():
    return jsonify(analysis.salary_range_count())


@stats_bp.get('/city-salary-avg')
def city_salary_avg():
    return jsonify(analysis.city_salary_avg(request.args.get('limit', 15, type=int)))


@stats_bp.get('/company-size')
def company_size_count():
    return jsonify(analysis.company_size_count(request.args.get('limit', 10, type=int)))


@stats_bp.get('/company-type')
def company_type_count():
    return jsonify(analysis.company_type_count(request.args.get('limit', 10, type=int)))


@stats_bp.get('/keyword')
def keyword_count():
    return jsonify(analysis.keyword_count(request.args.get('limit', 15, type=int)))


@stats_bp.get('/title-word')
def title_word_count():
    return jsonify(analysis.title_word_count(request.args.get('limit', 20, type=int)))


@stats_bp.get('/city-salary-range')
def city_salary_range():
    return jsonify(analysis.city_salary_range(request.args.get('top', 8, type=int)))


@stats_bp.get('/city-high-salary')
def city_high_salary():
    return jsonify(analysis.city_high_salary(request.args.get('limit', 10, type=int)))
