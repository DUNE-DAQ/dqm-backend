import numpy as np
import json
import os
import pandas as pd
from django.conf import settings

DATABASE_PATH = settings.PATH_DATABASE

def get_streams():
    """
    Return the available streams
    """
    ret = {}
    for source in os.listdir(DATABASE_PATH):
        ret[source] = set()
        for run_number in os.listdir(DATABASE_PATH + source):
            files = os.listdir(DATABASE_PATH + source + '/' + run_number)
            for f in files:
                if ''.join(f.split('-')[:2]) not in ret[source]:
                    ret[source].add(''.join(f.split('-')[:2]))
        ret[source] = sorted(list(ret[source]))
    print(f'Running get_streams with output {ret}')
    return ret

def get_runs(source):
    runs = os.listdir(DATABASE_PATH + source)
    return runs

class DataSource:
    def __init__(self, name):
        self.name = name

class DataStream:
    def __init__(self, name, source):
        self.name = name
        self.source = source

    def get_data(self, run_number='last'):
        plane_number = self.name[-1]
        source_name = self.source.name
        if run_number == 'last':
            run_number = sorted([f for f in os.listdir(DATABASE_PATH + source_name)])[-1]

        files = [f for f in os.listdir(DATABASE_PATH + source_name + '/' + run_number) if self.name[:-1] + f'-{plane_number}' in f]
        files.sort(reverse=True)
        if files:
            print('Reading file ' + DATABASE_PATH + source_name + '/' + run_number + '/' + files[0])
            try:
                return pd.read_hdf(DATABASE_PATH + source_name + '/' + run_number + '/' + files[0])
            except:
                print('Unable to read data')
                print((pd.read_hdf(DATABASE_PATH + source_name + '/' + run_number + '/' + files[0])))
                return None
        else:
            print('No data available')
            return None

def get_partitions():
    s = set()
    for source in os.listdir(DATABASE_PATH):
        s.add(source[:source.find('dqm')])
    return list(s)

def get_apps_for_partition(partition):
    apps = []
    for source in os.listdir(DATABASE_PATH):
        if source[:source.find('_dqm')] == partition:
            apps.append(source[source.find('dqm'):])
    return apps
