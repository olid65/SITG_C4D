# -*- coding: utf-8 -*-

import c4d
import shapefile, os

#TODO : vérifier qu'il y a bien un champ numérique alt_base et alt_haut dans le shape

CONTAINER_ORIGIN =1026473 
ID_BATI_PLQ = 1035057

#types pris en charge
TYPES = [shapefile.POLYGON]

#pour savoir si on est sur windows pour le codage des chemins de fichiers
WIN =  c4d.GeGetCurrentOS()==c4d.OPERATINGSYSTEM_WIN

NOM_CHAMP_BASE = 'alt_base'
NOM_CHAMP_HAUT = 'alt_haut'

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
    
    def __init__(self,fn,doc):
        self.doc = doc
        self.fn = fn
        #NOM du shape 
        self.nom = os.path.basename(self.fn)
        dic = {shapefile.POINT:self.point,
           shapefile.POLYLINE:self.polyline,
           shapefile.POLYGON:self.polygon,
           }
        self.reader = shapefile.Reader(self.fn)
        #on vérifie si le type st pris encharge
        if not self.reader.shapeType in TYPES:
            c4d.gui.MessageDialog("Ce n'est pas un shape de type polygone")
            return
        self.xmin,self.ymin,self.xmax,self.ymax = self.reader.bbox
        self.centre = c4d.Vector((self.xmin+self.xmax)/2,0,(self.ymax+self.ymin)/2)

        self.geoms = c4d.BaseObject(c4d.Onull)
        self.geoms.SetName(self.nom)

        self.fields_name = [f[0] for f in self.reader.fields[1:]]

        if NOM_CHAMP_BASE not in self.fields_name or NOM_CHAMP_HAUT not in self.fields_name:

            c4d.gui.MessageDialog("il faut un champ '{0}' et un champ '{1}' pour que cela fonctionne".format(NOM_CHAMP_BASE,NOM_CHAMP_HAUT))
            return

        if self.reader:
            for shp in self.reader.iterShapes():
                geom = dic.get(shp.shapeType,self.nomatch)(shp)
                #print shp.points
                #print shp.z
                #print shp.parts
        self.altitudeSelonChamp(NOM_CHAMP_BASE)
        self.extrusionSelonChamps(NOM_CHAMP_HAUT,NOM_CHAMP_BASE)
        creerGeoTag(self.geoms,self.doc,self.centre)
        self.doc.InsertObject(self.geoms)
        self.doc.SetActiveObject(self.geoms)
        
    def point(self,shp):
        pass
    
    def polyline(self,shp):
        pass
    
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
        extr.InsertUnderLast(self.geoms)
        
    def nomatch(self,shp) :
        print 'type de shape non pris en charge'   
    
    def altitudeSelonChamp(self,nom_champ):
        id_champ = self.fields_name.index(nom_champ)
        for rec,geom in zip(self.reader.iterRecords(),self.geoms.GetChildren()):
            mg = geom.GetMg()
            pos = mg.off
            pos.y = float(rec[id_champ])
            mg.off = pos
            geom.SetMg(mg)
    
    def extrusionSelonChamps(self,champHaut,champBas):
        idHaut = self.fields_name.index(champHaut)
        idBas = self.fields_name.index(champBas)
        for rec,extr in zip(self.reader.iterRecords(),self.geoms.GetChildren()):
            haut = float(rec[idHaut]) - float(rec[idBas])
            extr[c4d.EXTRUDEOBJECT_MOVE] = c4d.Vector(0,haut,0)
        
def testShape(fn):
    #on regarde si l'extension est la bonne
    if os.path.splitext(fn)[1] == '.shp' : return True
    return False        
            

def main():
    
    fn = c4d.storage.LoadDialog(type =c4d.FILESELECTTYPE_IMAGES,title="Séléctionnez le fichier .shp :")
    #fn = '/Users/donzeo/Downloads/Bati_projet_18_10_13/Bati_projet_18_10_13.shp'
    if not fn : return
    
    if not testShape(fn) : 
            c4d.gui.MessageDialog("Ce n'est pas un fichier shape (.shp)")
            return
    if WIN:
        fn = fn.decode('utf-8').encode('cp1252')
    
    shp = SHP4D(fn, c4d.documents.GetActiveDocument())
    
    c4d.EventAdd()
        

if __name__=='__main__':
    main()
