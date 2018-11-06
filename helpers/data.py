class Frame():
    def __init__(self, img=None, list_of_persons=list(), list_of_groups=list(), list_of_vehicles=list(),
                 list_of_zones=list(), image_height=1080, image_width=1920, bboxes=list()):
        self.image = img
        self.list_of_persons = list_of_persons
        self.list_of_groups = list_of_groups
        self.list__of_vehicles = list_of_vehicles
        self.time = None
        self.list_of_zones = list_of_zones
        self.image_width = image_width
        self.image_height = image_height
        self.list_of_bboxes = bboxes

    def filter_bbox_human(self, list_of_bboxes):
        list_of_persons = list()
        for elem in list_of_bboxes:
            if elem is not "" and elem[-1] is "0":
                list_of_persons.append(list(map(int, elem.split(",")[:-1])))
        self.list_of_persons = list_of_persons

    def check_for_neighbours(self):
        x_min, y_min, x_max, y_max = 0, 1, 2, 3
        groups = list()
        for person_idx in range(len(self.list_of_persons)):
            person1 = self.list_of_persons[person_idx]
            for person_to_comp_idx in range(len(self.list_of_persons)):
                if person_idx is person_to_comp_idx:
                    continue
                else:
                    person1_range_top = person1[y_min] - int((person1[y_max] - person1[y_min]) / 2)
                    person1_range_bottom = person1[y_max] + int((person1[y_max] - person1[y_min]) / 2)
                    person1_range_left = int((person1[x_min] - (person1[x_max] - person1[x_min])) * 1.05)
                    person1_range_right = int((person1[x_max] + (person1[x_max] - person1[x_min])) * 1.05)
                    person2 = self.list_of_persons[person_to_comp_idx]

                    # check whether the neighbour is in the near of the bottom or top point of person1
                    if (person1_range_top >= 0) and person1_range_top <= person2[y_min] <= person1[y_min] or \
                            (person1_range_bottom <= self.image_height) and person1_range_bottom <= person2[y_max] <= \
                            person1[
                                y_max]:

                        # check whether the neighbour is in the near of the left or right point of person1
                        if (person1_range_right <= self.image_width) and person1[x_min] <= person2[
                            x_min] <= person1_range_right or \
                                (person1_range_left >= 0) and person1_range_left <= person2[2] <= person1[x_min]:
                            is_already_in_group = False
                            if len(groups) > 0:
                                for g in groups:
                                    if person_idx in g.members and person_to_comp_idx not in g.members:
                                        g.members.append(person_to_comp_idx)
                                        g.update_min_max_values_of_group([self.list_of_persons[person_to_comp_idx]])
                                        is_already_in_group = True
                                        break
                            if not is_already_in_group:
                                new_g = Group(person_idx)
                                new_g.members.append(person_idx)
                                new_g.members.append(person_to_comp_idx)
                                new_g.update_min_max_values_of_group(
                                    [self.list_of_persons[person_idx], self.list_of_persons[person_to_comp_idx]])
                                groups.append(new_g)
        self.list_of_groups = groups


class Person():
    def __init__(self, id, bbox):
        self.id = id
        self.bbox = bbox
        self.prev_bbox = bbox
        self.path = list()
        self.avg_speed = None

    def is_falling(self):
        # bbox = (xmin, ymin, xmax, ymax)
        return self.bbox[2] - self.bbox[0] < self.bbox[3] - self.bbox[1]


class Group():
    def __init__(self, id):
        self.id = id
        self.members = list()
        self.min_x = 20000
        self.min_y = 20000
        self.max_x = 0
        self.max_y = 0
        self.bbox = [self.min_x, self.min_y, self.max_x, self.max_y]

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

            self.bbox = [self.min_x, self.min_y, self.max_x, self.max_y]
