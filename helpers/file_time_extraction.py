import numpy as np
import cv2
import os
import pytesseract
from PIL import Image
from pytesseract import image_to_string
import datetime
from pymediainfo import MediaInfo
import csv

indir = '/home/lukas/Desktop/Biberach_1'
file_date_list = []
duration = 0
end_date_time = ''

for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        video_path = indir + '/' + f

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps > 0:
            duration = frameCount / fps
        cap.release()

        array = f.strip('.mp4').split('-')

        year = array[1][0:4]
        month = array[1][4:6]
        date = array[1][6:8]

        hour = array[2][0:2]
        min = array[2][2:4]
        sec = array[2][4:6]

        then = datetime.datetime(int(year), int(month), int(date), int(hour), int(min), int(sec), 0)
        b = then + datetime.timedelta(0, 3)
        date_time = datetime.datetime.utcfromtimestamp(float(then.strftime('%s')))

        if duration != 0:
            end_date_time = date_time + datetime.timedelta(0, duration)

        file_date_dic = {"filename": f.strip('._'), "start_time": str(date_time), "end_time": str(end_date_time)}
        file_date_list.append(file_date_dic)

print(file_date_list)

with open('persons.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for ob in file_date_list:
        filewriter.writerow([ob["filename"], ob["start_time"], ob["end_time"]])
