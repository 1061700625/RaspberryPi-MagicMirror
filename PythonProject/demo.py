import snowboydecoder

import sys

import signal



interrupted = False



def signal_handler(signal, frame):

    global interrupted

    interrupted = True



def interrupt_callback():

    global interrupted

    return interrupted

def callback():
    print("OK")



model = 'audio/魔镜魔镜.pmdl'



signal.signal(signal.SIGINT, signal_handler)



detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)

print('Listening... Press Ctrl+C to exit')



detector.start(detected_callback=callback,

               interrupt_check=interrupt_callback,

               sleep_time=0.03)



detector.terminate()
