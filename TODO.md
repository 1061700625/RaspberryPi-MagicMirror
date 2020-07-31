[TOC]



- [x] 硬件组装
- [x] 系统唤醒与亮屏
- [x] 获取传感器信息并显示
- [x] 获取天气、新闻等信息并显示
- [x] UI界面绘制魔镜界面绘制
- [x] 安卓APP
- [x] 获取备忘录信息并显示
- [x] 推送使用情况到APP（能推，但不知道推啥）
- [x] 内容整合
- [x] 人脸识别
- [x] 情感监测
- [x] 语音对话



#### 无键盘无屏幕首次启动树莓派

1. SD卡安装完镜像，默认的用户名：pi，默认密码：raspberry
2. 开启ssh：boot目录下 新建一个 ssh 的文件 没有后缀
3. 设置WiFi：boot目录下 新建文件 wpa_supplicant.conf

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
ssid="HUAWEI P30"
psk="1061700625."
}
```

5. 或者用网线通过路由器连接：
   - 网线连接**树莓派**和**路由器**
   - **电脑**连接**路由器**
   - 查看树莓派的ip

6. 电脑ssh连接树莓派

7. 开启VNC：

- ```sudo raspi-config```

- 选择 ```Interfacing Options```

- 选择```VNC```



#### 安装虚拟桌面（远程桌面进入）

```
sudo apt-get install xrdp 
```

#### 屏幕唤醒与休眠

唤醒：

```
xset dpms force on
```

防止休眠：

```
xset dpms 0 0 0 
xset s off
```

立即关闭屏幕

```
xset dpms force off
```

#### 读取DHT11

```
sudo vim /boot/config.txt
```

config.txt:

```
#开启i2c
dtparam=i2c_arm=on
#开启spi
dtparam=spi=on
#DHT11支持
dtoverlay=dht11
```

读取：

```
cat /sys/devices/platform/dht11@0/iio:device0/in_temp_input
cat /sys/devices/platform/dht11@0/iio:device0/in_humidityrelative_input
```

#### 安装Adafruit_DHT

```
sudo git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install
```

#### git clone提速

```
git config --global http.postBuffer 524288000
```

#### 树莓派配置

```
sudo raspi-config
```

#### 屏幕旋转

```
display_rotate=0           不旋转 Normal 
display_rotate=1           转90 degrees 
display_rotate=2           转180 degrees 
display_rotate=3           转270 degrees 
display_rotate=0x10000        左右翻转horizontal flip 
display_rotate=0x20000        上下翻转vertical flip 
```

#### 换源

```
sudo vim /etc/apt/sources.list
deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib
deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib

sudo vim /etc/apt/sources.list.d/raspi.list
deb http://mirrors.tuna.tsinghua.edu.cn/raspberrypi/ buster main ui

sudo apt-get update
sudo apt-get upgrade

sudo mkdir ~/.pip
sudo vim ~/.pip/pip.conf
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=mirrors.aliyun.com
```

#### opencv安装

```
sudo apt-get install libhdf5-dev libhdf5-serial-dev -y
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 -y
sudo apt-get install libatlas-base-dev -y
sudo apt-get install libjasper-dev -y

pip3 install opencv_contrib_python-3.4.3.18-cp37-cp37m-linux_armv7l.whl
```

#### 安装字体

```
复制到/usr/share/fonts/
```

#### 安装Qt5

```
sudo apt-get install python3-pyqt5 -y
```

#### 安装portaudio

```
下载portaudio库http://portaudio.com/download.html
sudo apt install libasound-dev#一定要有这一句
sudo ./configure
sudo make
sudo make install
vim ~/.bashrc
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
sudo ldconfig
```

#### 安装snowboy

```
sudo apt-get install pulseaudio -y
sudo apt-get install sox -y
sox -d -d  # 测试
sudo apt-get install python3-pyaudio -y
sudo apt-get install swig -y
sudo apt-get install libatlas-base-dev -y
git clone https://github.com/Kitt-AI/snowboy.git
cd snowboy/swig/Python3 && make
snowboydecoder将第 5 行代码 from * import snowboydetect 改为 import snowboydetect 即可直接运行
```

#### 安装nginx

```
1、安装nginx  web服务器
sudo apt-get install nginx -y
2、启动nginx
sudo /etc/init.d/nginx start
nginx的www根目录默认在 /usr/share/nginx/www中
3、修改nginx的配置文件
sudo vim /etc/nginx/sites-available/default

listen   8080;## listen for ipv4; this line is default and implied
//监听的端口号，如果与其它软件冲突，可以在这里更改
root /usr/share/nginx/www;
//nginx 默认路径html所在路径
index index.html index.htm index.php;
//nginx默认寻找的网页类型，可以增加一个index.php
```

#### 安装Gst（playsound用到）

```
sudo apt-get install gir1.2-gst-plugins-base-1.0 -y
```

#### 树莓派配置麦克风录音

（亲测方法一没一点软用）

1、在用户目录下编辑文件~/.asoundrc，如果没有这个文件就新建一个

```
sudo vim ~/.asoundrc
```

2、将文件内容改为(音频输入使用声卡1（usb声卡），输出使用声卡0，即板载声卡。)：

```
pcm.!default {
  type asym
  playback.pcm {
    type plug
    slave.pcm "hw:0,0"
  }
  capture.pcm {
    type plug
    slave.pcm "hw:1,0"
  }
}
ctl.!default {
  type hw
  card 2
}
```

3、设置麦克风增加稍稍加强一些

```
alsamixer
```

4、按F6选择USB声卡,按F5显示所有选项,将两个Mic项调到100即可。

5、运行pulseaudio（一直不成功，结果这步没开，网上教程抄来抄去真蠢）

```
pulseaudio --start 

systemctl --user start pulseaudio.socket
systemctl --user start pulseaudio.service
```

6、测试录音

```
rec test.wav
```

7、pyaudio测试

```
python3
import pyaudio
pa = pyaudio.PyAudio()
pa.get_default_input_device_info()
pa.get_device_count()
```

#### 空闲隐藏鼠标

```
sudo apt-get install unclutter -y
sudo vim /etc/xdg/lxsession/LXDE/autostart
添加：@unclutter -idle 1 -root
# idle后面的数字是指空闲多少时间，单位秒，最短时间是1秒
```



