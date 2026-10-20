"""统计分析服务：所有图表数据都通过 SQL 聚合直接从数据库计算得到。"""
from collections import Counter

from sqlalchemy import case, func

from extensions import db
from models import Job
from services.cleaning import (EXCLUDE_CITIES, KEYWORDS, SALARY_RANGE_ORDER,
                               extract_title_words)


def _valid_city_query():
    """过滤掉 '异地招聘'/'未知'/空城市。"""
    return db.session.query(Job).filter(Job.city.notin_(EXCLUDE_CITIES), Job.city != '')


def overview():
    """顶部概览指标。"""
    total_jobs = db.session.query(func.count(Job.id)).scalar() or 0
    valid_salary_count = db.session.query(func.count(Job.id)) \
        .filter(Job.salary_avg.isnot(None)).scalar() or 0
    city_count_total = db.session.query(func.count(func.distinct(Job.city))) \
        .filter(Job.city.notin_(EXCLUDE_CITIES), Job.city != '').scalar() or 0
    industry_count_total = db.session.query(func.count(func.distinct(Job.industry_clean))) \
        .filter(Job.industry_clean != '').scalar() or 0
    avg_salary = db.session.query(func.avg(Job.salary_avg)) \
        .filter(Job.salary_avg.isnot(None)).scalar()

    return {
        'totalJobs': int(total_jobs),
        'validSalaryCount': int(valid_salary_count),
        'cityCountTotal': int(city_count_total),
        'industryCountTotal': int(industry_count_total),
        'avgSalary': round(float(avg_salary), 0) if avg_salary else 0,
    }


def city_count(limit=15):
    """招聘岗位城市分布 Top N。"""
    count = func.count(Job.id)
    rows = _valid_city_query().with_entities(Job.city, count) \
        .group_by(Job.city).order_by(count.desc()).limit(limit).all()
    return [{'城市': city, '岗位数量': int(num)} for city, num in rows]


def industry_count(limit=15):
    """行业分布 Top N。"""
    count = func.count(Job.id)
    rows = db.session.query(Job.industry_clean, count) \
        .filter(Job.industry_clean != '') \
        .group_by(Job.industry_clean).order_by(count.desc()).limit(limit).all()
    return [{'行业': name, '岗位数量': int(num)} for name, num in rows]


def salary_range_count():
    """薪资区间分布，按固定顺序返回全部区间（无数据的补 0）。"""
    rows = db.session.query(Job.salary_range, func.count(Job.id)) \
        .group_by(Job.salary_range).all()
    counted = {rng: int(num) for rng, num in rows}
    return [{'薪资区间': rng, '岗位数量': counted.get(rng, 0)} for rng in SALARY_RANGE_ORDER]


def city_salary_avg(limit=15):
    """各城市平均薪资 Top N。"""
    avg = func.avg(Job.salary_avg)
    rows = _valid_city_query().with_entities(Job.city, avg) \
        .filter(Job.salary_avg.isnot(None)) \
        .group_by(Job.city).order_by(avg.desc()).limit(limit).all()
    return [{'城市': city, '平均薪资': round(float(value), 0)} for city, value in rows]


def company_size_count(limit=10):
    """公司规模分布。"""
    count = func.count(Job.id)
    rows = db.session.query(Job.company_size_clean, count) \
        .filter(Job.company_size_clean != '') \
        .group_by(Job.company_size_clean).order_by(count.desc()).limit(limit).all()
    return [{'公司规模': name, '岗位数量': int(num)} for name, num in rows]


def company_type_count(limit=10):
    """公司类型分布。"""
    count = func.count(Job.id)
    rows = db.session.query(Job.company_type_clean, count) \
        .filter(Job.company_type_clean != '') \
        .group_by(Job.company_type_clean).order_by(count.desc()).limit(limit).all()
    return [{'公司类型': name, '岗位数量': int(num)} for name, num in rows]


def keyword_count(limit=15):
    """岗位名称中的行业关键词热度。"""
    result = []
    for keyword in KEYWORDS:
        num = db.session.query(func.count(Job.id)) \
            .filter(Job.title.like(f'%{keyword}%')).scalar() or 0
        if num:
            result.append({'关键词': keyword, '出现次数': int(num)})
    result.sort(key=lambda item: item['出现次数'], reverse=True)
    return result[:limit]


def title_word_count(limit=20):
    """岗位名称词频 Top N。"""
    rows = db.session.query(Job.title, func.count(Job.id)).group_by(Job.title).all()
    counter = Counter()
    for title, num in rows:
        for word in extract_title_words(title):
            counter[word] += int(num)
    return [{'岗位词': word, '出现次数': num} for word, num in counter.most_common(limit)]


def city_salary_range(top_n=8):
    """热门城市 × 薪资区间交叉统计（堆叠柱状图数据）。"""
    top_cities = [item['城市'] for item in city_count(top_n)]
    if not top_cities:
        return {'categories': SALARY_RANGE_ORDER, 'series': []}

    rows = db.session.query(Job.city, Job.salary_range, func.count(Job.id)) \
        .filter(Job.city.in_(top_cities)) \
        .group_by(Job.city, Job.salary_range).all()

    matrix = {city: {} for city in top_cities}
    for city, rng, num in rows:
        matrix[city][rng] = int(num)

    categories = [rng for rng in SALARY_RANGE_ORDER]
    series = [{'name': city, 'data': [matrix[city].get(rng, 0) for rng in categories]}
              for city in top_cities]
    return {'categories': categories, 'series': series}


def city_high_salary(limit=10, threshold=20000):
    """各城市高薪岗位（平均薪资 >= 2万）比例 Top N。"""
    city = Job.city
    total = func.count(Job.id)
    high = func.sum(case((Job.salary_avg >= threshold, 1), else_=0))

    rows = db.session.query(city, high, total) \
        .filter(Job.city.notin_(EXCLUDE_CITIES), Job.city != '', Job.salary_avg.isnot(None)) \
        .group_by(city).all()

    result = []
    for name, high_num, total_num in rows:
        if total_num:
            result.append({'城市': name, '高薪岗位比例': round(float(high_num) / total_num * 100, 1)})
    result.sort(key=lambda item: item['高薪岗位比例'], reverse=True)
    return result[:limit]


def dashboard():
    """一次性返回仪表盘所需的全部数据，减少前端请求次数。"""
    return {
        'overview': overview(),
        'cityCount': city_count(),
        'industryCount': industry_count(),
        'salaryRangeCount': salary_range_count(),
        'citySalaryAvg': city_salary_avg(),
        'companySizeCount': company_size_count(),
        'companyTypeCount': company_type_count(),
        'keywordCount': keyword_count(),
        'titleWordCount': title_word_count(),
        'citySalaryRange': city_salary_range(),
        'cityHighSalary': city_high_salary(),
    }
