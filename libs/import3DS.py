# -*- coding: utf-8 -*-

#modifié le 25 octore 2017
#nom selon le fichier


import c4d
import re,os

#valeurs de décalage des fichiers 3DS
DECAL_X = 2480000.00
DECAL_Z = 1109000.00
DECALAGE = c4d.Vector(2480000.00,0,1109000.00)

NOM_BAT3D = 'BATIMENTS_PROJETS'
NOM_BAT_PROJET = 'BATIMENTS'


CONTAINER_ORIGIN =1026473

ID_EGID_BC = 1030877 #no unique pour stocker les EGID et les polygones s'y rapportant (voir connectSupprim())

def connectSupprim(lst_obj,name,doc,bc =False):
    """bc est si on veut stocker les egid sous forme de basecontainer"""
    nb_pts = 0
    nb_poly = 0
    #BaseContainer pour stocker en etiquette l'EGID
    #en valeur un ss-conteneur stocke en 0 l'id du premier poly
    #et en 1 le nombre de polygones du batiment
    #ATTENTION de bien fusionner par noEGID avant pour ne pas avoir deux poly 
    #avec le meme no
    if bc : 
        #premier container qui contient en 0 le nombre de batiment ...
        bc_egid = c4d.BaseContainer() 
        #et en 1 le sous-container contenant tous les container pour chaque bâtiment
        sub_bc1 = c4d.BaseContainer()
    
    for i,obj in enumerate(lst_obj):
        if bc:
            egid = int(obj.GetName())
            ss_bc = c4d.BaseContainer()
            ss_bc[0] = nb_poly
            ss_bc[1] = obj.GetPolygonCount()
            ss_bc[2] = egid 
            sub_bc1.SetContainer(i, ss_bc)

        nb_pts+=obj.GetPointCount()
        nb_poly+=obj.GetPolygonCount()
    res = c4d.PolygonObject(nb_pts,nb_poly)
    #on lui colle le baseContainer avec les no EGID
    if bc : 
        #en 0 le nombre de bâtiemnt
        bc_egid[0] = len(lst_obj)
        #en 1 le sous
        bc_egid.SetContainer(1, sub_bc1)
        
        res[ID_EGID_BC] = bc_egid
        
        

    res.SetName(name)
    id_pt_dprt=0
    id_poly_dprt =0
    
    for obj in lst_obj:
        for i,pt in enumerate(obj.GetAllPoints()):
            res.SetPoint(i+id_pt_dprt,pt)
        for i,poly in enumerate(obj.GetAllPolygons()):
            poly.a += id_pt_dprt
            poly.b += id_pt_dprt
            poly.c += id_pt_dprt
            poly.d += id_pt_dprt
            
            res.SetPolygon(i+id_poly_dprt,poly)
        id_pt_dprt+=obj.GetPointCount()
        id_poly_dprt += obj.GetPolygonCount()    
        obj.Remove()
    res.Message(c4d.MSG_UPDATE)
    doc.InsertObject(res)
    doc.AddUndo(c4d.UNDOTYPE_NEW,res)
    return res
    
def centrerAxe(obj):
    mg = obj.GetMg()
    trans = obj.GetMp()
    trans.y = 0
    mg.off += trans
    if obj.GetPointCount():
        pts = [p-trans for p in obj.GetAllPoints()]
        obj.SetAllPoints(pts)
    obj.SetMg(mg)
    obj.Message(c4d.MSG_UPDATE)

def main(fn = None):
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

    
    doc = c4d.documents.GetActiveDocument()

    if not fn:
        fn = c4d.storage.LoadDialog(type = c4d.FILESELECTTYPE_SCENES,
                                title= "Fichier 3DS")

    if not fn : return
    nom, ext =  os.path.splitext(os.path.basename(fn))

    if not ext == '.3ds' : 
        c4d.gui.MessageDialog("Ce n'est pas un fichier 3ds")
        return
    
    doc.StartUndo()
    first_object = doc.GetFirstObject()
    
    c4d.documents.MergeDocument(doc, fn, c4d.SCENEFILTER_OBJECTS)
    
    objs = []
    obj = doc.GetFirstObject()
    while obj:
        if obj == first_object : break
        objs.append(obj)
        obj = obj.GetNext()
        
    #si on a des batiments existants ou projet on stocke les
    #les polygones pour pouvoir mettre à l'échelle différenciée
    #type échelle Magnin'
    bc = None
    if nom == NOM_BAT3D or nom == NOM_BAT_PROJET: bc = True
    connectSupprim(objs,nom,doc,bc)
    
    obj = doc.GetFirstObject()
    while obj:
        if obj == first_object : break
        centrerAxe(obj)
        mg = obj.GetMg()
        if not doc[CONTAINER_ORIGIN]:
            doc[CONTAINER_ORIGIN] = mg.off + DECALAGE
            mg.off = c4d.Vector()
        else :
            mg.off += DECALAGE - doc[CONTAINER_ORIGIN]
        obj.SetMg(mg)    
        obj = obj.GetNext()

    #c4d.CallCommand(12148) # Cadrer la géométrie
    c4d.EventAdd()
    doc.EndUndo()
    
    
if __name__=='__main__':
    main()