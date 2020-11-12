#烟台大学 计控学院
# lmz
#开发时间：2020/11/1 16:31
import psutil
import os
import time
import threading
# def endKill():
#     os._exit()
def startKill():
        while True:
            time.sleep(3)
            pids = psutil.pids()
            #print(pids)
            for pid in pids:
                p = psutil.Process(pid)
                #  print(p)
                # print('pid-%s,pname-%s' % (pid, p.name()))
                lst=['POWERPNT.EXE','WINWORD.EXE','EXCEL.EXE']
                for item in lst:
                    if p.name() == item:
                        cmd = 'taskkill /F /IM '+item
                        os.system(cmd)
            # t = threading.Timer(4.0, startKill)
            # t.start()
