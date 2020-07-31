
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget
from PyQt5.QtWidgets import QMessageBox
import sys
from PyQt5.QtCore import QObject, pyqtSignal
import requests
from bs4 import BeautifulSoup
import json, re
# 获取外网IP
def GetOuterIP():
    ip = requests.get('http://whatismyip.akamai.com/').text
    return ip

# 查询IP定位
def IPLocation(ip):
    url = "http://ip-api.com/json/%s?lang=zh-CN" % ip
    try:
        ip_dict = requests.get(url,  timeout=10).json()
        if ip_dict['status'] == 'fail':
            return None
        else:
            return ip_dict
            # country = ip_dict['country']
            # region = ip_dict['regionName']
            # citys = ip_dict['city']
            # isp = ip_dict['isp']
    except Exception as e:
        return None

def weather(locate):
    url = 'http://tianqi.2345.com/t/searchCity.php?q=%s&pType=local' % locate
    res = requests.get(url).json()
    url = r'http://tianqi.2345.com' + res['res'][0]['href']
    html = requests.get(url)
    html.encoding = 'gb2312'
    soup = BeautifulSoup(html.text, 'lxml')
    imgiconURL = 'http://img1.2345.com/tianqiimg%s.png' % re.findall(r'//img1.2345.com/tianqiimg(.*?).png', html.text)[0]
    weather_only = soup.find('a', class_='data only').get_text().replace(' ', '').strip().split('\n')
    weather = weather_only[0]
    temperature = weather_only[1]
    wind_force = soup.find('div', class_='wea-about').find('ul', class_='clearfix').find_all('li')[
        1].get_text().strip()
    emoticon = soup.find('div', class_='emoticon').get_text().strip()
    return [weather, imgiconURL, temperature, wind_force, emoticon]

def history():
    url = 'https://www.ipip5.com/today/api.php?type=json'
    print(requests.get(url))
    print(requests.get(url).text)
    return requests.get(url).json()

def headlines():
    url = 'https://api.xiaohuwei.cn/news.php'
    return random.choice(requests.get(url).json()['result'])

if __name__ == '__main__':
    # res = GetOuterIP()
    # print(res)
    # res = IPLocation(res)
    # print(res)
    # res = weather('huzhou')
    # print(res)
    res = history()
    print(res['result'][0])









