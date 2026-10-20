"""数据清洗与解析：把 CSV 原始字段派生为结构化字段。

原先 111.py 里的清洗逻辑被抽到这里，供导入脚本与统计接口共用。
"""
import re

# 城市统计时需要排除的无效值
EXCLUDE_CITIES = ('异地招聘', '未知')

# 薪资区间的固定展示顺序
SALARY_RANGE_ORDER = ['5千以下', '5-8千', '8千-1.2万', '1.2-2万', '2-3万', '3万以上', '未知']

# 岗位关键词词表
KEYWORDS = ['数据', '分析', '算法', '产品', '运营', '开发', '设计', '市场', '销售', '管理',
            '财务', '人事', '客服', '测试', '前端', '后端', '全栈', '大数据', '人工智能', '机器学习']

# 岗位名称分词时需要忽略的通用后缀
TITLE_STOPWORDS = {'专员', '助理', '主管', '经理', '总监', '工程师', '分析师', '专家', '人才', '招聘'}

_SALARY_RANGE_RE = re.compile(r'([\d.]+)\s*[-~]\s*([\d.]+)\s*(万|千)/月')
_SALARY_SINGLE_RE = re.compile(r'([\d.]+)\s*(万|千)/月')
_CITY_RE = re.compile(r'([\u4e00-\u9fa5]+)')
_TITLE_WORD_RE = re.compile(r'[\u4e00-\u9fa5]{2,}')


def _is_blank(value):
    """判断空值：None / 空串 / NaN。"""
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return str(value).strip() == ''


def parse_salary(salary_str):
    """解析薪资字符串，返回 (最低薪资, 最高薪资)，无法解析时返回 (None, None)。"""
    if _is_blank(salary_str):
        return None, None
    text = str(salary_str).strip()

    match = _SALARY_RANGE_RE.match(text)
    if match:
        factor = 10000 if match.group(3) == '万' else 1000
        return float(match.group(1)) * factor, float(match.group(2)) * factor

    match = _SALARY_SINGLE_RE.match(text)
    if match:
        factor = 10000 if match.group(2) == '万' else 1000
        value = float(match.group(1)) * factor
        return value, value

    return None, None


def classify_salary(avg):
    """按平均薪资划分薪资区间。"""
    if avg is None or avg != avg:  # None 或 NaN
        return '未知'
    if avg < 5000:
        return '5千以下'
    if avg < 8000:
        return '5-8千'
    if avg < 12000:
        return '8千-1.2万'
    if avg < 20000:
        return '1.2-2万'
    if avg < 30000:
        return '2-3万'
    return '3万以上'


def extract_city(city_str):
    """从 '广州-天河区' 这类文本中提取城市名。"""
    if _is_blank(city_str):
        return '未知'
    text = str(city_str).strip()
    match = re.match(r'([\u4e00-\u9fa5]+)-', text)
    if match:
        return match.group(1)
    match = _CITY_RE.match(text)
    if match:
        return match.group(1)
    return text


def clean_list_str(value):
    """去除列表字符串的方括号与引号，例如 "['民营公司']" -> "民营公司"。"""
    if _is_blank(value):
        return ''
    text = str(value).strip()
    if text.startswith('[') and text.endswith(']'):
        text = text[1:-1]
    return text.strip().strip("'\"").strip()


def clean_industry(value):
    """行业字段可能包含多个值，取第一个。"""
    text = clean_list_str(value)
    if ',' in text:
        text = text.split(',')[0]
    return text.strip()


def extract_title_words(title):
    """提取岗位名称中的中文词，用于词频统计。"""
    if _is_blank(title):
        return []
    return [w for w in _TITLE_WORD_RE.findall(str(title)) if w not in TITLE_STOPWORDS]
