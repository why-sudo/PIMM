import arcpy

def selectRelationSegWithDirection(point,layer,distance):
    relationSeg = []
    segmentCursor = arcpy.da.SearchCursor(layer,['shape@','DIRECTION'])
    for row in segmentCursor:
        if point.distanceTo(row[0]) <= distance:
            relationSeg.append([row[0], str(row[1])])
    return relationSeg

def selectSegT(point,segList,distance):
    relationSeg = []
    for i in segList:
        if point.distanceTo(i[0]) <= distance:
            relationSeg.append(i)
    return relationSeg

def selecttRelationSegByList(point,segList,distance):
    relationSeg = []
    for i in segList:
        if point.distanceTo(i[0]) <= distance:
            relationSeg.append(i)
    return relationSeg

def selecttRelationSegByListOnlyGeo(point,segList,distance):
    relationSeg = []
    for i in segList:
        if point.distanceTo(i) <= distance:
            relationSeg.append(i)
    return relationSeg

def createShp(dataList,outPath,shpName,type):
    line = arcpy.CreateFeatureclass_management(outPath,shpName,type)  # 初始化矢量
    insertCursor = arcpy.da.InsertCursor(line, ['Shape@'])
    for i in dataList:
        insertCursor.insertRow([i])
    del insertCursor


