import math

def cur_sum(list):
    angle_e = math.atan2(list[-1][0] - list[-2][0], list[-1][1] - list[-2][1])
    angle_s = math.atan2(list[1][0] - list[0][0], list[1][1] - list[0][1])
    dif_angle = abs(angle_e - angle_s)
    return dif_angle

def Global_similarity(tracklist,roadlist):
    if len(tracklist)>=2 and len(roadlist)>=2:
        tracklist_se = [tracklist[-1],tracklist[0]]
        roadlist_se = [roadlist[-1],roadlist[0]]
        vector_track = [tracklist_se[1][0] - tracklist_se[0][0], tracklist_se[1][1] - tracklist_se[0][1]]
        vector_road = [roadlist_se[1][0] - roadlist_se[0][0], roadlist_se[1][1] - roadlist_se[0][1]]
        Global_similarity = math.atan2(vector_track[1],vector_track[0])-math.atan2(vector_road[1],vector_road[0])
        return Global_similarity
    else:
        pass

def cur_diffence(track,road):
    dif_cur = abs(abs(cur_sum(track)) - abs(cur_sum(road)))
    print(dif_cur)
    return dif_cur

def CalListLength(list):
    print(list)
    length = 0
    for i in range(len(list)-1):
        distance = list[i].distanceTo(list[i+1])
        length = length + distance
    return length

def LengthControl(trackList,projectPointList):

    trackLength = CalListLength(trackList)
    proLength = CalListLength(projectPointList)
    if trackLength == 0 or proLength == 0:
        return False
    aspectRatio = proLength/trackLength
    print("aspectRatio",aspectRatio)
    if aspectRatio >0.3 and aspectRatio <2:
        return True
    else:
        return False

def getLengthControl(trackList,projectPointList):
    trackLength = CalListLength(trackList)
    proLength = CalListLength(projectPointList)
    if trackLength == 0 or proLength == 0:
        return False
    aspectRatio = abs(1-(proLength/trackLength))
    print(aspectRatio)
    return aspectRatio
