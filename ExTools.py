import urllib
import requests

import re
from time import  strftime
from datetime import datetime
import win32api,win32con,win32gui
import os
import sys

Path = 'F:\\screen\\'

day_list = []
history_list = []

def DlImgs():
    url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8'
    content = urllib.urlopen(url).read().decode('utf-8')
    reg = re.compile('"url":"(.*?)","urlbase"', re.S)
    text = re.findall(reg, content)
    for i in range(0, len(text)):
        img_url = 'http://cn.bing.com' + text[i]
        image = requests.get(img_url).content
        file_name = Path + '%s.bmp'%datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3].replace(':', '')
        with open(file_name, 'wb') as f:
            f.write(image)
            day_list.append(file_name)

def SetWallPaper(pic_path):
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,"Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "2") 
    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, pic_path, win32con.SPIF_SENDWININICHANGE)

def HistoryImgs():
    for root, dirs, files in os.walk(Path, topdown=False):
        for name in files:
            history_list.append(os.path.join(root, name))

def NeedDownLoad():
    if len(history_list) == 0:
        return True
    day =  strftime("%Y-%m-%d")
    for i in history_list:
        if(i.find(day) != -1):
            return False
    return True

if __name__ == "__main__":
    if len(history_list) == 0:
        HistoryImgs()
        SetWallPaper(history_list[0])
    if(NeedDownLoad()):
        print("start download...")
        DlImgs()
        SetWallPaper(day_list[0])
    if len(sys.argv) > 1:
        print(sys.argv)
    i = 0
    while str(input()) != "q":
        SetWallPaper(history_list[i])
        i += 1