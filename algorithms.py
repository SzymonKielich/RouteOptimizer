import sys
import heapq
import math
from collections import namedtuple
from pprint import pprint

from pandas import DataFrame
import time

import reader
import constants as const
from reader import time_int_to_str


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])  # stopnie dziesietne na radiany
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    result = (pow(math.sin(d_lat / 2), 2) + pow(math.sin(d_lon / 2), 2) * math.cos(lat1) * math.cos(lat2))
    result = 2 * const.EARTH_AVG_RADIUS * math.asin(math.sqrt(result))  # kilometers
    return result   # kilometers


def manhattan_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])  # wspolrzedne na radiany

    return const.EARTH_AVG_RADIUS * (abs(lat1 - lat2) + abs(lon1 - lon2))


def euclidean_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])  # wspolrzedne na radiany

    return const.EARTH_AVG_RADIUS * math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


# def unidimensional_distance(lat1, lon1, lat2, lon2):
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])  # wspolrzedne na radiany
#
#     return const.EARTH_AVG_RADIUS * max(abs(lat1 - lat2), abs(lon1 - lon2))


def cosine_distance(lat1, lon1, lat2, lon2):
    dot_product = lat1 * lat2 + lon1 * lon2
    magnitude_a = math.sqrt(lat1 ** 2 + lon1 ** 2)
    magnitude_b = math.sqrt(lat2 ** 2 + lon2 ** 2)
    return 1 - (dot_product / (magnitude_a * magnitude_b))


def chebyshev_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])  # wspolrzedne na radiany

    return const.EARTH_AVG_RADIUS * max(abs(lat1 - lat2), abs(lon1 - lon2))


def dijkstra(data: DataFrame, start_stop: str, end_stop: str, passenger_arrival_time: int):
    print("Dijkstra:")
    selected_cols = [const.END_STOP, const.LINE, const.DEPARTURE_TIME, const.ARRIVAL_TIME, const.TRAVEL_TIME]
    graph: DataFrame = data.groupby(const.START_STOP)[selected_cols].apply(lambda df: df.values)
    add_missing_stops(data, graph)
    # pprint(graph[start_stop])
    start_time = time.time()
    # queue: (cost, stop, prev_stop, line, arrival_time, departure_time)
    queue = [(0, start_stop, None, None, passenger_arrival_time, None)]
    heapq.heapify(queue)

    prev_stops = {start_stop: (None, None, None, passenger_arrival_time)}
    costs = {start_stop: 0}

    while queue:
        (cost, stop, prev_stop, prev_line, arrival_time, departure_time) = heapq.heappop(queue)

        if stop == end_stop:
            return get_result(prev_stops, end_stop, cost, passenger_arrival_time,
                              't'), time.time() - start_time  # kompilacja

        # print(queue)

        for next_stop, line, next_departure_time, next_arrival_time, travel_time in graph[stop]:
            await_time = next_departure_time - arrival_time
            # nie zdążymy się przesiasc/pierwsza/jedziemy tym samym
            # if (await_time == 0 and prev_line is not None and prev_line != line) or (await_time < 0):

            if (await_time == 0 and prev_line is not None and prev_line != line) or (await_time < 0):
                await_time += 24 * 60

            new_cost = cost + await_time + travel_time

            if next_stop not in costs or new_cost < costs[next_stop]:
                costs[next_stop] = new_cost
                prev_stops[next_stop] = (stop, line, next_departure_time, next_arrival_time)
                heapq.heappush(queue, (new_cost, next_stop, stop, line, next_arrival_time, next_departure_time))

    return sys.maxsize, []


def add_missing_stops(data: DataFrame, graph: DataFrame):
    unique_end_stops = data[const.END_STOP].unique()
    for stop in unique_end_stops:
        if stop not in graph:
            graph[stop] = []


def astar(data: DataFrame, start_stop: str, end_stop: str, passenger_arrival_time: int, param, heur):
    selected_cols = [const.END_STOP, const.LINE, const.DEPARTURE_TIME, const.ARRIVAL_TIME, const.TRAVEL_TIME,
                     const.END_STOP_LAT, const.END_STOP_LON]
    graph: DataFrame = data.groupby(const.START_STOP)[selected_cols].apply(lambda df: df.values)
    add_missing_stops(data, graph)

    end_stop_cords = get_stop_cords(data)[end_stop]

    print("A* kryterium czasowe z algorytmem: " + heur) if param == 't' else print("A* kryterium przesiadek")
    start_time = time.time()
    end_stop_lat, end_stop_lon = end_stop_cords['stop_lat'], end_stop_cords['stop_lon']
    # queue: (f_score, g_score, stop, prev_stop, line, arrival_time, departure_time)
    queue = [(0, 0, start_stop, None, None, passenger_arrival_time, None)]
    heapq.heapify(queue)

    prev_stops = {start_stop: (None, None, None, passenger_arrival_time)}
    costs = {start_stop: 0}

    time_penalty = 0 if param == 't' else 30

    while queue:
        (_, g_score, stop, prev_stop, prev_line, arrival_time, departure_time) = heapq.heappop(queue)

        if stop == end_stop:
            return get_result(prev_stops, end_stop, g_score, passenger_arrival_time,
                              param), time.time() - start_time  # czas kompilacji

        for next_stop, line, next_departure_time, next_arrival_time, travel_time, stop_lat, stop_lon in graph[stop]:
            await_time = next_departure_time - arrival_time
            if (await_time == 0 and prev_line is not None and prev_line != line) or (await_time < 0):
                await_time += 24 * 60
            new_g_score = g_score + await_time + travel_time
            # h_score = round(haversine(stop_lat, stop_lon, end_stop_lat, end_stop_lon) / const.TRANSPORT_AVG_SPEED * 60)
            if heur == "haversine":
                h_score = round(haversine(stop_lat, stop_lon, end_stop_lat, end_stop_lon)/ const.TRANSPORT_AVG_SPEED * 60)
            elif heur == "manhattan":
                h_score = round(manhattan_distance(stop_lat, stop_lon, end_stop_lat, end_stop_lon)/ const.TRANSPORT_AVG_SPEED * 60)
            elif heur == "euclidean":
                h_score = round(euclidean_distance(stop_lat, stop_lon, end_stop_lat, end_stop_lon)/ const.TRANSPORT_AVG_SPEED * 60)
            elif heur == "cosine":
                h_score = round(cosine_distance(stop_lat, stop_lon, end_stop_lat, end_stop_lon)/ const.TRANSPORT_AVG_SPEED * 60)
            else:
                h_score = round(chebyshev_distance(stop_lat, stop_lon, end_stop_lat, end_stop_lon)/ const.TRANSPORT_AVG_SPEED * 60)
            h_score = h_score
            # print(h_score)

            if param == 'p':
                new_g_score += time_penalty if prev_line is not None and line != prev_line else 0
            f_score = new_g_score + h_score

            if next_stop not in costs or new_g_score < costs[next_stop]:
                costs[next_stop] = new_g_score
                prev_stops[next_stop] = (stop, line, next_departure_time, next_arrival_time)
                heapq.heappush(queue,
                               (f_score, new_g_score, next_stop, stop, line, next_arrival_time, next_departure_time))
    return sys.maxsize, []


def calculate_cost(start_stop, solution, stops_cords):
    solution = [start_stop] + solution + [start_stop]
    cost = 0
    if len(solution) == 2:
        return cost
    for i in range(len(solution) - 1):
        stop1, stop2 = solution[i], solution[i + 1]
        stop1_lat, stop1_lon = stops_cords[stop1]['stop_lat'], stops_cords[stop1]['stop_lon']
        stop2_lat, stop2_lon = stops_cords[stop2]['stop_lat'], stops_cords[stop2]['stop_lon']
        cost += round(haversine(stop1_lat, stop1_lon, stop2_lat, stop2_lon) / const.TRANSPORT_AVG_SPEED * 60)
    return cost


def get_result(prev_stops, end_stop: str, cost: int, passenger_arrival_time: int, param):
    path = build_path(prev_stops, end_stop)
    return calculate_cost_and_format_result(path, cost, passenger_arrival_time, param)


def build_path(prev_stops, end_stop):
    path = []
    stop = end_stop
    while stop is not None:
        prev_stop, line, departure_time, arrival_time = prev_stops[stop]
        path.append(Transport(line=line, start_stop=prev_stop, departure_time=departure_time, end_stop=stop,
                              arrival_time=arrival_time))
        stop = prev_stop
    return path[:-1][::-1]


Transport = namedtuple('Transport', ['line', 'start_stop', 'departure_time', 'end_stop', 'arrival_time'])


def calculate_cost_and_format_result(path, cost, passenger_arrival_time, param):
    if not path:
        return 0, []
    result = []
    cur_line = None
    for segment in path:
        if segment.line != cur_line:
            result.append(Transport(segment.line, segment.start_stop, time_int_to_str(segment.departure_time),
                                    segment.end_stop, time_int_to_str(segment.arrival_time)))
            cur_line = segment.line
        else:
            result[-1] = Transport(result[-1].line, result[-1].start_stop, result[-1].departure_time, segment.end_stop,
                                   time_int_to_str(segment.arrival_time))

    if param == 't':
        cost -= path[0].departure_time - passenger_arrival_time
        if path[0].departure_time < passenger_arrival_time:
            cost -= 24 * 60
    else:
        cost = len(result) - 1
    return cost, result


def get_stop_cords(data):
    distinct_cords: DataFrame = \
        data[[const.START_STOP, const.START_STOP_LAT, const.START_STOP_LON]].drop_duplicates()
    stop_cords = distinct_cords.groupby(const.START_STOP) \
        .agg({const.START_STOP_LAT: 'mean', const.START_STOP_LON: 'mean'}) \
        .rename(columns={const.START_STOP: const.STOP, const.START_STOP_LAT: const.STOP_LAT,
                         const.START_STOP_LON: const.STOP_LON})

    return stop_cords.to_dict('index')


if __name__ == '__main__':
    # Szczepin - Inowrocławska
    lat1, lat2, lon1, lon2 = 51.11558686, 51.11709441, 17.01396139, 17.0079669
    print("Haversine:", haversine(lat1, lon1, lat2, lon2))
    print("Manhattan Distance:", manhattan_distance(lat1, lon1, lat2, lon2))
    print("Euclidean Distance:", euclidean_distance(lat1, lon1, lat2, lon2))
    # print("Towncenter Distance:", towncenter_distance(lat1, lon1, lat2, lon2))
    # print("Unidimensional Distance:", unidimensional_distance(lat1, lon1, lat2, lon2))
    print("Cosine Distance:", cosine_distance(lat1, lon1, lat2, lon2))
    print("Chebyshev Distance:", chebyshev_distance(lat1, lon1, lat2, lon2))

    # lat1, lat2, lon1, lon2 = 51.09381561, 51.09358878, 16.98037615, 17.00993331
    # print(haversine(lat1, lon1, lat2, lon2))
    # lat1, lat2, lon1, lon2 = 51.09381561, 51.09358878, 16.98037615, 17.00963331
    # print(haversine(lat1, lon1, lat2, lon2))
