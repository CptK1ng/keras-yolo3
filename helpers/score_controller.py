from helpers.actions import ActionDB, Action, GroupAction, FallingAction, ZoneAction


class ScoreController(object):
    action_db = None # (reference to) Database of type "ActionDB"

    def __init__(self, action_db):
        self.action_db = action_db

    def get_threat_level(self):
        return len(self.action_db.actions)


def test_sc():
    db = ActionDB()
    sc = ScoreController(db)

    db.add(Action(99, (9, 9, 19, 19)))  # timestamp,bbox
    db.add(GroupAction(2, 123, (100, 100, 200, 200)))  # nr,timestamp,bbox
    db.add(GroupAction(2, 124, (110, 105, 210, 205)))  # nr,timestamp,bbox
    print("THREAD LEVEl: ", sc.get_threat_level())
    db.add(FallingAction(4, (150, 150, 300, 300)))  # timestamp,bbox
    db.add(ZoneAction(0, 1, (10, 20, 50, 70)))  # zoneid,timestamp,bbox
    print(db)

    print("THREAD LEVEl: ", sc.get_threat_level())


#test_sc()