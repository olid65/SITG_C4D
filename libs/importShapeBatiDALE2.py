# -*- coding: utf-8 -*-

import c4d, os
from libs import shapefile

"""Pour importer un fichier shape de type polygone avec un champ HAUTEUR comme valeur d'extrusion"""

CONTAINER_ORIGIN = 1026473

# types pris en charge
TYPES = [shapefile.POLYGON]

# NOM_CHAMP_BASE = None
NOM_CHAMP_HAUT = 'HAUTEUR'


def creerGeoTag(obj, doc, centre):
    geoTag = c4d.BaseTag(1026472)  # GeoTag
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        origine = centre
        doc[CONTAINER_ORIGIN] = origine
    geoTag[CONTAINER_ORIGIN] = centre

    obj.InsertTag(geoTag)
    return geoTag


class SHP4D(object):

    def __init__(self, fn, doc):
        self.doc = doc
        self.fn = fn
        # NOM du shape
        self.nom = os.path.basename(self.fn)
        dic = {shapefile.POINT: self.point,
               shapefile.POLYLINE: self.polyline,
               shapefile.POLYGON: self.polygon,
               }
        self.reader = shapefile.Reader(self.fn)
        # on vérifie si le type st pris encharge
        if not self.reader.shapeType in TYPES:
            c4d.gui.MessageDialog("Ce n'est pas un shape de type polygone")
            return
        self.xmin, self.ymin, self.xmax, self.ymax = self.reader.bbox
        self.centre = c4d.Vector((self.xmin + self.xmax) / 2, 0, (self.ymax + self.ymin) / 2)

        self.geoms = c4d.BaseObject(c4d.Onull)
        self.geoms.SetName(self.nom)

        self.fields_name = [f[0] for f in self.reader.fields[1:]]

        if NOM_CHAMP_HAUT not in self.fields_name:
            c4d.gui.MessageDialog("il faut un champ '{0}'pour que cela fonctionne".format(NOM_CHAMP_HAUT))
            return

        if self.reader:
            for shp in self.reader.iterShapes():
                geom = dic.get(shp.shapeType, self.nomatch)(shp)

        # self.altitudeSelonChamp(NOM_CHAMP_BASE)
        self.extrusionSelonChamps(NOM_CHAMP_HAUT)
        creerGeoTag(self.geoms, self.doc, self.centre)
        self.doc.InsertObject(self.geoms)
        self.doc.SetActiveObject(self.geoms)
        centrerExtrusions(self.geoms)

    def point(self, shp):
        pass

    def polyline(self, shp):
        pass

    def polygon(self, shp):
        pts = [c4d.Vector(x, 0, y) - self.centre for x, y in shp.points]
        nb_pts = len(pts)
        # OBJET EXTRUSION
        extr = c4d.BaseObject(c4d.Oextrude)
        extr[c4d.EXTRUDEOBJECT_MOVE] = c4d.Vector(0)
        sp = c4d.SplineObject(nb_pts, c4d.SPLINETYPE_LINEAR)
        sp[c4d.SPLINEOBJECT_CLOSED] = True
        sp.SetAllPoints(pts)

        # SEGMENTS
        nb_seg = len(shp.parts)
        if nb_seg > 1:
            sp.ResizeObject(nb_pts, nb_seg)
            shp.parts.append(nb_pts)
            segs = [fin - dbt for dbt, fin in zip(shp.parts[:-1], shp.parts[1:])]
            for i, n in enumerate(segs):
                sp.SetSegment(i, n, closed=True)

        sp.Message(c4d.MSG_UPDATE)
        sp.InsertUnder(extr)
        extr.InsertUnderLast(self.geoms)

    def nomatch(self, shp):
        print ('type de shape non pris en charge')

    def altitudeSelonChamp(self, nom_champ):
        id_champ = self.fields_name.index(nom_champ)
        for rec, geom in zip(self.reader.iterRecords(), self.geoms.GetChildren()):
            mg = geom.GetMg()
            pos = mg.off
            pos.y = rec[15]
            mg.off = pos
            geom.SetMg(mg)

    def extrusionSelonChamps(self, champHaut):
        idHaut = self.fields_name.index(champHaut)
        for rec, extr in zip(self.reader.iterRecords(), self.geoms.GetChildren()):
            haut = rec[idHaut]
            try:
                haut = float(haut)
            except:
                haut = 0.
            extr[c4d.EXTRUDEOBJECT_MOVE] = c4d.Vector(0, haut, 0)


def testShape(fn):
    # on regarde si l'extension est la bonne
    if os.path.splitext(fn)[1] == '.shp': return True
    return False


def centrerExtrusions(op):
    for extr in op.GetChildren():
        sp = extr.GetDown()
        mg = extr.GetMg()
        pts = [p * mg for p in sp.GetAllPoints()]
        centre = c4d.Vector()
        nb_pts = len(pts)
        centre.x = sum([p.x for p in pts]) / nb_pts
        centre.y = sum([p.y for p in pts]) / nb_pts
        centre.z = sum([p.z for p in pts]) / nb_pts

        pts = [p - centre for p in pts]
        sp.SetAllPoints(pts)
        mg.off = centre
        extr.SetMg(mg)
        sp.Message(c4d.MSG_UPDATE)


def main():
    # fn = '/Volumes/mip/mandats/02_en_cours/DALE transfert technologie/Donnees_base/Shapes_Alexandre/Bati_cherpines.shp'
    fn = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Séléctionnez le fichier .shp :")
    if not fn: return

    if not testShape(fn):
        c4d.gui.MessageDialog("Ce n'est pas un fichier shape (.shp)")
        return

    shp = SHP4D(fn, c4d.documents.GetActiveDocument())

    c4d.EventAdd()


if __name__ == '__main__':
    main()
