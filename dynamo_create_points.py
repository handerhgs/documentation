# -*- coding: utf-8 -*-
"""Dynamo script to create location points in Revit.

This script is intended to run inside a Dynamo Python node. It receives a
list of dictionaries describing points, creates a family instance for each
point and fills identification parameters so that the instances can be
scheduled in Revit.

Inputs
------
point_data : list[dict]
    Each dict must contain the keys 'num', 'desc', 'x', 'y' and 'z'.
family_name : str
    Name of the Revit family used for the location point. The family must be
    loaded in the current project and contain parameters documented in the
    accompanying instructions.

Output
------
list[Element]
    The created Revit family instances.
"""

import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
import Autodesk.Revit.DB as DB
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

DOC = DocumentManager.Instance.CurrentDBDocument

point_data = IN[0]
family_name = IN[1]

def get_symbol(doc, fam_name):
    """Return the first family symbol matching ``fam_name``."""
    collector = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol)
    for symbol in collector:
        if symbol.Family.Name == fam_name:
            return symbol
    return None

symbol = get_symbol(DOC, family_name)
if symbol is None:
    raise ValueError('Family "{}" not found.'.format(family_name))

TransactionManager.Instance.EnsureInTransaction(DOC)
if not symbol.IsActive:
    symbol.Activate()
    DOC.Regenerate()
TransactionManager.Instance.TransactionTaskDone()

created = []
TransactionManager.Instance.EnsureInTransaction(DOC)
for data in point_data:
    loc = DB.XYZ(float(data['x']), float(data['y']), float(data['z']))
    inst = DOC.Create.NewFamilyInstance(
        loc, symbol, DB.Structure.StructuralType.NonStructural)
    inst.LookupParameter('Ponto_Numero').Set(str(data['num']))
    inst.LookupParameter('Ponto_Descricao').Set(str(data['desc']))
    inst.LookupParameter('Ponto_Coordenada_Leste (X)').Set(str(data['x']))
    inst.LookupParameter('Ponto_Coordenada_Norte (Y)').Set(str(data['y']))
    inst.LookupParameter('Ponto_Coordenada_Elevacao (Z)').Set(str(data['z']))
    created.append(inst)
TransactionManager.Instance.TransactionTaskDone()

OUT = created
