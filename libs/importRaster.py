# -*- coding: utf-8 -*-
import math
import os
import shutil

from libs.od_c4d_utils import undo_group

import c4d

CONTAINER_ORIGIN = 1026473
GEOTAG = 1026472


def read_matrix(path):
    with open(path, encoding="utf-8-sig") as stream:
        lines = stream.read().strip().splitlines()
    if len(lines) != 6:
        raise ValueError(f"{path} doit contenir six lignes (A, D, B, E, C, F).")
    values = []
    for i, line in enumerate(lines, 1):
        try:
            value = float(line.strip())
            if not math.isfinite(value):
                raise ValueError
        except ValueError:
            raise ValueError(f"{path}, ligne {i} : nombre invalide ({line}).")
        values.append(value)
    return values


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".tif", ".tiff", ".png", ".gif", ".bmp",
                    ".psd", ".psb", ".jp2", ".j2k", ".webp", ".tga", ".exr", ".hdr")


def world_suffixes(ext):
    return (ext[:2] + ext[-1:] + "w", ext + "w", ".wld")


def find_world_file(image):
    base, ext = os.path.splitext(os.path.basename(image).lower())
    directory = os.path.dirname(image)
    names = {name.lower(): name for name in sorted(os.listdir(directory))}
    for suffix in world_suffixes(ext):
        name = names.get(base + suffix)
        if name and os.path.isfile(os.path.join(directory, name)):
            return os.path.join(directory, name)
    raise ValueError(f"Aucun fichier de calage trouvé pour {image}.")


def image_for_world_file(path):
    directory = os.path.dirname(path)
    stem, suffix = os.path.splitext(os.path.basename(path).casefold())
    matches = []
    for name in sorted(os.listdir(directory)):
        base, ext = os.path.splitext(name.casefold())
        if base == stem and ext in IMAGE_EXTENSIONS and suffix in world_suffixes(ext):
            candidate = os.path.join(directory, name)
            if os.path.isfile(candidate):
                matches.append(candidate)
    if len(matches) == 1:
        return matches[0]
    reason = "Plusieurs images correspondent" if matches else "Aucune image correspondante"
    return c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, def_path=directory,
                                  title=f"{reason} : choisissez l’image pour {os.path.basename(path)}")


class Raster:
    def __init__(self, image, world_file):
        a, d, b, e, x, z = read_matrix(world_file)
        self.det = a * e - b * d
        if not math.isfinite(self.det) or not self.det:
            raise ValueError(f"{world_file} : la matrice ne peut pas être inversée.")
        bitmap = c4d.bitmaps.BaseBitmap()
        result, _ = bitmap.InitWith(image)
        self.width, self.height = bitmap.GetSize()
        if result != c4d.IMAGERESULT_OK or min(self.width, self.height) <= 0:
            raise ValueError(f"Image illisible : {image} (code Cinema 4D {result}).")
        self.column = c4d.Vector(a, 0, d)
        self.row = c4d.Vector(b, 0, e)
        # C et F désignent le centre du pixel supérieur gauche.
        self.centre = (c4d.Vector(x, 0, z) + self.column * ((self.width - 1) / 2)
                       + self.row * ((self.height - 1) / 2))

    def plane(self, origin):
        half_x = self.column * (self.width / 2)
        half_y = self.row * (self.height / 2)
        obj = c4d.PolygonObject(4, 1)
        obj.SetAllPoints([-half_x - half_y, half_x - half_y,
                          half_x + half_y, -half_x + half_y])
        indices = (0, 1, 2, 3) if self.det < 0 else (0, 3, 2, 1)
        obj.SetPolygon(0, c4d.CPolygon(*indices))
        obj.SetAbsPos(self.centre - origin)
        obj.Message(c4d.MSG_UPDATE)
        return obj

    def uv(self, delta):
        u = (self.row.z * delta.x - self.row.x * delta.z) / self.det
        v = (self.column.x * delta.z - self.column.z * delta.x) / self.det
        return c4d.Vector(0.5 + u / self.width, 0.5 + v / self.height, 0)

    def mapping(self, obj, origin, texture):
        matrix = obj.GetMg()
        matrix.off += origin - self.centre
        if obj.CheckType(c4d.Opolygon):
            count = obj.GetPolygonCount()
            if not count:
                raise ValueError("L’objet sélectionné ne contient aucun polygone.")
            coords = [self.uv(matrix * p) for p in obj.GetAllPoints()]
            uvw = c4d.UVWTag(count)
            for i, poly in enumerate(obj.GetAllPolygons()):
                uvw.SetSlow(i, coords[poly.a], coords[poly.b], coords[poly.c], coords[poly.d])
            texture[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW
            return uvw

        # La projection planaire native ne conserve que des axes orthogonaux.
        # Les gradients locaux incluent la transformation globale de l'objet.
        axes = (matrix.v1, matrix.v2, matrix.v3)
        samples = [self.uv(axis) - c4d.Vector(0.5, 0.5, 0) for axis in axes]
        gu = c4d.Vector(*(s.x for s in samples))
        gv = c4d.Vector(*(-s.y for s in samples))
        if not gu.GetLength() or not gv.GetLength() or abs(gu.GetNormalized().Dot(gv.GetNormalized())) > 1e-7:
            raise ValueError("Pour ce calage, rendez l’objet sélectionné polygonal ou désélectionnez-le pour créer un plan.")
        u = gu / (2 * gu.Dot(gu))
        v = gv / (2 * gv.Dot(gv))
        centre = self.uv(matrix.off)
        offset = u * (1 - 2 * centre.x) + v * (2 * centre.y - 1)
        texture[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_FLAT
        texture.SetMl(c4d.Matrix(offset, u, v, u.Cross(v).GetNormalized()))
        return None


def texture_reference(image, directory, alert):
    candidates = [os.path.basename(image)]
    if directory:
        try:
            relative = os.path.relpath(image, os.path.join(directory, "tex"))
        except ValueError:  # Volumes différents sous Windows.
            relative = os.pardir
        if relative.split(os.sep)[0] != os.pardir:
            candidates.extend((relative, os.path.join("tex", relative)))
    for name in candidates:
        resolved = c4d.GenerateTexturePath(directory, name, "")
        if resolved and os.path.isfile(resolved) and os.path.samefile(image, resolved):
            return name, None

    if directory:
        if c4d.gui.QuestionDialog(
            f"Copier « {os.path.basename(image)} » dans le dossier tex du projet "
            "pour utiliser un chemin relatif ?\n\nNon : conserver le chemin absolu de l’image."
        ):
            return copy_texture(image, os.path.join(directory, "tex"))
    elif alert:
        c4d.gui.MessageDialog("Document non enregistré : la texture utilisera le chemin absolu de l’image.")
    return image, None


def copy_texture(image, directory):
    os.makedirs(directory, exist_ok=True)
    name, ext = os.path.splitext(os.path.basename(image))
    index = 0
    while True:
        filename = (name if not index else f"{name}_{index}") + ext
        path = os.path.join(directory, filename)
        try:
            target = open(path, "xb")
        except FileExistsError:
            if os.path.samefile(image, path):
                return filename, None
            index += 1
            continue
        try:
            with target, open(image, "rb") as source:
                shutil.copyfileobj(source, target)
        except Exception:
            os.remove(path)
            raise
        return filename, path


def import_raster(doc, image, world_file, alert):
    if not os.path.isfile(image):
        raise ValueError(f"Image introuvable : {image}")
    raster = Raster(image, world_file or find_world_file(image))
    origin = doc[CONTAINER_ORIGIN]
    new_origin = origin is None
    if new_origin:
        origin = raster.centre
    obj = doc.GetActiveObject()
    if obj is not None and not c4d.gui.QuestionDialog(
        f"Appliquer le raster « {os.path.basename(image)} » à l’objet sélectionné « {obj.GetName()} » ?"
        "\n\nOui : appliquer la texture à cet objet.\nNon : créer un nouveau plan géoréférencé."
    ):
        obj = None
    new_plane = obj is None
    if new_plane:
        obj = raster.plane(origin)
        obj.SetName(os.path.basename(image))
        display = c4d.BaseTag(c4d.Tdisplay)
        display[c4d.DISPLAYTAG_AFFECT_DISPLAYMODE] = True
        display[c4d.DISPLAYTAG_SDISPLAYMODE] = 7
        obj.InsertTag(display)

    mat = c4d.BaseMaterial(c4d.Mmaterial)
    shader = c4d.BaseList2D(c4d.Xbitmap)
    mat.InsertShader(shader)
    mat[c4d.MATERIAL_COLOR_SHADER] = shader
    mat[c4d.MATERIAL_PREVIEWSIZE] = 12
    mat.SetName(os.path.splitext(os.path.basename(image))[0])
    texture = c4d.TextureTag()
    texture[c4d.TEXTURETAG_MATERIAL] = mat
    texture[c4d.TEXTURETAG_TILE] = False
    texture[CONTAINER_ORIGIN] = raster.centre
    uvw = raster.mapping(obj, origin, texture)
    geo = None
    if not obj.GetTag(GEOTAG):
        geo = c4d.BaseTag(GEOTAG)
        geo[CONTAINER_ORIGIN] = origin + obj.GetMg().off

    units = doc[c4d.DOCUMENT_DOCUNIT]
    change_units = units.GetUnitScale() != (1, c4d.DOCUMENT_UNIT_M)
    if change_units and not c4d.gui.QuestionDialog("Passer l’unité du document à 1 mètre pour importer le raster ?"):
        return False
    filename, copied = texture_reference(image, doc.GetDocumentPath(), alert)

    inserted = []
    old_scale = units.GetUnitScale()
    try:
        shader[c4d.BITMAPSHADER_FILENAME] = filename
        mat.Message(c4d.MSG_UPDATE)
        mat.Update(True, True)
        with undo_group(doc):
            try:
                if change_units:
                    units.SetUnitScale(1, c4d.DOCUMENT_UNIT_M)
                    doc[c4d.DOCUMENT_DOCUNIT] = units
                if new_origin:
                    doc[CONTAINER_ORIGIN] = origin
                doc.InsertMaterial(mat)
                inserted.append(mat)
                if new_plane:
                    doc.InsertObject(obj)
                    inserted.append(obj)
                # Le tag UVW immédiatement à droite du matériau lui est associé.
                for tag in (geo, texture, uvw):
                    if tag is not None:
                        tags = obj.GetTags()
                        obj.InsertTag(tag, tags[-1] if tags else None)
                        if not new_plane:
                            inserted.append(tag)
                for node in inserted:
                    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, node)
            except Exception:
                for node in reversed(inserted):
                    node.Remove()
                if new_origin:
                    doc.GetDataInstance().RemoveData(CONTAINER_ORIGIN)
                if change_units:
                    units.SetUnitScale(*old_scale)
                    doc[c4d.DOCUMENT_DOCUNIT] = units
                raise

    except Exception:
        if copied:
            os.remove(copied)
        raise
    c4d.EventAdd()
    return True


def main(fn=None, fn_calage=None, alerte=True):
    if not fn:
        fn = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_ANYTHING,
                                    title="Sélectionnez l’image ou son fichier de calage")
    if not fn:
        return False
    try:
        image = os.path.abspath(fn)
        suffix = os.path.splitext(image)[1].casefold()
        if not fn_calage and any(suffix in world_suffixes(ext) for ext in IMAGE_EXTENSIONS):
            fn_calage = image
            image = image_for_world_file(fn_calage)
            if not image:
                return False
        return import_raster(c4d.documents.GetActiveDocument(), image, fn_calage, alerte)
    except (ValueError, OSError, RuntimeError, MemoryError, TypeError, AttributeError) as error:
        c4d.gui.MessageDialog(f"Impossible d’importer {os.path.basename(fn)}.\n{error}")
        return False


if __name__ == "__main__":
    main()
