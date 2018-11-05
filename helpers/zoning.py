import cv2
import numpy as np


class PolygonDrawer(object):
    # ===============================================
    # POLYGON DRAWER modified from
    # https://stackoverflow.com/questions/37099262/
    # ===============================================
    def __init__(self, window_name, image):
        self.window_name = window_name  # Name for our window
        self.done = False  # Flag signalling we're done
        self.current = (0, 0)  # Current position, so we can draw the line-in-progress
        self.points = []  # List of points defining our polygon
        self.image = image
        self.canvas_size = image.shape if image is not None else (600, 800)
        self.final_line_color = (255, 255, 255)
        self.working_line_color = (127, 127, 127)

    def on_mouse(self, event, x, y, buttons, user_param):
        # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)

        if self.done:  # Nothing more to do
            return

        if event == cv2.EVENT_MOUSEMOVE:
            # We want to be able to draw the line-in-progress, so update current mouse position
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            # Left click means adding a point at current position to the list of points
            print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
            self.points.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click means we're done
            print("Completing polygon with %d points." % len(self.points))
            self.done = True

    def run(self):
        # Let's create our working window and set a mouse callback to handle events
        cv2.namedWindow(self.window_name, flags=cv2.WINDOW_AUTOSIZE)
        cv2.imshow(self.window_name, np.zeros(self.canvas_size, np.uint8))
        cv2.waitKey(1)
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        while (not self.done):
            # This is our drawing loop, we just continuously draw new images
            # and show them in the named window
            canvas = self.image if self.image is not None else np.zeros(self.canvas_size, np.uint8)
            if (len(self.points) > 0):
                # Draw all the current polygon segments
                cv2.polylines(canvas, np.array([self.points]), False, self.final_line_color, 1)
                # And  also show what the current segment would look like
                cv2.line(canvas, self.points[-1], self.current, self.working_line_color)
            # Update the window
            cv2.imshow(self.window_name, canvas)
            # And wait 50ms before next iteration (this will pump window messages meanwhile)
            if cv2.waitKey(50) == 27:  # ESC hit
                self.done = True

        # User finised entering the polygon points, so let's make the final drawing
        canvas = np.zeros(self.canvas_size, np.uint8)
        # of a filled polygon
        if (len(self.points) > 0):
            cv2.fillPoly(canvas, np.array([self.points]), self.final_line_color)
        # And show it
        cv2.imshow(self.window_name, canvas)
        # Waiting for the user to press any key
        # cv2.waitKey()

        cv2.destroyWindow(self.window_name)
        return canvas


# ============================================================================


class Zone:
    type = None  # [Warning=0,Forbidden=1,OK=2, Gray=else]
    area = []  # Array of Points (x, y)

    # Zone is a polygon with 4 corners

    def __init__(self, type, area):
        self.type = type
        self.area = area


class ZoneController():
    def __init__(self):
        self.zones = []

    def add_zone(self, image, type):
        # Add Zone interactively
        # zone1 = Zone(0,[(120,200),(125,230),(400,600),(450,700)])
        # poly = [(257, 144), (657, 263), (519, 478), (283, 383), (399, 126), (142, 286), (165, 38)]
        pd = PolygonDrawer("Polygon", self.draw_zones(image.copy()))
        pd.run()
        print("Polygon = %s" % pd.points)
        poly = pd.points
        self.zones.append(Zone(type, poly))

    def draw_zones(self, image):
        for zo in self.zones:
            color = (165, 165, 165)  # grey (BGR Color Code)
            if zo.type == 0:
                color = (64, 64, 232)  # red
            if zo.type == 1:
                color = (83, 243, 249)  # yellow
            if zo.type == 2:
                color = (102, 204, 0)  # green
            # Overlay image with zone translucent over image
            image_with_zone = image.copy()
            cv2.fillPoly(image_with_zone, np.array([zo.area]), color)
            cv2.addWeighted(image_with_zone, 0.2, image, 1 - 0.2, 0, image)
        return image

    def get_touching_zones_for_object(self, bbox):
        # returns the zones that the foot touches
        # bbox = (xmin, ymin, xmax, ymax)
        foot_center = (bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[3])
        touched_zones = []
        for zo_nr, zo in enumerate(self.zones):
            zo_area_contour = np.array(zo.area).reshape((-1, 1, 2)).astype(np.int32)
            # cv2.imshow("cntr",cv2.drawContours(image,[zo_area_contour],0,(255,255,255),1))
            # cv2.waitKey()
            if cv2.pointPolygonTest(zo_area_contour, foot_center, False) >= 0:
                touched_zones.append(zo_nr)
        return touched_zones


def test_zoning():
    image = cv2.imread("../screenshot.jpg")
    z = ZoneController()
    z.add_zone(image, type=0)
    z.add_zone(image, type=1)

    imageWithZones = z.draw_zones(image)
    cv2.imshow("test", imageWithZones)
    cv2.waitKey()

    # foreach person bbox:
    touching = z.get_touching_zones_for_object((100, 100, 200, 200))  # xmin, ymin, xmax, ymax
    if len(touching) > 0:
        print("Object is touching the following zones:", touching)

# test_zoning()

# TODO: Zählen der Personen in der jew. Zone
# TODO: Funktion um Typ der Zone bei Touching Zones zu bekommen
# for id in touching: print(z.zones[id].type)
