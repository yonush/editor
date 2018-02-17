#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Beremiz.
# See COPYING file for copyrights details.

from __future__ import absolute_import
from plcopen.XSLTModelQuery import XSLTModelQuery

def class_extraction(value):
    class_type = {
        "configuration": ITEM_CONFIGURATION,
        "resource": ITEM_RESOURCE,
        "action": ITEM_ACTION,
        "transition": ITEM_TRANSITION,
        "program": ITEM_PROGRAM}.get(value)
    if class_type is not None:
        return class_type

    pou_type = POU_TYPES.get(value)
    if pou_type is not None:
        return pou_type

    var_type = VAR_CLASS_INFOS.get(value)
    if var_type is not None:
        return var_type[1]

    return None


class _VariablesTreeItemInfos(object):
    __slots__ = ["name", "var_class", "type", "edit", "debug", "variables"]

    def __init__(self, *args):
        for attr, value in zip(self.__slots__, args):
            setattr(self, attr, value if value is not None else "")

    def copy(self):
        return _VariablesTreeItemInfos(*[getattr(self, attr) for attr in self.__slots__])


class VariablesTreeInfosFactory(object):

    def __init__(self):
        self.Root = None

    def GetRoot(self):
        return self.Root

    def SetRoot(self, context, *args):
        self.Root = _VariablesTreeItemInfos(
            *([''] + _translate_args(
                [class_extraction, _StringValue] + [_BoolValue] * 2,
                args) + [[]]))

    def AddVariable(self, context, *args):
        if self.Root is not None:
            self.Root.variables.append(_VariablesTreeItemInfos(
                *(_translate_args(
                    [_StringValue, class_extraction, _StringValue] +
                    [_BoolValue] * 2, args) + [[]])))



class POUVariablesCollector(XSLTModelQuery):
    """ object for collecting instances path list"""
    def __init__(self, controller):
        XSLTModelQuery.__init__(self,
                                controller,
                                "pou_variables.xslt",
                                [(name, lambda *x : getattr(self.factory, name)(*x)) 
                                    for name in ["SetRoot", "AddVariable"]])

    def Collect(self, root, debug):
        self.factory = VariablesTreeInfosFactory()
        self._process_xslt(root, debug)
        res = self.factory.GetRoot()
        self.factory = None
        return res
