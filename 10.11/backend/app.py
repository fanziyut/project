"""Flask 应用工厂：注册数据库、跨域与各业务蓝图。"""
import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config, DATA_DIR
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # 保证中文直接返回而不是 \uXXXX

    os.makedirs(DATA_DIR, exist_ok=True)
    db.init_app(app)

    # 蓝图在函数内导入，确保模型在应用初始化时完成注册
    from routes.jobs import jobs_bp
    from routes.stats import stats_bp
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    CORS(app, resources={r'/api/*': {'origins': '*'}})

    @app.get('/')
    def index():
        """访问后端根路径时返回提示,引导到真正的前端页面。"""
        return (
            '<!doctype html><meta charset="utf-8"><title>招聘数据分析平台 · 后端</title>'
            '<style>'
            'body{font-family:"PingFang SC","Microsoft YaHei",sans-serif;background:#f0f2f5;display:flex;'
            'align-items:center;justify-content:center;min-height:100vh;margin:0;color:#333}'
            '.card{background:#fff;padding:40px 48px;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.08);'
            'max-width:480px;text-align:center}'
            'h1{font-size:20px;margin:0 0 12px;color:#667eea}'
            'p{font-size:14px;line-height:1.8;color:#555;margin:0 0 18px}'
            'a.btn{display:inline-block;padding:10px 26px;border-radius:6px;background:#667eea;color:#fff;'
            'text-decoration:none;font-size:14px}'
            'code{background:#f4f5f9;padding:2px 6px;border-radius:4px;color:#c7254e}'
            '.sub{font-size:12px;color:#999;margin-top:20px}'
            '</style>'
            '<div class="card">'
            '<h1>招聘数据分析可视化平台 · 后端服务</h1>'
            '<p>你正在访问 Flask 后端 API 服务。<br>'
            '真正的可视化页面在 <code>http://localhost:5173</code></p>'
            '<a class="btn" href="http://localhost:5173">打开前端页面</a>'
            '<p class="sub">API 健康检查: <a href="/api/health">/api/health</a></p>'
            '</div>',
            200, {'Content-Type': 'text/html; charset=utf-8'}
        )

    @app.get('/api')
    def api_index():
        """API 清单。"""
        return jsonify({
            'service': 'recruitment-analysis-backend',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'dashboard': '/api/stats/dashboard',
                'stats': ['/api/stats/city-count', '/api/stats/industry-count',
                          '/api/stats/salary-range', '/api/stats/city-salary-avg',
                          '/api/stats/company-size', '/api/stats/company-type',
                          '/api/stats/keyword', '/api/stats/title-word',
                          '/api/stats/city-salary-range', '/api/stats/city-high-salary'],
                'jobs': ['/api/jobs?page=1&page_size=20', '/api/jobs/filters', '/api/jobs/<id>'],
            },
            'frontend': 'http://localhost:5173',
        })

    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({'message': '接口不存在'}), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return jsonify({'message': '服务器内部错误'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
