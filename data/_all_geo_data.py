import os
import pathlib
import re
from typing import Tuple

import pandas as pd
import geopandas as gpd
import numpy as np
import streamlit as st
import folium


# @st.cache(persist=True)
def _get_geojson_modification(list_path_data: list, index_for_data):
    temp_geo_data = "./admin_level_6.geojson" if os.path.exists(
        "./admin_level_6.geojson") else "../admin_level_6.geojson"
    temp_geo_data = gpd.read_file(temp_geo_data, encoding="utf-8")
    geo_data = folium.GeoJson(data=temp_geo_data).data
    del temp_geo_data
    path_data = './Данные csv/' if os.path.exists('./Данные csv/') else '../Данные csv/'
    # index_for_data = 'Городские округа:'
    # list_path_data = [i for i in get_all_data(path_data)]
    list_data = [i.name[:-4] for i in list_path_data]
    years = np.array(pd.read_csv(f'{list_path_data[6]}').set_index(index_for_data).columns.tolist(),
                     dtype=np.str_)

    for n, name in enumerate(list_data):
        for s in geo_data['features']:
            s['properties'][name] = {
                i: pd.read_csv(f'{list_path_data[n]}').set_index(index_for_data).astype('str').replace(r"[^-\d]+",
                                                                                                       "0",
                                                                                                       regex=True).loc[
                    s['properties']['name'], i] for i in
                years}

    del years, list_path_data, index_for_data, path_data
    return geo_data, list_data


def _get_all_melt(*, list_path_data: list, var_name: str = None, value_name: str = None,
                  gen_type: str = None, index_for_data) -> pd.DataFrame:
    path_data = './Данные csv/' if os.path.exists('./Данные csv/') else '../Данные csv/'
    #index_for_data = 'Городские округа:'
    # list_path_data = tuple(sorted([i for i in get_all_data(path_data)]))
    list_data = tuple([i.name[:-4] for i in list_path_data])
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
            get_data = pd.melt \
                    (
                    (pd.read_csv(f'{list_path_data[n]}')),
                    id_vars=index_for_data,#'Городские округа:',
                    var_name=var_name,
                    value_name=value_name,
                    value_vars=years
                )
            get_data[value_name] = get_data[value_name].replace(r"[\D]", "0", regex=True).astype(np.int32)
            yield get_data
    elif gen_type == "names":
        for name in list_data:
            yield name


def _display_fraud_facts(df: pd.DataFrame, year, metric_title, index_for_data, var: str = None, state_name=None, minikey=None):
    from data._globals import global_names
    #all_states = global_names['all_states']

    if not var:
        var: str = 'Динамика'

    kpnm = df[(df['Год'] == year)]
    kpnm['Динамика'] = kpnm['Динамика'].replace(r"[\D]", "0", regex=True).astype(np.int32)

    if state_name != global_names['all_states']:
        kpnm = kpnm[kpnm[index_for_data] == state_name]  #В kpnm[index_for_data] раньше столо "Городские округа:"

    # print(metric_title, '{:,}'.format(kpnm[var].sum()))

    a = re.match(r"Средне", minikey)
    if a:
        st.metric(metric_title, '{:,}'.format(round(kpnm[var].sum() / len(kpnm[index_for_data]))))
    else:
        st.metric(metric_title, '{:,}'.format(kpnm[var].sum()))


def get_all_data(path, suffix):
    if not suffix:
        suffix = '*.csv'

    dir = pathlib.Path(path).rglob(suffix)
    for fole in dir:
        yield fole


class StripChars:
    def __init__(self, chars):
        self.__chars = chars

    def __call__(self, *args, **kwargs):
        if not isinstance(args[0], str):
            raise TypeError('Аргумент должен быть строкой')

        return args[0].strip(self.__chars)

# def test_time(func):
#     import time
#
#     def wrapper(*args, **kwargs):
#         st = time.time()
#         res = func(*args, **kwargs)
#         et = time.time()
#         dt = et-st
#         print(f"Время работы программы: {dt}")
#         return res
#
#     return wrapper
#
# data = [i for i in _get_all_melt(gen_type='data')]
# name_files = [i for i in _get_all_melt(gen_type='names')]
# display_facts = test_time(_display_fraud_facts)
# res = display_facts(data[2], '2022', "Жопа")
# #print(res)
