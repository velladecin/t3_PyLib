#!/usr/bin/python
import sys, os
import os.path

"""
Requires the topo file to be in this format:

SA:5CPK-St_Marys:SWCMT0000068
SA:5ADB-Greenfields:SWCMT0000081
SA:5ADB-Greenfields:SWCMT0000080
SA:5ADB-Greenfields:SWCMT0000240
VIC:3FSR-Footscray:SWCMT0000181
VIC:3FSR-Footscray:SWCMT0000182
...
...

"""

class Topology:
    def __init__(self, topologyImportFile):
        try:
            tif = open(topologyImportFile, 'r')    
        except IOError as ioe:
            print str(ioe)
            sys.exit(1)

        topo = {}
        for line in tif.readlines():
            line = line.rstrip()
            state, hub, cmts = line.split(':')

            if not state in topo:
                topo[state] = {}

            if not hub in topo[state]:
                topo[state][hub] = {}

            # in case we ever need some info about cmts, eg: IP
            topo[state][hub][cmts] = 1

        self.topology = topo

    #
    # Methods

    def getStates(self):
        return sorted(self.topology.keys())

    def getState(self, state):
        try:
            return self.topology[state]
        except KeyError as e:
            print "No such state: %s" % state

        return {}

    def getHubs(self):
        hubs = []
        for state in sorted(self.topology.keys()):
            hubs.extend( sorted(self.topology[state].keys()) )

        return hubs
            

    def getHub(self, hub):
        for state in self.topology.keys():
            if hub in self.topology[state]:
                return self.topology[state][hub]

        print "No such hub: %s" % hub
        return {}
            

    def getCmts(self):
        cmts = []
        for state in sorted(self.topology.keys()):
            for hub in sorted(self.topology[state].keys()):
                cmts.extend( sorted(self.topology[state][hub].keys()) )

        return cmts
