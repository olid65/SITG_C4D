# -*- coding: utf-8 -*-

import c4d, re, sys
import glob  
import os.path  

sys.path.append(os.path.dirname(__file__))
from libs import shapefile
import import3DS, importMNT, importRaster


CONTAINER_ORIGIN =1026473

LST_EXTENSIONS_IMAGES = ['.jpg','.png','.tif']

PREFIXE_BAT3D = 'BATIMENTS'
PREFIXE_MNT = 'MNT'

NOM_ICA = 'SIPV_ICA_ARBRE_ISOLE.shp'

#pour savoir si on est sur windows pour le codage des chemins de fichiers
WIN =  c4d.GeGetCurrentOS()==c4d.OPERATINGSYSTEM_WIN



def winpath(path):
    return path.decode('utf-8').encode('cp1252')
  
def dicodirectory(path,dico = None):  
    """renvoie un dictionnaire avec en étiquette l'extension
       et en valeur la liste de tous les fichiers"""
    if not dico : dico={}  
    l = glob.glob(os.path.join(path,'*'))  
    for f in l:
        
        if os.path.isdir(f): dico =dicodirectory(f,dico)  
        else: 
            nom,ext = os.path.splitext(f)
            if ext:
                #on met toutes les extensions en minuscules pour éviter les problèmes
                dico.setdefault(ext.lower(),[]).append(f)
    return dico

def changeEXT(fn,ext):
    nom,ext_old = os.path.splitext(fn)
    return nom+ext

def getImgExt(fn_wld,dico_fn,ext):
    """renvoie le chemin de l'image liée au fichier de calage
       ou None selon l'extension"""
    if dico_fn.get(ext,None):
            fn_img = changeEXT(fn_wld,ext)
            if fn_img in dico_fn[ext]:
                return fn_img
    return None

def getImgGeoref(fn_wld,dico_fn):
    """renvoie le chemin de l'image liée au fichier de calage
       ou None selon l'extension"""
    for ext in LST_EXTENSIONS_IMAGES:
        fn_img =  getImgExt(fn_wld,dico_fn,ext)
        if fn_img : return fn_img

    return None

######################################################################
#MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN 
######################################################################

def main():
    
    doc = c4d.documents.GetActiveDocument()
    # MODIFICATION DES PARAMETRES D'IMPORTATION 3DS en metres
    # recuperation du 3DS Import plugin, 1001037
    #pour trouver l'id:
    #plugs = plugins.FilterPluginList(c4d.PLUGINTYPE_SCENELOADER, True)
    #for plug in plugs:
        #print(plug.GetName(), '-', plug.GetID())
        
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
        
    #path = '/Users/donzeo/Documents/Cours/CAS3D_2017/Cours_CINEMA4D_novembre_2017/exo_maquette_Jonction/extraction_SITG'
    #path = '/Users/donzeo/Documents/Cours/CAS3D_2017/Cours_CINEMA4D_novembre_2017/parc_geisendorf/SITG'
    path = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY,title="Dossier contenant les dossiers provenants du SITG")
    
    if not path : return
    #document en mètre
    us = doc[c4d.DOCUMENT_DOCUNIT]
    us.SetUnitScale(1,c4d.DOCUMENT_UNIT_M)
    doc[c4d.DOCUMENT_DOCUNIT]= us
    
    if WIN : path = winpath(path)
    
    dic_fn = dicodirectory(path)
    doc.StartUndo()
    
    bat = None
    mnt = None

    ######################################################################
    #import des 3ds
    ######################################################################
    lst_3ds =  dic_fn.get('.3ds', [])
    for fn_3ds in lst_3ds:
        name = os.path.basename(fn_3ds)
        #si le fichier commence par le PREFIXE_BAT c'est du bati3D'
        if re.search(r'^'+PREFIXE_BAT3D,name):
            import3DS.main(fn_3ds)

        #si le fichier commence par le PREFIXE_MNT c'est un MNT 3ds'
        elif re.search(r'^'+PREFIXE_MNT,name):
            import3DS.main(fn_3ds)

        #si le nom sans l'extension ne contient que des chiffres c'est un ouvrage d'art    
        elif name[:-4].isdigit():
            import3DS.main(fn_3ds)

        #si il y a un fichier shape avec le même nom c'est un batiment remarquable
        elif os.path.isfile(fn_3ds[:-4]+'.shp'):
            print (name,"->bâtiments remarquables pas encore pris en compte")
        
        #sinon on passe
        else:
            print (fn_3ds, "-> pas pris en compte")

    ######################################################################
    #import des shapefile
    ######################################################################
    lst_shp =  dic_fn.get('.shp', [])
    for fn_shp in lst_shp:
        name = os.path.basename(fn_shp)
        #ICA
        if name == NOM_ICA:
            print (name, "-> ICA")
        #AUTRES
        else:
            print (name)
    ######################################################################
    #import des images géoréférencées
    ######################################################################
    #TODO extension fichier jgw & co
    
    lst_img_georef = []
    lst_wld =  dic_fn.get('.wld', [])
    for fn_wld in lst_wld:
        fn_img = getImgGeoref(fn_wld,dic_fn)
        if fn_img:
            #on ajoute le tuple fichier calage, fichier image à la liste
            #lst_img_georef.append(fn_wld,fn_img)
            #materiaux et texturer les objets
            importRaster.main(fn_img,fn_wld, alerte = False)
    ######################################################################
    #import mnt et/ou mns asc
    ######################################################################
    lst_asc = dic_fn.get('.asc', [])
    for fn in lst_asc:
        importMNT.main(fn)
    

    
    
    
    doc.EndUndo()
    c4d.EventAdd()
    
if __name__=='__main__':
    main()
