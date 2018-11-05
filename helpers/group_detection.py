import cv2

image_width = 1920
image_height = 1080


class Group():
    def __init__(self, id):
        self.id = id
        self.members = list()
        self.min_x = 20000
        self.min_y = 20000
        self.max_x = 0
        self.max_y = 0

    def update_min_max_values_of_group(self, list_of_bboxes):
        for elem in list_of_bboxes:
            if elem[0] < self.min_x:
                self.min_x = elem[0]
            if elem[1] < self.min_y:
                self.min_y = elem[1]
            if elem[2] > self.max_x:
                self.max_x = elem[2]
            if elem[3] > self.max_y:
                self.max_y = elem[3]


def filter_bbox_human(list_of_bboxes):
    list_of_persons = list()
    for elem in list_of_bboxes:
        if elem is not "" and elem[-1] is "0":
            list_of_persons.append(list(map(int, elem.split(",")[:-1])))
    return list_of_persons


def check_for_neighbours(list_of_persons):
    global image_height, image_width
    x_min, y_min, x_max, y_max = 0, 1, 2, 3
    neighbours = list()
    groups = list()
    for person_idx in range(len(list_of_persons)):
        person1 = list_of_persons[person_idx]
        for person_to_comp_idx in range(len(list_of_persons)):
            if person_idx is person_to_comp_idx:
                continue
            else:
                person1_range_top = person1[y_min] - int((person1[y_max] - person1[y_min]) / 2)
                person1_range_bottom = person1[y_max] + int((person1[y_max] - person1[y_min]) / 2)
                person1_range_left = int((person1[x_min] - (person1[x_max] - person1[x_min])) * 1.05)
                person1_range_right = int((person1[x_max] + (person1[x_max] - person1[x_min])) * 1.05)
                person2 = list_of_persons[person_to_comp_idx]

                # check whether the neighbour is in the near of the bottom or top point of person1
                if (person1_range_top >= 0) and person1_range_top <= person2[y_min] <= person1[y_min] or \
                        (person1_range_bottom <= image_height) and person1_range_bottom <= person2[y_max] <= person1[
                    y_max]:

                    # check whether the neighbour is in the near of the left or right point of person1
                    if (person1_range_right <= image_width) and person1[x_min] <= person2[
                        x_min] <= person1_range_right or \
                            (person1_range_left >= 0) and person1_range_left <= person2[2] <= person1[x_min]:
                        is_already_in_group = False
                        if len(groups) > 0:
                            for g in groups:
                                if person_idx in g.members and person_to_comp_idx not in g.members:
                                    g.members.append(person_to_comp_idx)
                                    g.update_min_max_values_of_group([list_of_persons[person_to_comp_idx]])
                                    is_already_in_group = True
                                    break
                        if not is_already_in_group:
                            new_g = Group(person_idx)
                            new_g.members.append(person_idx)
                            new_g.members.append(person_to_comp_idx)
                            new_g.update_min_max_values_of_group(
                                [list_of_persons[person_idx], list_of_persons[person_to_comp_idx]])
                            groups.append(new_g)
    return groups


fname = "../data/detections_tag.txt"
lines = [line.rstrip('\n') for line in open(fname)]

cap = cv2.VideoCapture('../data/tag.mp4')
i = 1
while (cap.isOpened()):
    ret, frame = cap.read()
    objects = lines[i].split(" ")
    lst_of_ps = filter_bbox_human(objects[1:])
    groups = check_for_neighbours(lst_of_ps)
    for p in lst_of_ps:
        cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), (255, 0, 0), 1)
    for g in groups:
        cv2.rectangle(frame, (g.min_x, g.min_y), (g.max_x, g.max_y), (0, 255, 0), 1)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i += 1

cap.release()
cv2.destroyAllWindows()
