#烟台大学 计控学院
# lmz
#开发时间：2020/11/10 10:40


import wave
import threading
import pyaudio
import cv2

from os import remove, mkdir, listdir
from os.path import exists, splitext, basename, join
from datetime import datetime
from time import sleep
from shutil import rmtree
from PIL import ImageGrab
from numpy import array
from moviepy.editor import *
import shutil

Keep = True
def startExam():
    CHUNK_SIZE = 1024  # 尺寸
    CHANNELS = 1  # 频道
    FORMAT = pyaudio.paInt16  # 格式
    RATE = 48000  # 频率
    allowRecording = True  # 记录

    # 录制音频
    def record_audio():
        p = pyaudio.PyAudio()
        # 等待摄像头启动好，然后大家_起等3秒开始录制
        event.wait()
        sleep(3)
        # 创建输入流
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)
        wf = wave.open(audio_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        while allowRecording:
            # 从录音设备读取数据，直接写入wav文件
            data = stream.read(CHUNK_SIZE)
            wf.writeframes(data)  # 获取数据然后写入
        wf.close()
        stream.stop_stream()
        stream.close()
        p.terminate()

    # 录制屏幕
    def record_screen():
        # 等待摄像头启动好，然后大家_起等3秒开始录制
        event.wait()
        sleep(3)
        im = ImageGrab.grab()
        video = cv2.VideoWriter(screen_video_filename,
                                cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
                                25, im.size)  # 顿速和视频宽度、高度
        while allowRecording:
            im = ImageGrab.grab()
            im = cv2.cvtColor(array(im), cv2.COLOR_RGB2BGR)  # 录制并写入
            video.write(im)
        video.release()

    # 录制屏幕前人像
    def record_webcam():
        # 参数0表示笔记本自带摄像头
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # 启动好摄像头，发出通知，大家_起等3秒然后开始录
        event.set()
        sleep(3)
        aviFile = cv2.VideoWriter(cam1_video_filename, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 25,
                                  (640, 480))  # 顿速和视频宽度、高度

        while allowRecording and cap.isOpened():
            # 捕捉当前图像，ret=True表示成功，False表示失败
            ret, frame = cap.read()
            if ret:
                aviFile.write(frame)
        aviFile.release()
        cap.release()

    now = str(datetime.now())[: 19].replace(':', '_')
    audio_filename = f'output_{now}.mp3'
    cam1_video_filename = f'output_摄像头1{now}.mp4'
    cam2_video_filename = f'output_摄像头2{now}.mp4'
    cam3_video_filename = f'output_摄像头3{now}.mp4'

    screen_video_filename = f'output_屏幕{now}.mp4'
    jvideo_filename = f'output_合成{now}.mp4'
    # 创建两个线程，分别录音和录屏
    tl = threading.Thread(target=record_audio)  #录制音频
    t2 = threading.Thread(target=record_screen) #录制屏幕
    t3 = threading.Thread(target=record_webcam) #录制屏幕前人像

    # 创建时间，用于多个线程同步，等摄像头准备以后再_起等3秒开始录制
    event = threading.Event()
    event.clear()
    for t in (tl, t2, t3):
        t.start()

    # 等待摄像头准备好，提示用户3秒钟以后开始录制
    event.wait()

    print('3秒后开始录制 本次考试时间为两小时')
    print('Recording starts after 3 seconds, and the test duration is two hours')
    while True:
        sleep(30)  #暂时写死时间
        break
        # if input() == 'q':
        #     break

    allowRecording = False

    for t in (tl, t2, t3):
        t.join()

    print("开始合成视频图像")
    # 把录制的音频和屏幕截图合成为视频文件
    audio1 = AudioFileClip(audio_filename)

    video1 = VideoFileClip(screen_video_filename)
    ratio1 = audio1.duration / video1.duration
    video1 = (video1.fl_time(lambda t: t / ratio1, apply_to=['MPEG-4'])
              .set_end(audio1.duration))

    video2 = VideoFileClip(cam1_video_filename)
    ratio2 = audio1.duration / video2.duration
    video2 = (video2.fl_time(lambda t: t / ratio2, apply_to=['MPEG-4'])
              .set_end(audio1.duration)
              .resize((320, 240))
              .set_position(('right', 'bottom')))

    # joinVideo = CompositeVideoClip([videol,video2]).set_audio(audio)
    joinVideo = CompositeVideoClip([video1, video2]).set_audio(audio1)
    joinVideo.write_videofile(jvideo_filename, codec='libx264', fps=25)  # 输出文件

    # 删除临时音勒文件和视频文件^
    remove(audio_filename)
    remove(screen_video_filename)
    remove(cam1_video_filename)
    shutil.move(jvideo_filename, './video/')


