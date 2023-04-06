import arcpy

def getIntersectionP(road):
    arcpy.Delete_management('road_lyr')
    arcpy.MakeFeatureLayer_management(road, "road_lyr")
    cursor = arcpy.da.SearchCursor("road_lyr",["SHAPE@"])
    SLpoints=[]
    InsertP=[]
    for row in cursor:
        feat = row[0]
        SLpoints.append((feat.firstPoint,feat.lastPoint))

    for i in range(len(SLpoints)):
        print(i)
        for j in range(2):
            print(j)
            point = arcpy.PointGeometry(arcpy.Point(SLpoints[i][j].X, SLpoints[i][j].Y))
            a = isIntersectionP("road_lyr",point,0.001)
            print(a)
            if a == True:
                InsertP.append(SLpoints[i][j])
            else:
                pass
    print(InsertP)
    result = delDuplicateP(InsertP)
    print(len(result))
    return result

def delDuplicateP(point_list):
    result = []
    location_list = []
    transition = []

    for i in point_list:
        location_list.append((i.X,i.Y))

    for index in range(len(location_list)):
        if location_list[index] in transition:
            pass
        else:
            transition.append(location_list[index])
            result.append(point_list[index])
    return result


def isIntersectionP(road_lyr,point,dist):
    road_select = arcpy.SelectLayerByLocation_management(road_lyr, "WITHIN_A_DISTANCE",point, dist)
    cnt = int(arcpy.GetCount_management(road_select).getOutput(0))
    if cnt > 2:
        return True
    else:
        return False

def getTrackPoints(track):
    """
    Turns track shapefile into a list of point geometries, reprojecting to the planar RS of the network file
    """
    trackpoints = []
    if arcpy.Exists(track):
        for row in arcpy.da.SearchCursor(track, ["SHAPE@"]):
            geom = row[0]
            trackpoints.append(geom)
        print('track size:' + str(len(trackpoints)))
        return trackpoints
    else:
        print("Track file does not exist!")

def getSegmentCandidatates(point,segments,maxdist):
    arcpy.Delete_management('segments_lyr')
    arcpy.MakeFeatureLayer_management(segments, "segments_lyr")
    arcpy.SelectLayerByLocation_management("segments_lyr", "WITHIN_A_DISTANCE", point, maxdist)
    candidates= []
    cursor = arcpy.da.SearchCursor("segments_lyr",["SHAPE@"])
    for row in cursor:
        feat = row[0]
        candidates.append(feat)
    return candidates

def getInsertTrack(InsertP,Track,maxdist):
    select_point = arcpy.SelectLayerByLocation_management(Track, "WITHIN_A_DISTANCE", InsertP, maxdist)
    cursor = arcpy.da.SearchCursor(select_point, ["SHAPE@"])
    InsertTrack =[]
    for row in cursor:
        geom = row[0]
        InsertTrack.append(geom)
    return InsertTrack

def relateR(point,road):
    R = []
    cursor = arcpy.da.SearchCursor(road, ['shape@','DIRECTION'])
    for row in cursor:
        if point.distanceTo(row[0]) <= 0.001:
            unit = []
            unit.append(row[0])
            unit.append(row[1])
            R.append(unit)
    return R

def removeO(OP,points):
    print(len(points))
    for i in points:
        if OP.distanceTo(i)<10:
            print('remove',i)
            points.remove(i)
        else:
            print('zcd')
    return points


def getInsertPShp(line,path,name):
    InsertP = getIntersectionP(line)
    print(InsertP)
    points = arcpy.CreateFeatureclass_management(path, name, 'POINT')
    insertCursor = arcpy.da.InsertCursor(points, ['Shape@'])
    for i in InsertP:
        print(i)
        insertCursor.insertRow([i])
    del insertCursor
    return points

