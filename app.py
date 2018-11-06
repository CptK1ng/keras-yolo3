from yolo import YOLO
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import helpers.actions as a
from helpers.data import Frame
from helpers.zoning import ZoneController
from helpers.score_controller import ScoreController
from helpers.heatmap import Heatmap

def run_detection(video_path, mode, output_path=None, detection_file=None):
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
    zone_controller = ZoneController()
    score_controller = ScoreController(action_db,None)

    frame_number = 0
    lines = None
    lastimg = None

    while cap.isOpened():
        fr = Frame()
        if frame_number == 0:
            frame_number += 1
            continue
        return_value, img = cap.read()
        out_image = img.copy()

        if frame_number == 1:
            zone_controller.add_zone(out_image, type=0)
            # zone_controller.add_zone(out_image, type=1)

        if not return_value:
            print("Could not read Frame")
            break

        out_image = zone_controller.draw_zones(out_image)

        image = Image.fromarray(img)
        if mode is "productive":
            image = yolo.detect_image(image)
        else:
            lines = [line.rstrip('\n') for line in open(detection_file)]

        objects = lines[frame_number].split(" ")
        fr.filter_bbox_human(objects[1:])
        fr.filter_bbox_vehicles(objects[1:])
        for elem in fr.list_of_persons:
            touching = zone_controller.get_touching_zones_for_object(elem)  # xmin, ymin, xmax, ymax
            cv2.rectangle(out_image, (elem[0], elem[1]), (elem[2], elem[3]), (255, 0, 0), 1)

            if len(touching) > 0:
                for t in touching:
                    action_db.add(a.ZoneAction(t, frame_number, elem))
            if elem[2] - elem[0] > elem[3] - elem[1]:
                action_db.add(a.FallingAction(frame_number, elem))

        fr.check_for_neighbours()
        for elem in fr.list_of_groups:
            cv2.rectangle(out_image, (elem.min_x, elem.min_y), (elem.max_x, elem.max_y), (0, 255, 0), 2)
            action_db.add(a.GroupAction(len(elem.members),frame_number,[elem.min_x,elem.min_y,elem.max_x,elem.max_y]))

        framescore = score_controller.get_threat_level(frame_number)
        out_image = cv2.putText(out_image, "Threat-Level: "+  str(framescore*100) + "%", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        lastImg = out_image.copy()

        result = np.asarray(image)
        if mode is "output":
            out.write(result)
        cv2.imshow("result", out_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_number += 1
    #out.release()
    cap.release()
    print (action_db)

    cv2.imshow("heatmap", Heatmap(action_db, [], lastImg).draw())
    cv2.waitKey()


    cv2.DestroyAllWindows()
    yolo.close_session()


if __name__ == '__main__':
    run_detection('data/tag.mp4', "none", detection_file="data/detections_tag.txt")
