import numpy as np
import json
import os
import pandas as pd
from django.conf import settings

DATABASE_PATH = settings.PATH_DATABASE
DATABASE_PATH_RESULTS = settings.PATH_DATABASE_RESULTS

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

def get_ordered_runs(partition):
    """
    Get a list of the modification times and runs so they can be sorted in time
    """
    files = [x for x in os.listdir(DATABASE_PATH) if x.startswith(partition + '_dqm')]
    times = [os.path.getmtime(DATABASE_PATH + x) for x in files]
    most_recent_source = max(zip(times, files))[1]
    print(f'{most_recent_source=}')
    runs = [x for x in os.listdir(DATABASE_PATH + most_recent_source)]
    times = [os.path.getmtime(DATABASE_PATH + most_recent_source + '/' + x) for x in runs]
    return zip(times, runs)

def get_current_run(partition):
    """
    Get the current run based on the modification date
    """

    return max(get_ordered_runs(partition))[1]


def get_all_runs(partition):
    print(f'Calling get_all_runs with {partition=}')
    s = set()
    for d in [x for x in os.listdir(DATABASE_PATH) if x.startswith(partition + '_dqm')]:
        for run in os.listdir(DATABASE_PATH + '/' + d):
            s.add(run)
    return s

class DataStream:
    def __init__(self, name, source):
        self.name = name
        self.source = source

    def get_data(self, run_number='last'):
        plane_number = self.name[-1]
        if run_number == 'last':
            folders = [x for x in os.listdir(DATABASE_PATH + self.source)]
            times = [os.path.getmtime(DATABASE_PATH + self.source + '/' + x) for x in folders]
            run_number = max(zip(times, folders))[1]

        files = [f for f in os.listdir(DATABASE_PATH + self.source + '/' + run_number) if self.name[:-1] + f'-{plane_number}' in f]
        last_file = max(files)
        index = last_file.find('.hdf5')
        # Date has 13 digits, YYMMDD-HHMMSS
        date = last_file[index-13:index]

        if last_file:
            path = DATABASE_PATH + self.source + '/' + run_number + '/' + last_file
            print(f'Reading file {path}')
            try:
                return (pd.read_hdf(path), date)
            except:
                print('Unable to read data')
                print((pd.read_hdf(path)))
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

def get_last_result(source, stream_name):
    files = os.listdir(f'{DATABASE_PATH_RESULTS}/{source}')
    # max will return the latest one since they are called the same except for the date
    filename = max([f for f in files if f.startswith(stream_name)])
    return pd.read_hdf(f'{DATABASE_PATH_RESULTS}/{source}/{filename}')

def get_average(source, stream_name, run):
    """
    Get the average value for a stream for a whole run
    """
    files = [f'{DATABASE_PATH}/{source}/{run}/{f}' for f in os.listdir(f'{DATABASE_PATH}/{source}/{run}') if f.startswith(stream_name)]
    print(f'Reading {len(files)} files')
    data = pd.concat([pd.read_hdf(f) for f in files[:100]])
    mean = data.mean(axis=0)
    return mean.to_frame().T.reset_index(drop=True)
