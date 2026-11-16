# -*- coding: utf-8 -*-

# Modifié le 27 octobre 2017:
#  gestion des fichiers à 7 lignes d'entête avec dx et dy au lieu de cellsize'
# Modifié le 27 mars 2024:
#  gestion des valeurs d'altitude négatives -> 0

import os.path
from itertools import chain
from math import isfinite

import c4d
from libs.od_c4d_utils import undo_group

CONTAINER_ORIGIN = 1026473


def insert_geotag(obj, origine):
    geotag = c4d.BaseTag(1026472)
    geotag[CONTAINER_ORIGIN] = origine
    obj.InsertTag(geotag)


def polygonise(obj, nb_rows, nb_cols):
    for row in range(nb_rows - 1):
        for col in range(nb_cols - 1):
            i = row * nb_cols + col
            obj.SetPolygon(row * (nb_cols - 1) + col,
                           c4d.CPolygon(i, i + 1, i + 1 + nb_cols, i + nb_cols))


def terrainFromASC(fn):
    """Construit le terrain hors scène et vérifie chaque rangée avant insertion."""
    header = {}
    with open(fn, encoding="utf-8-sig") as stream:
        lines = (line.split() for line in stream if line.strip())
        for first_row in lines:
            if not first_row[0][0].isalpha():
                break
            if len(first_row) != 2:
                raise ValueError(f"En-tête ASC invalide : {' '.join(first_row)}")
            key, value = first_row
            header[key.lower()] = value.replace(",", ".")
        else:
            raise ValueError("Le fichier ASC ne contient aucune altitude.")

        try:
            ncols, nrows = int(header["ncols"]), int(header["nrows"])
            dx, dy = ((float(header["cellsize"]),) * 2 if "cellsize" in header
                      else (float(header["dx"]), float(header["dy"])))
            xcorner, ycorner = float(header["xllcorner"]), float(header["yllcorner"])
            nodata = float(header.get("nodata_value", 0))
        except (KeyError, ValueError) as error:
            raise ValueError(f"En-tête ASC incomplet ou invalide : {error}") from error
        if min(ncols, nrows, dx, dy) <= 0 or not all(map(isfinite, (dx, dy, xcorner, ycorner))):
            raise ValueError("Dimensions ou coordonnées ASC invalides.")

        poly = c4d.PolygonObject(ncols * nrows, (ncols - 1) * (nrows - 1))
        poly.SetName(os.path.splitext(os.path.basename(fn))[0])
        # L’origine du maillage est le centre de la cellule nord-ouest.
        origine = c4d.Vector(xcorner + dx / 2, 0, ycorner + (nrows - 0.5) * dy)
        rows = chain([first_row], lines)
        for row in range(nrows):
            values = next(rows, ())
            if len(values) != ncols:
                raise ValueError(f"Ligne ASC {row + 1} : {len(values)} altitudes pour {ncols} attendues.")
            for col, value in enumerate(values):
                try:
                    height = float(value.replace(",", "."))
                    if not isfinite(height):
                        raise ValueError
                except ValueError as error:
                    raise ValueError(f"Altitude invalide à la ligne {row + 1}, colonne {col + 1}.") from error
                # Convention du plugin : les altitudes négatives et NoData sont ramenées à zéro.
                height = 0 if height == nodata else max(0, height)
                poly.SetPoint(row * ncols + col, c4d.Vector(col * dx, height, -row * dy))
        if next(rows, None) is not None:
            raise ValueError("Le fichier ASC contient plus de lignes que prévu.")

    polygonise(poly, nrows, ncols)
    insert_geotag(poly, origine)
    tag = c4d.BaseTag(c4d.Tphong)
    tag[c4d.PHONGTAG_PHONG_ANGLELIMIT] = True
    poly.InsertTag(tag)

    poly.Message(c4d.MSG_UPDATE)
    return poly


def main(fn=None):
    doc = c4d.documents.GetActiveDocument()
    if not fn:
        fn = c4d.storage.LoadDialog()
    if not fn:
        return
    if os.path.splitext(fn)[1].lower() not in (".txt", ".asc"):
        raise ValueError("Sélectionnez un fichier de terrain .txt ou .asc.")

    terrain = terrainFromASC(fn)
    with undo_group(doc):
        data = doc[c4d.DOCUMENT_DOCUNIT]
        data.SetUnitScale(1, c4d.DOCUMENT_UNIT_M)
        doc[c4d.DOCUMENT_DOCUNIT] = data
        doc.InsertObject(terrain)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, terrain)
        doc.SetActiveObject(terrain)
    c4d.CallCommand(12151) # Zoom sur l'objet actif
    c4d.EventAdd()
    return


if __name__ == '__main__':
    main()
