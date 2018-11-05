def isFalling(bbox):
    #bbox = (xmin, ymin, xmax, ymax)
    return bbox[2] - bbox[0] < bbox[3] - bbox[1]
