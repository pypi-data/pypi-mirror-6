# -*- coding: utf-8 -*-
'''
keeping.py raet protocol keep classes
'''
# pylint: skip-file
# pylint: disable=W0611

# Import python libs
import os
from collections import deque

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from ioflo.base.odicting import odict
from ioflo.base import aiding

from .. import raeting
from .. import nacling
from .. import keeping

from ioflo.base.consoling import getConsole
console = getConsole()

class RoadKeep(keeping.Keep):
    '''
    RAET protocol estate on road data persistence for a given estate
    road specific data but not key data

    keep/
        stackname/
            local/
                estate.eid.ext
            remote/
                estate.eid.ext
                estate.eid.ext
    '''
    LocalFields = ['eid', 'name', 'main', 'host', 'port', 'sid']
    RemoteFields = ['eid', 'name', 'host', 'port', 'sid', 'rsid']

    def __init__(self, prefix='estate', **kwa):
        '''
        Setup RoadKeep instance
        '''
        super(RoadKeep, self).__init__(prefix=prefix, **kwa)


class SafeKeep(keeping.Keep):
    '''
    RAET protocol estate safe (key) data persistence and status
    '''
    LocalFields = ['eid', 'name', 'sighex', 'prihex']
    RemoteFields = ['eid', 'name', 'acceptance', 'verhex', 'pubhex']
    Auto = False #auto accept

    def __init__(self, prefix='key', auto=None, **kwa):
        '''
        Setup SafeKeep instance

        keep/
            local/
                key.eid.ext
            remote/
                key.eid.ext
                key.eid.ext

                pended/
                    key.eid.ext
                rejected/
                    key.eid.ext
        '''
        super(SafeKeep, self).__init__(prefix=prefix, **kwa)
        self.auto = auto if auto is not None else self.Auto

    def dumpRemote(self, remote):
        '''
        Dump the data from the remote estate
        '''
        data = odict([
                ('eid', remote.eid),
                ('name', remote.name),
                ('acceptance', remote.acceptance),
                ('verhex', remote.verfer.keyhex),
                ('pubhex', remote.pubber.keyhex),
                ])

        if self.verifyRemote(data):
            self.dumpRemoteData(data, remote.uid)

    def statusRemote(self, estate, verhex, pubhex, main=True):
        '''
        Evaluate acceptance status of estate per its keys
        persist key data differentially based on status
        '''
        data = self.loadRemoteData(estate.uid)
        status = data.get('acceptance') if data else None # pre-existing status

        if main: #main estate logic
            if self.auto:
                status = raeting.acceptances.accepted
            else:
                if status is None:
                    status = raeting.acceptances.pending

                elif status == raeting.acceptances.accepted:
                    if (data and (
                            (verhex != data.get('verhex')) or
                            (pubhex != data.get('pubhex')) )):
                        status = raeting.acceptances.rejected

                elif status == raeting.acceptances.rejected:
                    if (data and (
                            (verhex != data.get('verhex')) or
                            (pubhex != data.get('pubhex')) )):
                        status = raeting.acceptances.pending

                else: # pre-existing was pending
                    # waiting for external acceptance
                    pass

        else: #other estate logic
            if status is None:
                status = raeting.acceptances.accepted

            elif status == raeting.acceptances.accepted:
                if (  data and (
                        (verhex != data.get('verhex')) or
                        (pubhex != data.get('pubhex')) )):
                    status = raeting.acceptances.rejected

            elif status == raeting.acceptances.rejected:
                if (  data and (
                        (verhex != data.get('verhex')) or
                        (pubhex != data.get('pubhex')) )):
                    status = raeting.acceptances.accepted
            else: # pre-existing was pending
                status = raeting.acceptances.accepted

        if status != raeting.acceptances.rejected:
            if (verhex and verhex != estate.verfer.keyhex):
                estate.verfer = nacling.Verifier(verhex)
            if (pubhex and pubhex != estate.pubber.keyhex):
                estate.pubber = nacling.Publican(pubhex)
        estate.acceptance = status
        self.dumpRemote(estate)
        return status

    def rejectRemote(self, estate):
        '''
        Set acceptance status to rejected
        '''
        estate.acceptance = raeting.acceptances.rejected
        self.dumpRemote(estate)

    def pendRemote(self, estate):
        '''
        Set acceptance status to pending
        '''
        estate.acceptance = raeting.acceptances.pending
        self.dumpRemote(estate)

    def acceptRemote(self, estate):
        '''
        Set acceptance status to accepted
        '''
        estate.acceptance = raeting.acceptances.accepted
        self.dumpRemote(estate)

def clearAllRoadSafe(dirpath):
    '''
    Convenience function to clear all road and safe keep data in dirpath
    '''
    road = RoadKeep(dirpath=dirpath)
    road.clearLocalData()
    road.clearAllRemoteData()
    safe = SafeKeep(dirpath=dirpath)
    safe.clearLocalData()
    safe.clearAllRemoteData()
