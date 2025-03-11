import pprint
import sys
import time

from pandas import DataFrame

import constants
from algorithms import dijkstra, astar
from constants import STOP, STOP_LAT, STOP_LON
import reader


data_read_time = 0


def main():
    data_read_start_time = time.time()

    data: DataFrame = reader.read_data('connection_graph.csv')
    if data is None:
        print("Error reading data")
        sys.exit(1)

    global data_read_time
    data_read_time = time.time() - data_read_start_time
    sys.stderr.write(f"Data read time: {data_read_time}\n")
    # start_stop, end_stop = 'Magellana','LEŚNICA'

    start_stop, end_stop = 'PORT LOTNICZY','Chełmońskiego'
    # start_stop, end_stop = 'LEŚNICA', 'POŚWIĘTNE'
    # start_stop, end_stop = 'ZWYCIĘSKA', 'ZWYCIĘSKA'
    # start_stop, end_stop = 'TARNOGAJ', 'Wrocław Popowice (17.południk)'
    # start_stop, end_stop = 'Wrocław Popowice (17.południk)', 'TARNOGAJ'
    # start_stop, end_stop = 'TARNOGAJ', 'Port Popowice'
    # start_stop, end_stop = 'Port Popowice', 'TARNOGAJ'
    # start_stop, end_stop = 'PORT LOTNICZY', 'Swojczyce'
    start_stop1, end_stop1 = 'Świdnicka', 'Hala Stulecia'
    # start_stop, end_stop = 'SĘPOLNO', 'LEŚNICA'
    # start_stop, end_stop = 'LEŚNICA', 'IWINY - pętla'
    # start_stop, end_stop = 'RACŁAWICKA', 'Chłodna'
    # start_stop, end_stop = 'ZWYCIĘSKA', 'PL. GRUNWALDZKI'
    # start_stop, end_stop = 'rondo Św. Ojca Pio', 'PL. GRUNWALDZKI'
    # start_stop, end_stop = 'LEŚNICA', 'PL. GRUNWALDZKI'
    start_stop2, end_stop2 = 'SPISKA (Ośrodek sportu)', 'Inowrocławska'


    # passenger_arrival_time: int = time_converter_to_int('16:58:00')
    #
    # start_stop, end_stop = 'SPISKA (Ośrodek sportu)', 'Wallenroda'
    # passenger_arrival_time: int = time_converter_to_int('14:45:00')
    #
    # start_stop, end_stop = 'Kadłub NŻ', 'Rogowska (P+R)'
    # passenger_arrival_time: int = time_converter_to_int('00:44:00')
    #
    # start_stop, end_stop = 'krzyki'.upper(), 'Jarnołtów'.upper()
    # passenger_arrival_time: int = time_converter_to_int('23:04:00')

    if start_stop not in data[constants.START_STOP].values:
        print(f"Start stop {start_stop} not found in data")
        sys.exit(1)
    elif end_stop not in data[constants.START_STOP].values:
        print(f"End stop {end_stop} not found in data")
        sys.exit(1)

    # passenger_arrival_time: int = time_converter_to_int('23:40:00')
    # passenger_arrival_time: int = time_converter_to_int('09:20:00')
    passenger_arrival_time: int = reader.time_str_to_int('03:40:00')
    # passenger_arrival_time: int = time_converter_to_int('07:15:00')
    # passenger_arrival_time: int = time_converter_to_int('14:38:00')
    # passenger_arrival_time: int = time_converter_to_int('07:40:00')
    # passenger_arrival_time: int = time_converter_to_int('16:00:00')
    # passenger_arrival_time: int = time_converter_to_int('09:43:00')
    # passenger_arrival_time: int = time_converter_to_int('09:00:00')
    # passenger_arrival_time: int = time_converter_to_int('23:15:00')


    stops_to_visit = ['KRZYKI', 'Rondo', 'pl. Orląt Lwowskich', 'Ogród Botaniczny', 'Jagodzińska', 'Wschowska',
                      'Grabiszyńska', 'Prudnicka']

    for stop in stops_to_visit:
        if stop not in data[constants.START_STOP].values:
            print(f"Stop {stop} not found in data")
            sys.exit(1)
    print(data, start_stop, end_stop, passenger_arrival_time)
    print(astar(data, start_stop, end_stop, passenger_arrival_time, 't', 'haversine'))
    print(astar(data, start_stop, end_stop, passenger_arrival_time, 't','manhattan'))
    print(astar(data, start_stop, end_stop, passenger_arrival_time, 't','euclidean'))
    print(astar(data, start_stop, end_stop, passenger_arrival_time, 't','cosine'))
    print(astar(data, start_stop, end_stop, passenger_arrival_time, 't','chebyshev'))

    print(astar(data, start_stop1, end_stop1, passenger_arrival_time, 't', 'haversine'))
    print(astar(data, start_stop1, end_stop1, passenger_arrival_time, 't','manhattan'))
    print(astar(data, start_stop1, end_stop1, passenger_arrival_time, 't','euclidean'))
    print(astar(data, start_stop1, end_stop1, passenger_arrival_time, 't','cosine'))
    print(astar(data, start_stop1, end_stop1, passenger_arrival_time, 't','chebyshev'))

    print(astar(data, start_stop2, end_stop2, passenger_arrival_time, 't', 'haversine'))
    print(astar(data, start_stop2, end_stop2, passenger_arrival_time, 't','manhattan'))
    print(astar(data, start_stop2, end_stop2, passenger_arrival_time, 't','euclidean'))
    print(astar(data, start_stop2, end_stop2, passenger_arrival_time, 't','cosine'))
    print(astar(data, start_stop2, end_stop2, passenger_arrival_time, 't','chebyshev'))





    print(astar(data, start_stop, end_stop, passenger_arrival_time, 'p', 'cosine'))
    print(dijkstra(data, start_stop, end_stop, passenger_arrival_time))




def add_missing_stops(data: DataFrame, graph: DataFrame):
    unique_end_stops = data[constants.END_STOP].unique()
    for stop in unique_end_stops:
        if stop not in graph:
            graph[stop] = []



def get_stop_cords(data):
    distinct_cords: DataFrame = \
        data[[constants.START_STOP, constants.START_STOP_LAT, constants.START_STOP_LON]].drop_duplicates()

    stop_cords = distinct_cords.groupby(constants.START_STOP) \
        .agg({constants.START_STOP_LAT: 'mean', constants.START_STOP_LON: 'mean'}) \
        .rename(columns={constants.START_STOP: STOP, constants.START_STOP_LAT: STOP_LAT, constants.START_STOP_LON: STOP_LON})

    return stop_cords.to_dict('index')





def print_result(cost, path, comp_time):
    pprint.pprint(path)
    sys.stderr.write(f"Cost function value: {cost}\n")
    sys.stderr.write(f"Computation time: {comp_time}\n")
    sys.stderr.write(f"Total time: {comp_time + data_read_time}\n")


if __name__ == '__main__':
    main()
