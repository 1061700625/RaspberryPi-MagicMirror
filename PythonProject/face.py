# coding:utf8
import cv2
# import numpy
# from matplotlib import pyplot
import os
import threading
# import ctypes
from aip import AipFace
# import itchat
import time
import base64
import requests
import threading

class FaceFunction:
    def __init__(self):
        """人脸识别、情感判断，若是happy则保存照片"""
        self.APPID = '10922746'
        self.APIKEY = '4F7fylBmLUT4mVgda6UNF5BY'
        self.SECRETKEY = 'fI3ZU1bMa0THPkrrAEt0OHjTvGc45nIn'
        self.imgPath = 'img/cap.jpg'
        self.savePath = 'img/'
        self.threadRunning = False      # 判断faceProcess函数的线程是否运行
        self.isFaceVideo = False        # 判断FaceVideo(主要入口函数)是否运行
        self.getHappyFace = False       # 是否获取到happy图片

    # 人脸识别并截图（这里是主要入口函数）
    def faces_video(self):
        """人脸识别并截图（这里是主要入口函数）"""
        haarcascade_path = r'data/haarcascades/haarcascade_frontalface_alt.xml'
        face_cascade = cv2.CascadeClassifier(haarcascade_path)  # 获取训练好的人脸的参数数据
        load_succeed = face_cascade.load(haarcascade_path)
        print('load haarcascade: ', load_succeed)               # 训练数据文件是否导入成功
        cap = cv2.VideoCapture(0)                # 0为默认，1为第二个
        while self.isFaceVideo:
            ret, frame = cap.read()                             # 读取1帧摄像头图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)      # 图像矩阵
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1,
                                                  minNeighbors=5,
                                                  flags=cv2.CASCADE_DO_CANNY_PRUNING,  # cv2.CASCADE_SCALE_IMAGE,
                                                  minSize=(20, 20)
                                                  )
            print('faces: ', len(faces))
            if len(faces) > 0:
                cv2.imwrite(self.imgPath, frame)             # 保存图像
                try:
                    if self.threadRunning == False:
                        print('*******faceProcess_thread.start*******')
                        self.threadRunning = True
                        faceProThread = threading.Thread(target=self.faceProcess, args=(self.imgPath, self.savePath))
                        faceProThread.setDaemon(True)
                        faceProThread.start()
                        print('*******faceProcess_thread.end*******')
                except Exception as e:
                    print(e)
                    print('请移出镜头后重刷')
                for x, y, w, h in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + w), (0, 255, 0), 2)  # 画矩形
            #cv2.imshow('frame', frame)      # 显示图像
            #key = cv2.waitKey(1) & 0xFF     # 等待键盘输入，延时为毫秒级
            # if key == ord('q'):             # 按q退出
            #     break
        cap.release()                       # 释放摄像头
        # cv2.destroyWindow('frame')          # 删除窗口

    # 开始（作为子线程运行，这是必要的）
    def startFaceVideo(self):
        """开始（作为子线程运行，这是必要的）"""
        self.isFaceVideo = True
        self.getHappyFace = 0  # 0初始；1开心；2不开心
        facesVideoThread = threading.Thread(target=self.faces_video)
        facesVideoThread.setDaemon(True)
        facesVideoThread.start()

    # 停止
    def stopFaceVideo(self):
        """停止"""
        self.isFaceVideo = False

    # FaceVideo运行状态
    def isFaceVideoRun(self):
        return self.isFaceVideo

    # 人脸对比（目前没用到）
    def faceCompare(self):
        """人脸对比（目前没用到）"""
        with open('cap.jpg', 'rb') as f:
            imgs = f.read()
            imgs = base64.b64encode(imgs).decode()
        face = AipFace(appId=self.APPID, apiKey=self.APIKEY, secretKey=self.SECRETKEY)
        identify_face = face.search(group_id_list='A618', image=imgs, image_type='BASE64')
        user_id = identify_face['result']['user_list'][0]['user_id']
        scores = int(identify_face['result']['user_list'][0]['score'])
        group_id = identify_face['result']['user_list'][0]['group_id']
        if scores > 70:
            isuser = '匹配成功'
            print('*'*60, '\r\nscores: ', scores, '\r\nisuser: ', isuser, '\r\ngroup_id: ', group_id, ' --> uid: ', user_id,'\r\n', '*'*60, )
        else:
            isuser = '未匹配到'
            print('*' * 60, '\r\nscores: ', scores, '\r\nisuser: ', isuser, '\r\n', '*' * 60, )

    # 获取access_token
    def getNewToken(self):
        """获取access_token"""
        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(self.APIKEY, self.SECRETKEY)
        try:
            response = requests.get(host, timeout=5)
        except:
            return None
        if response:
            return response.json()['access_token']

    # 人脸检测（获得各种属性，目前只返回了emotion）
    def faceDetect(self, imgPath):
        """人脸检测（获得各种属性，目前只返回了emotion）"""
        if not imgPath:
            return
        with open(imgPath, 'rb') as f:
            imgs = f.read()
            imgs = base64.b64encode(imgs).decode()
        access_token = self.getNewToken()
        request_url = 'https://aip.baidubce.com/rest/2.0/face/v3/detect' + "?access_token=" + access_token
        params = {
            'image':imgs,
            'image_type':'BASE64',
            'face_field':'age,beauty,expression,face_shape,gender,glasses,landmark,landmark150,race,quality,eye_status,emotion',
        }
        headers = {'content-type': 'application/json'}
        try:
            response = requests.post(request_url, data=params, headers=headers, timeout=5)
        except:
            return None
        if response:
            res = response.json()
            error_code = res['error_code']
            error_msg = res['error_msg']
            if error_code == 0:
                res = res['result']['face_list'][0]
                # 年龄
                age = str(res['age'])
                # 美丑打分，范围0-100，越大表示越美
                beauty = str(res['beauty'])
                # 表情，none:不笑；smile:微笑；laugh:大笑
                expression = res['expression']['type']
                # 脸型，square: 正方形 triangle:三角形 oval: 椭圆 heart: 心形 round: 圆形
                face_shape = res['face_shape']['type']
                # 性别，male:男性 female:女性
                gender = res['gender']['type']
                # 是否带眼镜，none:无眼镜，common:普通眼镜，sun:墨镜
                glasses = res['glasses']['type']
                # 双眼状态（睁开/闭合）,越接近0闭合的可能性越大
                eye_status = str(res['eye_status']['left_eye']) + ', ' + str(res['eye_status']['right_eye'])
                # 情绪,angry:愤怒 disgust:厌恶 fear:恐惧 happy:高兴 sad:伤心 surprise:惊讶 neutral:无表情 pouty: 撅嘴 grimace:鬼脸
                emotion = res['emotion']['type']
                print('年龄:', age)
                print('美丑:', beauty)
                print('表情:', expression)
                print('脸型:', face_shape)
                print('性别:', gender)
                print('眼镜:', glasses)
                print('双眼:', eye_status)
                print('情绪:', emotion)
                return emotion
            else:
                print(error_msg)
                return None

    # 向服务器上传图片
    def uploadImg(self, filepath):
        url = 'http://121.36.68.53/web/MagicMirror/upload_file.php'
        filename = filepath.split('/')[-1]
        if filename:
            files = {"file": (filename, open(filepath, "rb"), "image/png")}
            html = requests.post(url, files=files, timeout=3)
            print(">> 上传完成！")

    # 人脸处理，用于获得人脸检测信息后要执行的内容（作为子线程运行，不用子线程也是可以的只是会卡图像）
    def faceProcess(self, imgPath, savePath):
        """人脸处理，用于获得人脸检测信息后要执行的内容（作为子线程运行，不用子线程也是可以的只是会卡图像）"""
        emotion = self.faceDetect(imgPath)  # 人脸检测
        # angry:愤怒 disgust:厌恶 fear:恐惧 happy:高兴 sad:伤心 surprise:惊讶 neutral:无表情 pouty: 撅嘴 grimace:鬼脸
        emoList = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral', 'pouty', 'grimace']
        if emotion == 'happy':
            timeNow = time.strftime("%Y-%m-%d %H_%M_%S ", time.localtime())
            tempSavePaty = savePath + timeNow + emotion + '.jpg'
            try:
                os.rename(imgPath, tempSavePaty)  # 重命名
                self.uploadImg(tempSavePaty)
                self.getHappyFace = 1
                print("已保存")
                # 此处可以做其他事，如上传到服务器/发送到微信
            except:
                pass
        elif emotion == 'sad':
            self.getHappyFace = 2
        self.threadRunning = False



if __name__ == '__main__':
    face = FaceFunction()
    face.startFaceVideo()
    time.sleep(30)
    face.stopFaceVideo()












