# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from persistent.mapping import PersistentMapping

from plone.keyring.interfaces import IKeyManager
from plone.keyring.keyring import Keyring

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

class SilvaKeyring(Keyring, SimpleItem):
    pass

class SilvaKeyManager(Folder):

    implements(IKeyManager)

    meta_type = 'Silva Key Manager'

    def __init__(self):
        Folder.__init__(self)
        self._setObject("system", SilvaKeyring())
        self["system"].rotate()


    def _newContainerData(self):
        return PersistentMapping()


    def clear(self, ring="system"):
        if ring is None:
            for ring in self.values():
                ring.clear()
        else:
            self[ring].clear()


    def rotate(self, ring="system"):
        if ring is None:
            for ring in self.values():
                ring.rotate()
        else:
            self[ring].rotate()


    def secret(self, ring="system"):
        return self[ring].current
