import cv2

class Zone:
    type = None #[Warning=0,Forbidden=1]
    area = [] # Array of Points (x, y)
    # Zone is a polygon with 4 corners

    def __init__(self, type, area):
        self.type = type
        self.area = area

class ZoneController:
    zones = []

    def __init__(self):
        self.defineZones()

    def defineZones(self):
        zone1 = Zone(0,[(120,200),(125,230),(400,600),(450,700)])
        self.zones.append(zone1)

    def drawZones(self, image):
        cv2.polylines(image, zones, isClosed=True, color[, thickness[, lineType[, shift]]]
