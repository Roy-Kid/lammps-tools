#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__auther__ = 'Roy Kid'

# A middle teir that can easily format data of lammps's fix
# and provide a serise of interfaces to access.
#


import re
import glob

oneline = 'Read LAMMPS dix files and extract mechaincs data'
docstr = """
    This module is used to extract position data from lammps dump.
"""

class Fix:
    def __init__(self, fpath):
        self._fname = glob.glob(fpath)[0]

    # def __iter__(self):
    #    return self.read_data(self._fname)

    def read_data(self):
        return self._read_data(self._fname)

    def _read_data(self, fname):
        fix = open(fname)
        line = fix.readline()
        self.stage = dict() 
        self.stage['DATA'] = list()
        i = 0
        for line in fix:
            self.stage['DATA'].append([float(i) for i in line.split()])
            i+=1

        self.stage['NUMBER_OF_DATA'] = i

        return self.stage

    def get_col(self, index):
        col = list()
        for i in self.stage['DATA']:
            col.append(i[index])
        return col





