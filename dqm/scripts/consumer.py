from kafka import KafkaConsumer
import numpy as np
import pandas as pd
import os
import sys
import traceback
from datetime import datetime
import pytz
import logging
import pathlib
import msgpack
import json

from django.conf import settings
from django_plotly_dash.consumers import send_to_pipe_channel

consumer = KafkaConsumer('DQM',
                         bootstrap_servers=settings.KAFKA_LOCATION,
                         client_id='test')

unpacker = msgpack.Unpacker(max_array_len=int(1e8))

# Time used
timezone = pytz.timezone('Europe/Madrid')

time_series = {}

#settings.configure()
PATH_DATABASE = settings.PATH_DATABASE
PATH_DATABASE_RESULTS = settings.PATH_DATABASE_RESULTS

# Add one logger for regular messages
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', datefmt='%Y-%b-%d %H:%M:%S')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Add another logger for the exception errors and messages
exc_logger = logging.getLogger('exception_logger')
exc_logger_handler = logging.FileHandler('consumer.log')
err_handler = logging.StreamHandler(stream=sys.stderr)
exc_logger_handler.setFormatter(formatter)
err_handler.setFormatter(formatter)
#exc_logger.addHandler(exc_logger_handler)
exc_logger.addHandler(err_handler)

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

class MessageBuffer:
    def __init__(self):
        self.buffer = {}

    def add_to_buffer(self, message, source, app, plane, part, total_parts):
        part = int(part)
        total_parts = int(total_parts)
        if (source, app, plane) not in self.buffer:
            self.buffer[(source, app, plane)] = [[None]*(part - 1) + [message] + [None] * (total_parts - part), 1, total_parts]
            return
        self.buffer[(source, app, plane)][0][part-1] = message
        self.buffer[(source, app, plane)][1] += 1

    def get_msg_if_available(self, source, app, plane):
        if self.buffer[(source, app, plane)][1] == self.buffer[(source, app, plane)][2]:
            return self.unpack_message(source, app, plane)
        return None

    def unpack_message(self, source, app, plane):
        # We're done so let's clean up
        msg = b''.join(self.buffer[(source, app, plane)][0])
        self.buffer.pop((source, app, plane))
        return msg

mebuf = MessageBuffer()

def write_database(data, header, stream_name):
    """
    Write DQM results coming from the DQM C++ part to the database
    so that they can be reused later
    """
    partition, app_name, run_number, plane = header["partition"], \
        header['app_name'], header['run_number'], header['plane']
    logger.info(f'Writing to database. partition={partition}, app={app_name}, stream={stream_name}, plane={plane}')
    values = data['value']
    if len(values.shape) == 1:
        values = values.reshape((1, -1))
    df = pd.DataFrame(values)
    if 'channels' in data:
        df.columns = data['channels']
    now = datetime.now(timezone).strftime('%y%m%d-%H%M%S')
    filename = f'{stream_name}-{plane}-{now}'
    os.makedirs(f'{PATH_DATABASE}/{partition}/{app_name}/{run_number}', exist_ok=True)
    df.to_hdf(f'{PATH_DATABASE}/{partition}/{app_name}/{run_number}/{filename}.hdf5', 'data')

def write_result_to_database(data, partition, app_name, stream_name, run_number, plane):
    """
    Write DQM results like the time evolution
    """
    df = pd.DataFrame(data)
    now = datetime.now(timezone).strftime('%y%m%d-%H%M%S')
    filename = f'{stream_name}-{plane}-{now}'
    os.makedirs(f'{PATH_DATABASE_RESULTS}/{partition}/{app_name}/{run_number}', exist_ok=True) 
    df.to_hdf(f'{PATH_DATABASE_RESULTS}/{partition}/{app_name}/{run_number}/{filename}.hdf5', 'data')


def main():
    time_map = {}
    time_last_data = datetime.now(timezone)
    for message in consumer:
        # print(str(message))

        ls = message.value.split(b'\n\n\n')
        nls = []

        header_bytes = ls[0]
        header = json.loads(header_bytes)

        if len(ls) > 3:
            continue

        if 'part' in header:
            mebuf.add_to_buffer(b'\n\n\n'.join(ls[1:]), header['source'], header['app_name'], header['plane'], header['part'], header['total_parts'])
            if (msg := mebuf.get_msg_if_available(header['source'], header['app_name'], header['plane'])):
                print('Buffer is complete', b'\n\n\n' in msg)
                ls = [None] + msg.split(b'\n\n\n')
            else:
                continue

        data_found = False

        if header['algorithm'] == 'std':
            print('std', len(ls))
            x = np.array(msgpack.unpackb(ls[1][1:]))
            y = np.array(msgpack.unpackb(ls[2][1:]))
            # if 'df' in header['app_name']:

            write_database({'channels': x, 'value': y}, header, 'std')

            timestamp = datetime.now(timezone).strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{header["partition"]}-std{header["plane"]}',
                                label=f'{header["partition"]}-std{header["plane"]}',
                                value=timestamp)
            data_found = True
        if header['algorithm'] == 'rms':
            print('rms', len(ls))
            x = np.array(msgpack.unpackb(ls[1][1:]))
            y = np.array(msgpack.unpackb(ls[2][1:]))
            print(x.shape, y.shape)

            write_database({'channels': x, 'value': y}, header, 'rms')

            timestamp = datetime.now(timezone).strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{header["partition"]}-rms{header["plane"]}',
                                label=f'{header["partition"]}-rms{header["plane"]}',
                                value=timestamp)
            data_found = True
        elif header['algorithm'] == 'fourier_plane':
            print('fourier_plane', len(ls))
            x = np.array(msgpack.unpackb(ls[1][1:]))
            y = np.array(msgpack.unpackb(ls[2][1:]))
            print(x.shape, y.shape)

            write_database({'channels': x[1:], 'value': y[1:]}, header, 'fourier_plane')

            timestamp = datetime.now(timezone).strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{header["partition"]}-fourier_plane{header["plane"]}',
                                label=f'{header["partition"]}-fourier_plane{header["plane"]}',
                                value=timestamp)
            data_found = True
        elif header['algorithm'] == 'raw':
            print('raw', len(ls))
            x = np.array(msgpack.unpackb(ls[1][1:]))
            y = np.array(msgpack.unpackb(ls[2][1:]))

            y = y.reshape((x.shape[0], -1)).T
            timestamps = np.arange(x.shape[0])
            print(x.shape, y.shape)

            #plot size limiter, switched off
            #if y.shape[0] > 100:
            #    y = y[:100]

            write_database({'value': y, 'channels': x, 'timestamps': timestamps},
                           header, 'raw')

            timestamp = datetime.now(timezone).strftime('%Y/%m/%d %H:%M:%S')
            send_to_pipe_channel(channel_name=f'{header["partition"]}-raw{header["plane"]}',
                                label=f'{header["partition"]}-raw{header["plane"]}',
                                value=timestamp)
            data_found = True
        if data_found and header['partition'] not in time_map:
            time_map[header['partition']] = time_last_data
        if data_found and (datetime.now(timezone) - time_map[header['partition']]).total_seconds() > 10:
            time_last_data = datetime.now(timezone)
            time_map[header['partition']] = time_last_data
            send_to_pipe_channel(channel_name=f'{header["partition"]}-pipe-run',
                                 label=f'{header["partition"]}-pipe-run',
                                 value=header['run_number'])

        continue

        # Only send to the time plot data coming from the first DQM-RU app
        if app_name == 'dqm0_ru':
            plane_index = int(plane)
            dindex = (source, plane_index)
            if dindex not in time_series:
                time_series[dindex] = TimeSeries(partition, app_name, 'std', plane, run_number)
            time_series[dindex].add(int(datetime.now(timezone).timestamp()), val[0], run_number)
            send_to_pipe_channel(channel_name=f'time_evol_{plane_index}',
                                label=f'time_evol_{plane_index}',
                                value={'values': time_series[dindex].data[:time_series[dindex].max_index],
                                    'timestamp': time_series[dindex].time[:time_series[dindex].max_index]}
                                )
            # send_to_pipe_channel(channel_name=f'time_evol_{plane_index}',
            #                     label=f'time_evol_{plane_index}',
            #                     value={'data': time_series[dindex].data[time_series[dindex].index-1],
            #                            'timestamp': time_series[dindex].time[time_series[dindex].index-1]}
            #                     )

if __name__ == 'django.core.management.commands.shell':

    try:
        logger.info('Waiting for messages...')
        main()
    except KeyboardInterrupt:
        logger.info('\nCtrl+C has been pressed, saving...')
        for time_series in time_series_ls:
            time_series.save()
    except Exception:
        tb = traceback.format_exc()
        exc_logger.error(' error in consumer with traceback: ' + tb)
        logger.info('An exception has been raised, check the log file for more details. Aborting...')
