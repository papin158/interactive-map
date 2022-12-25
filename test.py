import os
import pathlib
import re
from typing import Tuple

import pandas as pd
import geopandas as gpd
import numpy as np
import streamlit as st
import folium


def super_time(func):
    import time

    def wrapper(*args, **kwargs):
        st = time.time()
        res = ''
        for _ in range(1000):
            res = func(*args, **kwargs)
        end = time.time()
        dt = end - st
        print(f"Время работы программы: {dt}")
        return res

    return wrapper


#@super_time
def get_derictories(path) -> dict:
    path = f'./{path}/'
    all_files = [i for i in os.listdir(path)]
    dirs = [i for i in all_files if os.path.isdir(f'{path}{i}')]
    other_files = {
        "Другое": [i[0:-4] for i in all_files if os.path.isfile(path=f'{path}{i}') and re.search(r".+\.csv$", i)]}

    directories = {i: [j[0:-4] for j in os.listdir(path=f'{path}{i}') if re.search(r"\w+\.csv$", j)] for i in dirs}

    if other_files['Другое']:
        directories |= other_files

    return directories


def _get_geojson_modification():
    temp_geo_data = "./admin_level_6.geojson" if os.path.exists(
        "./admin_level_6.geojson") else "../admin_level_6.geojson"
    temp_geo_data = gpd.read_file(temp_geo_data, encoding="utf-8")
    geo_data = folium.GeoJson(data=temp_geo_data).data
    del temp_geo_data
    path_data = './Данные csv/' if os.path.exists('./Данные csv/') else '../Данные csv/'
    index_for_data = 'Городские округа:'
    list_path_data = [i for i in get_all_data(path_data)]
    list_data = [i.name[:-4] for i in list_path_data]
    years = np.array(pd.read_csv(f'{list_path_data[6]}').set_index(index_for_data).columns.tolist(),
                     dtype=np.str_)

    for n, name in enumerate(list_data):
            for s in geo_data['features']:
                s['properties'][name] = {
                    i: pd.read_csv(f'{list_path_data[n]}').set_index(index_for_data).astype('str').replace(r"[^-\d]",
                                                                                                         "0",
                                                                                                         regex=True).loc[
                        s['properties']['name'], i] for i in
                    years}

    del years, list_path_data, index_for_data, path_data
    return geo_data, list_data


def _get_all_melt(*, var_name: str = None, value_name: str = None, gen_type: str = None) -> pd.DataFrame:
    path_data = './Данные csv/' if os.path.exists('./Данные csv/') else '../Данные csv/'
    index_for_data = 'Городские округа:'
    list_path_data = tuple(sorted([i for i in get_all_data(path_data)]))
    list_data = tuple([i.name for i in list_path_data])
    years = np.array(pd.read_csv(f'{list_path_data[0]}').set_index(index_for_data).columns.tolist(),
                     dtype=np.str_)
    if not gen_type:
        gen_type = "data"
    if not value_name:
        value_name = "Динамика"
    if not var_name:
        var_name = 'Год'

    if gen_type == "data":
        for n, name in enumerate(list_data):
            get_data = pd.melt\
            (
                (pd.read_csv(f'{list_path_data[n]}')),
                id_vars='Городские округа:',
                var_name=var_name,
                value_name=value_name,
                value_vars=years
            )
            get_data[value_name] = get_data[value_name].replace(r"[\D]", "0", regex=True).astype(np.int32)
            yield get_data
    elif gen_type == "names":
        for name in list_data:
            yield name[:-4]


def get_all_data(path, nameOnly=False):
    dir = pathlib.Path(path).rglob('*.csv')
    for fole in dir:
        yield fole


# print(list(get_all_data("./test_dir/")))
# a,b = _get_geojson_modification()
# print(a['features'][0]['properties'])