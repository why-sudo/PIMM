# -*- coding: utf-8 -*-
import arcpy
import time
import incrementalMatching
import util
import roadFilter
import math

arcpy.env.overwriteOutput = True

def matchProcess(workspace,lengthRatio,radius,step):
    start = time.time()
    track = workspace+'\\track.shp'
    filterCostTime = roadFilter.filterProcess(workspace,lengthRatio,math.pi/2)
    filterRoad = workspace+'\\filter_road_link.shp'
    track_list = []
    road_list = []
    track_cursor = arcpy.da.SearchCursor(track,['shape@'])
    for row in track_cursor:
        track_list.append(row[0])
    road_cursor = arcpy.da.SearchCursor(filterRoad,['shape@','DIRECTION'])
    for row in road_cursor:
        unit = []
        unit.append(row[0])
        unit.append(row[1])
        road_list.append(unit)

    firstTrack = track_list[0]
    arcpy.Delete_management('road_lyr')
    arcpy.MakeFeatureLayer_management(filterRoad, "road_lyr")  # 创建道路图层
    buffer_radius = radius
    while True:
        select_road = util.selecttRelationSegByList(firstTrack,road_list,buffer_radius)
        if len(select_road)==0:
            buffer_radius = buffer_radius + 5
        else:
            break
    dis_list = []
    for i in select_road:
        dis_list.append(firstTrack.distanceTo(i[0]))
    startRoad = select_road[dis_list.index(min(dis_list))]
    startJudgePoint = incrementalMatching.getStartJudgePointByRoadList(filterRoad,startRoad)
    match_road,flag = incrementalMatching.Increment(filterRoad,track,startRoad,startJudgePoint,radius,step)
    res_line = arcpy.CreateFeatureclass_management(workspace, 'relines.shp', 'POLYLINE')
    insertCursor = arcpy.da.InsertCursor(res_line, ['Shape@'])
    for i in match_road:
        insertCursor.insertRow([i])
    del insertCursor
    end = time.time()
    if flag == 0:
        print("Matching completed, total time spent:%.2f秒"%(end-start+filterCostTime))
        return end-start
    else:
        print("error",end-start+filterCostTime)
        return -1

if __name__ == '__main__':
    costTime = matchProcess("demo/20080422111154_1",0.9,20,5)
















