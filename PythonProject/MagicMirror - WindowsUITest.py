# -*- coding: utf-8 -*-

import paho.mqtt.client as pahomqtt
import time
import random
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys, os
from mirrorUI import Ui_MainWindow
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# import Adafruit_DHT
# import RPi.GPIO as GPIO
import json
import requests
from bs4 import BeautifulSoup
import urllib
import re
# from face import FaceFunction
# from speech import SpeechFunction
import threading

# 本类为MQTT的实现
class MQTT(QObject):
    mqttSignal = pyqtSignal(object)  # 信号，传字符串
    def __init__(self):
        super(MQTT, self).__init__()
        self.client = pahomqtt.Client()  # MQTT实例
        self.CLIENTID = 'MagicMirror'  # MQTT 订阅ID
        self.MQTTHOST = "121.36.68.53"
        self.MQTTPORT = 1883
        self.USERNAME = 'SXF'
        self.PASSWORD = "sxf1061700625"
        self.HEARTBEAT = 60
        self.topic_publish = '/RaspberryPi/MagicMirror/AdrSub_MirPub/'
        self.topic_subscribe = '/RaspberryPi/MagicMirror/AdrPub_MirSub/'
        # self.content = {"source": "mirror", "content": [[{"title": "xxxx", "msg": "xxxx"}]]}

    # MQTT连接回调
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(">> 连接成功")
            client.subscribe(self.topic_subscribe)

    # MQTT接收回调
    def on_message(self, client, userdata, msg):
        MQTT_Rx_Buff = str(msg.payload, encoding='utf-8')
        # print(MQTT_Rx_Buff)
        self.mqttSignal.emit(MQTT_Rx_Buff)

    def mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.USERNAME, self.PASSWORD)
        self.client.will_set(self.topic_publish, '>> Offline:' + self.topic_subscribe, 1)
        self.client.connect(self.MQTTHOST, self.MQTTPORT, self.HEARTBEAT)
        self.client.loop_start()  # 线程

    # UI类中发送消息 触发信号量uiSignal 给 MQTT类中mqttSlot_Send函数进行发布
    def mqttSlot_Send(self, payload):
        content = {
            "source": "mirror",
            "content": payload
        }
        self.client.publish(self.topic_publish, json.dumps(content))  # 将字典形式的数据转化为字符串


# 本类主要是第三方API的调用
class ThirdPartInfo:
    def __init__(self):
        pass

    # 获取外网IP
    def GetOuterIP(self):
        ip = requests.get('http://whatismyip.akamai.com/').text
        return ip

    # 查询IP定位
    def IPLocation(self, ip):
        url = "http://ip-api.com/json/%s?lang=zh-CN" % ip
        while True:
            try:
                sess = requests.session()
                sess.keep_alive = False
                ip_dict = sess.get(url, timeout=10).json()
                if ip_dict['status'] == 'fail':
                    continue
                else:
                    return ip_dict
            except Exception as e:
                print("IPLocation Err!", str(e))
                continue

    # 输入位置，查询天气
    def weather(self, locate):
        url = 'http://tianqi.2345.com/t/searchCity.php?q=%s&pType=local' % locate
        res = requests.get(url).json()
        url = r'http://tianqi.2345.com' + res['res'][0]['href']
        html = requests.get(url)
        html.encoding = 'gb2312'
        soup = BeautifulSoup(html.text, 'lxml')
        imgiconURL = 'http://img2.' + re.findall(r'2345.com/tianqiimg/tianqi_icon/\w+.png', html.text)[0]
        weather_only = soup.find('a', class_='data').get_text().replace(' ', '').strip().split('\n')
        weather = weather_only[0]
        temperature = weather_only[1]
        wind_force = soup.find('div', class_='wea-about').find('ul', class_='clearfix').find_all('li')[1].get_text().strip()
        emoticon = soup.find('div', class_='emoticon').get_text().strip()
        return [weather, imgiconURL, temperature, wind_force, emoticon]

    # 下载图片
    def downloadPic(self, url, path):
        with open(path, 'wb') as f:
            f.write(requests.get(url).content)


# 本类用于执行一些循环、耗时的函数，并通过信号发射到UI界面
class ExQThread(QThread):
    weatherSignal = pyqtSignal(list, str)
    historySignal = pyqtSignal(str)
    headlinesSignal = pyqtSignal(str)
    timeSignal = pyqtSignal(str, str, str)
    tempHumSignal = pyqtSignal(str, str)

    def __init__(self):
        super(ExQThread, self).__init__()
        self.thirdPart = ThirdPartInfo()
        self.running = True

    def updateTime(self):
        datetime = QDateTime.currentDateTime()
        time = datetime.toString('hh:mm')
        date = datetime.toString('yyyy年MM月dd日')
        week = datetime.toString('dddd')
        self.timeSignal.emit(time, date, week)

    def updateTempHum(self):
        pass
        # sensor = Adafruit_DHT.DHT11
        # gpio = 4
        # humidity, temperature = Adafruit_DHT.read(sensor, gpio)
        # if humidity:
        #     humidity = str(humidity) + '%'
        #     print(humidity)
        # if temperature:
        #     temperature = str(temperature) + '°'
        #     print(temperature)
        # self.tempHumSignal.emit(temperature, humidity)

    def updateWeather(self):
        ip = self.thirdPart.GetOuterIP()
        # print('>> ip:', ip)
        locate = self.thirdPart.IPLocation(ip)
        # print('>> locate:', locate)
        res = self.thirdPart.weather(locate['city'])
        # print('>> weather:', res)
        weather = res[0]
        iconURL = res[1]
        path = 'source/icon/' + weather + '.png'
        for i in os.listdir('source/icon/'):
            if weather == i.split('.')[0]:
                path = 'source/icon/' + i
                self.weatherSignal.emit(res, path)
                return
        self.thirdPart.downloadPic(iconURL, path)
        self.weatherSignal.emit(res, path)

    def updateHistory(self):
        url = 'https://www.ipip5.com/today/api.php?type=json'
        while True:
            try:
                res = random.choice(requests.get(url).json()['result'])
                content = res['year'] + '年 ' + res['title']
                self.historySignal.emit(content)
                break
            except:
                continue

    def updateHeadlines(self):
        url = 'https://api.xiaohuwei.cn/news.php'
        res = requests.get(url).json()
        res = random.sample(res, 2)
        title1 = '>> ' + res[0]['title']
        title2 = '>> ' + res[1]['title']
        content = title1 + '\n' + title2
        self.headlinesSignal.emit(content)

    def run(self):
        cnt = 0
        while self.running:
            try:
                if cnt % 10 == 0:
                    self.updateTime()
                    print('updateTime')
                if cnt % 600 == 0:
                    self.updateWeather()
                    print('updateWeather')
                if cnt % 10 == 0:
                    self.updateHistory()
                    print('updateHistory')
                if cnt % 10 == 0:
                    self.updateHeadlines()
                    print('updateHeadlines')
                if cnt % 60 == 0:
                    self.updateTempHum()
                    print('updateTempHum')
                if cnt >= 600:
                    cnt = 0
            except Exception as e:
                print(e)
            cnt += 1
            time.sleep(1)

# 本类为状态机，用于检测有人、系统唤醒亮屏、人脸识别、语音交互等的实现
class SpImgThread(QThread):
    communicateSignal = pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)
        # self.face = FaceFunction()
        # self.speech = SpeechFunction()
        self.MODE = 0
        # GPIO.setwarnings(False)
        # self.photo_sensor = 19                  # 光电传感器所连GPIO脚（空闲时高电平）
        # GPIO.setmode(GPIO.BCM)                  # BCM编码
        # GPIO.setup(self.photo_sensor, GPIO.IN)  # GPIO输入模式
        # self.LED_Pin = 26                       # LED所连GPIO脚
        # GPIO.setup(self.LED_Pin, GPIO.OUT)      # GPIO输出模式
        # GPIO.output(self.LED_Pin, GPIO.LOW)     # 输出低电平
        self.onePhraseCnt = 0

    # 强制关闭线程
    def _async_raise(self,tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    def stop_thread(self,thread):
        self._async_raise(thread.ident, SystemExit)

    def setLEDon(self):
        pass
        # GPIO.output(self.LED_Pin, GPIO.HIGH)  # 输出高电平

    def setLEDoff(self):
        pass
        # GPIO.output(self.LED_Pin, GPIO.LOW)  # 输出低电平

    # 检查是否有人靠近(GPIO0)
    def isSomeoneClose(self):
        return 0
        # input = GPIO.input(self.photo_sensor)
        # if input == 1:          # 人已离开
        #     return 1
        # else:                   # 有人靠近
        #     return 0

    # 唤醒屏幕
    def screenWakeUp(self):
        os.popen('sudo xset dpms force on')   # 唤醒

    # 检查屏幕的点亮状态
    def checkScreenStatOn(self):
        try:
            stat = os.popen('sudo xset q').readlines()[-1].strip()
        except:
            return True
        print(stat)
        if 'Monitor is Off' in stat:
            return False
        elif 'Monitor is On' in stat:
            return True

    # 关闭屏幕
    def setScreenOff(self):
        os.popen('sudo xset dpms force off')  # 立即关闭屏幕

    # 唯美短句、影视金句等
    def onePhrase(self):
        url = 'https://v1.hitokoto.cn/?encode=json&charset=utf-8'
        try:
            res = requests.get(url).json()
        except:
            return None
        hitokoto = res['hitokoto']
        source = res['from']
        content = "{}\n--《{}》".format(hitokoto, source)
        return content

    # 状态机
    def stateCheck(self):
        pass
        # if self.speech.robotText:               # 机器人有回话
        #     self.communicateSignal.emit(self.speech.robotText)
        #     self.speech.robotText = None        # 状态复位
        #     self.onePhraseCnt = 0
        # else:
        #     self.onePhraseCnt += 1
        #     if self.onePhraseCnt >= 10:
        #         print(">> 更新短句")
        #         self.onePhraseCnt = 0
        #         res = self.onePhrase()
        #         if res:
        #             self.communicateSignal.emit(res)
        # if self.MODE == 0:                      # 等待状态
        #     res = self.isSomeoneClose()         # 检测是否有人靠近
        #     if res == 0:                        # 确实有人
        #         print(">> 确实有人")
        #         print(">> 亮屏")
        #         self.screenWakeUp()  # 亮屏
        #         while not self.checkScreenStatOn():
        #             time.sleep(1)
        #         time.sleep(2)
        #         self.MODE = 1                   # 改变状态
        # elif self.MODE == 1:                    # 有人靠近状态
        #     print(">> 有人靠近状态")
            # self.speech.playAudio("audio/nihao.mp3")
            # msg = self.onePhrase()
            # self.speech.TextToPlay(msg)
            # self.MODE = 2                       # 改变状态
        # elif self.MODE == 2:                    # 人脸识别状态
            # if not self.face.isFaceVideoRun():  # 如果FaceVideo不在运行
            #     print(">> 开始人脸检测")
            #     self.setLEDon()
            #     self.face.startFaceVideo()      # 开始人脸检测（内开子线程运行）
            # if self.face.getHappyFace == 1:     # 若开心
            #     print(">> 检测到开心，停止人脸检测")
            #     # self.speech.textSpeechFunc("好开心")
            #     self.setLEDoff()
            #     self.face.stopFaceVideo()       # 停止人脸检测
            #     self.MODE = 3                   # 改变状态
            # elif self.face.getHappyFace == 2:   # 若不开心
            #     self.face.getHappyFace = 0      # 复位，否则复读
            #     print(">> 检测到不开心")
            #     self.speech.textSpeechFunc("好伤心，快安慰我")
            # res = self.isSomeoneClose()         # 检测是否有人靠近(防止没happy图但人已离开的情况)
            # if res == 1:                        # 没有人了
            #     print(">> 没有人了2")
            #     self.setLEDoff()
            #     self.face.stopFaceVideo()       # 停止人脸检测
            #     self.MODE = 3                   # 改变状态
        # elif self.MODE == 3:                    # 判断人有没有走状态
        #     res = self.isSomeoneClose()         # 检测是否有人靠近
        #     if res == 1:                        # 没有人了
        #         print(">> 没有人了3")
        #         # self.speech.playAudio("audio/baibai.mp3")
        #         # self.speech.textSpeechFunc("拜拜")
        #         self.MODE = 4                   # 改变状态
        # elif self.MODE == 4:                    # 执行完毕人走远状态
        #     print(">> 关闭屏幕与休眠")
        #     # while self.speech.checkAudioPlaying():
        #     #     time.sleep(1)
        #     time.sleep(2)
        #     self.setScreenOff()                 # 关闭屏幕与休眠
        #     self.MODE = 0                       # 改变状态
        # else:
        #     print(">> 错误状态!")

    def run(self):
        # 一开始就启动语音交互功能(热词唤醒：魔镜魔镜)
        # speechThread = threading.Thread(target=self.speech.waitUntilAwakened)
        # speechThread.setDaemon(True)
        # speechThread.start()
        print(">> SpImgThread - run")
        # 标志位初始化
        self.MODE = 0
        # 状态机循环检测
        while True:
            try:
                self.stateCheck()
            except Exception as e:
                print(e)
            time.sleep(1)

# 本类用于界面UI处理，主要为槽函数，接收信号。
class MagicUI(Ui_MainWindow, QObject):
    uiSignal = pyqtSignal(object)  # 信号，用于mqtt发消息
    def __init__(self):
        self.todo_string = ''
        self.todo_cnt = 0
        super(MagicUI, self).__init__()

    def setupUi(self, MainWindow):
        super(MagicUI, self).setupUi(MainWindow)
        self.gif = QMovie("source/洛天依_黑.gif")
        self.label_gif.setMovie(self.gif)
        self.gif.start()

    # 强制刷新界面
    def refresh(self):
        # 实时刷新界面
        QApplication.processEvents()

    # 更新时间、日期等，定时高频更新
    def updateTime(self, time, date, week):
        self.label_time.setText(time)
        self.label_date.setText(date)
        self.label_week.setText(week)

    # 获取温湿度传感器信息，这部分获取可能很慢，定时低频更新
    def updateTempHum(self, temperature, humidity):
        if humidity:
            self.label_humidity.setText(humidity)
        if temperature:
            self.label_temperature.setText(temperature)

    # MQTT类中接收到消息 触发信号量mqttSignal 给 UI类中mqttSlot函数进行处理
    def mqttSlot(self, msg):
        print('mqttSlot:', msg)
        payload = json.loads(msg)  # str转为json格式
        if payload['source'] == 'app':  # 说明消息来自于手机
            content = payload['content']
            for item in content:
                if item[0]['title'] == 'addMirrorToDoItem':  # 说明属于“今日事项”的内容
                    self.todo_cnt += 1
                    self.todo_string = self.todo_string + str(self.todo_cnt) + '. ' + item[0]['msg'] + '\n'
                    # self.todo_string = self.todo_string.lstrip('\n')
                    if self.todo_string:
                        self.label_todomsg.setText(self.todo_string)
                        self.setMirrorToDoItems()
                elif item[0]['title'] == 'getMirrorToDoItems':  # 安卓端要获取“今日事项”的内容
                    self.setMirrorToDoItems()
                elif item[0]['title'] == 'delMirrorToDoItem':  # 删除某一项
                    if item[0]['msg'] in self.todo_string:
                        self.todo_cnt -= 1
                        self.todo_string = self.todo_string.replace(item[0]['msg'] + '\n', '')
                        tempArr = self.todo_string.split('\n')
                        for i in range(len(tempArr)):
                            if tempArr[i]:
                                tempArr[i] = str(i+1) + '.' + ''.join(tempArr[i].split('.')[1:])
                        self.todo_string = '\n'.join(tempArr)
                        self.label_todomsg.setText(self.todo_string)
                        self.setMirrorToDoItems()

    # 清空TODO项目界面
    def clearToDoPayload(self):
        self.todo_cnt = 0
        self.todo_string = ''
        self.label_todomsg.setText(self.todo_string)

    # 向安卓发送TODO项目
    def setMirrorToDoItems(self):
        tempStr = self.todo_string.split('\n')
        tempList = []
        for i in tempStr:
            tempList.append(["setMirrorToDoItems", i])
        if tempList:
            self.send2mqttSignal(tempList)

    # UI类中发送消息 触发信号量uiSignal 给 MQTT类中mqttSlot_Send函数进行发布
    def send2mqttSignal(self, arr):
        temp = []
        for i in arr:  # [[a,b],[a,b],[a,b]]
            temp.append([{"title": i[0], "msg": i[1]}])
        self.uiSignal.emit(temp)

    # 更新天气信息/天气提示/天气图标，定时低频更新
    def updateWeather(self, res, path):
        weather = res[0]
        tips = res[-1]
        self.label_weather.setText(weather.center(8))
        self.label_weathertips.setText(tips)
        self.label_weathericon.setPixmap(QtGui.QPixmap(path))

    # 更新历史上的今天，定时低频更新（不同年份的滚动）
    def updateHistory(self, content):
        self.label_historymsg.setText(content)

    # 更新时事热点，定时中频更新
    def updateHeadlines(self, content):
        self.label_headlinesmsg.setText(content)

    # 更新中间区域显示的文字
    def updateCommunicate(self, msg):
        self.label_communicate.setText(msg)

# 主函数入口
def main():
    app = QtWidgets.QApplication(sys.argv)                          # 定义Qt应用
    MainWindow = QtWidgets.QMainWindow()                            # 窗口实例
    ui = MagicUI()                                                  # 界面UI实例
    mqtt = MQTT()                                                   # MQTT实例
    mqtt.mqttSignal.connect(ui.mqttSlot)                            # 信号连接槽函数
    mqtt.mqtt()                                                     # MQTT开始运行
    ui.uiSignal.connect(mqtt.mqttSlot_Send)                         # 信号连接槽函数
    ui.setupUi(MainWindow)                                          # 绘制界面
    exQthread = ExQThread()                                         # 线程实例
    exQthread.weatherSignal.connect(ui.updateWeather)               # 信号连接槽函数
    exQthread.historySignal.connect(ui.updateHistory)               # 信号连接槽函数
    exQthread.headlinesSignal.connect(ui.updateHeadlines)           # 信号连接槽函数
    exQthread.tempHumSignal.connect(ui.updateTempHum)               # 信号连接槽函数
    exQthread.timeSignal.connect(ui.updateTime)                     # 信号连接槽函数
    exQthread.start()                                               # 线程开始运行
    spImgQthread = SpImgThread()                                    # 线程实例
    spImgQthread.communicateSignal.connect(ui.updateCommunicate)    # 信号连接槽函数
    spImgQthread.start()                                            # 线程开始运行
    MainWindow.show()                                               # 显示窗口
    sys.exit(app.exec_())                                           # 应用关闭


# 程序从此开始执行
if __name__ == '__main__':
    main()
