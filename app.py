from yolo import YOLO
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from helpers.actions import ActionDB


def run_detection(video_path,mode, output_path=None):
    yolo = YOLO()
    out = None
    cap = cv2.VideoCapture(video_path)

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    video_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                  int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    if mode is "output":
        out = cv2.VideoWriter("daemmerung.avi", fourcc, video_fps, video_size)
    while cap.isOpened():
        return_value, frame = cap.read()
        if not return_value:
            print("Could not read Frame")
            break
        image = Image.fromarray(frame)
        image = yolo.detect_image(image)
        result = np.asarray(image)

        cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        out.write(result)
        cv2.imshow("result", result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    out.release()
    cap.release()
    cv2.DestroyAllWindows()
    yolo.close_session()


if __name__ == '__main__':
    run_detection()
