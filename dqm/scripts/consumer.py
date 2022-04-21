from kafka import KafkaConsumer
import numpy as np
import pandas as pd
import os
import traceback
from datetime import datetime
import logging

from django.conf import settings
from django_plotly_dash.consumers import send_to_pipe_channel
from django_plotly_dash.consumers import send_to_pipe_channel

time_series = {}

PATH_DATABASE = settings.PATH_DATABASE

logging.basicConfig(filename='consumer.log',
                    level=logging.ERROR, format='%(asctime)s %(message)s')


MAX_POINTS = 10000

class TimeSeries:
    def __init__(self):
        self.data = [0] * MAX_POINTS
        self.time = [0] * MAX_POINTS
        self.index = 0
        self.max_index = 0
    def add(self, date, value):
        self.data[self.index] = value
        self.time[self.index] = date
        self.index += 1
        self.max_index = max(self.max_index, self.index)
        if self.index >= MAX_POINTS:
            self.index = 0

def write_database(data, source, stream_name, run_number, plane):
    """
    Write DQM results coming from the DQM C++ part to the database
    so that they can be reused later
    """
    print('Writing to database', source, stream_name, plane)
    values = data['value']
    if len(values.shape) == 1:
        values = values.reshape((1, -1))
    df = pd.DataFrame(values)
    if 'channels' in data:
        df.columns = data['channels']
    from datetime import datetime
    now = datetime.now().strftime('%y%m%d-%H%M%S')
    filename = f'{stream_name}-{plane}-{now}'
    if not os.path.exists(f'{PATH_DATABASE}/{source}'):
        print(f'Creating directory at {PATH_DATABASE}/{source}')
        os.mkdir(f'{PATH_DATABASE}/{source}')
    if not os.path.exists(f'{PATH_DATABASE}/{source}/{run_number}'):
        print(f'Creating directory at {PATH_DATABASE}/{source}/{run_number}')
        os.mkdir(f'{PATH_DATABASE}/{source}/{run_number}')
    df.to_hdf(f'{PATH_DATABASE}/{source}/{run_number}/{filename}.hdf5', 'data')

consumer = KafkaConsumer('testdunedqm',
                         bootstrap_servers='monkafka:30092',
                         client_id='test')

for message in consumer:
    # print(str(message))

    message = str(message.value).split(';')
    # print(message)

    source = message[0][2:]
    run_number = message[2]
    app_name = message[8]
    plane = message[10]

    try:
        if 'fft_sums_display' in message[1]:
            m = message[-1].split('\\n')
            freq = np.fromstring(m[0], sep=' ')
            val = np.fromstring(m[-2], sep=' ')
            # At f = 0 Hz there will be a huge value that doesn't let
            # us see the rest of the points
            write_database({'value': val[1:], 'channels': freq[1:]},
                            source, 'fft_sums_display',
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
                        source, 'raw_display',
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
                        source, 'rmsm_display',
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
                    time_series[dindex] = TimeSeries()
                time_series[dindex].add(int(datetime.now().timestamp()), val[0])
                send_to_pipe_channel(channel_name=f'time_evol_{plane_index}',
                                    label=f'time_evol_{plane_index}',
                                    value={'data': time_series[dindex].data[:time_series[dindex].max_index],
                                        'timestamp': time_series[dindex].time[:time_series[dindex].max_index]}
                                    )
    except KeyboardInterrupt:
        print('Exiting...')
    except Exception:
        tb = traceback.format_exc()
        logging.error(' error in consumer with traceback: ' + tb + '\nAnd the message is ' + str(message))
        print('EXCEPTION')
        continue
