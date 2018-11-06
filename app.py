from yolo import YOLO
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import helpers.actions as a
from helpers.data import Frame

def run_detection(video_path, mode, output_path=None, detection_file = None):
    yolo = None
    if mode is "productive":
        yolo = YOLO()
    out = None
    cap = cv2.VideoCapture(video_path)

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    video_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                  int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    if mode is "output":
        out = cv2.VideoWriter("daemmerung.avi", fourcc, video_fps, video_size)

    action_db = a.ActionDB()

    frame_number = 0
    lines = None
    while cap.isOpened():
        fr = Frame()
        if frame_number == 0:
            frame_number += 1
            continue
        return_value, img = cap.read()
        if not return_value:
            print("Could not read Frame")
            break
        image = Image.fromarray(img)
        if mode is "productive":
            image = yolo.detect_image(image)
        else:
            lines = [line.rstrip('\n') for line in open(detection_file)]

        objects = lines[frame_number].split(" ")
        fr.filter_bbox_human(objects[1:])
        fr.

        result = np.asarray(image)
        if mode is "output":
            out.write(result)
        cv2.imshow("result", result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    out.release()
    cap.release()
    cv2.DestroyAllWindows()
    yolo.close_session()


if __name__ == '__main__':
    run_detection('data/tag.mp4',"none", detection_file="data/detections_tag.txt")
