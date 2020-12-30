import c4d, math, os

TXT_NO_SPLINE = "Vous devez sélectionner au moins une spline ou un objet neutre contenant des splines !"
TXT_MANY_SPLINE = "Il y a plusieurs splines sélectionnées, uniquement la première ({}) sera utilisée.\nVoulez-vous continuer ?"
TXT_CHECK_SPLINE = "La spline est fermée, il risque de manquer le dernier segment.\nVoulez-vous continuer ?"
TXT_NO_POLYOBJECT = "Vous devez sélectionner également un objet polygonal (terrain)"
TXT_MANY_POLYOBJECT = "Il y a plusieurs objets polygonaux sélectionné, le premier ({}) sera utilisé comme terrain.\nVoulez-vous continuer?"


NOM_RES = "Arbres_lignes"
TXT_ALERT = "Un problème est survenu\n"
TXT_ALERT2 = "Un problème est survenu\nVérifiez que la ou les lignes intersectent bien le terrain en plan et que les points soient à l'intérieur du périmètre du terrain."

NOM_SRCE_ARBRES = 'sources_vegetation'

DELTA_ALT = 10  # marge de sécurité pour altitude (utilisé dans getMinMax)

DISTANCE_CLONE = 10
RAYON_SPHERE_DEFAULT = 3


##############################################################################

# Main function
def main(
        fn_arbres_srce='/Users/donzeo/Library/Preferences/MAXON/Maxon Cinema 4D R23_2FE1299C/plugins/SITG_C4D/__arbres_2018__.c4d'):
    doc = c4d.documents.GetActiveDocument()

    # récupération des splines sélectionnées et du terrain
    sel = getSplinesAndMNT(doc)
    if not sel: return
    sp, mnt = sel

    res = arbresLignes(sp, mnt, fn_arbres_srce=fn_arbres_srce)
    if res:
        res.SetName(NOM_RES)
        doc.StartUndo()
        doc.InsertObject(res, pred=mnt)
        doc.AddUndo(c4d.UNDOTYPE_NEW, res)
        res.ChangeNBit(c4d.NBIT_OM1_FOLD, c4d.NBITCONTROL_SET)
        doc.EndUndo()
    c4d.EventAdd()


##############################################################################
def getArbresSourcesFromFile(
        fn='/Users/donzeo/Library/Preferences/MAXON/Maxon Cinema 4D R23_2FE1299C/plugins/SITG_C4D/__arbres_2018__.c4d'):
    if not fn: return None

    if not os.path.isfile(fn):
        return None

    doc_arbres = c4d.documents.LoadDocument(fn, c4d.SCENEFILTER_OBJECTS)
    srce_veget = doc_arbres.SearchObject('sources_vegetation')

    if not srce_veget: return None

    return [o.GetClone() for o in srce_veget.GetChildren()]


def getMinMaxY(obj):
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT


def setAltPointObj(obj, alt):
    mg = obj.GetMg()
    alt_v = lambda v, h: c4d.Vector(v.x, h, v.z)
    pts = [alt_v(p * mg, alt) * ~ mg for p in obj.GetAllPoints()]
    obj.SetAllPoints(pts)
    obj.Message(c4d.MSG_UPDATE)


# RECUPERATION SPLINES ET TERRAIN ######################################################

def getSplinesAndMNT(doc):
    """renvoie la première spline sélectionnée et le premier objet polygonal (MNT)
       du document actif"""

    splines = doc.GetActiveObjectsFilter(1, c4d.Ospline, c4d.NOTOK)
    if not splines:
        c4d.gui.MessageDialog(TXT_NO_SPLINE)
        return False

    # si il y a plusieurs splines on ne prend que la première
    if len(splines) > 1:
        rep = c4d.gui.QuestionDialog(TXT_MANY_SPLINE)
        if not rep: return False
    sp = splines[0]

    # TODO si les splines sont fermées ont copie le premier au dernier point et on les ouvres
    # pour l'instant on les ouvre
    if sp.IsClosed():
        rep = c4d.gui.QuestionDialog(TXT_CHECK_SPLINE)
        if not rep: return False

    polyobj = doc.GetActiveObjectsFilter(1, c4d.Opolygon, c4d.NOTOK)
    if not polyobj:
        c4d.gui.MessageDialog(TXT_NO_POLYOBJECT)
        return False

    # si il y a au moins un objet polygonal on prend le premier
    if polyobj: mnt = polyobj[0]

    if len(polyobj) > 1:
        rep = c4d.gui.QuestionDialog(TXT_MANY_POLYOBJECT.format(mnt.GetName()))
        if not rep: return False

    return sp, mnt


def arbresLignes(sp, mnt, fn_arbres_srce):
    minY, maxY = getMinMaxY(mnt)

    doc_temp = c4d.documents.BaseDocument()

    # altitude des points de la copie de la spline au minimum du mnt (-delta)
    sp = sp.GetClone()
    sp[c4d.SPLINEOBJECT_CLOSED] = False
    setAltPointObj(sp, minY)

    # extrusion
    extr = c4d.BaseObject(c4d.Oextrude)
    extr[c4d.EXTRUDEOBJECT_DIRECTION] = c4d.EXTRUDEOBJECT_DIRECTION_Y
    extr[c4d.EXTRUDEOBJECT_EXTRUSIONOFFSET] = maxY - minY
    sp.InsertUnder(extr)

    # boolean
    boolObj = c4d.BaseObject(c4d.Oboole)
    boolObj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_WITHOUT
    boolObj[c4d.BOOLEOBJECT_HIGHQUALITY] = True
    boolObj[c4d.BOOLEOBJECT_SEL_CUT_EDGES] = True

    mnt.GetClone().InsertUnder(boolObj)
    extr.InsertUnder(boolObj)
    doc_temp.InsertObject(boolObj)

    doc_temp = doc_temp.Polygonize()

    decoupe = doc_temp.GetFirstObject().GetDown()

    if not decoupe:
        c4d.gui.MessageDialog(TXT_ALERT)
        return

    settings = c4d.BaseContainer()  # Settings

    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_EDGE_TO_SPLINE,
                                        list=[decoupe],
                                        mode=c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                        bc=settings,
                                        doc=doc_temp)
    if not decoupe.GetDown():
        c4d.gui.MessageDialog(TXT_ALERT2)
        return

    sp_decoupe = decoupe.GetDown().GetClone()
    sp_decoupe.SetName(NOM_RES)
    # sp_decoupe.SetMg(mnt.GetMg())
    sp_decoupe[c4d.SPLINEOBJECT_INTERPOLATION] = c4d.SPLINEOBJECT_INTERPOLATION_UNIFORM
    sp_decoupe[c4d.SPLINEOBJECT_SUB] = 0

    # cloneur
    cloner = c4d.BaseObject(1018544)
    cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = c4d.ID_MG_MOTIONGENERATOR_MODE_OBJECT
    cloner[c4d.MGCLONER_MODE] = c4d.MGCLONER_MODE_RANDOM
    cloner[c4d.MGCLONER_VOLUMEINSTANCES_MODE] = c4d.MGCLONER_VOLUMEINSTANCES_MODE_RENDERMULTIINSTANCE
    cloner[c4d.MG_OBJECT_LINK] = sp_decoupe
    cloner[c4d.MG_POLY_MODE_] = c4d.MG_POLY_MODE_SURFACE
    cloner[c4d.MG_OBJECT_ALIGN] = False
    cloner[c4d.MG_SPLINE_MODE] = c4d.MG_SPLINE_MODE_STEP

    cloner[c4d.MG_SPLINE_STEP] = DISTANCE_CLONE

    objs_to_clone = getArbresSourcesFromFile(fn_arbres_srce)
    if objs_to_clone:
        for o in objs_to_clone:
            o.InsertUnderLast(cloner)
    else:
        nobj = c4d.BaseObject(c4d.Onull)
        sphere = c4d.BaseObject(c4d.Osphere)
        sphere[c4d.PRIM_SPHERE_RAD] = RAYON_SPHERE_DEFAULT
        sphere.InsertUnder(nobj)
        sphere.SetRelPos(c4d.Vector(0, RAYON_SPHERE_DEFAULT, 0))

        nobj.InsertUnder(cloner)

    # random effector
    rdm_effector = c4d.BaseObject(1018643)
    in_ex_data = cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
    in_ex_data.InsertObject(rdm_effector, 1)
    cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST] = in_ex_data

    rdm_effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_ROTATE_ACTIVE] = True
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_ROTATION, c4d.VECTOR_X] = math.pi * 2

    rdm_effector.InsertUnder(sp_decoupe)
    cloner.InsertUnder(sp_decoupe)
    return sp_decoupe


# Execute main()
if __name__ == '__main__':
    main()