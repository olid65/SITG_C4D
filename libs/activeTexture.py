# -*- coding: utf-8 -*-

import c4d


TERRAIN_NAME = 'TERRAIN'



class MaquetteSITG(object):
    
    def __init__(self,doc):
        self.doc = doc
        self.terrain = self.doc.Search(TERRAIN_NAME)
        #TO BE CONTINUED
    

def getTexTags(op):
    """renvoie tous les Ttexture d'un objet"""
    res = []
    i=0
    tag = op.GetTag(c4d.Ttexture,i)
    while tag:
        i+=1
        res.append(tag)
        tag = op.GetTag(c4d.Ttexture,i)
    return res

def getLastTag(op):
    """renvoie le dernier tag d'un objet"""
    tag = op.GetFirstTag()
    while tag:
        if not tag.GetNext() : break
        tag = tag.GetNext()
    return tag


def activeTag(op,tag,doc):
    """met le tag en dernier"""
    last = getLastTag(op)
    if tag == last : return
    doc.AddUndo(c4d.UNDOTYPE_CHANGE,tag)
    op.InsertTag(tag,pred = last)
    
    
def activeMat(op,mat,doc):
    while op:
        for tag in getTexTags(op):
            if tag[c4d.TEXTURETAG_MATERIAL] == mat:
                activeTag(op,tag,doc)
        activeMat(op.GetDown(),mat,doc)
        op = op.GetNext()


def activeSelectMat(doc):
    doc.StartUndo()
    mat = doc.GetActiveMaterial()
    if not mat : return
    activeMat(doc.GetFirstObject(),doc.GetActiveMaterial(),doc)
    doc.EndUndo()
    
def main():
    activeSelectMat(c4d.documents.GetActiveDocument())
    c4d.EventAdd()