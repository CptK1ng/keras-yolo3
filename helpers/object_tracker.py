# import the necessary packages
import argparse
import time
import cv2
from helpers.data import Person

# initialize a dictionary that maps strings to their corresponding
# OpenCV object tracker implementations

'''OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}'''

trackers = cv2.MultiTracker_create()
persons = list()
persons_counter_list = list()
person_id = 0

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
        trackers.add(cv2.TrackerCSRT_create(), frame_n, (box[0], box[1], box[2] - box[0], box[3] - box[1]))
        i += 1
    person_id = i


# import the necessary packages
from collections import namedtuple
import numpy as np
import cv2

# define the `Detection` object
Detection = namedtuple("Detection", ["image_path", "gt", "pred"])



def get_iou(box_tracker, box_detector, epsilon=1e-5):
    """ Given two boxes `a` and `b` defined as a list of four numbers:
            [x1,y1,x2,y2]
        where:
            x1,y1 represent the upper left corner
            x2,y2 represent the lower right corner
        It returns the Intersect of Union score for these two boxes.

    Args:
        box_tracker:          (list of 4 numbers) [x1,y1,x2,y2]
        box_detector:          (list of 4 numbers) [x1,y1,x2,y2]
        epsilon:    (float) Small value to prevent division by zero

    Returns:
        (float) The Intersect of Union score.
    """


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


fname = "../data/detections_tag.txt"
lines = [line.rstrip('\n') for line in open(fname)]



cap = cv2.VideoCapture('../data/tag.mp4')
i = 1
while (cap.isOpened()):
    ret, frame = cap.read()

    objects = lines[i].split(" ")
    humans = filter_bbox_human(objects[1:])
    humans_new = humans
    j = 0

    for person in persons:
        if person is None:
            continue

        if person.id == 22:
            print(person.bbox, person.prev_bbox)
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
                del(persons_counter_list[j])
                person_removed = True
                break
        if person_removed:
            continue

        cv2.rectangle(frame, (person.bbox[0], person.bbox[1]), (person.bbox[2], person.bbox[3]), (0, 255, 0), 2)
        cv2.putText(frame, str(person.id), (person.bbox[0], person.bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
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
            persons[j].prev_bbox = persons[j].bbox
            persons[j].bbox = human_to_delete
            humans_new.remove(human_to_delete)

        else:
            max_intersec = 0
            for human in humans:
                n_i_s = get_iou(person.prev_bbox, human)
                if n_i_s > max_intersec:
                    max_intersec = n_i_s
                    human_to_delete = human

            persons[j].prev_bbox = persons[j].bbox
            if human_to_delete != None:
                persons[j].bbox = human_to_delete
                humans_new.remove(human_to_delete)


        j += 1
    if i > 2:
        for human in humans_new:
            person_id += 1
            persons.append(Person(person_id, human))
            persons_counter_list.append(0)

    cv2.imshow('frame', frame)
    key = cv2.waitKey(1) & 0xFF

    if i == 1:
        objects = lines[1].split(" ")
        start_initial_trackers(frame, filter_bbox_human(objects[1:]))

    i += 1

cap.release()
cv2.destroyAllWindows()

"""
    objects = lines[i].split(" ")
    lst_of_ps = filter_bbox_human(objects[1:])
    groups = check_for_neighbours(lst_of_ps)
    for p in lst_of_ps:
        cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), (255, 0, 0), 1)
    for g in groups:
        cv2.rectangle(frame, (g.min_x, g.min_y), (g.max_x, g.max_y), (0, 255, 0), 1)
"""

'''
    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
    if key == ord("s"):
        # select the bounding box of the object we want to track (make
        # sure you press ENTER or SPACE after selecting the ROI)
        box = cv2.selectROI("Frame", frame, fromCenter=False,
                            showCrosshair=True)

        # create a new object tracker for the bounding box and add it
        # to our multi-object tracker
        tracker = OPENCV_OBJECT_TRACKERS["csrt"]()
        trackers.add(tracker, frame, box)
'''
