# -*- coding: utf-8 -*-

import c4d
import webbrowser 

"""Script pour ouvrir l'extracteur web du SITG dans le browser par défaut
   
   Si le document actif est géoréférencé : ouvre d'après le centre du document à l'échelle 1:2500
   
   si en plus un objet est sélectionné : 
        si l'objet possède un géométrie : ouvre d'après l'emprise de l'objet
        sinon : ouvre en centrant sur l'objet à l'échelle 1:2500
   
   v1.0 16 novembre 2014
   © Olivier Donzé"""

CONTAINER_ORIGIN =1026473

def main():
    doc = c4d.documents.GetActiveDocument()
    op = doc.GetActiveObject()

    #url de base avec extracteur
    url = 'https://www.etat.ge.ch/geoportail/pro/?method=showextractpanel'
    
    #calcul de l'extension de la carte par rapport à l'objet sélectionné
    origine = doc[CONTAINER_ORIGIN]
    
    if origine:
        #si on a un objet sélectionné
        if op :
            dim = op.GetRad()
            centre = op.GetMp() * op.GetMg() + origine
            #si l'objet sélectionné a une géométrie
            if dim.x>0 and dim.z > 0:            
                xmin = str(round(centre.x - dim.x)).split('.')[0]
                xmax = str(round(centre.x + dim.x)).split('.')[0]
                ymin = str(round(centre.z - dim.z)).split('.')[0]
                ymax = str(round(centre.z + dim.z)).split('.')[0]
    
                url += '&extent='+xmin+','+ymin+','+xmax+','+ymax
                
            #si pas de gémétrie on centre sur l'objet à l'échelle 1:2500
            else :
                centerX = str(round(centre.x)).split('.')[0]
                centerY = str(round(centre.z)).split('.')[0]
                url += '&center='+centerX+','+centerY + '&scale=2500'
                
        
        #si pas d'objet sélectionné on ouvre en centrant sur l'origine
        #au 1:2500
        else:
            centerX = str(round(origine.x)).split('.')[0]
            centerY = str(round(origine.z)).split('.')[0]
            url += '&center='+centerX+','+centerY + '&scale=2500'
  
            
    webbrowser.open(url)