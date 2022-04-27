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

def get_runs(partition, app_name):
    """
    Get a sorted list of all the runs in the database
    """
    return list(map(str, sorted(map(int, os.listdir(f'{DATABASE_PATH}/{partition}/{app_name}')))))

def get_ordered_runs(partition):
    """
    Get a list of the modification times and runs so they can be sorted in time
    """
    apps = os.listdir(f'{DATABASE_PATH}/{partition}')
    runs = {}
    for app in apps:
        for run in os.listdir(f'{DATABASE_PATH}/{partition}/{app}'):
            runs[run] = max(os.path.getmtime(f'{DATABASE_PATH}/{partition}/{app}/{run}'), runs[app] if app in runs else 0)
    times = [os.path.getmtime(f'{DATABASE_PATH}/{partition}/{app}/{run}') for app in apps for run in os.listdir(f'{DATABASE_PATH}/{partition}/{app}')]
    # most_recent_source = max(zip(times, files))[1]
    # print(f'{most_recent_source=}')
    # runs = [x for x in os.listdir(DATABASE_PATH + most_recent_source)]
    # times = [os.path.getmtime(DATABASE_PATH + most_recent_source + '/' + x) for x in runs]
    return zip(runs.values(), runs.keys())

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
    def __init__(self, name, partition, app_name):
        self.name = name
        self.partition = partition
        self.app_name = app_name

    def get_data(self, run_number='last'):
        plane_number = self.name[-1]
        if run_number == 'last':
            folders = os.listdir(f'{DATABASE_PATH}/{self.partition}/{self.app_name}')
            times = [os.path.getmtime(f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{x}') for x in folders]
            run_number = max(zip(times, folders))[1]

        files = [f for f in os.listdir(f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{run_number}') if self.name[:-1] + f'-{plane_number}' in f]
        last_file = max(files)
        index = last_file.find('.hdf5')
        # Date has 13 digits, YYMMDD-HHMMSS
        date = last_file[index-13:index]

        if last_file:
            path = f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{run_number}/{last_file}'
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
    return os.listdir(DATABASE_PATH)

def get_apps_for_partition(partition):
    return os.listdir(f'{DATABASE_PATH}/{partition}')

def get_last_result(partition, app_name, stream_name):
    files = os.listdir(f'{DATABASE_PATH_RESULTS}/{partition}/{app_name}')
    # max will return the latest one since they are called the same except for the date
    filename = max([f for f in files if f.startswith(stream_name)])
    return pd.read_hdf(f'{DATABASE_PATH_RESULTS}/{partition}/{app_name}/{filename}')

def get_average(source, stream_name, run):
    """
    Get the average value for a stream for a whole run
    """
    files = [f'{DATABASE_PATH}/{source}/{run}/{f}' for f in os.listdir(f'{DATABASE_PATH}/{source}/{run}') if f.startswith(stream_name)]
    print(f'Reading {len(files)} files')
    data = pd.concat([pd.read_hdf(f) for f in files[:100]])
    mean = data.mean(axis=0)
    return mean.to_frame().T.reset_index(drop=True)
