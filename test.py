'''

慕课视频下载器

'''

import sys

import os

import re

import json

from time import clock, sleep

from socket import timeout

from urllib import request

from urllib import parse

from urllib.error import ContentTooShortError, URLError, HTTPError

author = "Dreams孤独患者"

email  = "1079339655@qq.com"

CODE = 'Mooc.jpg'   #  支付宝二维码领红包的图片
file = r"E:\py36_project\Intelligent-Test_Face-Recognition"
PATH = os.path.dirname(os.path.abspath(file))  # 程序当前路径

TIMEOUT = 20  # 请求超时时间为 20 秒

winre = re.compile(r'[?|<>:"/\\r\n\t]')  # windoes 文件非法字符匹配
start_time = clock()
start_size = 0
speed = 0
class Mooc:
    def init(self):

        names = map(lambda s:re.sub(r'[{}# ]', '', s), names)

        names = map(lambda s:s.encode('utf8').decode('unicode_escape'), names)

        schools = re.findall(r'highlightUniversity="(._?)"', text)
        schools = map(lambda s:re.sub(r'[{}# ]', '', s), schools)
        schools = map(lambda s:s.encode('utf8').decode('unicode_escape'), schools)
        urls = re.findall(r'courseId=(\d_);', text)

        urls = map(lambda s: "https://www.icourse163.org/course/WHUT-"+s, urls)

        courses = [{'name':na,'school':sch,'url':url} for na,sch,url in zip(names,schools,urls)]

        return courses

    def getTitle(self, course_url):  # 获取指定慕课URL的课程标题

        response = request.urlopen(course_url, timeout=TIMEOUT)

        text = response.read().decode('utf8')

        response.close()

        title = text[text.find('')+7:text.find('')].strip()

        self.title = winre.sub('', title) # 用于除去win文件非法字符

        return title

    def getContent(self, course_url):  # 获取指定慕课URL的课程视频和课件链接，最后保存为字典

        self.course_data['course_url'] = course_url

        params = '?' + ''.join(k+'='+self.course_data[k]+'&' for k in self.course_data)

        response = request.urlopen(self.mooc_url+params, timeout=TIMEOUT)

        self.content = json.loads(response.read().decode('utf8'))['data']

        response.close()

    def getSize(self, course_url):  # 获取待下载视频的大小

        cnt = 0

        while cnt < 5:
            try:
                response = request.urlopen(course_url, timeout=TIMEOUT)
                header =  dict(response.getheaders())
                size = float(header['Content-Length']) / (1024*1024)
                return size
            except URLError:
                cnt += 1
                sleep(1)
            finally:
                response.close()
        raise Exception("网络异常")
    def download_lesson(self, source ,dirname):  # 下载每个课程
        unit_titles = ['None', 'None'] # 每一单元的标题，包含视频和课件
        unit_urls = [None, None]  # 每一单元的资源链接，包含视频和课件
        for url_name in ('shdUrl', 'hdUrl'):  # 优先获取高清视频资源
            if (unit_urls[0] is None):
                unit_urls[0] = source.get(url_name,None)
                unit_titles[0] = winre.sub('',source.get('unit_title', 'None'))
            if (unit_urls[1] is None):
                unit_urls[1] = source.get('project_url', None)
                unit_titles[1] = winre.sub('',source.get('unit_title', 'None'))
        if unit_urls[0]:
            self.num += 1
            video_name = "("+str(self.num)+")--"+unit_titles[0]
            mooc_video = os.path.join(dirname, video_name)+'.mp4' # 视频路径
            if not os.path.exists(mooc_video):
                size = self.getSize(unit_urls[0])
                print("  |-{}    大小: {:.2f}M".format(align(video_name,50), size))
                try:
                    downlaod_file(unit_urls[0], mooc_video, schedule) #下载文件，这里下载的是高清资源\
                except KeyboardInterrupt:  # 如果用户中断，则删除下载不完整的文件
                    if os.path.exists(mooc_video):
                        os.remove(mooc_video)
                    raise KeyboardInterrupt()
            else:
                print("  |-{}    已经成功下载！".format(align(video_name,50)))
        if unit_urls[1]:
            pdf_name = unit_titles[1]
            mooc_pdf = os.path.join(dirname, pdf_name)+'.pdf' # 课件路径
            if not os.path.exists(mooc_pdf):
                try:
                    downlaod_file(unit_urls[1], mooc_pdf)
                except KeyboardInterrupt:
                    if os.path.exists(mooc_pdf):
                        os.remove(mooc_pdf)
                    raise KeyboardInterrupt()
    def download(self):  # 根据课程视频链接来下载高清MP4慕课视频, 成功下载完毕返回 True
        print('\n{:^60s}'.format(self.title))
        rootDir = os.path.join(PATH, self.title)
        if not os.path.exists(rootDir):
            os.mkdir(rootDir)
        try:
            for chapter in self.content:  # 去除 win 文价夹中的非法字符
                chapter_title = winre.sub('', chapter['chapter_title'].strip())
                chapterDir = os.path.join(rootDir, chapter_title)
                if not os.path.exists(chapterDir):
                    os.mkdir(chapterDir)
                print(chapter_title)
                for unit in chapter:
                    if unit=='chapter_title': continue
                    lesson_title = winre.sub('', chapter[unit]['lesson_title'])
                    lessonDir = os.path.join(chapterDir, lesson_title)
                    if not os.path.exists(lessonDir):
                        os.mkdir(lessonDir)
                    print("  "+lesson_title)
                    self.num = 0
                    for lesson in chapter[unit]:
                        if lesson == 'lesson_title': continue
                        source = chapter[unit][lesson]
                        self.download_lesson(source, lessonDir)
            return True
        except (Exception, KeyboardInterrupt) as err:
            if isinstance(err, KeyboardInterrupt):  # 如果是用户自己中断
                print()
            else:                                   # 否则即使网络问题
                print("\n请检查网络状态是否良好…")
            return False
    def schedule(a, b, c):  #下载进度指示 a:已经下载的数据块  b:数据块的大小 c:远程文件的大小
        global start_time, start_size, speed
        length = 66
        sch = min(100 * a * b / c, 100)
        per = min( length * a * b // c, length)
        if a%5 == 0 or per == length:
            if per <= length:
                print('\r  |-['+per+'_'+(length-per)+'.'+']  {:.2f}%  {:.2f}M/s'.format(sch,speed),end='  (ctrl+c中断)')
                if clock()-start_time > 0.5:  # 时间差大于0.5秒的时候刷新平均速度
                    speed = (a+b-start_size) / ((clock()-start_time)+1024+1024)
                    start_size = a+b
                    start_time = clock()
            if per == length:
                print()
    def align(string, width):  #  对齐汉字字符窜，同时截断多余输出
        res = ""
        size = 0
        for ch in string:
            if (size+3 > width):
                break
            size += 1 if ord(ch) <= 127 else 2
            res += ch
        res += (width-size)+' '
        return res
    def downlaod_file(url, filename, backfunc = None):  # 用于处理网络状态不好时，重新下载
        global start_time, start_size, speed            # 若三次后还是无法下载，则报错
        cnt = 0
        while cnt < 5:
            try:
                start_time = clock()  #  初始化时间，大小和速度
                speed = start_size = 0
                request.urlretrieve(url, filename, backfunc)
                return
            except (ContentTooShortError, URLError, ConnectionResetError, timeout):
                if os.path.exists(filename):
                    os.remove(filename)  # 删除未下载完毕的文件
                cnt += 1
                sleep(1)
            finally:
                request.urlcleanup()
                sleep(0.1)
        raise Exception("网络不可用")
    def get_SourceFile(filename):  # 获取打包后资源文件的位置，这里为二维码图片的路径
        if getattr(sys, 'frozen', False): #是否打包
            file_path = sys._MEIPASS
        else:
            file_path = PATH
        return os.path.join(file_path, filename)
def UI_interface(mooc):
        try:
            while True:
                os.system("cls")
                print("\t"+"="+80)
                print('\t|\t\t\t中国大学视频下载器  \t\t作者: {:^16s} |'.format(author))
               # print("\t|\t\t\twww.icourse163.org\t\t邮箱: {:^16s} |".format(email)… [y/n]: ") != 'n'):

                alipy = mooc.get_SourceFile(CODE)
                os.startfile(alipy)
        except:
            pass



def main():

    mooc = Mooc()

    try:

        UI_interface(mooc)

    except (KeyboardInterrupt, EOFError):

        pass

    os.system("pause")

if __name__ == '__main__':

    main()

