from kafka import KafkaConsumer
import numpy as np
import pandas as pd
from django.conf import settings
import os

PATH_DATABASE = settings.PATH_DATABASE

def write_database(data, source, stream_name, run_number, plane):
    print('Writing to database', stream_name)
    database_path = PATH_DATABASE
    values = data['value']
    if len(values.shape) == 1:
        values = values.reshape((1, -1))
    # print(values.shape)
    # print(data['channels'].shape)
    df = pd.DataFrame(values)
    if 'channels' in data:
        df.columns = data['channels']
        # print(df.columns)
    from datetime import datetime
    now = datetime.now().strftime('%y%m%d-%H%M%S')
    filename = f'{stream_name}-{plane}-{run_number}-{now}'
    try:
        os.listdir(f'{PATH_DATABASE}/{source}')
    except OSError:
        print('EXCEPTION')
        print(f'Creating directory at {PATH_DATABASE}/{source}')
        os.mkdir(f'{PATH_DATABASE}/{source}')
    df.to_hdf(f'{PATH_DATABASE}/{source}/{filename}.hdf5', 'data')

consumer = KafkaConsumer('testdunedqm',
                         bootstrap_servers='monkafka:30092',
                         client_id='test')

for message in consumer:
    # print(message)

    message = str(message.value).split(';')
    # print(message)
    # message[0] = message[0].replace("b", "")
    # message[0] = message[0].replace("'", "")
    # message[0] = message[0].replace('"', "")
    # message[8] = message[8].replace("'", "")

    source = message[0][2:]
    # originalDataId = message[0]
    # originalRecordId = message[1]
    # dataPath = message[2]
    # encoding = message[3]
    # originalDataName = message[4]
    plane = message[10]

    if 'fft_sums_display' in message[1]:
        m = message[-1].split('\\n')
        freq = np.fromstring(m[0], sep=' ')
        val = np.fromstring(m[-2], sep=' ')
        # write_database({'value': val, 'channels': freq},
        #                'rmsm_display',
        #                run_number, plane)
        # print(freq, val)

    if 'raw_display' in message[1]:
        m = message[-1].split('\\n')
        channels = np.fromstring(m[0].split(',')[-1], sep=' ')
        timestamps = np.array(m[1:-1:2], dtype=int)
        val = np.fromstring(' '.join(m[2::2]), sep=' ').reshape(( len(timestamps), len(channels) ))
        run_number = 1

        write_database({'value': val, 'channels': channels, 'timestamps': timestamps},
                       source, 'raw_display', 
                       run_number, plane)
                       
    if 'rmsm_display' in message[1]:
        m = message[-1].split('\\n')
        channels = np.fromstring(m[0].split(',')[-1], sep=' ')
        val = np.fromstring(m[-2], sep=' ')
        # Random noise to see the plots updating
        val += np.random.random(val.shape[0]) * 20
        run_number = 1
        write_database({'value': val, 'channels': channels},
                       source, 'rmsm_display', 
                       run_number, plane)
