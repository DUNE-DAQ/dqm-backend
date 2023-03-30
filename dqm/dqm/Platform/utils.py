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

def get_ordered_runs(partition, results=False):
    """
    Get a list of the modification times and runs so they can be sorted in time
    """
    if results:
        DATABASE = DATABASE_PATH_RESULTS
    else:
        DATABASE = DATABASE_PATH
    try:
        apps = os.listdir(f'{DATABASE}/{partition}')
    except FileNotFoundError:
        print(f'Directory {DATABASE}/{partition} was not found')
        return []
    runs = {}
    for app in apps:
        for run in os.listdir(f'{DATABASE}/{partition}/{app}'):
            runs[run] = max(os.path.getmtime(f'{DATABASE}/{partition}/{app}/{run}'), runs[app] if app in runs else 0)
    times = [os.path.getmtime(f'{DATABASE}/{partition}/{app}/{run}') for app in apps for run in os.listdir(f'{DATABASE}/{partition}/{app}')]
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

        print(f'Calling get_data, {DATABASE_PATH}/{self.partition}/{self.app_name}/{run_number}')
        print(self.name[:-1] + f'-{plane_number}')

        files = [f for f in os.listdir(f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{run_number}') if self.name[:-1] + f'-{plane_number}' in f]
        print(files)
        print(len(files))
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

    def get_all_streams(self, stream_name, run_number='last'):
        if run_number == 'last':
            folders = os.listdir(f'{DATABASE_PATH}/{self.partition}/{self.app_name}')
            times = [os.path.getmtime(f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{x}') for x in folders]
            run_number = max(zip(times, folders))[1]

        # files = [f for f in  if self.name[:-1] in f]
        all_files = os.listdir(f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{run_number}')
        last_files = [max([f for f in all_files if f'{stream_name}-{i}' in f]) for i in range(3)]
        index = last_files[0].find('.hdf5')
        # Date has 13 digits, YYMMDD-HHMMSS
        date = last_files[0][index-13:index]

        if last_files:
            dfs = []
            for f in last_files:
                path = f'{DATABASE_PATH}/{self.partition}/{self.app_name}/{run_number}/{f}'
                print(f'Reading file {path}')
                try:
                    dfs.append(pd.read_hdf(path))
                except:
                    print('Unable to read data')
                    print((pd.read_hdf(path)))
                    return
            try:
                return (pd.concat(dfs, axis=1), date)
            except:
                print('Unable to read data')
                print(dfs)
                return
        else:
            print('No data available')
            return

def get_partitions():
    """
    Get a list with all the partitions that have sent data
    """
    return os.listdir(DATABASE_PATH)

def get_apps_for_partition(partition):
    """
    Get a list of all the app names that have sent data
    """
    return sorted(os.listdir(f'{DATABASE_PATH}/{partition}'))

def get_last_result(partition, app_name, stream_name, max_files=10, max_rows=5000):
    ord_runs = get_ordered_runs(partition, True)
    ls = []
    total_rows = 0
    total_files = 0

    for pair in sorted(ord_runs, reverse=True):
        time, run = pair
        for f in sorted(os.listdir(f'{DATABASE_PATH_RESULTS}/{partition}/{app_name}/{run}'), reverse=True):
            print(f)
            ls.append(pd.read_hdf(f'{DATABASE_PATH_RESULTS}/{partition}/{app_name}/{run}/{f}'))
            rows = len(ls[-1])
            total_rows += rows
            total_files += 1
            if total_rows >= max_rows or total_files >= max_files:
                break

    # last_run = max(ord_runs)[1]

    # files = os.listdir()
    # # max will return the latest one since they are called the same except for the date
    # filename = max([f for f in files if f.startswith(stream_name)])
    # return pd.read_hdf(f'{DATABASE_PATH_RESULTS}/{partition}/{app_name}/{last_run}/{filename}')
    return pd.concat(ls)

def get_average(partition, app_name, stream_name, run):
    """
    Get the average value for a stream for a whole run
    """
    files = [f'{DATABASE_PATH}/{partition}/{app_name}/{run}/{f}' for f in os.listdir(f'{DATABASE_PATH}/{partition}/{app_name}/{run}') if f.startswith(stream_name)]
    print(f'Reading {len(files)} files')
    data = pd.concat([pd.read_hdf(f) for f in files[:100]])
    mean = data.mean(axis=0)
    return mean.to_frame().T.reset_index(drop=True)

