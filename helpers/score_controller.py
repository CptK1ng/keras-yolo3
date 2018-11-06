from helpers.actions import ActionDB, Action, GroupAction, FallingAction, ZoneAction


class ScoreController(object):
    action_db = None # (reference to) Database of type "ActionDB"
    frames = None

    def __init__(self, action_db, frames):
        self.action_db = action_db
        self.frames = frames

    def get_feel_good_level(self, framenr=None):
        return 1-self.get_threat_level(framenr)
        #if framenr is None:
        #    return len(self.action_db.filter([]))
        #else:
        #    return False # else calc frame level score

    def get_threat_level(self, framenr=None):
        if framenr is None:
            return len(self.action_db.actions)#+self.frames.nr_of_cars
        else:
            nr_of_persons = 0
            nr_of_groups = 0
            nr_of_cars = 0
            nr_of_warning_zones = 0
            nr_of_danger_zones = 0
            avg_person_speed = 4
            nr_of_falling = 0
            isHighVol = False
            time_day = True
            if time_day:
                score = int(nr_of_persons >= 100)*0.15+int(nr_of_groups >= 10)*0.05\
                    +int(nr_of_cars >= 1)*0.2+int(nr_of_warning_zones >= 5)*0.05\
                    +int(nr_of_danger_zones >= 1)*0.1+int(avg_person_speed>=6)*0.1\
                    +int(nr_of_falling>=1)*0.25+int(isHighVol)*0.1
            else:
                score = int(nr_of_persons >= 30 or nr_of_persons <= 5) * 0.15 \
                    +int(nr_of_groups >= 1)*0.15\
                    +int(nr_of_cars >= 1)*0.2+int(nr_of_warning_zones >= 1)*0.05\
                    +int(nr_of_danger_zones >= 1)*0.1+int(avg_person_speed>=6)*0.05\
                    +int(nr_of_falling>=1)*0.2+int(isHighVol)*0.15

            return score


def test_sc():
    db = ActionDB()
    sc = ScoreController(db, None)

    db.add(Action(99, (9, 9, 19, 19)))  # timestamp,bbox
    db.add(GroupAction(2, 123, (100, 100, 200, 200)))  # nr,timestamp,bbox
    db.add(GroupAction(2, 124, (110, 105, 210, 205)))  # nr,timestamp,bbox
    print("THREAD LEVEl: ", sc.get_threat_level())
    db.add(FallingAction(4, (150, 150, 300, 300)))  # timestamp,bbox
    db.add(ZoneAction(0, 1, (10, 20, 50, 70)))  # zoneid,timestamp,bbox
    print(db)

    print("FEEL GOOD LEVEl: ", sc.get_feel_good_level())
    print("THREAD LEVEl: ", sc.get_threat_level())

    print("IN FRAME 30")
    t = sc.get_threat_level(30)
    print("FEEL GOOD LEVEl: ", 1-t)
    print("THREAD LEVEl: ", t)

test_sc()