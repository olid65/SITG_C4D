import c4d,os,math
from random import random



TXT_PB_SELECTION = "Vous devez sélectionner deux objets dans l'ordre (points,terrain)"
TXT_NOT_POINTSOBJECT = "Le premier objet doit contenir des points (objet polygonal ou spline)"
TXT_NOT_POLYGON = "Le second objet doit être un objet polygonal"

SUFFIXE_OBJ_POINT = "_points"


DELTA_ALT = 100

def getMinMaxY(obj):
    """renvoie le minY et le maxY en valeur du monde d'un objet"""
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT

def pointsOnSurface(op,mnt):
    grc = c4d.utils.GeRayCollider()
    grc.Init(mnt)

    mg_op = op.GetMg()
    mg_mnt = mnt.GetMg()
    invmg_mnt = ~mg_mnt
    invmg_op = ~op.GetMg()

    minY,maxY = getMinMaxY(mnt)

    ray_dir = ((c4d.Vector(0,0,0)*invmg_mnt) - (c4d.Vector(0,1,0)*invmg_mnt)).GetNormalized()
    length = maxY-minY
    for i,p in enumerate(op.GetAllPoints()):
        p = p*mg_op
        dprt = c4d.Vector(p.x,maxY,p.z)*invmg_mnt
        intersect = grc.Intersect(dprt,ray_dir,length)
        if intersect :
            pos = grc.GetNearestIntersection()['hitpos']
            op.SetPoint(i,pos*mg_mnt*invmg_op)

    op.Message(c4d.MSG_UPDATE)

def getArbresSourcesFromFile(
        fn='/Users/donzeo/Library/Preferences/MAXON/Maxon Cinema 4D R23_2FE1299C/plugins/SITG_C4D/__arbres_2018__.c4d'):
    if not fn: return None

    if not os.path.isfile(fn):
        return None

    doc_arbres = c4d.documents.LoadDocument(fn, c4d.SCENEFILTER_OBJECTS)
    srce_veget = doc_arbres.SearchObject('sources_vegetation')

    if not srce_veget: return None

    return [o.GetClone() for o in srce_veget.GetChildren()]

def randomRotMatriceH():
    angle = random()*math.pi*2
    return c4d.utils.MatrixRotY(angle)

def randomRotMultiInst(multi_inst):
    matrices = [m*randomRotMatriceH() for m in multi_inst.GetInstanceMatrices()]
    multi_inst.SetInstanceMatrices(matrices)
    multi_inst.Message(c4d.MSG_UPDATE)

def main():
    doc = c4d.documents.GetActiveDocument()
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    if not len(objs)==2 :
        c4d.gui.MessageDialog(TXT_PB_SELECTION)
        return
    obj_pts,mnt = objs

    if not obj_pts.CheckType(c4d.Opoint):
        c4d.gui.MessageDialog(TXT_NOT_POINTSOBJECT)
        return

    if not mnt.CheckType(c4d.Opolygon):
        c4d.gui.MessageDialog(TXT_NOT_POLYGON)
        return

    rep = c4d.gui.QuestionDialog(f"""Les points de "{obj_pts.GetName()}" seront projetés sur "{mnt.GetName()}"\nVoulez-vous continuer ?""")

    if not rep : return
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE,obj_pts)
    pointsOnSurface(obj_pts,mnt)
    doc.EndUndo()
    c4d.EventAdd()


if __name__=='__main__':
    main()