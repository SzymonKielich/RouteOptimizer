import logging
import os
from typing import Union

import pandas as pd

from constants import use_cols, csv_types, TRAVEL_TIME, ARRIVAL_TIME, DEPARTURE_TIME

logging.basicConfig(level=logging.INFO)




def time_str_to_int(time_str: str) -> int:
    result = int(time_str[:2]) * 60 + int(time_str[3:5])
    if result >= 24 * 60:
        result -= 24 * 60
    return result


def time_int_to_str(time_int: int) -> str:
    hour = time_int // 60
    if hour >= 24:
        days = hour // 24
        hour -= days * 24
    minute = time_int % 60
    return f"{hour:02d}:{minute:02d}:00"


def read_data(file_path: str) -> Union[pd.DataFrame, None]:
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist.")
        return None

    try:
        df = pd.read_csv(
            file_path,
            converters={'departure_time': time_str_to_int, 'arrival_time': time_str_to_int},
            usecols=use_cols,
            dtype=csv_types
        )
        df[TRAVEL_TIME] = df[ARRIVAL_TIME] - df[DEPARTURE_TIME]
        # print("aaaaaaaaaaa",df.loc[df[TRAVEL_TIME] < 0][reader.DEPARTURE_TIME])
        df.loc[df[TRAVEL_TIME] < 0, TRAVEL_TIME] += 24 * 60
        return df
    except Exception as e:
        logging.error(f"Error reading data from {file_path}: {e}")
        return None


if __name__ == '__main__':
    df = read_data('connection_graph.csv')


