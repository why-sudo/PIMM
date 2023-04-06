#-*-coding:UTF-8 -*-
import arcpy
import math
import itertools
import incrementalMatching
import time
import util

arcpy.env.overwriteOutput = True

def incrementalPruning(tracklist,roadlist):
    startPoint = tracklist[0]
    endPoint = tracklist[-1]
    filter2_road = []
    startDistance = []
    endDistance = []

    roadListInner = []
    for i in roadlist:
        roadListInner.append(i)
        startDistance.append(startPoint.distanceTo(i))
        endDistance.append(endPoint.distanceTo(i))
    startRoad = roadlist[startDistance.index(min(startDistance))]
    sPoint = startRoad.firstPoint
    if len(util.selecttRelationSegByListOnlyGeo(arcpy.PointGeometry(sPoint),roadListInner,0.001))==1:
        pass
    else:
        sPoint = startRoad.lastPoint
    sJudgedPoint = arcpy.PointGeometry(sPoint)
    sSelectList = incrementalMatching.GetDoubleConnected(roadlist, startRoad, sJudgedPoint)

    endRoad = roadlist[endDistance.index(min(endDistance))]
    ePoint = endRoad.firstPoint
    if len(util.selecttRelationSegByListOnlyGeo(arcpy.PointGeometry(ePoint),roadListInner,0.001))==1:
        pass
    else:
        ePoint = endRoad.lastPoint
    eJudgedPoint = arcpy.PointGeometry(ePoint)
    eSelectList = incrementalMatching.GetDoubleConnected(roadlist, endRoad, eJudgedPoint)

    sampleList = []
    for i in roadListInner:
        startFirstPoint = arcpy.PointGeometry(arcpy.Point(i.firstPoint.X, i.firstPoint.Y))
        startLastPoint = arcpy.PointGeometry(arcpy.Point(i.lastPoint.X, i.lastPoint.Y))
        pointList = [startLastPoint,startFirstPoint]
        for point in pointList:
            if point.equals(sJudgedPoint) or point.equals(eJudgedPoint):
                pass
            else:
                segList = util.selecttRelationSegByListOnlyGeo(point,roadListInner,0.001)
                if len(segList) == 1:
                    judge = pointList[0]
                    if judge.equals(point):
                        sample = [pointList[1],i]
                    else:
                        sample = [judge,i]
                    sampleList.append(sample)
    delRoadList = []
    for i in sampleList:
        delRoadSample = incrementalDelete(roadListInner,i[1],i[0])
        delRoadList.append(delRoadSample)
    delRoadListResult = list(itertools.chain.from_iterable(delRoadList))
    for i in roadListInner:
        if i in delRoadListResult:
            pass
        else:
            filter2_road.append(i)
    return filter2_road,sSelectList,eSelectList

def incrementalDelete(road,startingSection,judgePoint):
    delRoadList = []
    delRoadList.append(startingSection)
    judge = judgePoint
    starting = startingSection

    while True:
        P = util.selecttRelationSegByListOnlyGeo(judge, road,0.001)
        if len(P) >=3:
            break
        elif len(P)==2:
            if P[0].equals(starting):
                starting = P[1]
            elif P[1].equals(starting):
                starting = P[0]
            print(starting.firstPoint,starting.lastPoint)
            judge = incrementalMatching.GetJudgedPoint(starting, judge)
            delRoadList.append(starting)
        elif len(P)==1:
            break
    return delRoadList

def FineEdgeCulling(tracklist,roadlist):
    startPoint = tracklist[0]
    endPoint = tracklist[-1]
    filter2_road = []
    startDistance = []
    endDistance = []
    for i in roadlist:
        startDistance.append(startPoint.distanceTo(i))
        endDistance.append(endPoint.distanceTo(i))
    startRoad = roadlist[startDistance.index(min(startDistance))]
    sPoint = startRoad.firstPoint
    for i in roadlist:
        if sPoint.equals(i.firstPoint) or sPoint.equals(i.lastPoint):
            sPoint = startRoad.lastPoint
            break
        else:
            pass
    sJudgedPoint = arcpy.PointGeometry(sPoint)
    sSelectList = incrementalMatching.GetDoubleConnected(roadlist,startRoad,sJudgedPoint)
    for i in sSelectList:
        filter2_road.append(i)
    fre_brokenLine = 2
    startFre = 1
    roadListInner = []
    for i in roadlist:
        roadListInner.append(i)
    roadListLength = len(roadListInner)
    while startFre  <=  1*fre_brokenLine:
        for i in roadListInner:
            startcount = 0
            endcount = 0
            for j in roadListInner:
                if i==j:
                    pass
                else:
                    if i.firstPoint.equals(j.firstPoint) or i.firstPoint.equals(j.lastPoint):
                        startcount = startcount + 1
                    elif i.lastPoint.equals(j.firstPoint) or i.lastPoint.equals(j.lastPoint):
                        endcount = endcount + 1
                    else:
                        pass
            if startcount == 0 or endcount == 0:
                roadListInner.remove(i)

        if roadListLength == len(roadListInner):
            startFre = startFre + 1
        else:
            pass
        roadListLength = len(roadListInner)

    for i in roadListInner:
        filter2_road.append(i)

    endRoad = roadlist[endDistance.index(min(endDistance))]
    ePoint = endRoad.firstPoint
    for i in roadlist:
        if ePoint.equals(i.firstPoint) or ePoint.equals(i.lastPoint):
            ePoint = endRoad.lastPoint
            break
        else:
            pass
    eJudgedPoint = arcpy.PointGeometry(ePoint)
    eSelectList = incrementalMatching.GetDoubleConnected(roadlist,endRoad,eJudgedPoint)
    for i in eSelectList:
        filter2_road.append(i)
    return filter2_road

def filterProcess(workspace,lengthRatio,angleDifference):
    print("-"*10 + "start filtering" + "-"*10)
    arcpy.env.workspace = workspace
    roadPath = workspace+"\\road.shp"
    track = 'track.shp'
    road = 'road.shp'
    start = time.time()
    track_list = []
    road_list = []
    track_cursor = arcpy.da.SearchCursor(track, ['shape@'])
    for row in track_cursor:
        track_list.append(row[0])
    road_cursor = arcpy.da.SearchCursor(road, ['shape@'])
    for row in road_cursor:
        road_list.append(row[0])
    fields = arcpy.ListFields(road)
    fields_name = []
    angle_filter = []
    for i in range(len(track_list)):
        angle_filter.append([])

    arcpy.Delete_management('road_lyr')
    arcpy.MakeFeatureLayer_management(road, "road_lyr")
    select_road = []
    for i in fields:
        fields_name.append(str(i.name))
    segmentCursor = arcpy.da.SearchCursor("road_lyr",['shape@','DIRECTION'])
    wwwlist = []
    for row in segmentCursor:
        wwwlist.append([row[0], str(int(row[1]))])
    if 'DIRECTION' in fields_name:
        for i in range(len(track_list)):
            radius = 30
            while True:
                select = util.selectSegT(track_list[i],wwwlist,radius)
                if len(select)==0:
                    radius = radius + 5
                else:
                    break
            select_road.append(select)
        fre_angle = 1
        start_angle = 1
        while start_angle <= 1 * fre_angle:
            for i in range(len(select_road) - 1):
                for j in select_road[i]:
                    for k in select_road[i + 1]:
                        j_firstPoint = j[0].firstPoint
                        j_lastPoint = j[0].lastPoint
                        k_firstPoint = k[0].firstPoint
                        k_lastPoint = k[0].lastPoint
                        if j[1] == '3' and k[1] == '3':
                            j_firstPoint = j[0].lastPoint
                            j_lastPoint = j[0].firstPoint
                            k_firstPoint = k[0].lastPoint
                            k_lastPoint = k[0].firstPoint
                        elif j[1] == '3' and k[1] == '2':
                            j_firstPoint = j[0].lastPoint
                            j_lastPoint = j[0].firstPoint
                        elif j[1] == '2' and k[1] == '3':
                            k_firstPoint = k[0].lastPoint
                            k_lastPoint = k[0].firstPoint
                        elif j[1] == '2' and k[1] == '2':
                            pass
                        elif j[1] == '3' and k[1] == '1':
                            j_firstPoint = j[0].lastPoint
                            j_lastPoint = j[0].firstPoint
                        elif j[1] == '2' and k[1] == '1':
                            pass
                        elif j[1] == '1' and k[1] == '3':
                            k_firstPoint = k[0].lastPoint
                            k_lastPoint = k[0].firstPoint
                        elif j[1] == '1' and k[1] == '2':
                            pass
                        elif j[1] == '1' and k[1] == '1':
                            pass
                        else:
                            print('error')
                        if j[1] == '1' or k[1] == '1':
                            if j[0].firstPoint.equals(k[0].firstPoint) or j[0].firstPoint.equals(k[0].lastPoint) or j[
                                0].lastPoint.equals(k[0].firstPoint) or j[0].lastPoint.equals(k[0].lastPoint):
                                track_j_list = j[0].queryPointAndDistance(track_list[i])
                                track_k_list = k[0].queryPointAndDistance(track_list[i + 1])
                                track_j = track_j_list[0]
                                track_k = track_k_list[0]
                                print(track_list[i].firstPoint.X, track_list[i].firstPoint.Y)
                                LenRatio = ((track_j.distanceTo(track_k) / track_list[i].distanceTo(track_list[i + 1])))
                                if LenRatio < lengthRatio:
                                    pass
                                else:
                                    angle_filter[i].append(j)
                                    angle_filter[i + 1].append(k)

                        elif (j[1] == '3' and k[1] == '1') or (j[1] == '2' and k[1] == '1'):
                            if j_lastPoint.equals(k_firstPoint) or j_lastPoint.equals(k_lastPoint):
                                track_j_list = j[0].queryPointAndDistance(track_list[i])
                                track_k_list = k[0].queryPointAndDistance(track_list[i + 1])
                                track_j = track_j_list[0]
                                track_k = track_k_list[0]
                                LenRatio = ((track_j.distanceTo(track_k) / track_list[i].distanceTo(track_list[i + 1])))
                                if LenRatio < lengthRatio:
                                    pass
                                else:
                                    vector_track = [track_list[i + 1].firstPoint.X - track_list[i].firstPoint.X,
                                                    track_list[i + 1].firstPoint.Y - track_list[i].firstPoint.Y]
                                    vector_road = [track_k.firstPoint.X - track_j.firstPoint.X,
                                                   track_k.firstPoint.Y - track_j.firstPoint.Y]
                                    AngleDifference = math.atan2(vector_track[1], vector_track[0]) - math.atan2(
                                        vector_road[1], vector_road[0])
                                    if AngleDifference < angleDifference:
                                        angle_filter[i].append(j)
                                        angle_filter[i + 1].append(k)
                            else:
                                pass

                        elif (j[1] == '1' and k[1] == '2') or (j[1] == '1' and k[1] == '3'):
                            if k_firstPoint.equals(j_firstPoint) or k_firstPoint.equals(k_lastPoint):
                                track_j_list = j[0].queryPointAndDistance(track_list[i])
                                track_k_list = k[0].queryPointAndDistance(track_list[i + 1])
                                track_j = track_j_list[0]
                                track_k = track_k_list[0]
                                LenRatio = ((track_j.distanceTo(track_k) / track_list[i].distanceTo(track_list[i + 1])))
                                if LenRatio < lengthRatio:
                                    pass
                                else:
                                    vector_track = [track_list[i + 1].firstPoint.X - track_list[i].firstPoint.X,
                                                    track_list[i + 1].firstPoint.Y - track_list[i].firstPoint.Y]
                                    vector_road = [track_k.firstPoint.X - track_j.firstPoint.X,
                                                   track_k.firstPoint.Y - track_j.firstPoint.Y]
                                    AngleDifference = math.atan2(vector_track[1], vector_track[0]) - math.atan2(
                                        vector_road[1], vector_road[0])
                                    if AngleDifference < angleDifference:
                                        angle_filter[i].append(j)
                                        angle_filter[i + 1].append(k)
                            else:
                                pass

                        else:
                            if j_lastPoint.equals(k_firstPoint):
                                track_j_list = j[0].queryPointAndDistance(track_list[i])
                                track_k_list = k[0].queryPointAndDistance(track_list[i + 1])
                                track_j = track_j_list[0]
                                track_k = track_k_list[0]
                                LenRatio = ((track_j.distanceTo(track_k) / track_list[i].distanceTo(track_list[i + 1])))
                                if LenRatio < lengthRatio:
                                    pass
                                else:
                                    vector_track = [track_list[i + 1].firstPoint.X - track_list[i].firstPoint.X,
                                                    track_list[i + 1].firstPoint.Y - track_list[i].firstPoint.Y]
                                    vector_road = [track_k.firstPoint.X - track_j.firstPoint.X,
                                                   track_k.firstPoint.Y - track_j.firstPoint.Y]
                                    AngleDifference = math.atan2(vector_track[1], vector_track[0]) - math.atan2(
                                        vector_road[1], vector_road[0])
                                    if AngleDifference < angleDifference:
                                        angle_filter[i].append(j)
                                        angle_filter[i + 1].append(k)
                            else:
                                pass
            start_angle = start_angle + 1
    f1time = time.time()
    filter1_road = []
    for i in range(len(angle_filter)):
        for j in angle_filter[i]:
            if j[0] in filter1_road:
                pass
            else:
                filter1_road.append(j[0])

    filterRoad = filter1_road
    filterLength = len(filterRoad)

    while True:
        filter2_road,sSelectList,eSelectList = incrementalPruning(track_list,filterRoad)
        if len(filter2_road)==filterLength:
            break
        else:
            filterRoad = filter2_road
            filterLength = len(filterRoad)
    crs = arcpy.SpatialReference(4548)
    fliter_road = workspace+"\\filter_road.shp"
    filter_road_link = workspace+"\\filter_road_link"
    line = arcpy.CreateFeatureclass_management(workspace, 'filter_road.shp','POLYLINE',"","","",crs)
    insertCursor = arcpy.da.InsertCursor(line, ['Shape@'])
    for i in filterRoad:
        insertCursor.insertRow([i])
    del insertCursor
    arcpy.SpatialJoin_analysis(fliter_road,roadPath,filter_road_link,"JOIN_ONE_TO_ONE","","","CONTAINS")

    end = time.time()
    costTime = f1time-start
    print("filtering process cost time:%.2f秒"%(end-start))
    arcpy.Delete_management(fliter_road)
    return costTime








