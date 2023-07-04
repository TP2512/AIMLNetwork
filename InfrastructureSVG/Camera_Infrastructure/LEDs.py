import threading
import time
import zipfile
import os
from skimage import measure
import numpy as np
import imutils
import cv2
from datetime import datetime


class CameraRecorder:
    def __init__(self):
        self.stop = None
        self.end = [{'LED GNB': "Off", 'LED BH': "Off", "time": datetime.now().strftime("%H:%M:%S")}]
        self.c_range = {
            "Green": range(50, 74),
            "Red": range(170,210),
            "Orange": range(1, 50),
            "Blue": range(75, 89),
            "white": range(90, 160)
        }
        self.blink = False
        self.final = []

    def detect_color(self, hue_value, s_value, v_value, colour):
        if hue_value in self.c_range.get("Green"):
            colour = "Green"
        if hue_value in self.c_range.get("Red") or hue_value == 0 and s_value > 250 and 115 < v_value < 220:
            colour = "Red"
        if hue_value in self.c_range.get("Orange"):
            colour = "Orange"
        if hue_value in self.c_range.get("Blue"):
            colour = "Blue"
        if hue_value in self.c_range.get("white") or hue_value == 0 and v_value == 255:
            colour = "white"
        if v_value == 0 and s_value == 0:
            colour = "Off"
        return colour

    @staticmethod
    def create_label(blurred, lower_red, upper_red):
        mask = cv2.inRange(blurred, lower_red, upper_red)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel)
        cnts = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts

    @staticmethod
    def define_leds(colour, cY, leds, height):
        pos = "BH" if int(cY) < int(height / 2) else "GNB"
        leds[f"LED {pos}"] = colour
        leds["time"] = datetime.now().strftime("%H:%M:%S")

    def filter_colours(self, hsv_frame, radius_min, radius_max, c, leds, height, frame):
        colour = "Unknown"
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        LED_colour = hsv_frame[int(cY), int(cX)]
        hue_value = LED_colour[0]
        s_value = LED_colour[1]
        v_value = LED_colour[2]
        for colours in self.c_range.values():
            if radius_min < int(radius) < radius_max:
                colour = self.detect_color(hue_value, s_value, v_value, colour)
                self.define_leds(colour, cY, leds, height)
                cv2.circle(frame, (int(cX), int(cY)), int(radius),
                           (0, 0, 255), 3)
                cv2.putText(frame, f"{colour} Radius - {int(radius)} HSV - {LED_colour}", (x, y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 2)

    def rec(self, **kwargs):
        rtsp = kwargs.get('rtsp')
        vid_path = kwargs.get("path") or None
        radius_min = kwargs.get('radius_min') or 20
        radius_max = kwargs.get('radius_max') or 30
        thread_obj = kwargs.get('obj')
        capture = cv2.VideoCapture(rtsp)
        frame_width = int(capture.get(3))
        frame_height = int(capture.get(4))
        if vid_path:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            size = (frame_width, frame_height)
            out = cv2.VideoWriter(fr'{vid_path}\Led_Record {datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.avi', fourcc,
                                  10, size)
        while thread_obj.exit_flag:
            _, frame = capture.read()
            if frame is not None:
                height, width, _ = frame.shape
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                blurred = cv2.GaussianBlur(hsv_frame, (5, 5), 3)
                blurred = cv2.bilateralFilter(blurred, 9, 75, 75)
                leds = {'LED GNB': "Off", 'LED BH': "Off", "blink": False, "time": datetime.now().strftime("%H:%M:%S")}
                lower_red = np.array([0, 0, 0])
                upper_red = np.array([255, 185, 168])
                mask = cv2.inRange(blurred, lower_red, upper_red)
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.erode(mask, kernel)
                cnts = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                for c in self.create_label(blurred,lower_red, upper_red):
                    area = cv2.contourArea(c)
                    approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
                    self.filter_colours(hsv_frame, radius_min, radius_max, c, leds, height, frame)
                if leds['LED GNB'] != self.end[-1]['LED GNB']:
                    self.end.append(leds)
                cv2.imshow('LED Check', frame)
                cv2.waitKey(1)
                out.write(frame) if vid_path else None
            else:
                capture = cv2.VideoCapture(rtsp)
        capture.release()
        if vid_path:
            out.release()


    def filter_blink(self, change, index):
        if self.end[index - 1]['LED GNB'] == "Off" \
                and self.end[index + 1]['LED GNB'] == "Off" and \
                int(datetime.strptime(self.end[index + 1]['time'], "%H:%M:%S").second
                    - datetime.strptime(change['time'], "%H:%M:%S").second) < 10 and \
                int(datetime.strptime(change['time'], "%H:%M:%S").second
                    - datetime.strptime(self.end[index - 1]['time'], "%H:%M:%S").second) < 10:
            change['blink'] = True
            self.end[index + 1]['blink'] = "remove"
            self.end[index - 1]['blink'] = "remove"
        elif self.end[index - 1]['LED GNB'] == "Off" and \
                self.end[index + 1]['LED GNB'] != change['LED GNB'] and \
                int(datetime.strptime(self.end[index + 1]['time'], "%H:%M:%S").second
                    - datetime.strptime(change['time'], "%H:%M:%S").second) < 10 and \
                int(datetime.strptime(change['time'], "%H:%M:%S").second
                    - datetime.strptime(self.end[index - 1]['time'], "%H:%M:%S").second) < 10:
            change['blink'] = "remove"

    def cat_result(self):
        self.end.remove(self.end[0])
        if len(self.end) > 2:
            for index, change in enumerate(self.end):
                if index == 0:
                    continue
                elif index != len(self.end) - 1:
                    self.filter_blink(change, index)
                if index == len(self.end) and change['blink'] == False and \
                        self.end[index - 1]['blink'] == True and \
                        int(datetime.strptime(change['time'], "%H:%M:%S").second -
                            datetime.strptime(self.end[index - 1]['time'], "%H:%M:%S").second) <= 3:
                    change['blink'] = 'remove'

    def init_analyze_rec(self):
        self.cat_result()
        cnt = 0
        for element in self.end:
            if element["blink"] and element['blink'] != "remove":
                if cnt == 0:
                    self.final.append(element)
                    cnt = 1
            elif element['blink'] != "remove":
                cnt = 0
                self.final.append(element)

    def clean_final(self):
        for item in self.final:
            if item["blink"] == True and item["LED BH"] == "Off":
                item["LED BH"] = item["LED GNB"]
            item.pop("time")

    def analyze_rec(self):
        self.init_analyze_rec()
        for index, element in enumerate(self.final):
            if len(self.final) >= 1 and self.final[index - 1]['LED GNB'] == element['LED GNB'] and \
                    int(datetime.strptime(element['time'], "%H:%M:%S").second
                        - datetime.strptime(self.final[index - 1]['time'], "%H:%M:%S").second) <= 7 and \
                    index != 0:
                self.final.remove(self.final[index - 1])
        self.clean_final()
        # return self.final

    def start_recording(self, rtsp, min_blur=135, max_blur=160, min_raduis=9.5, max_raduis=20):
        tr = threading.Thread(target=self.rec, args=[rtsp, min_blur, max_blur, min_raduis, max_raduis])
        tr.start()

    def stop_recording(self):
        self.stop = True

    @staticmethod
    def rec_compression(path):
        with zipfile.ZipFile(fr"{path}\records.zip", "a") as archive:
            for vid in os.listdir(path):
                if vid not in archive.namelist() and "Led_Record" in vid:
                    archive.write(fr"{path}\{vid}", vid)
                    for _ in range(3):
                        try:
                            os.remove(fr"{path}\{vid}") if "Led_Record" in vid else vid
                        except Exception:
                            time.sleep(1)
            archive.close()


if __name__ == "__main__":
    x = CameraRecorder()
    x.start_recording('rtsp://admin:admin@192.168.127.88:554/12')
    time.sleep(60 * 80)
    x.stop_recording()
    print(x.analyze_rec())
