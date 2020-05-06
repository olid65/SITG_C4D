# -*- coding: utf-8 -*-


import c4d, os, sys
import webbrowser 
#from c4d import plugins, bitmaps, gui, documents, Vector
from c4d.plugins import GeLoadString as txt

__version__ = 1.20
__date__    = "28/04/2020"

""" TODO :
    - undo pour import MNT (voir si besoin pour les autres)
    - barre import qui ne disparait pas et qui ne tourne pas quand on annule
    - centrer les polylignes et polygones lors de l'import shape
    - peupler des polygones avec instances
    """

"""Fait le 18 févier 2015:
        - verouillage selon n° de série
        - import pour Fabien
        - import pour Alexandre
        """
"""11 mars: 2015
        - options d'importation 3Ds en mètres"""
"""22 avril v1.1:
        -batiPLQ
        -import arbres SSIG"""
"""4 mai 2015 v1.11:
   - correction bug importation importBatiShape2
   - bati PLQ champ hauteur avec possibilité d'avoir le rez plus haut"""
"""28 mai :
   - bati PLQ réglages de tous les interdépendance lors de la modification d'un champ"""
"""5 novembre 2017
        -rajouté un module Importer un dossier Jeu de données 3D pour l'importation
         d'un dossier SITG spécifique
        -modification du script des arbres IGN, depuis un fichier c4d __arbresIGN__.c4d
         placé à la racine du plugin (au lieu du shape avant avec un fichier qui donnait le chemin)
        -géoréférencer les objets sélectionnés au lieu d'un seul
        -import 3DS : modification suite aux changements du SITG, + ajout d'import ouvrages d'art
        -import mnt ASC : lecture des entêtes à 5,6 ou même 7 lignes (type QGis avec dx et dy à la place de cellsize)
        -import dossier : tous les fichiers sont pris en compte dans la hiérarchie -> à terminer et à améliorer
"""

sys.path.append(os.path.join(os.path.dirname(__file__),'libs'))
import importDossier
import importJeuDonneesMaquette
import extracteurWeb
import activeTexture
import importRaster
import importMNT
import import3DS
import importArbresSSIG
import groupeTerrain
import georefObjet
import importShapefile
import importShapeBatiDALE
import importShapeBatiDALE2

SITG_MODULE_ID                  = 1034152 
SITG_IMPORT_DOSSIER_ID          = 1034151
SITG_IMPORT_JEU_DONNEES_ID      = 1035167
SITG_EXTRACTEUR_WEB_ID          = 1034153 
SITG_ACTIVETEXTURE_ID           = 1034157
SITG_IMPORT_RASTER_ID           = 1034158     
SITG_IMPORT_SHAPE_ID            = 1034159     
SITG_IMPORT_MNT_ID              = 1034160     
SITG_IMPORT_3DS_ID              = 1034161  
SITG_GROUPE_SUR_TERRAIN_ID      = 1034191
SITG_GEOREFERENCER_UN_OBJET_ID  = 1034192  
SITG_IMPORT_SHAPE_BATI_DALE_ID  = 1034565 
SITG_IMPORT_SHAPE_BATI_DALE2_ID = 1034660 
SITG_IMPORT_ARBRES_SSIG_ID      = 1035166 


SITG_SEPARATOR_01       = 1034154     
SITG_SEPARATOR_02       = 1034155
SITG_SEPARATOR_03       = 1034156    

SITG_IMPORT_DOSSIER_NOM    = 1101
SITG_IMPORT_DOSSIER_HLP     =1002

SITG_IMPORT_JEU_DONNEES_NOM  = 1151
SITG_IMPORT_JEU_DONNEES_HLP  = 1052

SITG_EXTRACTEUR_WEB_NOM    = 1201
SITG_EXTRACTEUR_WEB_HLP    = 1202

SITG_ACTIVETEXTURE_NOM     = 1301
SITG_ACTIVETEXTURE_HLP     = 1302

SITG_IMPORT_RASTER_NOM     = 1501
SITG_IMPORT_RASTER_HLP     = 1502

SITG_IMPORT_SHAPE_NOM      = 1601
SITG_IMPORT_SHAPE_HLP      = 1602

SITG_IMPORT_MNT_MNT        = 1701
SITG_IMPORT_MNT_HLP        = 1702

SITG_IMPORT_3DS_NOM        = 1801
SITG_IMPORT_3DS_HLP        = 1802

SITG_IMPORT_ARBRES_SSIG_NOM = 1851
SITG_IMPORT_ARBRES_SSIG_HLP = 1852

SITG_GRPE_SUR_TERRAIN_NOM  = 1901
SITG_GRPE_SUR_TERRAIN_HLP  = 1902

SITG_GEOREF_OBJ_NOM        = 1951
SITG_GEOREF_OBJ_HLP        = 1952

SITG_IMPORT_SHAPE_BATI_NOM = 2001
SITG_IMPORT_SHAPE_BATI_HLP = 2002

SITG_IMPORT_SHAPE_BATI2_NOM = 2101
SITG_IMPORT_SHAPE_BATI2_HLP = 2102

NAME_FILE_ARBRES_IGN = '__arbres_2018__.c4d'


    

class ImportDossier(c4d.plugins.CommandData):
    def Execute(self, doc) :
        importDossier.main()
        return True

class ImportJeuDonneesMaquette(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        importJeuDonneesMaquette.main(fn_arbres)
        return True

class ExtracteurWeb(c4d.plugins.CommandData):
    def Execute(self, doc) :
        extracteurWeb.main()
        return True

class ActiveTexture(c4d.plugins.CommandData):
    def Execute(self, doc) :
        activeTexture.main()
        return True
class ImportRaster(c4d.plugins.CommandData):
    def Execute(self, doc) :
        importRaster.main()
        return True
class ImportShape(c4d.plugins.CommandData):
    def Execute(self, doc) :
        importShapefile.main()
        return True

class ImportShapeBatiDALE(c4d.plugins.CommandData):
    def Execute(self, doc) :
        importShapeBatiDALE.main()
        return True

class ImportShapeBatiDALE2(c4d.plugins.CommandData):
    def Execute(self, doc) :
        importShapeBatiDALE2.main()
        return True

class ImportMNT(c4d.plugins.CommandData):
    def Execute(self, doc) :
        importMNT.main()
        return True
class Import3DS(c4d.plugins.CommandData):
    def Execute(self, doc) :
        import3DS.main()
        return True

class ImportArbresSSIG(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        importArbresSSIG.main(fn_arbres)
        return True


class GroupeSurTerrain(c4d.plugins.CommandData):
    def Execute(self, doc) :
        groupeTerrain.main()
        return True

class GeorefObj(c4d.plugins.CommandData):
    def Execute(self, doc) :
        georefObjet.main()
        return True

class SITG(c4d.plugins.CommandData) :
    def Execute(self, doc) :
        webbrowser.open('http://mip.hesge.ch')
        return True 
   

def icone(nom) :
    bmp = c4d.bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "res", nom)
    bmp.InitWith(fn)
    return bmp
    
if __name__=='__main__':
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_JEU_DONNEES_ID, str="#$00" + txt(SITG_IMPORT_JEU_DONNEES_NOM),
                                      info=0, help=txt(SITG_IMPORT_JEU_DONNEES_HLP), dat=ImportJeuDonneesMaquette(),
                                      icon=icone("sitg2.tif"))

    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_DOSSIER_ID, str = "#$01" + txt(SITG_IMPORT_DOSSIER_NOM), info = 0, help = txt(SITG_IMPORT_DOSSIER_HLP), dat = ImportDossier(), icon = icone("sitg2.tif"))


    
    c4d.plugins.RegisterCommandPlugin(id=SITG_SEPARATOR_01, str = "#$05--", info = 0, help = "", dat = SITG(), icon = None)

    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_RASTER_ID, str = "#$06" + txt(SITG_IMPORT_RASTER_NOM), info = 0, help = txt(SITG_IMPORT_RASTER_HLP), dat = ImportRaster(), icon = icone("wld.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_SHAPE_ID, str = "#$07" + txt(SITG_IMPORT_SHAPE_NOM), info = 0, help = txt(SITG_IMPORT_SHAPE_HLP), dat = ImportShape(), icon = icone("shp.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_SHAPE_BATI_DALE_ID, str = "#$08" + txt(SITG_IMPORT_SHAPE_BATI_NOM), info = 0, help = txt(SITG_IMPORT_SHAPE_BATI_HLP), dat = ImportShapeBatiDALE(), icon = icone("shp.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_SHAPE_BATI_DALE2_ID, str = "#$09" + txt(SITG_IMPORT_SHAPE_BATI2_NOM), info = 0, help = txt(SITG_IMPORT_SHAPE_BATI2_HLP), dat = ImportShapeBatiDALE2(), icon = icone("shp.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_MNT_ID, str = "#$10" + txt(SITG_IMPORT_MNT_MNT), info = 0, help = txt(SITG_IMPORT_MNT_HLP), dat = ImportMNT(), icon = icone("asc.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_3DS_ID, str = "#$11" + txt(SITG_IMPORT_3DS_NOM), info = 0, help = txt(SITG_IMPORT_3DS_HLP), dat = Import3DS(), icon = icone("3ds.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_ARBRES_SSIG_ID, str = "#$12" + txt(SITG_IMPORT_ARBRES_SSIG_NOM), info = 0, help = txt(SITG_IMPORT_ARBRES_SSIG_HLP), dat = ImportArbresSSIG(), icon = icone("arbresSSIG.tif"))

    c4d.plugins.RegisterCommandPlugin(id=SITG_SEPARATOR_02, str = "#$15--", info = 0, help = "", dat = SITG(), icon = None)

    
    c4d.plugins.RegisterCommandPlugin(id=SITG_ACTIVETEXTURE_ID, str = "#$16" + txt(SITG_ACTIVETEXTURE_NOM), info = 0, help = txt(SITG_ACTIVETEXTURE_HLP), dat = ActiveTexture(), icon = icone("activeTex2.png"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_GROUPE_SUR_TERRAIN_ID, str = "#$17"+ txt(SITG_GRPE_SUR_TERRAIN_NOM), info = 0, help = txt(SITG_GRPE_SUR_TERRAIN_HLP), dat = GroupeSurTerrain(), icon = icone("grpeTerrain.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_GEOREFERENCER_UN_OBJET_ID, str = "#$18"+ txt(SITG_GEOREF_OBJ_NOM), info = 0, help = txt(SITG_GEOREF_OBJ_HLP), dat = GeorefObj(), icon = icone("georef.tif"))

    c4d.plugins.RegisterCommandPlugin(id=SITG_SEPARATOR_03, str = "#$50--", info = 0, help = "", dat = SITG(), icon = None)

    c4d.plugins.RegisterCommandPlugin(id=SITG_EXTRACTEUR_WEB_ID, str = "#$51"+ txt(SITG_EXTRACTEUR_WEB_NOM), info = 0, help = txt(SITG_EXTRACTEUR_WEB_HLP), dat = ExtracteurWeb(), icon = icone("http.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_MODULE_ID, str = "#$52v{0} du {1} - http://mip.hesge.ch".format(__version__, __date__), info = 0, help = "http://mip.hesge.ch", dat = SITG(), icon = icone("mip.tif"))