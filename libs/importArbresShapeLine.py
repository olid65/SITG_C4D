# -*- coding: utf-8 -*-

import c4d
from libs import shapefile
from libs import treesFromLines
import os

CONTAINER_ORIGIN = 1026473

TXT_NO_MNT = "Vous devez sélectionner un terrain (objet polygonal) sur lequel les zones vont être plantées"
TXT_NO_ORIGIN = "Le document n'est pas géoréférencé, opération impossible !"
TXT_NO_SHP = "Ce n'est pas un fichier shape (.shp)"
TXT_SHP_NOT_POLYGON = "Ce n'est pas un shapefile de type polyligne"

def testShape(fn):
    # on regarde si l'extension est la bonne
    if os.path.splitext(fn)[1] == '.shp': return True
    return False

def shpPoly2spline(shp,centre,hasZ = False):
    pts = []
    if hasZ:
        pts = [c4d.Vector(x, z, y) - centre for (x, y), z in zip(shp.points, shp.z)]
    else:
        pts = [c4d.Vector(x, 0, y) - centre for x, y in shp.points]
    nb_pts = len(pts)
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
    return sp


def splinesFromShapefile(fn,origine):

    reader = shapefile.Reader(fn)



    hasZ = False

    if reader.shapeType == shapefile.POLYLINE:
        hasZ = False
    elif reader.shapeType == shapefile.POLYLINEZ:
        hasZ = True
    else :
        c4d.gui.MessageDialog(TXT_SHP_NOT_POLYGON)
        return None

    splines = []

    for shp in reader.iterShapes():
        splines.append(shpPoly2spline(shp,origine,hasZ))

    return splines


def fusionSplines(lst_sp, nom=None):
    """fusionne toute les splines de la liste en une seule en une"""
    pts = []
    nb_seg = 0
    seg = []

    for sp in lst_sp:
        mg = sp.GetMg()
        pts.extend([p * mg for p in sp.GetAllPoints()])
        if sp.GetSegmentCount():
            for id in range(sp.GetSegmentCount()):
                seg.append(sp.GetSegment(id)['cnt'])
                nb_seg += 1
        else:
            seg.append(sp.GetPointCount())
            nb_seg += 1

    nb_pts = sum([s.GetPointCount() for s in lst_sp])
    res = c4d.SplineObject(nb_pts, c4d.SPLINETYPE_LINEAR)
    if nom: res.SetName(nom)
    res[c4d.SPLINEOBJECT_CLOSED] = False
    res.ResizeObject(nb_pts, nb_seg)
    res.SetAllPoints(pts)

    for id, cnt in enumerate(seg):
        res.SetSegment(id, cnt, closed=False)

    res.Message(c4d.MSG_UPDATE)
    return res


# Main function
def main(fn_arbres_srce = '/Users/olivier.donze/Library/Preferences/MAXON/Maxon Cinema 4D R23_2FE1299C/plugins/SITG_C4D/__arbres_2018__.c4d'):

    #récupération du MNT
    doc = c4d.documents.GetActiveDocument()
    mnt = doc.GetActiveObject()

    if not mnt or not mnt.CheckType(c4d.Opolygon) :
        c4d.gui.MessageDialog(TXT_NO_MNT)
        return

    #Verification du georeferencement du fichier
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        c4d.gui.MessageDialog(TXT_NO_ORIGIN)
        return


    #SHAPEFILE polyline
    fn = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Sélectionnez le fichier .shp :")
    #fn = '/Users/olivier.donze/TEMP/LaPage_modele_donnees/PP_ARBRE_S.shp'
    if not fn: return

    if not testShape(fn):
        c4d.gui.MessageDialog(TXT_NO_SHP)
        return

    splines = splinesFromShapefile(fn, origine)
    if not splines : return
    sp = fusionSplines(splines)

    res = treesFromLines.arbresLignes(sp, mnt, fn_arbres_srce=fn_arbres_srce)
    if res:
        doc.InsertObject(res, pred=mnt)
        doc.AddUndo(c4d.UNDOTYPE_NEW, res)
        res.ChangeNBit(c4d.NBIT_OM1_FOLD, c4d.NBITCONTROL_SET)
        doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()