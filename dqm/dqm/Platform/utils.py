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
    """
    Get a sorted list of all the runs in the database
    """
    return list(map(str, sorted(map(int, os.listdir(DATABASE_PATH + source)))))

def get_current_run(partition):
    """
    Get the current run based on the modification date
    """

    files = [x for x in os.listdir(DATABASE_PATH) if x.startswith(partition + '_dqm')]
    times = [os.path.getmtime(DATABASE_PATH + x) for x in files]
    most_recent_source = max(zip(times, files))[1]
    print(f'{most_recent_source=}')
    runs = [x for x in os.listdir(DATABASE_PATH + most_recent_source)]
    times = [os.path.getmtime(DATABASE_PATH + most_recent_source + '/' + x) for x in runs]
    print(runs, times)
    return max(zip(times, runs))[1]


def get_all_runs(partition):
    print(f'Calling get_all_runs with {partition=}')
    s = set()
    for d in [x for x in os.listdir(DATABASE_PATH) if x.startswith(partition + '_dqm')]:
        for run in os.listdir(DATABASE_PATH + '/' + d):
            s.add(run)
    return s

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
        s.add(source[:source.find('_dqm')])
    return list(s)

def get_apps_for_partition(partition):
    apps = []
    for source in os.listdir(DATABASE_PATH):
        if source[:source.find('_dqm')] == partition:
            apps.append(source[source.find('dqm'):])
    return apps

