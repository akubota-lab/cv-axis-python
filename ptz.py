import requests
import cv2
from requests.auth import HTTPDigestAuth
import time
import math
import argparse

"""
PTZカメラクラス
Args:
    ip (str): カメラのIPアドレス
    username (str): カメラのユーザー名
    password (str): カメラのパスワード
    resolution (str, optional): カメラの解像度. デフォルトはResolution._720p.
Methods:
    capture: カメラからフレームをキャプチャする
    show: キャプチャしたフレームを表示する
    save: キャプチャしたフレームを保存する
    update: カメラのパラメータを更新する
    get: カメラの現在の位置を取得する
    zoom: ズームを設定する
    setPanTilt: パンとチルトを設定する
    setXYZ: X、Y、Z座標を設定する
    movePanTilt: パンとチルトを移動する
"""
class PTZCamera:
    class Resolution:
        _1080p = "1920x1080"
        _720p = "1280x720"
        _450p = "800x450"
        _360p = "640x360"
        _270p = "480x270"
        _180p = "320x180"
    
    def __init__(self, ip, username, password, resolution=Resolution._720p):
        self.ip = ip
        self.username = username
        self.password = password
        self.resolution = resolution
        self.params = {
            "pan": 0,
            "tilt": 0,
            "zoom": 0,
            "focus": 0,
            "brightness": 0,
            "autofocus": "on"
        }
        res = requests.get(f"http://{self.ip}/axis-cgi/pingtest.cgi")
        print(res.text)


    def capture(self):
        cap = cv2.VideoCapture(f"http://{self.username}:{self.password}@{self.ip}/axis-cgi/mjpg/video.cgi?resolution={self.resolution}")
        if not cap.isOpened():
            raise ValueError(f"Unable to connect to {self.ip}")
        ret, frame = cap.read()
        if not ret:
            raise ValueError("Unable to read frame")
        return frame

    def show(self, windowName="frame", waitTime=0):
        cv2.imshow(windowName, self.capture())
        key = cv2.waitKey(waitTime)

    def save(self, dirpath="."):
        filepath = f"{dirpath}/{time.strftime('%Y%m%d-%H%M%S')}.jpg" # e.g. 20210701-123456.jpg or 20210701-123456.jpg
        cv2.imwrite(filepath, self.capture())

    def update(self):
        res = requests.get(f"http://{self.ip}/axis-cgi/com/ptz.cgi?action=update", params=self.params, auth=HTTPDigestAuth(self.username, self.password))
        ## TODO: add error handling
        time.sleep(2) # Wait for the camera to update the parameter

    def get(self):
        res = requests.get(f"http://{self.ip}/axis-cgi/com/ptz.cgi?query=position", auth=HTTPDigestAuth(self.username, self.password))
        for line in res.text.splitlines():
            key, value = line.split("=")
            self.params[key] = value

    def zoom(self, zoom):
        self.params["zoom"] = zoom
        self.update()

    def setPanTilt(self, pan, tilt):
        self.params["pan"] = pan
        self.params["tilt"] = tilt
        self.update()

    def setXYZ(self, x, y, z):
        self.params["pan"] = math.degrees(math.atan2(x, z))
        self.params["tilt"] = math.degrees(math.atan2(y, math.sqrt(x**2 + z**2)))
        self.update()

    def movePanTilt(self, pan, tilt):
        self.params["pan"] += pan
        self.params["tilt"] += tilt
        self.update()

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--ip", type=str, default="192.168.0.90")
    args.add_argument("--username", type=str, default="root")
    args.add_argument("--password", type=str, default="Pass123")
    args.add_argument("--resolution", type=str, default=PTZCamera.Resolution._1080p)
    args = args.parse_args()
    
    camera = PTZCamera(args.ip, args.username, args.password, args.resolution)
    # 移動前の位置を表示＆保存
    camera.save()
    camera.show("before", 1)
    # パンとチルトを移動
    camera.get()
    camera.movePanTilt(10, 10)
    # 移動後の位置を表示＆保存
    camera.save()
    camera.show("after", 0)