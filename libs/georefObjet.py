# -*- coding: utf-8 -*-

import c4d

CONTAINER_ORIGIN =1026473

def isGeoref(obj):
    t = obj.GetFirstTag()
    while t:
        if t.CheckType(1026472) :
            return True
        t = t.GetNext()
    return False

def georefObj(obj,doc):
    if isGeoref(obj) : return
    tg = c4d.BaseTag(1026472) #GEOTAG
    pos = obj.GetAbsPos()
    tg[CONTAINER_ORIGIN] = doc[CONTAINER_ORIGIN]+pos
    obj.InsertTag(tg)
    doc.AddUndo(c4d.UNDOTYPE_NEW,tg)

def main():
    doc = c4d.documents.GetActiveDocument()

    origine = doc[CONTAINER_ORIGIN]
    if not origine :
        print ("document non géoréférencé")
        return
    doc.StartUndo()
    for o in doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0):
        georefObj(o,doc)

    doc.EndUndo()
    c4d.EventAdd()


if __name__=='__main__':
    main()