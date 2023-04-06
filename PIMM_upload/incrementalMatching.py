# -*- coding: utf-8 -*-
import arcpy
import ruleMatch
import curvature
import math
import time
def segments_select(track,road,startInsertPoint):
    P = ruleMatch.relateR(startInsertPoint,road)
    Q_Track = []
    R = ruleMatch.getInsertTrack(startInsertPoint, track, 30)
    for trackpoint in R:
        Q_Track.append([trackpoint.firstPoint.X, trackpoint.firstPoint.Y])
    print('Q_trcak',Q_Track)
    if Q_Track == []:
        return 0
    else:
        projection = [] #[[[firstRoad,secondRoad],[track1,track2,...,trackn]],[[firstRoad,secondRoad],[track1,track2,...,trackn]],[[firstRoad,secondRoad],[track1,track2,...,trackn]]]
        for firstRoad in P:
            for secondRoad in P:
                projectionList = []
                projecttionPointList = []
                currentSection = [firstRoad,secondRoad]
                projectionList.append(currentSection)
                for point in R:
                    distance = []
                    for selectR in currentSection:
                        distance.append(point.distanceTo(selectR))
                    select_road = currentSection[distance.index(min(distance))]
                    projecttionPoint = select_road.queryPointAndDistance(point)
                    projecttionPointList.append(projecttionPoint[0])
                projectionList.append(projecttionPointList)
                projection.append(projectionList)
        difference = []
        for i in projection:
            if curvature.LengthControl(R,i[1])==True:
                P_road = []
                for j in i[1]:
                    P_road.append([j.firstPoint.X,j.firstPoint.Y])
                cur_difference = curvature.cur_diffence(Q_Track,P_road)
                difference.append(cur_difference)
            else:
                difference.append(1000)
        print('difference',difference)
        selectRoads = projection[difference.index(min(difference))][0]
        print(selectRoads[0].firstPoint,selectRoads[0].lastPoint,selectRoads[1].firstPoint,selectRoads[1].lastPoint)
        selectRoad = selectRoads[0]
        if R[-1].distanceTo(selectRoads[0])>R[-1].distanceTo(selectRoads[1]):
            selectRoad = selectRoads[1]
        else:
            pass
        judgePoint = GetJudgedPoint(selectRoad,startInsertPoint)

        return selectRoad,judgePoint

def GetJudgedPoint(selectRoad,previousPoint):
    selectRoadPoints = [selectRoad.firstPoint,selectRoad.lastPoint]
    judgePoint = selectRoadPoints[1]
    if selectRoadPoints[0].equals(previousPoint):
        pass
    else:
        judgePoint = arcpy.Point(selectRoadPoints[0].X,selectRoadPoints[0].Y)
    judgePoint = arcpy.PointGeometry(judgePoint)
    return judgePoint

def front_back_judge(insp,R):
    Q_Track = []
    for trackpoint in R:
        Q_Track.append([trackpoint.firstPoint.X, trackpoint.firstPoint.Y])
    frontTrack = []
    behindTrack = []
    for i in range(len(Q_Track) - 1):
        points = [Q_Track[i], Q_Track[i + 1]]
        path = arcpy.Array([arcpy.Point(*p) for p in points])
        line_Geometry = arcpy.Polyline(path)
        insertProjList = line_Geometry.queryPointAndDistance(insp)
        insertProj = insertProjList[0]
        if insertProj.firstPoint.X == Q_Track[i][0] and insertProj.firstPoint.Y == Q_Track[i][1]:
            if Q_Track[i] in behindTrack:
                pass
            else:
                behindTrack.append(Q_Track[i])

            if Q_Track[i + 1] in behindTrack:
                pass
            else:
                behindTrack.append(Q_Track[i + 1])

        elif insertProj.firstPoint.X == Q_Track[i + 1][0] and insertProj.firstPoint.Y == Q_Track[i + 1][1]:
            if Q_Track[i] in frontTrack:
                pass
            else:
                frontTrack.append(Q_Track[i])

            if Q_Track[i + 1] in frontTrack:
                pass
            else:
                frontTrack.append(Q_Track[i + 1])

        else:
            if Q_Track[i] in frontTrack:
                pass
            else:
                frontTrack.append(Q_Track[i])

            if Q_Track[i + 1] in behindTrack:
                pass
            else:
                behindTrack.append(Q_Track[i + 1])
    return Q_Track,frontTrack,behindTrack


def Increment(road,track,startingSection,judgePoint,radius = 20,step = 5): #增量过程
    print("-"*10 + "start increment matching"+"-"*10)
    flag = 0
    startTime = time.time()
    match_road = []
    match_road.append(startingSection[0])
    judge = judgePoint
    starting = startingSection

    while True:
        cost = time.time()-startTime
        if cost>99999999999:
            flag = -1
            break
        else:
            P = ruleMatch.relateR(judge,road)
            if len(P)==1:
                break
            elif len(P)==2:
                if P[0][0].equals(starting[0]):
                    starting = P[1]
                else:
                    starting = P[0]
                judge = GetJudgedPoint(starting[0],judge)
                if starting[0] in match_road:
                    flag = -1
                    break
                match_road.append(starting[0])
            elif len(P)>=3:
                projection = []
                while True:
                    R = ruleMatch.getInsertTrack(judge, track, radius)
                    if len(R) <= 1:
                        radius = radius + step
                    else:
                        Q_Track,frontTrack,behindTrack = front_back_judge(judge, R)
                        if len(frontTrack) == 0 or len(behindTrack)==0:
                            radius = radius + step
                        else:
                            break
                for i in P:
                    if i[0].equals(starting[0]):
                        pass
                    else:
                            currentSection = [starting, i]
                            projectionList = []
                            projecttionPointList = []
                            pointToCurDistance = []
                            for pointXY in frontTrack:
                                arcpyPoint = arcpy.Point(pointXY[0],pointXY[1])
                                point = arcpy.PointGeometry(arcpyPoint)
                                projecttionPointFront = currentSection[0][0].queryPointAndDistance(point)
                                projecttionPointBack = currentSection[1][0].queryPointAndDistance(point)
                                if projecttionPointFront[2]>=projecttionPointBack[2]:
                                    projecttionPointList.append(projecttionPointBack[0])
                                    pointToCurDistance.append(projecttionPointBack[2])
                                elif projecttionPointFront[2]<projecttionPointBack[2]:
                                    projecttionPointList.append(projecttionPointFront[0])
                                    pointToCurDistance.append(projecttionPointFront[2])
                            projecttionPointList.append(judge)
                            trackCount = 0
                            for pointXY in behindTrack:
                                arcpyPoint = arcpy.Point(pointXY[0],pointXY[1])
                                point = arcpy.PointGeometry(arcpyPoint)
                                projecttionPointFront = currentSection[0][0].queryPointAndDistance(point)
                                projecttionPointBack = currentSection[1][0].queryPointAndDistance(point)
                                if projecttionPointFront[2]>projecttionPointBack[2]:
                                    projecttionPointList.append(projecttionPointBack[0])
                                    pointToCurDistance.append(projecttionPointBack[2])
                                elif projecttionPointFront[2]<projecttionPointBack[2]:
                                    projecttionPointList.append(projecttionPointFront[0])
                                    pointToCurDistance.append(projecttionPointFront[2])
                                elif projecttionPointFront[2]==projecttionPointBack[2]:
                                    projecttionPointList.append(projecttionPointBack[0])
                                    pointToCurDistance.append(projecttionPointBack[2])
                                    trackCount = trackCount + 1
                            print("pointToCurDistance",pointToCurDistance)
                            if trackCount == len(behindTrack):
                                pass
                            else:
                                projectionList.append(currentSection)
                                print(pointToCurDistance)
                                hausdorffDistance = math.e ** (max(pointToCurDistance))
                                print("hausdorffDistance:{0}".format(hausdorffDistance))
                                projectionList.append(projecttionPointList)
                                projectionList.append(hausdorffDistance)
                                projection.append(projectionList)
                difference = []
                for i in projection:
                    if curvature.LengthControl(R,i[1])==True:
                        P_road = []
                        for j in i[1]:
                            P_road.append([j.firstPoint.X,j.firstPoint.Y])
                        cur_difference = curvature.cur_diffence(Q_Track,P_road) * i[2]
                        difference.append(cur_difference)
                    else:
                        difference.append(float('inf'))
                print('difference',difference)
                selectRoads = projection[difference.index(min(difference))][0]
                selectRoad = selectRoads[1]
                starting = selectRoad
                judgedPoint = GetJudgedPoint(selectRoad[0],judge)
                judge = judgedPoint
                if starting[0] in match_road:
                    flag = -1
                    break
                else:
                    match_road.append(starting[0])
            else:
                print('error')
                break
    print(match_road)
    return match_road,flag

def relateR(point,road):
    selsect_line = arcpy.SelectLayerByLocation_management(road, "WITHIN_A_DISTANCE", point, 0.1)
    print(selsect_line)
    cursor = arcpy.da.SearchCursor(selsect_line, ["SHAPE@"])
    R = []
    for row in cursor:
        geom = row[0]
        R.append(geom)
    return R

def GetDoubleConnected(roadlist,startingSection,judgePoint):
    match_road = []
    match_road.append(startingSection)
    judge = judgePoint
    starting = startingSection
    while True:
        P = []
        for i in roadlist:
            if judge.distanceTo(i)==0:
                P.append(i)
        print('P',len(P))
        for i in P:
            print(i.firstPoint,i.lastPoint)
        if len(P)==1:
            break
        elif len(P)==2:
            if P[0].equals(starting):
                starting = P[1]
            else:
                starting = P[0]
            judge = GetJudgedPoint(starting,judge)
            match_road.append(starting)
        elif len(P)>=3:
            break
        else:
            print('topology error')
    print(match_road)
    return match_road


def getStartJudgePoint(road,startRoad):
    startRoadList = []
    startFirstPoint = arcpy.Point(startRoad.firstPoint.X, startRoad.firstPoint.Y)
    startLastPoint = arcpy.Point(startRoad.lastPoint.X, startRoad.lastPoint.Y)
    startRoadList.append(arcpy.PointGeometry(startFirstPoint))
    startRoadList.append(arcpy.PointGeometry(startLastPoint))
    startJudgePoint = startRoadList[0]
    for i in startRoadList:
        P = ruleMatch.relateR(i, road)
        if len(P) != 1:
            startJudgePoint = i
    return startJudgePoint

def getStartJudgePointByRoadList(road,startRoadF):
    startRoad = startRoadF[0]
    startRoadList = []
    startFirstPoint = arcpy.Point(startRoad.firstPoint.X, startRoad.firstPoint.Y)
    startLastPoint = arcpy.Point(startRoad.lastPoint.X, startRoad.lastPoint.Y)
    startRoadList.append(arcpy.PointGeometry(startFirstPoint))
    startRoadList.append(arcpy.PointGeometry(startLastPoint))
    startJudgePoint = startRoadList[0]
    for i in startRoadList:
        P = ruleMatch.relateR(i, road)
        if len(P) != 1:
            startJudgePoint = i
    return startJudgePoint



