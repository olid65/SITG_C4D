# coding: utf8

""" droits réservés Olivier Donzé juillet 2017
    à l'usage exclusif de mes étudiants en bachelor, master et formation continue de l'hepia
    
    version 2.0 du 28 avril 2020"""

import c4d, os, random, math
from glob import glob

WIN =  c4d.GeGetCurrentOS()==c4d.OPERATINGSYSTEM_WIN

CONTAINER_ORIGIN =1026473


NOM_FICHIER_ARBRES = '__arbres_2018__.c4d'



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
    """renvoie une liste de tuple (position,diamètre, hauteur)
       pour chaque arbres contenu dans la bbox"""
       
    tags = ptObj.GetTags()
    tag_vmax_diam =  tags[0]
    tag_vmax_haut = tags[1]
    
    res = []
    for pos,diam,haut in zip(ptObj.GetAllPoints(), 
                               tag_vmax_diam.GetAllHighlevelData(),
                               tag_vmax_haut.GetAllHighlevelData()):
        if bbox.ptIsInside(pos+origin_doc_arbres):
            #pos.y-=haut
            res.append((pos+origin_doc_arbres,diam,haut))
    return res

def arbresIGN(mnt,fn_arbres):
    """renvoie tous les arbres selon l'emprise de la bbox de obj"""
    res = c4d.BaseObject(c4d.Onull)
    res.SetName('ARBRES')
    doc = c4d.documents.GetActiveDocument()
    origin = doc[CONTAINER_ORIGIN]
    
    if not os.path.isfile(fn_arbres):
        c4d.gui.MessageDialog("""Il manque le fichier : \n{0}\n\nL'import des arbres est impossible""".format(fn_arbres))
        return None
    doc_arbres = c4d.documents.LoadDocument(fn_arbres, c4d.SCENEFILTER_OBJECTS)
    #c4d.documents.LoadFile(fn_arbres)
    #doc_arbres = c4d.documents.GetActiveDocument()
    
    origin_doc_arbres = doc_arbres[CONTAINER_ORIGIN]
    srce_veget = doc_arbres.SearchObject('sources_vegetation').GetClone()
    
    srce_veget.InsertUnder(res)
    srces = srce_veget.GetChildren()
    #doc.AddUndo
    
    #o_forets = doc_arbres.SearchObject('FORET_IGN')
    o_isoles = doc_arbres.SearchObject('ARBRES')
    
    
    bbox = Bbox.fromObj(mnt,origin)
    
    #on vérifie que l'objet a bien une largeur et une profondeur'
    if not bbox.largeur or not bbox.hauteur :
        c4d.gui.MessageDialog("L'objet séléctionné ne semble pas avoir de largeur ou de profondeur")
        return None
    
    #data_foret = getArbres(o_forets,bbox,origin_doc_arbres)
    data_isoles = getArbres(o_isoles,bbox,origin_doc_arbres)
    
    #creation des instances
    #arbres_isoles
    isoles = c4d.BaseObject(c4d.Onull)
    isoles.SetName('ARBRES')
    
    for pos,diam,haut in data_isoles:
        inst = c4d.BaseObject(c4d.Oinstance)
        inst.SetAbsPos(pos-origin)
        inst.SetAbsRot(c4d.Vector(random.random()*6.3,0,0))
        inst.SetAbsScale(c4d.Vector(diam/10,haut/10,diam/10))
        inst[c4d.INSTANCEOBJECT_LINK] = random.choice(srces)
        inst.InsertUnder(isoles)
    isoles.InsertUnder(res)
    
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
    
    
    return res

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
    arbres =arbresIGN(op,fn_arbres)
    if arbres:
        doc.InsertObject(arbres)
        doc.AddUndo(c4d.UNDOTYPE_NEW,arbres)
    
    doc.EndUndo()
    c4d.EventAdd()
  

if __name__=='__main__':
    fn_arbres = os.path.join(os.path.dirname(__file__),NOM_FICHIER_ARBRES)
    main(fn_arbres)
