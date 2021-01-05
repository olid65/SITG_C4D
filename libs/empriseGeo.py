# -*- coding: utf-8 -*-

import c4d
import shapefile
import os

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
# def state():
#    return True

CONTAINER_ORIGIN = 1026473


def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi, largeur, hauteur


def empriseObject(obj, origine):
    mg = obj.GetMg()

    rad = obj.GetRad()
    centre = obj.GetMp()

    # 4 points de la bbox selon orientation de l'objet
    pts = [c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z + rad.z) * mg]

    mini = c4d.Vector(min([p.x for p in pts]), min([p.y for p in pts]), min([p.z for p in pts])) + origine
    maxi = c4d.Vector(max([p.x for p in pts]), max([p.y for p in pts]), max([p.z for p in pts])) + origine

    return mini, maxi


def fichierPRJ(fn):
    fn = os.path.splitext(fn)[0] + '.prj'
    f = open(fn, 'w')
    f.write(
        """PROJCS["CH1903+_LV95",GEOGCS["GCS_CH1903+",DATUM["D_CH1903+",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",46.95240555555556],PARAMETER["longitude_of_center",7.439583333333333],PARAMETER["azimuth",90],PARAMETER["scale_factor",1],PARAMETER["false_easting",2600000],PARAMETER["false_northing",1200000],UNIT["Meter",1]]""")
    f.close()


def bbox2shapefile(mini, maxi):
    poly = [[[mini.x, mini.z], [mini.x, maxi.z], [maxi.x, maxi.z], [maxi.x, mini.z]]]

    fn = c4d.storage.LoadDialog(flags=c4d.FILESELECT_SAVE)

    if not fn: return
    with shapefile.Writer(fn, shapefile.POLYGON) as w:
        w.field('id', 'I')
        w.record(1)
        w.poly(poly)

        fichierPRJ(fn)


class DlgBbox(c4d.gui.GeDialog):
    N_MIN = 1015
    N_MAX = 1016
    E_MIN = 1017
    E_MAX = 1018

    BTON_FROM_OBJECT = 1050
    BTON_FROM_VIEW = 1051
    BTON_COPY_ALL = 1052
    BTON_PLANE = 1053
    BTON_EXPORT_SHP = 1054

    BTON_N_MIN = 1055
    BTON_N_MAX = 1056
    BTON_E_MIN = 1057
    BTON_E_MAX = 1058

    TXT_NO_ORIGIN = "Le document n'est pas géoréférencé !"
    TXT_NOT_VIEW_TOP = "Vous devez activer une vue de haut !"
    TXT_NO_SELECTION = "Vous devez sélectionner un objet !"
    TXT_MULTI_SELECTION = "Vous devez sélectionner un seul objet !"

    MARGIN = 5
    LARG_COORD = 130

    def CreateLayout(self):

        self.SetTitle("Emprise géographique")
        # CADRAGE
        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.AddStaticText(1001, name="N max :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.N_MAX, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_N_MAX, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=7, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.AddStaticText(1003, name="E min :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.E_MIN, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_E_MIN, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.AddStaticText(1005, name="", flags=c4d.BFH_MASK, initw=200)
        self.AddStaticText(1004, name="E max :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.E_MAX, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_E_MAX, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.AddStaticText(1002, name="N min :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.N_MIN, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_N_MIN, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=2, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, 0)

        self.AddButton(self.BTON_FROM_OBJECT, flags=c4d.BFH_MASK, initw=150, inith=20, name="depuis la sélection")
        self.AddButton(self.BTON_FROM_VIEW, flags=c4d.BFH_MASK, initw=150, inith=20, name="depuis la vue")

        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, 0, self.MARGIN, self.MARGIN)

        self.AddButton(self.BTON_COPY_ALL, flags=c4d.BFH_MASK, initw=150, inith=20, name="copier toutes les valeurs")
        self.AddButton(self.BTON_PLANE, flags=c4d.BFH_MASK, initw=150, inith=20, name="créer un plan")
        self.AddButton(self.BTON_EXPORT_SHP, flags=c4d.BFH_MASK, initw=150, inith=20, name="créer un shapefile")

        self.GroupEnd()

        return True

    def InitValues(self):
        self.SetMeter(self.N_MAX, 0.0)
        self.SetMeter(self.N_MIN, 0.0)
        self.SetMeter(self.E_MIN, 0.0)
        self.SetMeter(self.E_MAX, 0.0)
        return True

    def getBbox(self):
        mini = c4d.Vector()
        maxi = c4d.Vector()
        maxi.z = self.GetFloat(self.N_MAX)
        mini.z = self.GetFloat(self.N_MIN)
        maxi.x = self.GetFloat(self.E_MAX)
        mini.x = self.GetFloat(self.E_MIN)
        return mini, maxi

    def planeFromBbox(self, mini, maxi, origine):
        plane = c4d.BaseObject(c4d.Oplane)
        plane[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_YP
        plane[c4d.PRIM_PLANE_SUBW] = 1
        plane[c4d.PRIM_PLANE_SUBH] = 1

        plane[c4d.PRIM_PLANE_WIDTH] = maxi.x - mini.x
        plane[c4d.PRIM_PLANE_HEIGHT] = maxi.z - mini.z

        pos = (mini + maxi) / 2 - origine

        plane.SetAbsPos(pos)
        return plane

    def Command(self, id, msg):
        # DEPUIS L'OBJET ACTIF
        # TODO : sélection multiple
        if id == self.BTON_FROM_OBJECT:
            doc = c4d.documents.GetActiveDocument()
            origine = doc[CONTAINER_ORIGIN]
            if not origine:
                c4d.gui.MessageDialog(self.TXT_NO_ORIGIN)
                return True
            op = doc.GetActiveObjects(0)
            if not op:
                c4d.gui.MessageDialog(self.TXT_NO_SELECTION)
                return True
            if len(op) > 1:
                c4d.gui.MessageDialog(self.TXT_MULTI_SELECTION)
                return True
            obj = op[0]

            mini, maxi = empriseObject(obj, origine)
            self.SetMeter(self.N_MAX, maxi.z)
            self.SetMeter(self.N_MIN, mini.z)
            self.SetMeter(self.E_MIN, mini.x)
            self.SetMeter(self.E_MAX, maxi.x)

        # DEPUIS LA VUE DE HAUT
        if id == self.BTON_FROM_VIEW:
            doc = c4d.documents.GetActiveDocument()
            origine = doc[CONTAINER_ORIGIN]
            if not origine:
                c4d.gui.MessageDialog(self.TXT_NO_ORIGIN)
                return True

            bd = doc.GetActiveBaseDraw()
            camera = bd.GetSceneCamera(doc)
            if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
                c4d.gui.MessageDialog(self.TXT_NOT_VIEW_TOP)
                return True

            mini, maxi, larg, haut = empriseVueHaut(bd, origine)
            self.SetMeter(self.N_MAX, maxi.z)
            self.SetMeter(self.N_MIN, mini.z)
            self.SetMeter(self.E_MIN, mini.x)
            self.SetMeter(self.E_MAX, maxi.x)

        # COPIER LES VALEURS (et print)
        if id == self.BTON_COPY_ALL:
            n_max = self.GetFloat(self.N_MAX)
            n_min = self.GetFloat(self.N_MIN)
            e_max = self.GetFloat(self.E_MAX)
            e_min = self.GetFloat(self.E_MIN)
            txt = "{0},{1},{2},{3}".format(e_min,n_min,e_max,n_max)
            print(txt)
            c4d.CopyStringToClipboard(txt)

        # CREER UN PLAN
        if id == self.BTON_PLANE:

            mini, maxi = self.getBbox()

            if mini == c4d.Vector(0) or maxi == c4d.Vector(0):
                return True
            doc = c4d.documents.GetActiveDocument()
            doc.StartUndo()
            origine = doc[CONTAINER_ORIGIN]
            if not origine:
                origine = (mini + maxi) / 2
                # pas réussi à faire un undo pour le doc !
                doc[CONTAINER_ORIGIN] = origine

            plane = self.planeFromBbox(mini, maxi, origine)
            doc.AddUndo(c4d.UNDOTYPE_NEW, plane)
            doc.InsertObject(plane)
            doc.EndUndo()
            c4d.EventAdd()

        # EXPORT SHAPEFILE
        if id == self.BTON_EXPORT_SHP:
            mini, maxi = self.getBbox()
            if mini == c4d.Vector(0) or maxi == c4d.Vector(0):
                return True

            bbox2shapefile(mini, maxi)

        # BOUTONS COPIE COORDONNöE
        if id == self.BTON_N_MIN:
            c4d.CopyStringToClipboard(str(self.GetFloat(self.N_MIN)))

        if id == self.BTON_N_MAX:
            c4d.CopyStringToClipboard(self.GetFloat(self.N_MAX))

        if id == self.BTON_E_MIN:
            c4d.CopyStringToClipboard(str(self.GetFloat(self.E_MIN)))

        if id == self.BTON_E_MAX:
            c4d.CopyStringToClipboard(str(self.GetFloat(self.E_MAX)))

        return True

def main():
    dlg = DlgBbox()
    dlg.Open(c4d.DLG_TYPE_ASYNC)


# Execute main()
if __name__ == '__main__':
    main()