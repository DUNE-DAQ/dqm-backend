from kafka import KafkaConsumer
import numpy as np
import pandas as pd
import os
import traceback
from datetime import datetime
import logging

from django.conf import settings
from django_plotly_dash.consumers import send_to_pipe_channel

consumer = KafkaConsumer('testdunedqm',
                         bootstrap_servers='monkafka:30092',
                         client_id='test')

time_series = {}

#settings.configure()
PATH_DATABASE = settings.PATH_DATABASE
PATH_DATABASE_RESULTS = settings.PATH_DATABASE_RESULTS

logging.basicConfig(filename='consumer.log', level=logging.ERROR, format='%(asctime)s %(message)s')

MAX_POINTS = 1000

time_series_ls = []
class TimeSeries:
    def __init__(self, partition, app_name, stream_name, plane, run_number):
        self.partition = partition
        self.app_name = app_name
        self.stream_name = stream_name
        self.plane = plane
        time_series_ls.append(self)
        self.data = [0] * MAX_POINTS
        self.time = [0] * MAX_POINTS
        self.index = 0
        self.max_index = 0
        self.run_number = run_number
    def add(self, date, value, run_number):
        if run_number != self.run_number:
            self.save()
            self.run_number = run_number
            self.index = 0
            self.max_index = 0

        self.data[self.index] = value
        self.time[self.index] = date
        self.index += 1
        self.max_index = max(self.max_index, self.index)
        if self.index >= MAX_POINTS:
            self.index = 0
            self.save()
    def save(self):
        max_index = self.index if self.index != 0 else MAX_POINTS
        dic = {'values': self.data[:max_index], 'timestamp': self.time[:max_index]}
        write_result_to_database(dic, self.partition, self.app_name, self.stream_name, self.run_number, self.plane)

def write_database(data, partition, app_name, stream_name, run_number, plane):
    """
    Write DQM results coming from the DQM C++ part to the database
    so that they can be reused later
    """
    print('Writing to database', partition, app_name, stream_name, plane)
    values = data['value']
    if len(values.shape) == 1:
        values = values.reshape((1, -1))
    df = pd.DataFrame(values)
    if 'channels' in data:
        df.columns = data['channels']
    now = datetime.now().strftime('%y%m%d-%H%M%S')
    filename = f'{stream_name}-{plane}-{now}'
    os.makedirs(f'{PATH_DATABASE}/{partition}/{app_name}/{run_number}', exist_ok=True)
    df.to_hdf(f'{PATH_DATABASE}/{partition}/{app_name}/{run_number}/{filename}.hdf5', 'data')

def write_result_to_database(data, partition, app_name, stream_name, run_number, plane):
    """
    Write DQM results like the time evolution
    """
    df = pd.DataFrame(data)
    now = datetime.now().strftime('%y%m%d-%H%M%S')
    filename = f'{stream_name}-{plane}-{now}'
    os.makedirs(f'{PATH_DATABASE_RESULTS}/{partition}/{app_name}/{run_number}', exist_ok=True) 
    df.to_hdf(f'{PATH_DATABASE_RESULTS}/{partition}/{app_name}/{run_number}/{filename}.hdf5', 'data')


def main():
    for message in consumer:
        # print(str(message))

        message = str(message.value).split(';')
        # print(message)

        source = message[0][2:]
        run_number = message[2]
        partition = message[7]
        app_name = message[8]
        plane = message[10]

        if 'fft_sums_display' in message[1]:
            m = message[-1].split('\\n')
            freq = np.fromstring(m[0], sep=' ')
            val = np.fromstring(m[-2], sep=' ')
            # At f = 0 Hz there will be a huge value that doesn't let
            # us see the rest of the points
            write_database({'value': val[1:], 'channels': freq[1:]},
                            partition, app_name, 'fft_sums_display',
                            run_number, plane)


            timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{source}-fft_sums_display{plane}',
                                label=f'{source}-fft_sums_display{plane}',
                                value=timestamp)

        if 'raw_display' in message[1]:
            m = message[-1].split('\\n')
            channels = np.fromstring(m[0].split(',')[-1], sep=' ', dtype=np.int)
            timestamps = np.array(m[1:-1:2], dtype=int)
            val = np.fromstring(' '.join(m[2::2]), sep=' ', dtype=np.int).reshape(( len(timestamps), len(channels) ))

            write_database({'value': val, 'channels': channels, 'timestamps': timestamps},
                        partition, app_name, 'raw_display',
                        run_number, plane)

            timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{source}-raw_display{plane}',
                                label=f'{source}-raw_display{plane}',
                                value=timestamp)

        if 'rmsm_display' in message[1]:
            m = message[-1].split('\\n')
            channels = np.fromstring(m[0].split(',')[-1], sep=' ', dtype=np.int)
            val = np.fromstring(m[-2], sep=' ')
            write_database({'value': val, 'channels': channels},
                        partition, app_name, 'rmsm_display',
                        run_number, plane)

            timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{source}-rmsm_display{plane}',
                                label=f'{source}-rmsm_display{plane}',
                                value=timestamp)

            # Only send to the time plot data coming from the first DQM-RU app
            if app_name == 'dqm0_ru':
                plane_index = int(plane)
                dindex = (source, plane_index)
                if dindex not in time_series:
                    time_series[dindex] = TimeSeries(partition, app_name, 'rmsm_display', plane, run_number)
                time_series[dindex].add(int(datetime.now().timestamp()), val[0], run_number)
                send_to_pipe_channel(channel_name=f'time_evol_{plane_index}',
                                    label=f'time_evol_{plane_index}',
                                    value={'values': time_series[dindex].data[:time_series[dindex].max_index],
                                        'timestamp': time_series[dindex].time[:time_series[dindex].max_index]}
                                    )
        if 'channel_mask_display' in message[1]:
            m = message[-1].split('\\n')
            channels = np.fromstring(m[0].split(',')[-1], sep=' ', dtype=np.int)
            val = np.fromstring(m[1], sep=' ')
            write_database({'value': val, 'channels': channels},
                        partition, app_name, 'channel_mask_display',
                        run_number, plane)

            timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{source}-channel_mask_display{plane}',
                                label=f'{source}-channel_mask_display{plane}',
                                value=timestamp)

if __name__ == 'django.core.management.commands.shell':

    try:
        main()
    except KeyboardInterrupt:
        print('Saving')
        for time_series in time_series_ls:
            time_series.save()
        exit()
    except Exception:
        tb = traceback.format_exc()
        logging.error(' error in consumer with traceback: ' + tb)
        print('EXCEPTION')
