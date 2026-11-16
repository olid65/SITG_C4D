"""Ressources et conventions communes aux commandes SITG."""
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import traceback

import c4d


TREE_LIBRARY = str(Path(__file__).resolve().parent.parent / "__arbres_2018__.c4d")
_undo_documents = []


@contextmanager
def undo_group(doc):
    """Les sous-imports participent au groupe d’annulation de la commande parente."""
    if doc in _undo_documents:
        yield
        return
    if not doc.StartUndo():
        raise RuntimeError("Impossible d’ouvrir le groupe d’annulation.")
    _undo_documents.append(doc)
    try:
        yield
    finally:
        _undo_documents.pop()
        doc.EndUndo()


def report_errors(action):
    """Conserve la trace technique en console et signale l’échec dans Cinema 4D."""
    @wraps(action)
    def run(*args, **kwargs):
        try:
            return action(*args, **kwargs)
        except Exception as error:
            traceback.print_exc()
            c4d.gui.MessageDialog(f"SITG — {error}")
            return False
    return run


def getArbresSourcesFromFile(fn=TREE_LIBRARY):
    """Clone les modèles pour que la scène cible en possède sa propre copie."""
    if not fn or not Path(fn).is_file():
        return None
    library = c4d.documents.LoadDocument(fn, c4d.SCENEFILTER_OBJECTS)
    if library is None:
        raise ValueError(f"Bibliothèque d’arbres illisible : {fn}")
    source = library.SearchObject("sources_vegetation")
    return [child.GetClone() for child in source.GetChildren()] if source else None
