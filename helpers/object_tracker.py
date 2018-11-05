# import the necessary packages
import argparse
import time
import cv2

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


def filter_bbox_human(list_of_bboxes):
    list_of_persons = list()
    for elem in list_of_bboxes:
        if elem is not "" and elem[-1] is "0":
            list_of_persons.append(list(map(int, elem.split(",")[:-1])))
    return list_of_persons


def start_initial_trackers(frame_n, bboxes):


    for box in bboxes:
        trackers.add(cv2.TrackerCSRT_create(), frame_n, (box[0], box[1], box[2] - box[0], box[3] - box[1]))
        print(len(trackers))



fname = "../data/detections_tag.txt"
lines = [line.rstrip('\n') for line in open(fname)]

cap = cv2.VideoCapture('../data/tag.mp4')
i = 1
while (cap.isOpened()):
    ret, frame = cap.read()

    # object tracker updating and drawing
    #frame = cv2.resize(frame, (1280, 720))
    (success, boxes) = trackers.update(frame)
    # loop over the bounding boxes and draw then on the frame
    for box in boxes:
        (x, y, w, h) = [int(v) for v in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
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
