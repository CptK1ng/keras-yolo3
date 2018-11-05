import cv2
from helpers.actions import ActionDB, Action, GroupAction, FallingAction, ZoneAction


class Heatmap(object):
    action_db = None # (reference to) Database of type "ActionDB"
    filter = [] #array of action types to put on heatmap, empty for no filter
    bgimage = None #black or white image or frame from livestream, should be size of livestream

    def __init__(self,action_db,filter,bgimage):
        self.action_db = action_db
        self.filter = filter
        self.bgimage = bgimage

    def draw(self):
        img_out = self.bgimage.copy()
        actions = self.action_db.filter(self.filter) if len(self.filter) > 0 else self.action_db.actions

        for a in actions:
            color = (165, 165, 165)  # grey (BGR Color Code)
            if a.__class__ == ZoneAction:
                color = (64, 64, 232)  # red
            if a.__class__ == FallingAction:
                color = (83, 243, 249)  # yellow
            if a.__class__ == GroupAction:
                color = (102, 204, 0)  # green

            # Overlay image with zone translucent over image
            notrans_img = img_out.copy()
            cv2.circle(notrans_img,
                       (int(a.bbox[0] + (a.bbox[2] - a.bbox[0]) / 2), int(a.bbox[1] + (a.bbox[3] - a.bbox[1]) / 2)),
                       radius=20, color=color, thickness=-1, lineType=8, shift=0)
            cv2.addWeighted(notrans_img, 0.2, img_out, 1 - 0.2, 0, img_out)

        return img_out


def test_heatmap():
    db = ActionDB()
    db.add(Action(99, (9, 9, 19, 19)))  # timestamp,bbox
    db.add(GroupAction(2, 123, (100, 100, 200, 200)))  # nr,timestamp,bbox
    db.add(GroupAction(2, 124, (110, 105, 210, 205)))  # nr,timestamp,bbox
    db.add(FallingAction(4, (150, 150, 300, 300)))  # timestamp,bbox
    db.add(ZoneAction(0, 1, (10, 20, 50, 70)))  # zoneid,timestamp,bbox
    print(db)
    image = cv2.imread("../screenshot.jpg")
    hm = Heatmap(db, [GroupAction], image)
    hm_img = hm.draw()
    #cv2.imshow("HM",hm_img)
    #cv2.imshow("HM2", Heatmap(db, [Action, GroupAction, FallingAction, ZoneAction], image).draw())
    cv2.imshow("HM3", Heatmap(db, [], image).draw())

    cv2.waitKey()

test_heatmap()