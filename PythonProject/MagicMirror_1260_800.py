# -*- coding: utf-8 -*-

import paho.mqtt.client as pahomqtt
import time
import random
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys, os
from mirrorUI_2 import Ui_MainWindow
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import requests
from bs4 import BeautifulSoup
import urllib
import re
import threading

# 本类用于界面UI处理，主要为槽函数，接收信号。
class MagicUI(Ui_MainWindow):
    def __init__(self):
        self.todo_string = ''
        self.todo_cnt = 0
        super(MagicUI, self).__init__()

    def setupUi(self, MainWindow):
        super(MagicUI, self).setupUi(MainWindow)


# 主函数入口
def main():
    app = QtWidgets.QApplication(sys.argv)                          # 定义Qt应用
    MainWindow = QtWidgets.QMainWindow()                            # 窗口实例
    ui = MagicUI()                                                  # 界面UI实例
    ui.setupUi(MainWindow)                                          # 绘制界面
    MainWindow.show()                                               # 显示窗口
    sys.exit(app.exec_())                                           # 应用关闭


# 程序从此开始执行
if __name__ == '__main__':
    main()
