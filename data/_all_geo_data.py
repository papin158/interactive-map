import os
from typing import Tuple

import pandas as pd
import geopandas as gpd
import numpy as np
import streamlit as st
import folium


@st.cache(persist=True)
def _get_geojson_modification() -> Tuple[gpd.GeoDataFrame, list]:
    temp_geo_data = "./admin_level_6.geojson" if os.path.exists(
        "./admin_level_6.geojson") else "../admin_level_6.geojson"
    temp_geo_data = gpd.read_file(temp_geo_data, encoding="utf-8")
    geo_data = folium.GeoJson(data=temp_geo_data).data
    del temp_geo_data
    path_data = './Данные csv' if os.path.exists('./Данные csv') else '../Данные csv'
    index_for_data = 'Городские округа:'
    list_data = os.listdir(path=path_data)
    years = np.array(pd.read_csv(f'{path_data}/{list_data[0]}').set_index(index_for_data).columns.tolist(),
                     dtype=np.str_)

    new_list_data = [name[:-4] for name in list_data]
    for name in list_data:
        for s in geo_data['features']:
            s['properties'][name[:-4]] = {
                i: pd.read_csv(f'{path_data}/{name}').set_index(index_for_data).astype('str').replace(r"[^-\d]", "0", regex=True).loc[
                    s['properties']['name'], i] for i in
                years}
    del years, list_data, index_for_data, path_data
    return geo_data, new_list_data


def _get_all_melt(*, var_name: str = None, value_name: str = None, gen_type: str = None) -> pd.DataFrame:
    path_data = './Данные csv' if os.path.exists('./Данные csv') else '../Данные csv'
    index_for_data = 'Городские округа:'
    list_data = tuple(sorted(os.listdir(path=path_data)))
    years = np.array(pd.read_csv(f'{path_data}/{list_data[0]}').set_index(index_for_data).columns.tolist(),
                     dtype=np.str_)
    if not gen_type:
        gen_type = "data"
    if not value_name:
        value_name = "Динамика"
    if not var_name:
        var_name = 'Год'

    if gen_type == "data":
        for name in list_data:
            get_data = pd.melt\
            (
                (pd.read_csv(f'{path_data}/{name}')),
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


def _display_fraud_facts(df: pd.DataFrame, year, metric_title, var: str = None, state_name=None, minikey=None):
    if not var:
        var: str = 'Динамика'

    kpnm = df[(df['Год'] == year)]
    kpnm['Динамика'] = kpnm['Динамика'].replace(r"[\D]", "0", regex=True).astype(np.int32)

    if state_name != "Все":
        kpnm = kpnm[kpnm['Городские округа:'] == state_name]

    # print(metric_title, '{:,}'.format(kpnm[var].sum()))
    import re
    a = re.match(r"Средне", minikey)
    if a:
        st.metric(metric_title, '{:,}'.format(round(kpnm[var].sum()/len(kpnm['Городские округа:']))))
    else:
        st.metric(metric_title, '{:,}'.format(kpnm[var].sum()))

# import time
#
# start = time.time()
# data = [i for i in _get_all_melt(gen_type='data')]
# name_files = [i for i in _get_all_melt(gen_type='names')]
# #print(data[2])
# _display_fraud_facts(data[2], '2022', "Жопа")
# end = time.time()
# total = end - start
# print(total)
