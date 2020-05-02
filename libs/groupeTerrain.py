# -*- coding: utf-8 -*-

import c4d

#Mettre le neutre contenant les objet juste au dessus du terrain dans la hierarchie

def plaquer_sur_poly(groupe,terrain):
    objs = groupe.GetChildren()
    if not objs : return None
	
    if not terrain.GetType()==c4d.Opolygon:
        c4d.gui.MessageDialog('Le terrain doit être un objet polygonal')
        return False        

    rc = c4d.utils.GeRayCollider()
    rc.Init(terrain)
    bbox = terrain.GetRad()
    mg_t = terrain.GetMg()
    inv_m = ~mg_t
    centre = terrain.GetMp()*mg_t

    y_max = centre.y +  bbox.y + 1000
    lg = bbox.y * 2 + 2000
  
    for o in objs :
        mg =o.GetMg()
        i_m= ~mg
        pos = mg.off*inv_m
        pos.y = y_max
		
        if rc.Intersect(pos, c4d.Vector(0,-1,0),lg):
            x= rc.GetNearestIntersection()
            pos.y-=x['distance']
            mg.off = pos*mg_t
            o.SetMg(mg)

    return True

def main():
    doc = c4d.documents.GetActiveDocument()
    obj = doc.GetActiveObject()
    if not obj:
        c4d.gui.MessageDialog("Vous devez séléctionner le groupe d'objets à plaquer")
        return
    terrain = obj.GetNext()
    if not terrain:
        c4d.gui.MessageDialog("Le terrain doit être placé juste après le groupe d'objets dans la hiérarchie")
        return
    plaquer_sur_poly(obj,terrain)

    c4d.EventAdd()


if __name__=='__main__':
    main()