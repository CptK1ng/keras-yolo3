from yolo import YOLO
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import helpers.actions as a
from helpers.data import Frame
from helpers.zoning import ZoneController
from helpers.score_controller import ScoreController
from helpers.heatmap import Heatmap
from helpers.data import Person
# import the necessary packages
from collections import namedtuple

# Object Detection start
trackers = cv2.MultiTracker_create()
persons = list()
persons_counter_list = list()
person_id = 0

# define the `Detection` object
Detection = namedtuple("Detection", ["image_path", "gt", "pred"])


# Object Detection end

def filter_bbox_human(list_of_bboxes):
    list_of_persons = list()
    for elem in list_of_bboxes:
        if elem is not "" and elem[-1] is "0":
            list_of_persons.append(list(map(int, elem.split(",")[:-1])))
    return list_of_persons


def start_initial_trackers(frame_n, bboxes):
    global person_id
    i = 0
    for box in bboxes:
        persons.append(Person(i, box))
        persons_counter_list.append(0)
        #trackers.add(cv2.TrackerCSRT_create(), frame_n, (box[0], box[1], box[2] - box[0], box[3] - box[1]))
        i += 1
    person_id = i

def get_iou(box_tracker, box_detector, epsilon=1e-5):

    # COORDINATES OF THE INTERSECTION BOX
    x1 = max(box_tracker[0], box_detector[0])
    y1 = max(box_tracker[1], box_detector[1])
    x2 = min(box_tracker[2], box_detector[2])
    y2 = min(box_tracker[3], box_detector[3])

    # AREA OF OVERLAP - Area where the boxes intersect
    width = (x2 - x1)
    height = (y2 - y1)
    # handle case where there is NO overlap
    if (width<0) or (height <0):
        return 0.0
    area_overlap = width * height

    # COMBINED AREA
    area_a = (box_tracker[2] - box_tracker[0]) * (box_tracker[3] - box_tracker[1])
    area_b = (box_detector[2] - box_detector[0]) * (box_detector[3] - box_detector[1])
    area_combined = area_a + area_b - area_overlap

    # RATIO OF AREA OF OVERLAP OVER COMBINED AREA
    iou = area_overlap / (area_combined+epsilon)
    return iou


def run_detection(video_path, mode, output_path=None, detection_file=None):
    global person_id
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


        #Object tracker start
        humans = fr.list_of_persons
        humans_new = humans
        j = 0
        for person in persons:
            if person is None:
                continue

            if person.prev_bbox[0] is person.bbox[0] \
                    and person.prev_bbox[1] is person.bbox[1] \
                    and person.prev_bbox[2] is person.bbox[2] \
                    and person.prev_bbox[3] is person.bbox[3]:
                persons_counter_list[j] += 1
            else:
                persons_counter_list[j] = 0

            person_removed = False
            for counter in persons_counter_list:
                if counter >= 10:
                    persons.remove(person)
                    del (persons_counter_list[j])
                    person_removed = True
                    break
            if person_removed:
                continue

            cv2.rectangle(out_image, (person.bbox[0], person.bbox[1]), (person.bbox[2], person.bbox[3]), (255, 0, 0), 2)
            cv2.putText(out_image, str(person.id), (person.bbox[0], person.bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)
            if person.avg_speed is not None:
                speed = "%.1f" % person.avg_speed
                cv2.putText(out_image, str(speed), (person.bbox[0] + 40, person.bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2)


            inter_secs = np.zeros(len(humans))
            idx_in_humans = 0
            max_intersec = 0
            human_to_delete = None
            for human in humans:
                n_i_s = get_iou(person.bbox, human)
                if n_i_s > max_intersec:
                    max_intersec = n_i_s
                    human_to_delete = human

            if human_to_delete != None:
                person.update_person(human_to_delete)
                humans_new.remove(human_to_delete)

            else:
                max_intersec = 0
                for human in humans:
                    n_i_s = get_iou(person.prev_bbox, human)
                    if n_i_s > max_intersec:
                        max_intersec = n_i_s
                        human_to_delete = human

                person.update_person(persons[j].bbox, True)
                if human_to_delete != None:
                    persons[j].bbox = human_to_delete
                    humans_new.remove(human_to_delete)

            j += 1
        if frame_number > 2:
            for human in humans_new:
                person_id += 1
                persons.append(Person(person_id, human))
                persons_counter_list.append(0)


        if frame_number == 1:
            start_initial_trackers(out_image, fr.list_of_persons)

        # Object tracker end








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
