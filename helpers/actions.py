class Action:
    timestamp = None
    bbox = None

    def __init__(self, timestamp, bbox):
        self.timestamp = timestamp
        self.bbox = bbox

    def __str__(self):
        return "[" + str(self.__class__.__name__) + "] timestamp: " + str(self.timestamp) + ", bbox: " + str(self.bbox) + " "


class FallingAction(Action):
    thisClassHasNoExtraVars = None


class SoundAction(Action):
    thisClassHasNoExtraVars = None


class GroupAction(Action):
    nr_of_people = None

    def __init__(self,nr_of_people,*args, **kwargs): #can be called with GroupAction(nr,timestamp,bbox)
        super(self.__class__, self).__init__(*args, **kwargs)
        self.nr_of_people = nr_of_people

    def __str__(self):
        return str(super(self.__class__, self).__str__()) + ", nr_of_people: " + str(self.nr_of_people)


class ZoneAction(Action):
    zone_id = None

    def __init__(self,zone_id,*args, **kwargs): #can be called with GroupAction(nr,timestamp,bbox)
        super(self.__class__, self).__init__(*args, **kwargs)
        self.zone_id = zone_id

    def __str__(self):
        return str(super(self.__class__, self).__str__()) + ", zone_id: " + str(self.zone_id)





class ActionDB:
    actions = []
    def __init__(self):
        print("")

    def add(self, action):
        self.actions.append(action)

    def __str__(self):
        s = "[" + str(self.__class__.__name__) + "]\n"
        for a in self.actions:
            s += "|-"+str(a)+"\n"
        return s

    def filter(self, action_classes):
        return [a for a in self.actions if a.__class__ in action_classes]



def test_actions():
    db = ActionDB()
    db.add(Action(99, (9,9,19,19))) #timestamp,bbox
    db.add(GroupAction(2, 123, (100,100,200,200))) #nr_of_people,timestamp,bbox
    db.add(FallingAction(4, (150, 150, 300, 300))) #timestamp,bbox
    db.add(ZoneAction(0, 1, (10, 20, 50, 70))) #zoneid,timestamp,bbox
    print(db)


#test_actions()