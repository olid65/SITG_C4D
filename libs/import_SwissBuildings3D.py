# -*- coding: utf-8 -*-

import c4d
from libs import shapefile
import os
from glob import glob

CONTAINER_ORIGIN =1026473

#types pris en charge
TYPES = [shapefile.POINT,
         shapefile.POLYLINE,
         shapefile.POLYGON,
         shapefile.POINTZ,
         shapefile.MULTIPOINT,
         shapefile.MULTIPATCH]

#pour savoir si on est sur windows pour le codage des chemins de fichiers
WIN =  c4d.GeGetCurrentOS()==c4d.OPERATINGSYSTEM_WIN

def creerGeoTag(obj,doc,centre):
    geoTag = c4d.BaseTag(1026472) #GeoTag
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        origine = centre
        doc[CONTAINER_ORIGIN]= origine
    geoTag[CONTAINER_ORIGIN] = centre

    obj.InsertTag(geoTag)
    return geoTag

class SHP4D(object):

    def __init__(self,fn, doc = c4d.documents.GetActiveDocument()):

        self.doc = doc
        self.fn = fn

        #NOM du shape
        self.nom = os.path.basename(self.fn)

        dic = {shapefile.POINT:self.point,
           shapefile.POLYLINE:self.polyline,
           shapefile.POLYGON:self.polygon,
           shapefile.POINTZ:self.pointz,
           shapefile.MULTIPOINT:self.multipoint,
           shapefile.MULTIPATCH : self.multipatch
           }

        self.reader = shapefile.Reader(self.fn)
        #on vérifie si le type st pris encharge
        if not self.reader.shapeType in TYPES:
            c4d.gui.MessageDialog("Ce type de shape n'est pas pris en charge")
            return

        self.xmin,self.ymin,self.xmax,self.ymax = self.reader.bbox
        self.centre = c4d.Vector((self.xmin+self.xmax)/2,0,(self.ymax+self.ymin)/2)
        self.geoms = c4d.BaseObject(c4d.Onull)
        self.geoms.SetName(self.nom)
        self.srce = None #source pour les instances

        self.fields_name = [f[0] for f in self.reader.fields[1:]]
        if self.reader:
            for shp in self.reader.iterShapes():
                geom = dic.get(shp.shapeType,self.nomatch)(shp)

        creerGeoTag(self.geoms,self.doc,self.centre)
        self.doc.InsertObject(self.geoms)
        self.doc.SetActiveObject(self.geoms)

    def point(self,shp):
        if not self.srce:
            self.srce = c4d.BaseObject(c4d.Onull)
            self.srce.SetName(self.nom+'_source')
            self.doc.InsertObject(self.srce)
        pts = [c4d.Vector(x,0,y)-self.centre for x,y in shp.points]
        for p in pts:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetAbsPos(p)
            inst.InsertUnderLast(self.geoms)
            inst[c4d.INSTANCEOBJECT_LINK] = self.srce

    #A TESTER
    def pointz(self,shp):
        if not self.srce:
            self.srce = c4d.BaseObject(c4d.Onull)
            self.srce.SetName(self.nom+'_source')
            self.doc.InsertObject(self.srce)
        pts = [c4d.Vector(x,z,y)-self.centre for x,y,z in shp.points]
        for p in pts:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetAbsPos(p)
            inst.InsertUnderLast(self.geoms)
            inst[c4d.INSTANCEOBJECT_LINK] = self.srce

    #A TESTER AVEC DU MULTIPOINT REEL
    def multipoint(self,shp):
        if not self.srce:
            self.srce = c4d.BaseObject(c4d.Onull)
            self.srce.SetName(self.nom+'_source')
            self.doc.InsertObject(self.srce)
        pts = [c4d.Vector(x,0,y)-self.centre for x,y in shp.points]
        for p in pts:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetAbsPos(p)
            inst.InsertUnderLast(self.geoms)
            inst[c4d.INSTANCEOBJECT_LINK] = self.srce

    def polyline(self,shp):
        pts = [c4d.Vector(x,0,y)-self.centre for x,y in shp.points]
        nb_pts = len(pts)
        sp = c4d.SplineObject(nb_pts,c4d.SPLINETYPE_LINEAR)
        sp.SetAllPoints(pts)
        #SEGMENTS
        nb_seg = len(shp.parts)
        if nb_seg>1:
            sp.ResizeObject(nb_pts,nb_seg)
            shp.parts.append(nb_pts)
            segs = [fin-dbt for dbt,fin in zip(shp.parts[:-1], shp.parts[1:])]
            for i,n in enumerate(segs):
                sp.SetSegment(i,n,closed = True)

        sp.Message(c4d.MSG_UPDATE)
        sp.InsertUnderLast(self.geoms)

    def polygon(self,shp):
        pts = [c4d.Vector(x,0,y)-self.centre for x,y in shp.points]
        nb_pts = len(pts)
        #OBJET EXTRUSION
        extr = c4d.BaseObject(c4d.Oextrude)
        extr[c4d.EXTRUDEOBJECT_MOVE] = c4d.Vector(0)
        sp = c4d.SplineObject(nb_pts,c4d.SPLINETYPE_LINEAR)
        sp[c4d.SPLINEOBJECT_CLOSED] = True
        sp.SetAllPoints(pts)

        #SEGMENTS
        nb_seg = len(shp.parts)
        if nb_seg>1:
            sp.ResizeObject(nb_pts,nb_seg)
            shp.parts.append(nb_pts)
            segs = [fin-dbt for dbt,fin in zip(shp.parts[:-1], shp.parts[1:])]
            for i,n in enumerate(segs):
                sp.SetSegment(i,n,closed = True)

        sp.Message(c4d.MSG_UPDATE)
        sp.InsertUnder(extr)
        extr.InsertUnder(self.geoms)

    def multipatch(self,shp):
        pts = [c4d.Vector(x,z,y)-self.centre for (x,y),z in zip(shp.points,shp.z)]
        nb_pts = len(pts)
        polys = []

        id_pt = 0

        n = 0
        for p1,p2 in zip(shp.parts[:-1], shp.parts[1:]):
            nb_cotes = p2-p1
            #Triangles
            if nb_cotes ==3:
                poly = c4d.CPolygon(id_pt+n,id_pt+n+1,id_pt+n+2)
                polys.append(poly)
            #Quadrangles
            elif nb_cotes == 4 :
                poly = c4d.CPolygon(id_pt+n,id_pt+n+1,id_pt+n+2,id_pt+n+3)
                polys.append(poly)
            #Autres
            else:
                print('attention ngons!')
                pass
            n+= nb_cotes

        res =c4d.PolygonObject(nb_pts,len(polys))
        #TODO : tag phong !
        res.SetAllPoints(pts)
        for i,poly in enumerate(polys):
            res.SetPolygon(i,poly)

        res.Message(c4d.MSG_UPDATE)

        res.InsertUnder(self.geoms)

        #sp.Message(c4d.MSG_UPDATE)
        #sp.InsertUnder(extr)
        #extr.InsertUnder(self.geoms)

    def nomatch(self,shp) :
        print ('type de shape non pris en charge')

    def altitudeSelonChamp(self,nom_champ):
        id_champ = self.fields_name.index(nom_champ)
        for rec,geom in zip(self.reader.iterRecords(),self.geoms.GetChildren()):
            mg = geom.GetMg()
            pos = mg.off
            pos.y = rec[15]
            mg.off = pos
            geom.SetMg(mg)

    def extrusionSelonChamps(self,champHaut,champBas):
        idHaut = self.fields_name.index(champHaut)
        idBas = self.fields_name.index(champBas)
        for rec,extr in zip(self.reader.iterRecords(),self.geoms.GetChildren()):
            haut = rec[idHaut]-rec[idBas]
            extr[c4d.EXTRUDEOBJECT_MOVE] = c4d.Vector(0,haut,0)

def testShape(fn):
    #on regarde si l'extension est la bonne
    if os.path.splitext(fn)[1] == '.shp' : return True
    return False


def main(path = None):
    if not path :
        path = c4d.storage.LoadDialog(type =c4d.FILESELECTTYPE_ANYTHING,flags = c4d.FILESELECT_DIRECTORY, title="Séléctionnez le fichier .shp :")
    if not path : return
    for fn in glob(os.path.join(path,'*.shp')):
        if WIN:
            fn = fn.decode('utf-8').encode('cp1252')

        shp = SHP4D(fn, doc = c4d.documents.GetActiveDocument())
    #doc.InsertObject(shp.geoms)
    c4d.EventAdd()


if __name__=='__main__':
    main()
