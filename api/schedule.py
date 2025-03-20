from http.server import BaseHTTPRequestHandler
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import os

# 从环境变量获取凭据
USERNAME = os.getenv('JW_USERNAME')
PASSWORD = os.getenv('JW_PASSWORD')

def login(session):
    """登录教务系统"""
    try:
        # 获取登录页面
        login_page_url = "http://jw.glut.edu.cn/academic/affairLogin.do"
        response = session.get(login_page_url)
        if response.status_code != 200:
            return False

        # 解析隐藏参数
        soup = BeautifulSoup(response.text, 'html.parser')
        lt = soup.find('input', {'name': 'lt'})['value']
        execution = soup.find('input', {'name': 'execution'})['value']

        # 提交登录
        login_url = "http://jw.glut.edu.cn/academic/j_acegi_security_check"
        login_data = {
            'j_username': USERNAME,
            'j_password': PASSWORD,
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
            'submit': '登录'
        }
        response = session.post(login_url, data=login_data, allow_redirects=True)
        return "index.do" in response.url  # 验证登录成功
    except:
        return False

def get_schedule(date=None):
    """获取课表数据"""
    session = requests.Session()
    session.verify = False  # 禁用 SSL 验证
    if not login(session):
        return {"error": "登录失败"}

    date = date or datetime.now().strftime("%Y-%m-%d")
    schedule_url = "http://jw.glut.edu.cn/academic/student/schedule/currentTodaySchedule.do"
    response = session.post(schedule_url, data={'date': date, 'semesterId': '2023-1'})
    
    try:
        return response.json()
    except:
        return {"error": "数据解析失败"}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        date = self.path.split('?date=')[1] if '?date=' in self.path else None
        result = get_schedule(date)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # 允许跨域
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
