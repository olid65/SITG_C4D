import c4d
from libs import shapefile

CONTAINER_ORIGIN = 1026473


def getPts(shp, origin, hasZ=False):
    if hasZ:
        return [c4d.Vector(x, z, y) - origin for (x, y), z in zip(shp.points, shp.z)]
    else:
        return [c4d.Vector(x, 0, y) - origin for x, y in shp.points]


def shp2splines(fn, origin):
    """renvoie une liste de splines multisegments"""
    res = []

    with shapefile.Reader(fn) as reader:
        if reader.shapeType not in [shapefile.POLYLINE, shapefile.POLYGON, shapefile.POLYLINEZ, shapefile.POLYGONZ]:
            return False

        closed = False
        if reader.shapeType in [shapefile.POLYGON, shapefile.POLYGONZ]:
            closed = True

        hasZ = False
        if reader.shapeType in [shapefile.POLYLINEZ, shapefile.POLYGONZ]:
            hasZ = True

        for shp in reader.iterShapes():
            pts = getPts(shp, origin, hasZ)
            nb_pts = len(pts)
            sp = c4d.SplineObject(nb_pts, c4d.SPLINETYPE_LINEAR)
            sp.SetAllPoints(pts)
            # SEGMENTS
            nb_seg = len(shp.parts)
            if nb_seg > 1:
                sp.ResizeObject(nb_pts, nb_seg)
                shp.parts.append(nb_pts)
                segs = [fin - dbt for dbt, fin in zip(shp.parts[:-1], shp.parts[1:])]
                for i, n in enumerate(segs):
                    sp.SetSegment(i, n, closed=closed)
            sp[c4d.SPLINEOBJECT_CLOSED] = closed
            sp.Message(c4d.MSG_UPDATE)
            res.append(sp)
    return res


def shp2instances(fn, origin, sources):
    """renvoie une liste d'instances"""
    pass


def shp2multiinstance(fn, origin, sources):
    """renvoie un objet multiinstance par objet source avec tous les points"""
    pass


def shp2cloner(fn, origin, sources):
    """renvoie un neutre avec en enfant un objet point pour les positions
       et un cloner en mode objet"""
    pass


def shp2polygon(fn, origin):
    """renvoie une liste d'objets polygonaux (un par entité)
       depuis un multipatch ou polygone 3D"""
    pass


def main():
    fn = '/Users/olivier.donze/Mandats/Penetrantes_vertes_2021/SIG/isoligne_poly_mnt20m_Simplif_lissage100m.shp'
    origin = doc[CONTAINER_ORIGIN]
    res = c4d.BaseObject(c4d.Onull)
    for sp in shp2splines(fn, origin):
        sp.InsertUnderLast(res)
    doc.InsertObject(res)
    c4d.EventAdd()


if __name__ == "__main_":
    main()