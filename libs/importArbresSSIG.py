# coding: utf8

""" droits réservés Olivier Donzé juillet 2017
    à l'usage exclusif de mes étudiants en bachelor, master et formation continue de l'hepia
    
    version 2.0 du 28 avril 2020"""

import c4d, os, random, math
from glob import glob
from math import pi

WIN =  c4d.GeGetCurrentOS()==c4d.OPERATINGSYSTEM_WIN

CONTAINER_ORIGIN =1026473


NOM_FICHIER_ARBRES = '__arbres_2018__.c4d'

ID_CLONER = 1018544
ID_TAG_INFLUENCE_MOGRAPH = 440000231
ID_PLAIN_EFFECTOR = 1021337
ID_RANDOM_EFFECTOR = 1018643

NOM_OBJ_POINTS = "arbres_SITG_2018"
NOM_CLONER = NOM_OBJ_POINTS+"_cloneur"
NOM_TAG_DIAMETRES = "diametres"
NOM_TAG_HAUTEURS = "hauteurs"
NOM_POINT_OBJECT = "points_"+NOM_OBJ_POINTS
NOM_EFFECTOR_DIAMETRES = "effecteur_"+NOM_TAG_DIAMETRES
NOM_EFFECTOR_HAUTEURS = "effecteur_"+NOM_TAG_HAUTEURS
NOM_EFFECTOR_RANDOM ="effecteur_rotation_aleatoire"
NULL_NAME = NOM_OBJ_POINTS

#ATTENTION LE FACTEUR EST FAIT POUR UN ARBRE SOURCE DE 10m de haut
#et de 10m de diametre
#ensuite on pondère chaque clone en faisant hauteur de l'arbre/ hauteur max (125m)
#et diamète del'arbres / diametre max (30m)

HAUT_SRCE = 10. #on part avec une source qui fait 10m de haut
DIAM_SRCE = 10. #idem pour le diametre

FACTEUR_HAUT = 1.
FACTEUR_DIAMETRE = 1.


def create_point_object(points):
    res = c4d.PolygonObject(len(points),0)
    res.SetAllPoints(points)
    res.Message(c4d.MSG_UPDATE)
    return res


def create_effector(name,select = None, typ = ID_PLAIN_EFFECTOR):
    res = c4d.BaseObject(typ)
    res.SetName(name)
    if select:
        res[c4d.ID_MG_BASEEFFECTOR_SELECTION] = select
    return res


def create_mograph_cloner(doc,points, hauteurs, diametres, objs_srces):
    # tag = doc.GetActiveTag()
    # print c4d.modules.mograph.GeGetMoDataWeights(tag)
    # return

    res = c4d.BaseObject(c4d.Onull)
    res.SetName(NULL_NAME)

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
    #ATTENTION bien mettre des float dans la liste sinon cela ne marche pas !
    scale_factor_haut = lambda x : float(x)/HAUT_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagHauteurs, [scale_factor_haut(h) for h in hauteurs])
    #tagHauteurs.SetDirty(c4d.DIRTYFLAGS_DATA) #plus besoin depuis la r21 !

    tagDiametres = c4d.BaseTag(440000231)
    cloner.InsertTag(tagDiametres)
    tagDiametres.SetName(NOM_TAG_DIAMETRES)
    scale_factor_diam = lambda x: float(x*2)/DIAM_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagDiametres, [scale_factor_diam(d) for d in diametres])
    #tagDiametres.SetDirty(c4d.DIRTYFLAGS_DATA) #plus besoin depuis la r21 !

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



###############
#ARBRES
###############
class Bbox(object):
    def __init__(self,mini,maxi):

        self.min = mini
        self.max = maxi
        self.centre = (self.min+self.max)/2
        self.largeur = self.max.x - self.min.x
        self.hauteur = self.max.z - self.min.z
    def __str__(self):
        return ('X : '+str(self.min.x)+'-'+str(self.max.x)+'->'+str(self.max.x-self.min.x)+'\n'+
                'Y : '+str(self.min.z)+'-'+str(self.max.z)+'->'+str(self.max.z-self.min.z))    
    def xInside(self,x):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return x>= self.min.x and x<= self.max.x
    
    def zInside(self,y):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return y>= self.min.z and y<= self.max.z
        
    def isInsideX(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.xInside(bbox2.xmin)
        maxInside = self.xInside(bbox2.xmax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.xmin < self.min.x and bbox2.xmax > self.max.x : return 2
        return 0
    
    def isInsideZ(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.zInside(bbox2.ymin)
        maxInside = self.zInside(bbox2.ymax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.ymin < self.min.z and bbox2.ymax > self.max.z : return 2
        return 0
    
    def ptIsInside(self,pt):
        """renvoie vrai si point c4d est à l'intérieur"""
        return  self.xInside(pt.x) and self.zInside(pt.z)
    
    @staticmethod
    def fromObj(obj,origine = c4d.Vector()):
        """renvoie la bbox 2d de l'objet"""
        mg = obj.GetMg()
    
        rad = obj.GetRad()
        centre = obj.GetMp()
        
        #4 points de la bbox selon orientation de l'objet
        pts = [ c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z+rad.z) * mg]
    
        mini = c4d.Vector(min([p.x for p in pts]),min([p.y for p in pts]),min([p.z for p in pts])) + origine
        maxi = c4d.Vector(max([p.x for p in pts]),max([p.y for p in pts]),max([p.z for p in pts])) + origine
    
        return Bbox(mini,maxi)


def getArbres(ptObj,bbox, origin_doc_arbres):
    """renvoie untuple de liste(positions,diamètres, hauteurs)
       pour chaque arbres contenu dans la bbox"""
       
    tags = ptObj.GetTags()
    tag_vmax_diam =  tags[0]
    tag_vmax_haut = tags[1]
    
    points = []
    diametres = []
    hauteurs = []
    for pos,diam,haut in zip(ptObj.GetAllPoints(), 
                               tag_vmax_diam.GetAllHighlevelData(),
                               tag_vmax_haut.GetAllHighlevelData()):
        if bbox.ptIsInside(pos+origin_doc_arbres):
            points.append(pos+origin_doc_arbres)

            diametres.append(diam)
            hauteurs.append(haut)

    return points,diametres,hauteurs

def arbresIGN(mnt,fn_arbres,doc):
    """renvoie tous les arbres selon l'emprise de la bbox de obj"""

    origin = doc[CONTAINER_ORIGIN]
    
    if not os.path.isfile(fn_arbres):
        c4d.gui.MessageDialog("""Il manque le fichier : \n{0}\n\nL'import des arbres est impossible""".format(fn_arbres))
        return None
    doc_arbres = c4d.documents.LoadDocument(fn_arbres, c4d.SCENEFILTER_OBJECTS)
    #c4d.documents.LoadFile(fn_arbres)
    #doc_arbres = c4d.documents.GetActiveDocument()
    
    origin_doc_arbres = doc_arbres[CONTAINER_ORIGIN]
    srce_veget = doc_arbres.SearchObject('sources_vegetation')

    #doc.AddUndo
    
    #o_forets = doc_arbres.SearchObject('FORET_IGN')
    o_isoles = doc_arbres.SearchObject('ARBRES')
    
    
    bbox = Bbox.fromObj(mnt,origin)
    
    #on vérifie que l'objet a bien une largeur et une profondeur'
    if not bbox.largeur or not bbox.hauteur :
        c4d.gui.MessageDialog("L'objet séléctionné ne semble pas avoir de largeur ou de profondeur")
        return None
    
    #data_foret = getArbres(o_forets,bbox,origin_doc_arbres)
    pos, diam, haut = getArbres(o_isoles,bbox,origin_doc_arbres)
    pos = [p-origin for p in pos]
    
    #creation des instances

    create_mograph_cloner(doc,pos, haut, diam, srce_veget)
    
    #foret
    # foret = c4d.BaseObject(c4d.Onull)
    # foret.SetName('ARBRES_FORET')
    
    # for pos,diam,haut in data_foret:
    #     inst = c4d.BaseObject(c4d.Oinstance)
    #     inst.SetAbsPos(pos-origin)
    #     inst.SetAbsScale(c4d.Vector(diam/10,haut/10,diam/10))
    #     inst.SetAbsRot(c4d.Vector(random.random()*6.3,0,0))
    #     inst[c4d.INSTANCEOBJECT_LINK] = random.choice(srces)
    #     inst.InsertUnder(foret)
    # foret.InsertUnder(res)

    return

##############################################################################################################################
#MAIN
##############################################################################################################################

def main(fn_arbres):
    doc = c4d.documents.GetActiveDocument()
    op = doc.GetActiveObject()
    #vérification du géoréférencement du document
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        c4d.gui.MessageDialog("Le document n'est pas géoréférencé, l'extraction est impossible !")
        return
    #vérification qu'il y a bien un objet sélectionné
    if not op : 
        c4d.gui.MessageDialog("Vous devez d'abord séléctionner un objet pour l'emprise")
        return
    #on vérifie que l'objet à bien une dimension
    obj = op.GetCache()
    if not obj:
        if not op.CheckType(c4d.Opoint):
            c4d.gui.MessageDialog("Vous devez séléctionner un objet avec une géométrie")
            return
        else : obj = op

    
    doc.StartUndo()
        
    #ARBRES
    arbresIGN(op,fn_arbres,doc)
    
    doc.EndUndo()
    c4d.EventAdd()
  

if __name__=='__main__':
    fn_arbres = os.path.join(os.path.dirname(__file__),NOM_FICHIER_ARBRES)
    main(fn_arbres)
