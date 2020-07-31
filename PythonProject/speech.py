#coding = utf-8
import urllib
import urllib3
import requests
import time
import json
from bs4 import BeautifulSoup
from aip import AipSpeech
import os, sys
from playsound import playsound
import wave
import threading
import pyaudio
import random, string
import hashlib
import base64
import snowboydecoder
import signal

class SpeechFunction:
    def __init__(self):
        self.APP_ID = '10507675'
        self.API_KEY = 'ocAxiR6MnNAAIKGW50YU1c1s'
        self.SECRET_KEY = 'WNypVvOIFzy3AS02M8yapWX8SnkEyW7B'
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.playThreadArr = None
        self.audio2textPath = 'audio/audio2text.pcm'
        self.text2audioPath = 'audio/text2audio.mp3'
        self.recordRunning = False
        self.interrupted = False     # 用于语音唤醒功能snowboy
        self.detector = None         # 用于语音唤醒功能snowboy
        self.allowSpeechFunc = True  # 是否允许mainSpeechFunc函数允许
        self.robotText = None        # 机器人有回话

    # 使用ffmpeg将MP3/WAV格式转为PCM格式，百度文字转语音需要pcm/wav格式音频
    def mp3wavConverpcm(self, filePath, newfilePath):
        """使用ffmpeg将MP3/WAV格式转为PCM格式，百度文字转语音需要pcm/wav格式音频。ffmpeg: http://ffmpeg.org/"""
        cmd = "ffmpeg -y  -i {}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {}".format(filePath, newfilePath)
        os.system(cmd)
        return newfilePath

    # 语音转文字，只接受pcm格式音频
    def audioToText(self, filePath):
        """语音转文字，只接受pcm格式音频。filePath 语音所在路径"""
        with open(filePath, 'rb') as fp:
            content = fp.read()
        res = self.client.asr(content, 'pcm', 16000)
        if res['err_msg'] == 'success.':
            result = str(res["result"][0])
            return result
        return None

    # 文字转语音，百度接口，单次最长1024字节
    def textToAudio(self, message, filePath):
        """字转语音，百度接口，单次最长1024字节。 message 要转的文字; filePath 语音存放路径"""
        result = self.client.synthesis(message, 'zh', 1, {'vol': 5, 'per': 111})
        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        if not isinstance(result, dict):
            with open(filePath, 'wb') as f:
                f.write(result)
                return True
        return False

    # 文字转语音，腾讯接口
    def tencentTextToAudio(self, message, filePath):
        """字转语音，腾讯接口。 message 要转的文字; filePath 语音存放路径"""
        APPID = '2129556483'
        APPKEY = 'Fq5Ug4VtNiHZSiV8'
        url = 'https://api.ai.qq.com/fcgi-bin/aai/aai_tts'
        params = {
            'app_id': APPID,
            'time_stamp': str(int(time.time())),
            'nonce_str': ''.join(random.choice(string.ascii_letters + string.digits) for x in range(16)),
            'text': message.encode('utf-8'),
            'speaker': '7',
            'format': '3',
            'volume': '0',
            'speed': '100',
            'aht': '0',
            'apc': '58'
        }
        sign_before = ''
        for key in sorted(params):
            # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。
            sign_before += '{}={}&'.format(key, urllib.parse.quote(params[key], safe=''))
            # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
        sign_before += 'app_key={}'.format(APPKEY)

        # 对字符串sign_before进行MD5运算，得到接口请求签名
        sign = hashlib.md5(sign_before.encode('UTF-8')).hexdigest().upper()
        params['sign'] = sign
        html = requests.post(url, data=params).json()
        # print(html)
        if html['ret'] == 0:
            content = base64.b64decode(html['data']['speech'])
            with open(filePath, "wb") as f:
                f.write(content)
            return True
        return False

    # 播放音频（以子线程运行）
    def playAudio(self, filePath):
        """播放音频（以子线程运行）。filePath 要播放的音频的路径"""
        while self.checkAudioPlaying():  # 检查音频播放线程是否结束
            time.sleep(1)
        print(">> 开始播")
        playThread = threading.Thread(target=playsound, args=(filePath,))
        playThread.setDaemon(True)
        playThread.start()
        self.playThreadArr = playThread

    # 检查是否播放结束
    def checkAudioPlaying(self):
        """检查是否播放结束"""
        if self.playThreadArr:
            return self.playThreadArr.is_alive()
        return False

    # 录音
    def recordAudio(self, filePath, recordSeconds=5):
        """录音。filePath 录音文件保存位置；recordSeconds 录音时长"""
        print(">> 录音开始...", recordSeconds)
        p = pyaudio.PyAudio()
        stream = p.open(format=8, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        self.recordRunning = True
        frames = []
        for i in range(0, int(16000 / 1024 * recordSeconds)):
            if self.recordRunning:
                data = stream.read(1024)
                frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(filePath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(8))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()
        self.recordRunning = False
        print(">> 录音结束!")

    # 图灵聊天机器人
    def tulingBot(self, msg):
        api_key = "66a6b27a9a5e432db91af4a2eec822ff"
        url = 'http://openapi.tuling123.com/openapi/api/v2'
        data = {
            "perception": {"inputText": {"text": msg}},
            "userInfo": {"apiKey": api_key,"userId": str(random.randint(0,1000))}
        }
        datas = json.dumps(data)
        html = requests.post(url, datas).json()
        if html['intent']['code'] == 4003:
            print(">> 次数用完")
            return self.tencentBot(msg)
        return html['results'][0]['values']['text']

    # 腾讯闲聊机器人
    def tencentBot(self, msg):
        """腾讯闲聊机器人"""
        APPID = '2129556483'
        APPKEY = 'Fq5Ug4VtNiHZSiV8'
        url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'
        params = {
            'app_id': APPID,
            'time_stamp': str(int(time.time())),
            'nonce_str': ''.join(random.choice(string.ascii_letters + string.digits) for x in range(16)),
            'session': '10000'.encode('utf-8'),
            'question': msg.encode('utf-8')
        }
        sign_before = ''
        for key in sorted(params):
            # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。
            sign_before += '{}={}&'.format(key, urllib.parse.quote(params[key], safe=''))
            # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
        sign_before += 'app_key={}'.format(APPKEY)

        # 对字符串sign_before进行MD5运算，得到接口请求签名
        sign = hashlib.md5(sign_before.encode('UTF-8')).hexdigest().upper()
        params['sign'] = sign
        # print(params)
        html = requests.post(url, data=params).json()
        return html['data']['answer']

    # 文字转语音后播放，可直接调用的函数
    def TextToPlay(self, msg):
        if not msg:
            print(">> 传入文本为空!")
            return
        # self.textToAudio(msg, 'audio/text2audio.mp3')  # 文字转语音
        self.robotText = msg
        if self.tencentTextToAudio(msg, 'audio/text2audio.mp3'):
            self.playAudio('audio/text2audio.mp3')  # 播放语音

    # 文字经机器人后播放，可直接调用的函数
    def textSpeechFunc(self, res):
        # msg = self.tencentBot(res)
        msg = self.tulingBot(res)
        if msg:
            print(">> 机器人：", msg)
            self.robotText = msg
            # self.textToAudio(msg, 'audio/text2audio.mp3')  # 文字转语音
            self.tencentTextToAudio(msg, 'audio/text2audio.mp3')
            self.playAudio('audio/text2audio.mp3')  # 播放语音
            # while self.checkAudioPlaying():  # 检查音频播放线程是否结束
            #     time.sleep(1)

    # 唤醒后要执行的函数
    def mainSpeechFunc(self):
        if self.allowSpeechFunc:
            self.playAudio("audio/zaide.mp3")
            while self.checkAudioPlaying():  # 检查音频播放线程是否结束
                time.sleep(1)
            self.recordAudio('audio/record.pcm', 5)         # 录音
            res = self.audioToText('audio/record.pcm')      # 语音转文字
            if res:
                print(">> 你说的：", res)
                # msg = self.tencentBot(res)
                msg = self.tulingBot(res)
                if msg:
                    print(">> 机器人：", msg)
                    self.robotText = msg
                    # self.textToAudio(msg, 'audio/text2audio.mp3')   # 文字转语音
                    res = self.tencentTextToAudio(msg, 'audio/text2audio.mp3')
                    if not res:  # 腾讯失败，就用百度
                        res = self.textToAudio(msg, 'audio/text2audio.mp3')
                    if res:
                        self.playAudio('audio/text2audio.mp3')          # 播放语音
                        while self.checkAudioPlaying():                 # 检查音频播放线程是否结束
                            time.sleep(1)
        print("\r\n>> 结束!")

    # 语音唤醒相关
    def wakeupSignalHandler(self, signal, frame):
        self.interrupted = True

    # 语音唤醒相关
    def wakeupInterruptCallback(self):
        return self.interrupted

    # 语音唤醒相关
    def wakeupCallbacks(self):
        print(">> 语音唤醒")
        # 语音唤醒后，提示ding两声
        snowboydecoder.play_audio_file()
        snowboydecoder.play_audio_file()
        # 关闭snowboy功能
        self.detector.terminate()
        # 开启语音识别
        ## 这里放唤醒后要执行的函数
        self.mainSpeechFunc()
        # 打开snowboy功能
        self.waitUntilAwakened()  # wake_up —> monitor —> wake_up  递归调用

    # 热词唤醒（snowboy目前暂不支持Windows）
    def waitUntilAwakened(self):
        model = 'audio/魔镜魔镜.pmdl'  # 唤醒词为 魔镜魔镜
        # capture SIGINT signal, e.g., Ctrl+C
        # signal.signal(signal.SIGINT, self.wakeupSignalHandler)
        # 唤醒词检测函数，调整sensitivity参数可修改唤醒词检测的准确性
        self.detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
        print('监听中...')
        # 修改回调函数可实现我们想要的功能
        self.detector.start(detected_callback=self.wakeupCallbacks,  # 自定义回调函数
                           interrupt_check=self.wakeupInterruptCallback,
                           sleep_time=0.03)
        # 释放资源
        self.detector.terminate()


def test():
    speech = SpeechFunction()  # 实例化
    speech.recordAudio('audio/record.pcm', 5)  # 录音
    # filePath = speech.mp3wavConverpcm('audio/text2audio.mp3', 'audio/text2audio.pcm')  # mp3转pcm
    res = speech.audioToText('audio/record.pcm')  # 语音转文字
    print(">> 你说的：", res)
    if res:
        # msg = speech.tulingBot(res)
        msg = speech.tencentBot(res)
        print(">> 机器人：", msg)
        # speech.tencentTextToAudio(msg, 'audio/text2audio.mp3')
        speech.textToAudio(msg, 'audio/text2audio.mp3')     # 文字转语音
        speech.playAudio('audio/text2audio.mp3')  # 播放语音
        while speech.checkAudioPlaying():  # 检查音频播放线程是否结束
            time.sleep(1)
        print("\r\n>> 结束!")

if __name__ == '__main__':
    test()
    # input(">> 任意键退出")




