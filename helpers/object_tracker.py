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


def filter_bbox_human(list_of_bboxes):
    list_of_persons = list()
    for elem in list_of_bboxes:
        if elem is not "" and elem[-1] is "0":
            list_of_persons.append(list(map(int, elem.split(",")[:-1])))
    return list_of_persons


def start_initial_trackers(frame_n, bboxes):
    i = 0
    for box in bboxes:
        persons.append(Person(i, box))
        trackers.add(cv2.TrackerCSRT_create(), frame_n, (box[0], box[1], box[2] - box[0], box[3] - box[1]))
        i += 1


# import the necessary packages
from collections import namedtuple
import numpy as np
import cv2

# define the `Detection` object
Detection = namedtuple("Detection", ["image_path", "gt", "pred"])


def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


fname = "../data/detections_tag.txt"
lines = [line.rstrip('\n') for line in open(fname)]

cap = cv2.VideoCapture('../data/tag.mp4')
i = 1
while (cap.isOpened()):
    ret, frame = cap.read()

    # object tracker updating and drawing
    # frame = cv2.resize(frame, (1280, 720))
    (success, boxes) = trackers.update(frame)
    # loop over the bounding boxes and draw then on the frame
    objects = lines[i].split(" ")
    humans = filter_bbox_human(objects[1:])
    humans_new = humans
    j = 0
    for box in boxes:
        (x, y, w, h) = [int(v) for v in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, str(persons[j].id), (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        for human in humans:
            inter_sec = bb_intersection_over_union(box, human)
            if inter_sec > 0.9:
                persons[j].bbox = human
                humans_new.remove(human)

        j += 1
    '''if i > 2:
        for human in humans_new:
            persons.append(Person(len(persons), human))
            trackers.add(cv2.TrackerCSRT_create(), frame, (human[0], human[1], human[2] - human[0], human[3] - human[1]))
    '''
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
