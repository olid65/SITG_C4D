# coding: utf8


import c4d, os, random, math
from glob import glob

WIN =  c4d.GeGetCurrentOS()==c4d.OPERATINGSYSTEM_WIN

CONTAINER_ORIGIN =1026473


NOM_FICHIER_ARBRES = '__arbres2018__.c4d'
NOM_FICHIER_ORTHO = 'ORTHOPHOTOS.tif'
NOM_FICHIER_CALAGE = 'ORTHOPHOTOS.tfw'


MNT_FILE = 'MNT.3ds'
BAT3D_FILE = 'BATIMENTS.3ds'
BAT_PROJET = 'BATIMENTS_PROJETS.3ds'

NOM_OA = "OUVRAGES D'ART"

TRANSLATION_3DS = c4d.Vector(2480000.00,0,1109000.00)

def refCPoly(cpoly,id):
    """rajoute id aux valeurs a,b,c,d du polygon"""
    cpoly.a+=id
    cpoly.b+=id
    cpoly.c+=id
    cpoly.d+=id
    return cpoly

def connect(lst_poly, nom = None):
    """connecte tous les polys entre eux et renvoie
       un polygon object avec l'axe au centre à la base du batiment
       ATTENTION lancer la commande OPTIMIZE APRES"""
    pts = []
    polys = []
    
    pos = 0
    for poly in lst_poly:
        mg = poly.GetMg()
        pts+=[p*mg for p in poly.GetAllPoints()]
        polys += [refCPoly(p,pos) for p in poly.GetAllPolygons()]
        pos+=poly.GetPointCount()
    res = c4d.PolygonObject(len(pts),len(polys))
    res.SetAllPoints(pts)
    for i,p in enumerate(polys): res.SetPolygon(i,p)
    res.Message(c4d.MSG_UPDATE)
    centre = res.GetMp()
    rad = res.GetRad()
    centre.y-=rad.y
    pts = [p-centre for p in pts]
    res.SetAllPoints(pts)
    mg = res.GetMg()
    mg.off = centre
    res.SetMg(mg)
    if nom : res.SetName(nom)
    res.Message(c4d.MSG_UPDATE)
    return res  

def isInMetre(doc):
    scale, unit = doc[c4d.DOCUMENT_DOCUNIT].GetUnitScale()
    if unit == c4d.DOCUMENT_UNIT_M :return True
    return False
        

def getBbox3D(obj, addY = 2000):
    #creation d'un cube au dimension du MNT
    cube = c4d.BaseObject(c4d.Ocube)
    mg = obj.GetMg()
    cube.SetAbsPos(obj.GetMp()*mg)
    cube[c4d.PRIM_CUBE_LEN] = obj.GetRad()*2
    #on rajoute addY en hauteur pour etre sur que cela englobe les batiments
    cube[c4d.PRIM_CUBE_LEN,c4d.VECTOR_Y]+=addY
    return cube

def cutModel(obj,null_model):
    cube = getBbox3D(obj)
    boole = c4d.BaseObject(c4d.Oboole)
    boole[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_INTERSECT
    boole[c4d.BOOLEOBJECT_HIGHQUALITY]= False
    cube.InsertUnder(boole)
    null_model.InsertUnder(boole)
    #on ouvre un autre doc pour le resultat du booleen
    temp = c4d.documents.BaseDocument()
    temp.SetData(c4d.documents.GetActiveDocument().GetData())
    temp.InsertObject(boole)
    #polygonize renvoie un document avec tous les objets edites
    temp = temp.Polygonize()
    #on recupere notre groupe de batiments
    res = temp.GetFirstObject().GetDown().GetClone()
    temp.Remove()
    return res

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
            pos.y-=haut
            res.append((pos+origin_doc_arbres,diam,haut))
    return res

def arbresIGN(mnt,fn_arbres):
    """renvoie tous les arbres selon l'emprise de la bbox de obj"""
    res = c4d.BaseObject(c4d.Onull)
    res.SetName('ARBRES')
    doc = c4d.documents.GetActiveDocument()
    origin = doc[CONTAINER_ORIGIN]
    #fn_arbres = os.path.join(os.path.dirname(__file__),NOM_FICHIER_ARBRES)
    if not os.path.isfile(fn_arbres):
        c4d.gui.MessageDialog("""Il manque le fichier : \n{0}\n\nL'import des arbres est impossible""".format(fn_arbres))
        return False
    doc_arbres = c4d.documents.LoadDocument(fn_arbres, c4d.SCENEFILTER_OBJECTS)
    #c4d.documents.LoadFile(fn_arbres)
    #doc_arbres = c4d.documents.GetActiveDocument()
    
    origin_doc_arbres = doc_arbres[CONTAINER_ORIGIN]
    srce_veget = doc_arbres.SearchObject('sources_vegetation').GetClone()
    
    srce_veget.InsertUnder(res)
    srces = srce_veget.GetChildren()
    #doc.AddUndo
    
    o_forets = doc_arbres.SearchObject('FORET_IGN')
    o_isoles = doc_arbres.SearchObject('ARBRE_IGN_ICA')
    
    
    bbox = Bbox.fromObj(mnt,origin)
    
    data_foret = getArbres(o_forets,bbox,origin_doc_arbres)
    data_isoles = getArbres(o_isoles,bbox,origin_doc_arbres)
    
    #creation des instances
    #arbres_isoles
    isoles = c4d.BaseObject(c4d.Onull)
    isoles.SetName('ARBRES_ISOLES')
    
    for pos,diam,haut in data_isoles:
        inst = c4d.BaseObject(c4d.Oinstance)
        inst.SetAbsPos(pos-origin)
        inst.SetAbsRot(c4d.Vector(random.random()*6.3,0,0))
        inst.SetAbsScale(c4d.Vector(diam/10,haut/10,diam/10))
        inst[c4d.INSTANCEOBJECT_LINK] = random.choice(srces)
        inst.InsertUnder(isoles)
    isoles.InsertUnder(res)
    
    #foret
    foret = c4d.BaseObject(c4d.Onull)
    foret.SetName('ARBRES_FORET')
    
    for pos,diam,haut in data_foret:
        inst = c4d.BaseObject(c4d.Oinstance)
        inst.SetAbsPos(pos-origin)
        inst.SetAbsScale(c4d.Vector(diam/10,haut/10,diam/10))
        inst.SetAbsRot(c4d.Vector(random.random()*6.3,0,0))
        inst[c4d.INSTANCEOBJECT_LINK] = random.choice(srces)
        inst.InsertUnder(foret)
    foret.InsertUnder(res)
    
    
    return res

#################################
#ORTHOPHOTO
##################################

def listdirectory(path): 
    """retourne une liste de tous les dossiers en enfants de path"""
    res=[] 
    
    for root, dirs, files in os.walk(path): 
        for i in dirs: 
            res.append(os.path.join(root, i))
    return res

def is_in_doc_path(fn,doc):
    """retourne vrai si le fichier est au meme endroit que doc 
       ou dans tex ou dans un sous dossier de tex"""
    path_img,name_img = os.path.split(fn)
    path_doc = doc.GetDocumentPath()    
    if not path_doc : 
        return False
    if path_doc==path_img:
        return True
    path_tex = os.path.join(path_doc,'tex')
    if path_tex == path_img:
        return True
    lst_dir =listdirectory(path_tex)
    if path_img in lst_dir:
        return True
    return False

class Geopict ():

    """classe pour la gestion d'images g\or\f\renc\es"""

    def __init__(self,fn,fn_calage,doc):
        self.doc = doc
        self.fn = fn
        name = os.path.splitext(self.fn)[0]
        self.f_calage = fn_calage
        self.readCalage()
        self.calculRef()

            

    def readCalage(self):
        """fonction pour la lecture du fichier de calage"""
        try :
            with open(self.f_calage,'r') as f :
               self.val_pix = float(f.readline().split()[0])
               val2 = float(f.readline().split()[0])
               val3 = float(f.readline().split()[0])
               val4 = float(f.readline().split()[0])
               #ATTENTION DANS L?IMPORT SITG GROUPö LE FICHIER DE CALAGE 
               #A LA MEME TRANSLATION QUE LE 3DS
               self.val_x = float(f.readline().split()[0]) + TRANSLATION_3DS.x
               self.val_z = float(f.readline().split()[0]) + TRANSLATION_3DS.z
               f.close()


        except IOError:
            print ("Il n'y a pas de fichier de calage")
            return False

            

        else :
            return True

            

    def calculRef(self):

        bmp = c4d.bitmaps.BaseBitmap()

        try:
            fn = self.fn
            if WIN : fn = self.fn.decode('cp1252').encode('utf-8')
            bmp.InitWith(fn)
            self.size_px = bmp.GetSize()
            self.size = c4d.Vector(self.size_px[0]*self.val_pix,0,
                         self.size_px[1]*self.val_pix)
            #pour le min et max ne pas oublier que sur le fichier de calage la position est le centre du premier pixel
            self.min = c4d.Vector(self.val_x - self.val_pix/2.0,0.0,self.val_z + self.val_pix/2.0 -self.size.z)
            self.max = self.min+self.size
            self.centre = (self.min+self.max)/2.0
        except :

            print ("Probleme avec l'image")

            

    def creerTexture(self,relatif = False, win = False):
        self.mat = c4d.BaseMaterial(c4d.Mmaterial)
        self.doc.InsertMaterial(self.mat)
        self.doc.AddUndo(c4d.UNDOTYPE_NEW,self.mat)
        shd = c4d.BaseList2D(c4d.Xbitmap)
        #ATENTION au backslash suivi de t ou de p cela est consid\r\ comme tab ou 
        fn = self.fn
        if WIN :
            fn = self.fn.decode('cp1252').encode('utf-8')
        if is_in_doc_path(fn,self.doc):
            shd[c4d.BITMAPSHADER_FILENAME] = os.path.basename(fn)
        else:
            shd[c4d.BITMAPSHADER_FILENAME] = fn
        self.mat[c4d.MATERIAL_COLOR_SHADER] = shd
        self.mat.InsertShader(shd)
        self.mat[c4d.MATERIAL_USE_REFLECTION] = False
        self.mat[c4d.MATERIAL_PREVIEWSIZE]=12#taille de pr\visualisation
        self.mat.SetName(os.path.basename(fn)[:-4])
        self.mat.Message(c4d.MSG_UPDATE)
        self.mat.Update(True, True)

    def creerPlan(self):

        plan = c4d.BaseObject(c4d.Oplane)
        plan[c4d.PRIM_PLANE_WIDTH]=self.size.x
        plan[c4d.PRIM_PLANE_HEIGHT]=self.size.z
        plan[c4d.PRIM_PLANE_SUBW]=1
        plan[c4d.PRIM_PLANE_SUBH] =1
        
        origine = self.doc[CONTAINER_ORIGIN]
        if not origine:
            origine = self.centre
            self.doc[CONTAINER_ORIGIN]= origine
        plan.SetAbsPos(self.centre-origine)
        plan.SetName(os.path.basename(self.fn))
        self.creerTagTex(plan)
        self.creerGeoTag(plan)
        self.doc.InsertObject(plan)  
        self.doc.AddUndo(c4d.UNDOTYPE_NEW,plan)     

    def creerTagTex(self,obj,displayTag = True):
        if displayTag:
            tgdisp = c4d.BaseTag(c4d.Tdisplay)#tag affichage
            tgdisp[c4d.DISPLAYTAG_AFFECT_DISPLAYMODE]=True
            tgdisp[c4d.DISPLAYTAG_SDISPLAYMODE]=7 #Ombrage constant
            
            obj.InsertTag(tgdisp)
   

        tgtex = c4d.BaseTag(c4d.Ttexture)#tag affichage
        tgtex[c4d.TEXTURETAG_MATERIAL]=self.mat
        tgtex[c4d.TEXTURETAG_PROJECTION]=2 #projection planaire
        tgtex[c4d.TEXTURETAG_TILE]=False #r\p\titions
        tgtex[c4d.TEXTURETAG_SIZE]=c4d.Vector(self.size.x/2,self.size.z/2, 1)
        tgtex[c4d.TEXTURETAG_ROTATION]=c4d.Vector(0,-math.pi/2,0)
        
        tgtex[CONTAINER_ORIGIN] = self.centre

        #dernier tag
        last = None
        tags = obj.GetTags()
        if len(tags):
            last = tags[-1]

        obj.InsertTag(tgtex, last)
        return tgtex
        
    def creerGeoTag(self,obj):
        pos = obj.GetMg().off
        geoTag = c4d.BaseTag(1026472) #GeoTag
        origine = self.doc[CONTAINER_ORIGIN]
        if not origine:
            origine = self.centre
            self.doc[CONTAINER_ORIGIN]= origine
        geoTag[CONTAINER_ORIGIN] = origine + pos
        
        obj.InsertTag(geoTag)
        return geoTag


    def __str__(self):
        sp = 40
        txt = ('-'*sp*3+'\n'+
                "FICHIER DE CALAGE :\n"+
                ' '*sp+self.f_calage+'\n'+
                ' '*sp+'valeur du pixel : '+str(self.val_pix)+'\n'+
                ' '*sp+'coord x         : '+str(self.val_x)+'\n'+
                ' '*sp+'coord z         : '+str(self.val_z)+'\n'+
                '-'*sp*3+'\n'+

                "IMAGE :\n"+
                ' '*sp+self.fn+'\n'+
                ' '*sp+'taille (px)     : '+str(self.size_px)+'\n'+
                ' '*sp+'taille (m)      : '+str(self.size)+'\n'+
                ' '*sp+'min             : '+str(self.min)+'\n'+
                ' '*sp+'max             : '+str(self.max)+'\n'+
                ' '*sp+'centre          : '+str(self.centre)+'\n'+
                '-'*sp*3)
        return txt



def readTFW(fn):
    if fn :
        try :
            with open(fn,'r') as f :
               val_pix = float(f.readline().split()[0])
               val2 = float(f.readline().split()[0])
               val3 = float(f.readline().split()[0])
               val4 = float(f.readline().split()[0])
               val_x = float(f.readline().split()[0])
               val_z = float(f.readline().split()[0])
               f.close()

        except IOError:
            print ("Il n'y a pas de fichier")
            return False            

        else :
            return True

    else :
        return False
##############################################################################################################################
#MAIN
##############################################################################################################################

def main(fn_arbres):
    doc = c4d.documents.GetActiveDocument()
    #on verifie que le document est en metres
    if not isInMetre(doc):
        #res = c4d.gui.QuestionDialog("""L'unité du document n'est pas le mètre, ce paramètre va être modifié\n\nVoulez-vous continuer? (pas d'annulation possible)""")
        #if not res : return
        #doc.AddUndo(c4d.UNDOTYPE_CHANGE,doc) #-> ne fonctionne pas !
        us = doc[c4d.DOCUMENT_DOCUNIT]
        us.SetUnitScale(1, c4d.DOCUMENT_UNIT_M)
        doc[c4d.DOCUMENT_DOCUNIT] = us
    
    #mise en cm des option d'importation 3DS
    plug = c4d.plugins.FindPlugin(1001037, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        print ("pas de module d'import 3DS")
        return 
    op = {}
   
    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):
        
        import_data = op.get("imexporter",None)
        if not import_data:
            print ("pas de data pour l'import 3Ds")
            return
        
        # Change 3DS import settings
        scale = import_data[c4d.F3DSIMPORTFILTER_SCALE]
        scale.SetUnitScale(1,c4d.DOCUMENT_UNIT_M)
        import_data[c4d.F3DSIMPORTFILTER_SCALE] = scale
    
    
    origin = doc[CONTAINER_ORIGIN]

    path = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY,title="Séléctionnez le dossier décompressé téléchargé depuis le SITG :")
    
    
    if not path: return
    
    #TODO : vérifier que c'est bien un dossier maquette

    # pour windows pour essayer de régler les histoires d'accents'
    if WIN:
        path = path.decode('utf-8').encode('cp1252')
    
    
    last = None
    oa = None
    
    lst_objs = []
    last = doc.GetFirstObject()
    
    doc.StartUndo()
    first_o = doc.GetFirstObject()
    first_mat = doc.GetFirstMaterial()
    
    #iIMPORT TERRAIN,BATIMENTS; BATI PROJET
    for fn in glob(path+'/*.3ds'):

        #lst_objs.append(onull)
        
        name = os.path.basename(fn[:-4])

        res = c4d.documents.MergeDocument(doc, fn, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MATERIALS)

        objs = []
        objs[:] = [] #pour etre sur que la liste soit bien vide
        
        obj = doc.GetFirstObject()

        while(obj and obj != last):
            objs.append(obj)
            obj = obj.GetNext()
        
        #si c'est le mnt ou bati on regroupe sur un seul objet polygonal'
        if name == 'MNT' or name =='BATIMENTS':
            o = connect(objs, name)
            if o:
                doc.InsertObject(o)
                doc.AddUndo(c4d.UNDOTYPE_NEW,o)
                last = o
                lst_objs.append(o)
                #on efface les objets polygonaux
                for obj in objs:
                    obj.Remove()
            
        else:
            onull = c4d.BaseObject(c4d.Onull)
            doc.InsertObject(onull)
            doc.AddUndo(c4d.UNDOTYPE_NEW,onull)
            onull.SetName(os.path.basename(fn[:-4]))
            last = onull
            for o in objs:
                o.InsertUnder(onull)
                lst_objs.append(o)
 
 

    #IMPORT OUVRAGES ART
    for fn in os.listdir(path):
        nom_compl = os.path.join(path,fn)
        if os.path.isdir(nom_compl):
            if not oa:
                oa = c4d.BaseObject(c4d.Onull)
                oa.SetName(NOM_OA)
                doc.InsertObject(oa)
                
                doc.AddUndo(c4d.UNDOTYPE_NEW,oa)
                last = oa
            onull = c4d.BaseObject(c4d.Onull)
            onull.SetName(fn)
            onull.InsertUnderLast(oa)
            
            
            for fn_3ds in glob(nom_compl+'/*.3ds'):
                res = c4d.documents.MergeDocument(doc, fn_3ds, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MATERIALS)
            
            obj = doc.GetFirstObject()
            while(obj and obj != last):
                obj.InsertUnder(onull)
                lst_objs.append(obj)
                obj = doc.GetFirstObject()
                
    #CENTRAGE DANS LA SCENE
    #si le document n'est pas georeference on centre sur l'emprise du MNT
    centre = None
    
    mnt = doc.SearchObject('MNT')
    
    if not mnt :
        print ('pas de centre')
        return
    
    centre = mnt.GetMg().off

    
    if not origin:
        origin =  TRANSLATION_3DS + centre
        doc[CONTAINER_ORIGIN] = origin
        
    
    if not origin or not centre:
        print ("pas d'origine")
        return
         
    #on fait une translation avec tous les objets polygonaux importés
    trans = origin - TRANSLATION_3DS
    for o in lst_objs:
        mg = o.GetMg()
        mg.off+=TRANSLATION_3DS -origin
        o.SetMg(mg)
        
        #suppression des tags de texture
        t =o.GetTag(c4d.Ttexture)
    
        while t:
            t.Remove()
            t =o.GetTag(c4d.Ttexture)
    
    model = c4d.BaseObject(c4d.Onull)
    model.SetName(os.path.basename(path))
    doc.InsertObject(model)
    doc.AddUndo(c4d.UNDOTYPE_NEW,model)
    
    obj = model.GetNext()
    while obj and obj!= first_o :
        pred = obj
        obj = obj.GetNext()
        pred.InsertUnder(model)
    
    model_cut = cutModel(mnt,model)
    doc.InsertObject(model_cut)
    
    #suppression des materiaux
    mat = doc.GetFirstMaterial()
    while mat and mat!=first_mat:
        pred = mat
        mat = mat.GetNext()
        pred.Remove()
        
    #ARBRES
    # mnt = doc.SearchObject('MNT')
    # arbres = arbresIGN(mnt,fn_arbres)
    # if arbres :
    #     arbres.InsertUnder(model_cut)
    
    ###ORTHOPHOTO
    fn_ortho = os.path.join(path,NOM_FICHIER_ORTHO)
    fn_calage = os.path.join(path,NOM_FICHIER_CALAGE)
    if os.path.isfile(fn_ortho) and os.path.isfile(fn_calage):
        #MATERIAL
        gp = Geopict(fn_ortho,fn_calage,c4d.documents.GetActiveDocument())
        gp.creerTexture(relatif = False, win = WIN)
    
        gp.creerTagTex(model_cut,displayTag = False)
    
    doc.EndUndo()
    c4d.EventAdd()
  

if __name__=='__main__':
    fn_arbres = fn_arbres = os.path.join(os.path.dirname(__file__),NOM_FICHIER_ARBRES)
    main(fn_arbres)
