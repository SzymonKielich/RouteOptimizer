
TRANSPORT_AVG_SPEED = (17.7 + 22.8)/2 # km/h
EARTH_AVG_RADIUS = 6371 # km

STOP = 'stop'
STOP_LAT = 'stop_lat'
STOP_LON = 'stop_lon'


LINE = 'line'
START_STOP = 'start_stop'
START_STOP_LAT = 'start_stop_lat'
START_STOP_LON = 'start_stop_lon'
END_STOP = 'end_stop'
END_STOP_LAT = 'end_stop_lat'
END_STOP_LON = 'end_stop_lon'
DEPARTURE_TIME = 'departure_time'
ARRIVAL_TIME = 'arrival_time'
TRAVEL_TIME = 'travel_time'

use_cols = [
    LINE,
    DEPARTURE_TIME,
    ARRIVAL_TIME,
    START_STOP,
    END_STOP,
    START_STOP_LAT,
    START_STOP_LON,
    END_STOP_LAT,
    END_STOP_LON
]

csv_types = {
    LINE: str,
    START_STOP: str,
    END_STOP: str,
    START_STOP_LAT: float,
    START_STOP_LON: float,
    END_STOP_LAT: float,
    END_STOP_LON: float
}
