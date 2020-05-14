# -*- coding: utf-8 -*-

import c4d
import shapefile, os, random
from math import pi

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
# def state():
#    return True

# pour savoir si on est sur windows pour le codage des chemins de fichiers
WIN = c4d.GeGetCurrentOS() == c4d.OPERATINGSYSTEM_WIN

CONTAINER_ORIGIN = 1026473

NOM_CHAMP_HAUT = 'HAUTEUR'
NOM_CHAMP_DIAMETRE = 'DIAMETRE'
NOM_CHAMP_Z = 'Z'

HAUTEUR_DEFAUT = 15.
DIAMETRE_DEFAUT = 7.5

PROPORTIONS_DEFAUT = 0.35  # proportion entre le diametre et la hauteur pour si il manque un des champs

CONTAINER_ORIGIN = 1026473

NOM_FICHIER_ARBRES = '__arbres_2018__.c4d'

ID_CLONER = 1018544
ID_TAG_INFLUENCE_MOGRAPH = 440000231
ID_PLAIN_EFFECTOR = 1021337
ID_RANDOM_EFFECTOR = 1018643

NOM_OBJ_POINTS = "arbres"
NOM_CLONER = NOM_OBJ_POINTS + "_cloneur"
NOM_TAG_DIAMETRES = "diametres"
NOM_TAG_HAUTEURS = "hauteurs"
NOM_POINT_OBJECT = "points_" + NOM_OBJ_POINTS
NOM_EFFECTOR_DIAMETRES = "effecteur_" + NOM_TAG_DIAMETRES
NOM_EFFECTOR_HAUTEURS = "effecteur_" + NOM_TAG_HAUTEURS
NOM_EFFECTOR_RANDOM = "effecteur_rotation_aleatoire"
NULL_NAME = NOM_OBJ_POINTS

HAUT_SRCE = 10.  # on part avec une source qui fait 10m de haut
DIAM_SRCE = 10.  # idem pour le diametre

FACTEUR_HAUT = 1.
FACTEUR_DIAMETRE = 1.


def testShape(fn):
    # on regarde si l'extension est la bonne
    if os.path.splitext(fn)[1] == '.shp': return True
    return False


def create_point_object(points):
    res = c4d.PolygonObject(len(points), 0)
    res.SetAllPoints(points)
    res.Message(c4d.MSG_UPDATE)
    return res


def create_effector(name, select=None, typ=ID_PLAIN_EFFECTOR):
    res = c4d.BaseObject(typ)
    res.SetName(name)
    if select:
        res[c4d.ID_MG_BASEEFFECTOR_SELECTION] = select
    return res


def create_mograph_cloner(doc, points, hauteurs, diametres, objs_srces, centre=None, name=None):
    # tag = doc.GetActiveTag()
    # print c4d.modules.mograph.GeGetMoDataWeights(tag)
    # return

    res = c4d.BaseObject(c4d.Onull)
    if not name: name = NULL_NAME
    res.SetName(name)

    if centre:
        creerGeoTag(res, doc, centre)

    poly_o = create_point_object(points)
    poly_o.SetName(NOM_POINT_OBJECT)

    cloner = c4d.BaseObject(ID_CLONER)
    cloner.SetName(NOM_CLONER)
    cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = 0  # mode objet
    cloner[c4d.MG_OBJECT_LINK] = poly_o
    cloner[c4d.MG_POLY_MODE_] = 0  # mode point
    cloner[c4d.MG_OBJECT_ALIGN] = False
    cloner[c4d.MGCLONER_VOLUMEINSTANCES_MODE] = 2  # multiinstances
    cloner[c4d.MGCLONER_MODE] = 2  # repartition aleatoire des clones

    # insertion des objets source
    for o in objs_srces.GetChildren():
        clone = o.GetClone()
        clone.InsertUnderLast(cloner)

    tagHauteurs = c4d.BaseTag(440000231)
    cloner.InsertTag(tagHauteurs)
    tagHauteurs.SetName(NOM_TAG_HAUTEURS)
    # ATTENTION bien mettre des float dans la liste sinon cela ne marche pas !
    scale_factor_haut = lambda x: float(x) / HAUT_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagHauteurs, [scale_factor_haut(h) for h in hauteurs])
    # tagHauteurs.SetDirty(c4d.DIRTYFLAGS_DATA) #plus besoin depuis la r21 !

    tagDiametres = c4d.BaseTag(440000231)
    cloner.InsertTag(tagDiametres)
    tagDiametres.SetName(NOM_TAG_DIAMETRES)
    scale_factor_diam = lambda x: float(x * 2) / DIAM_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagDiametres, [scale_factor_diam(d) for d in diametres])
    # tagDiametres.SetDirty(c4d.DIRTYFLAGS_DATA) #plus besoin depuis la r21 !

    # Effecteur simple hauteurs
    effector_heights = create_effector(NOM_EFFECTOR_HAUTEURS, select=tagHauteurs.GetName())
    effector_heights[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    effector_heights[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    effector_heights[c4d.ID_MG_BASEEFFECTOR_SCALE, c4d.VECTOR_Y] = FACTEUR_HAUT

    # Effecteur simple diametres
    effector_diam = create_effector(NOM_EFFECTOR_DIAMETRES, select=tagDiametres.GetName())
    effector_diam[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    effector_diam[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    effector_diam[c4d.ID_MG_BASEEFFECTOR_SCALE] = c4d.Vector(FACTEUR_DIAMETRE, 0, FACTEUR_DIAMETRE)

    # Effecteur random
    effector_random = create_effector(NOM_EFFECTOR_RANDOM, typ=ID_RANDOM_EFFECTOR)
    effector_random[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    effector_random[c4d.ID_MG_BASEEFFECTOR_ROTATE_ACTIVE] = True
    effector_random[c4d.ID_MG_BASEEFFECTOR_ROTATION, c4d.VECTOR_X] = pi * 2

    ie_data = cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
    ie_data.InsertObject(effector_heights, 1)

    ie_data.InsertObject(effector_diam, 1)
    ie_data.InsertObject(effector_random, 1)
    cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST] = ie_data

    cloner.Message(c4d.MSG_UPDATE)
    cloner.InsertUnder(res)
    effector_heights.InsertUnder(res)
    effector_diam.InsertUnder(res)
    effector_random.InsertUnder(res)
    poly_o.InsertUnder(res)

    doc.InsertObject(res)
    doc.AddUndo(c4d.UNDOTYPE_NEW, res)

    effector_heights.Message(c4d.MSG_MENUPREPARE, doc)
    effector_diam.Message(c4d.MSG_MENUPREPARE, doc)
    effector_random.Message(c4d.MSG_MENUPREPARE, doc)

    return


def index(liste, nom):
    """retourne le ns° d'index si nom est dans la liste
       sinon retourne -1"""

    if nom not in liste: return -1
    return liste.index(nom)


def niHaut_niDiam(haut=None, diam=None):
    return HAUTEUR_DEFAUT, DIAMETRE_DEFAUT


def pasHaut(haut=None, diam=None):
    return diam / PROPORTIONS_DEFAUT, diam


def pasDiam(haut=None, diam=None):
    return haut, haut * PROPORTIONS_DEFAUT


def hautDiam(haut=None, diam=None):
    return haut, diam


def centreBbox(bbox):
    x = (bbox[0] + bbox[2]) / 2.
    y = (bbox[1] + bbox[3]) / 2.
    return c4d.Vector(x, 0, y)


def creerGeoTag(obj, doc, centre):
    geoTag = c4d.BaseTag(1026472)  # GeoTag
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        origine = centre
        doc[CONTAINER_ORIGIN] = origine
    geoTag[CONTAINER_ORIGIN] = centre

    obj.InsertTag(geoTag)
    return geoTag


# Main function
def main(fn=None,
         fn_arbres='/Users/donzeo/Library/Preferences/MAXON/Maxon Cinema 4D R21_90860A1D/plugins/SITG_C4D/__arbres_2018__.c4d'):
    fn = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Séléctionnez le fichier .shp :")
    if not fn: return

    if not testShape(fn):
        c4d.gui.MessageDialog("Ce n'est pas un fichier shape (.shp)")
        return
    if WIN:
        fn = fn.decode('utf-8').encode('cp1252')

    doc = c4d.documents.GetActiveDocument()

    if not os.path.isfile(fn_arbres):
        c4d.gui.MessageDialog(
            """Il manque le fichier : \n{0}\n\nL'import des arbres est impossible""".format(fn_arbres))
        return None

    doc_arbres = c4d.documents.LoadDocument(fn_arbres, c4d.SCENEFILTER_OBJECTS)
    # c4d.documents.LoadFile(fn_arbres)
    # doc_arbres = c4d.documents.GetActiveDocument()

    origin_doc_arbres = doc_arbres[CONTAINER_ORIGIN]
    srce_veget = doc_arbres.SearchObject('sources_vegetation')

    reader = shapefile.Reader(fn)
    centre = centreBbox(reader.bbox)

    fields_name = [f[0].lower() for f in reader.fields][1:]

    nom_champ_haut = NOM_CHAMP_HAUT.lower()
    nom_champ_diametre = NOM_CHAMP_DIAMETRE.lower()
    nom_champ_z = NOM_CHAMP_Z.lower()

    id_haut = index(fields_name, nom_champ_haut)
    id_diam = index(fields_name, nom_champ_diametre)
    id_z = index(fields_name, nom_champ_z)

    haut = diam = None
    z = None

    # selon le cas de figure on applique une fonction differente
    if id_haut == -1 and id_diam == -1:
        fonction = niHaut_niDiam
    elif id_haut == -1:
        fonction = pasHaut
    elif id_diam == -1:
        fonction = pasDiam
    else:
        fonction = hautDiam

    num = 0

    points = []
    hauteurs = []
    diametres = []

    for shp, rec in zip(reader.iterShapes(), reader.iterRecords()):
        if id_haut >= 0:
            haut = rec[id_haut]
        if id_diam >= 0:
            diam = rec[id_diam]
        haut, diam = fonction(haut, diam)
        hauteurs.append(haut)
        diametres.append(diam)

        # on prend d'abord le champ z
        z = 0
        if id_z >= 0:
            z = rec[id_z]

        if len(shp.points) > 1:
            # TODO traiter les multipoints !
            print 'MULTIPOINT !'
        else:
            x, y = shp.points[0]
            if not z:
                z = shp.z[0]
            pos = c4d.Vector(x, z, y) - centre
            points.append(pos)

    create_mograph_cloner(doc, points, hauteurs, diametres, srce_veget, centre=centre, name=os.path.basename(fn))
    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    # fn = '/Users/donzeo/Documents/TEMP/NYON_SPLA/C4D/arbres_script.shp'
    # fn = '/Users/donzeo/Documents/TEMP/NYON_SPLA/test_arbre.shp'
    main()