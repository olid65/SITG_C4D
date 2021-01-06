# -*- coding: utf-8 -*-


import c4d, os, sys
import webbrowser 
#from c4d import plugins, bitmaps, gui, documents, Vector
from c4d.plugins import GeLoadString as txt

__version__ = 3.13
__date__    = "06/01/2021"



sys.path.append(os.path.dirname(__file__))
from libs import importDossier
from libs import importJeuDonneesMaquette
from libs import extracteurWeb
from libs import activeTexture
from libs import importRaster
from libs import importMNT
from libs import import3DS
from libs import importArbresSSIG
from libs import groupeTerrain
from libs import pointsOnSurface
from libs import georefObjet
from libs import importShapefile
from libs import importShapeBatiDALE
from libs import importShapeBatiDALE2
from libs import importArbresShapePoint
from libs import importArbresShapeLine
from libs import importArbresShapePoly
from libs import import_SwissBuildings3D
from libs import treesFromPolygons
from libs import treesFromLines
from libs import empriseGeo

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
SITG_POINTS_ON_SURFACE_ID       = 1056430

SITG_GEOREFERENCER_UN_OBJET_ID  = 1034192  
SITG_IMPORT_SHAPE_BATI_DALE_ID  = 1034565 
SITG_IMPORT_SHAPE_BATI_DALE2_ID = 1034660 
SITG_IMPORT_ARBRES_SSIG_ID      = 1035166
SITG_IMPORT_ARBRE_SHAPE_PT_ID   = 1055059
SITG_IMPORT_ARBRE_SHAPE_LINE_ID = 1056359
SITG_IMPORT_ARBRE_SHAPE_POLY_ID = 1056360
SITG_IMPORT_BATI_SWISSTOPO_ID   = 1055062

SITG_TREES_FROM_POLYGON_ID      = 1056404
SITG_TREES_FROM_LINE_ID         = 1056405

SITG_EMPRISE_GEO_ID             = 1056428


SITG_SEPARATOR_01       = 1034154     
SITG_SEPARATOR_02       = 1034155
SITG_SEPARATOR_03       = 1034156
SITG_SEPARATOR_04       = 1056361

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

SITG_IMPORT_ARBRE_SHAPE_PT_NOM = 2201
SITG_IMPORT_ARBRE_SHAPE_PT_HLP = 2202

SITG_IMPORT_ARBRE_SHAPE_LINE_NOM = 2203
SITG_IMPORT_ARBRE_SHAPE_LINE_HLP = 2204

SITG_IMPORT_ARBRE_SHAPE_POLY_NOM = 2205
SITG_IMPORT_ARBRE_SHAPE_POLY_HLP = 2206

SITG_IMPORT_BATI_SWISSTOPO_NOM = 2301
SITG_IMPORT_BATI_SWISSTOPO_HLP = 2302

SITG_TREES_FROM_POLYGON_NOM      = 2401
SITG_TREES_FROM_POLYGON_HLP      = 2402

SITG_TREES_FROM_LINE_NOM         = 2405
SITG_TREES_FROM_LINE_HLP         = 2406

SITG_EMPRISE_GEO_NOM             =2410
SITG_EMPRISE_GEO_HLP             =2411

SITG_POINTS_ON_SURFACE_NOM       =1903
SITG_POINTS_ON_SURFACE_HLP       =1904




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

class ImportSwissBuildings3Dshape(c4d.plugins.CommandData):
    def Execute(self, doc) :
        import_SwissBuildings3D.main()
        return True

class ImportArbresSSIG(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        importArbresSSIG.main(fn_arbres)
        return True

class ImportArbresShapePoint(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        importArbresShapePoint.main(fn_arbres = fn_arbres)
        return True

class ImportArbresShapeLine(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        importArbresShapeLine.main(fn_arbres_srce = fn_arbres)
        return True

class ImportArbresShapePoly(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        importArbresShapePoly.main(fn_arbres_srce = fn_arbres)
        return True

class TreesFromPolygons(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        treesFromPolygons.main(fn_arbres_srce = fn_arbres)
        return True

class TreesFromLines(c4d.plugins.CommandData):
    def Execute(self, doc) :
        fn_arbres = os.path.join(os.path.dirname(__file__),NAME_FILE_ARBRES_IGN)
        treesFromLines.main(fn_arbres_srce = fn_arbres)
        return True

class GroupeSurTerrain(c4d.plugins.CommandData):
    def Execute(self, doc) :
        groupeTerrain.main()
        return True

class PointsOnSurface(c4d.plugins.CommandData):
    def Execute(self, doc) :
        pointsOnSurface.main()
        return True

class GeorefObj(c4d.plugins.CommandData):
    def Execute(self, doc) :
        georefObjet.main()
        return True

class empriseGeographique(c4d.plugins.CommandData):
    dialog = None
    def Execute(self, doc) :
        if self.dialog is None:
            self.dialog = empriseGeo.DlgBbox()

            # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=SITG_EMPRISE_GEO_ID, defaultw=250, defaulth=150)

class SITG(c4d.plugins.CommandData) :
    def Execute(self, doc) :
        webbrowser.open('https://www.hesge.ch/hepia/groupe/modelisation-informatique-paysage')
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

    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_MNT_ID, str = "#$06" + txt(SITG_IMPORT_MNT_MNT), info = 0, help = txt(SITG_IMPORT_MNT_HLP), dat = ImportMNT(), icon = icone("asc.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_RASTER_ID, str = "#$07" + txt(SITG_IMPORT_RASTER_NOM), info = 0, help = txt(SITG_IMPORT_RASTER_HLP), dat = ImportRaster(), icon = icone("wld.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_ARBRES_SSIG_ID, str = "#$08" + txt(SITG_IMPORT_ARBRES_SSIG_NOM), info = 0, help = txt(SITG_IMPORT_ARBRES_SSIG_HLP), dat = ImportArbresSSIG(), icon = icone("arbresSSIG.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_3DS_ID, str = "#$09" + txt(SITG_IMPORT_3DS_NOM), info = 0, help = txt(SITG_IMPORT_3DS_HLP), dat = Import3DS(), icon = icone("3ds.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_BATI_SWISSTOPO_ID, str="#$10" + txt(SITG_IMPORT_BATI_SWISSTOPO_NOM), info=0,
                                      help=txt(SITG_IMPORT_BATI_SWISSTOPO_HLP), dat=ImportSwissBuildings3Dshape(), icon=icone("shp.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_SHAPE_ID, str = "#$11" + txt(SITG_IMPORT_SHAPE_NOM), info = 0, help = txt(SITG_IMPORT_SHAPE_HLP), dat = ImportShape(), icon = icone("shp.tif"))


    c4d.plugins.RegisterCommandPlugin(id=SITG_SEPARATOR_02, str = "#$15--", info = 0, help = "", dat = SITG(), icon = None)

    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_ARBRE_SHAPE_PT_ID, str = "#$16" + txt(SITG_IMPORT_ARBRE_SHAPE_PT_NOM), info = 0, help = txt(SITG_IMPORT_ARBRE_SHAPE_PT_HLP), dat = ImportArbresShapePoint(), icon = icone("arbresSSIG.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_ARBRE_SHAPE_LINE_ID, str = "#$17" + txt(SITG_IMPORT_ARBRE_SHAPE_LINE_NOM), info = 0, help = txt(SITG_IMPORT_ARBRE_SHAPE_LINE_HLP), dat = ImportArbresShapeLine(), icon = icone("arbresSSIG.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_ARBRE_SHAPE_POLY_ID, str = "#$18" + txt(SITG_IMPORT_ARBRE_SHAPE_POLY_NOM), info = 0, help = txt(SITG_IMPORT_ARBRE_SHAPE_POLY_HLP), dat = ImportArbresShapePoly(), icon = icone("arbresSSIG.tif"))

    c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_SHAPE_BATI_DALE_ID, str = "#$19" + txt(SITG_IMPORT_SHAPE_BATI_NOM), info = 0, help = txt(SITG_IMPORT_SHAPE_BATI_HLP), dat = ImportShapeBatiDALE(), icon = icone("shp.tif"))
    #c4d.plugins.RegisterCommandPlugin(id=SITG_IMPORT_SHAPE_BATI_DALE2_ID, str = "#$18" + txt(SITG_IMPORT_SHAPE_BATI2_NOM), info = 0, help = txt(SITG_IMPORT_SHAPE_BATI2_HLP), dat = ImportShapeBatiDALE2(), icon = icone("shp.tif"))

    c4d.plugins.RegisterCommandPlugin(id=SITG_SEPARATOR_03, str = "#$50--", info = 0, help = "", dat = SITG(), icon = None)

    c4d.plugins.RegisterCommandPlugin(id=SITG_TREES_FROM_POLYGON_ID, str = "#$51"+ txt(SITG_TREES_FROM_POLYGON_NOM), info = 0, help = txt(SITG_TREES_FROM_POLYGON_HLP), dat = TreesFromPolygons(), icon = icone("grpeTerrain.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_TREES_FROM_LINE_ID, str = "#$52"+ txt(SITG_TREES_FROM_LINE_NOM), info = 0, help = txt(SITG_TREES_FROM_LINE_HLP), dat = TreesFromLines(), icon = icone("grpeTerrain.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_GROUPE_SUR_TERRAIN_ID, str = "#$53"+ txt(SITG_GRPE_SUR_TERRAIN_NOM), info = 0, help = txt(SITG_GRPE_SUR_TERRAIN_HLP), dat = GroupeSurTerrain(), icon = icone("grpeTerrain.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_POINTS_ON_SURFACE_ID, str = "#$54"+ txt(SITG_POINTS_ON_SURFACE_NOM), info = 0, help = txt(SITG_POINTS_ON_SURFACE_HLP), dat = PointsOnSurface(), icon = icone("grpeTerrain.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_GEOREFERENCER_UN_OBJET_ID, str = "#$55"+ txt(SITG_GEOREF_OBJ_NOM), info = 0, help = txt(SITG_GEOREF_OBJ_HLP), dat = GeorefObj(), icon = icone("georef.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_ACTIVETEXTURE_ID, str = "#$56" + txt(SITG_ACTIVETEXTURE_NOM), info = 0, help = txt(SITG_ACTIVETEXTURE_HLP), dat = ActiveTexture(), icon = icone("activeTex2.png"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_EMPRISE_GEO_ID, str="#$57" + txt(SITG_EMPRISE_GEO_NOM), info=0, help=txt(SITG_EMPRISE_GEO_HLP), dat=empriseGeographique(), icon=icone("georef.tif"))

    c4d.plugins.RegisterCommandPlugin(id=SITG_SEPARATOR_04, str = "#$60--", info = 0, help = "", dat = SITG(), icon = None)

    c4d.plugins.RegisterCommandPlugin(id=SITG_EXTRACTEUR_WEB_ID, str = "#$61"+ txt(SITG_EXTRACTEUR_WEB_NOM), info = 0, help = txt(SITG_EXTRACTEUR_WEB_HLP), dat = ExtracteurWeb(), icon = icone("http.tif"))
    c4d.plugins.RegisterCommandPlugin(id=SITG_MODULE_ID, str = "#$62v{0} du {1} - http://mip.hesge.ch".format(__version__, __date__), info = 0, help = "http://mip.hesge.ch", dat = SITG(), icon = icone("mip.tif"))