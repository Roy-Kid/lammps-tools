#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__auther__ = 'Roy Kid'

# A middle teir that can easily format data of lammps'log
# and provide a serise of interfaces to access.


import re
import glob

class Log:
    def __init__(self, fpath, summary=False):
        self._fname = glob.glob(fpath)[0]
        self._issummary = summary

    def __iter__(self):
        return self._read_data(self._fname)

    def _read_data(self, fname):
        log = open(fname)
        line = log.readline()
        stage_index = 0
        from collections import defaultdict
        self._summary = defaultdict(list)
        while not line.startswith('Total wall') :
            line = log.readline()
            
            if line.startswith('Step') or line.startswith('Custom'):
                stage = dict()
                stage['STAGE'] = stage_index
                stage['HEADER'] = line.split()
                stage['DATA'] = list()
                for line in log:
                    try:
                        stage['DATA'].append([float(i) for i in line.split()])
                    except:
                        stage_index+=1
                        if self._issummary:
                            for data in stage['DATA']:
                                for i, item in enumerate(data):
                                    self._summary[stage['HEADER'][i]].append(item)

                        yield stage
                        break

    def get_col(self, item, stage=None):
        if stage is None: 
            return self._summary[item]
        else:
            col = list()
            for i in stage['DATA']:

                col.append(i[stage['HEADER'].index(item)])

            return col

