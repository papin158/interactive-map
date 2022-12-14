import asyncio
import branca
import folium
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt
import json
import collections
import colorsys

import matplotlib

from folium.plugins import MousePosition, DualMap
# Import folium DivIcon plugin
from folium.features import DivIcon, GeoJsonTooltip, GeoJsonPopup

st.set_page_config(page_title="Карта", layout="wide")

st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 12rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 12rem;}}
    </style>
''', unsafe_allow_html=True)


@st.cache
def init_json_kld():
    geojson_kld_sub = gpd.read_file(r"./admin_level_6.geojson", encoding="utf8")
    geojson_kld_sub = geojson_kld_sub.loc[geojson_kld_sub['addr:region'] == "Калининградская область"]
    return geojson_kld_sub


@st.cache(allow_output_mutation=True)
def init_data_kld():
    data_kld = pd.read_csv('./Данные csv/КалининградСтат - Данные - Численность населения.csv',
                           encoding='utf-8')
    bra = branch(df=data_kld)
    data_kld = pd.melt(data_kld, id_vars='Городские округа:', var_name='Год', value_name="Население",
                       value_vars=bra)
    data_kld_ind = data_kld.set_index('Городские округа:')
    return data_kld, data_kld_ind


@st.cache(allow_output_mutation=True)
def init_natural_move():
    kld_natural_move = pd.read_csv('./Данные csv/КалининградСтат - Данные - Естест. движение насел.csv')
    kld_natural_move_ind = (kld_natural_move.set_index('Городские округа:')).astype('str')

    return kld_natural_move, kld_natural_move_ind


@st.cache(allow_output_mutation=True)
def init_migratory_movement():
    data = pd.read_csv('./Данные csv/КалининградСтат - Данные - Миграционное движение.csv')

    return data


async def get_my_dict_string(feature, *, year: str = None):
    v1 = feature["properties"]['name']

    data_loc = data_locale()
    for _ in data_loc['Городские округа:']:
        data_loc = data_loc.loc[data_loc['Городские округа:'] == f'{v1}']

    feature = feature["properties"]['Ест_движ_нас']
    my_td = '''<!DOCTYPE html><html><head>
    <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
    </head>'''
    my_td += f'''<Body style="background-color:white;width: 302px">
     <h4 style="color:rgb(2, 0, 105);background-color: oldlace;bottom:0px; padding-bottom:0px;margin-bottom: 0px; margin-top: 5px; margin-left:2px;width: 298px;">Естесственное движение населения</h4>
     <table style="margin-left:0px;">
        <tbody>
             <tr><td style= background-color:oldlace;width:100px> <span style= columns:#343434;3434>Городской округ:</span> </td>
                <td style= background-color:oldlace;width:200px> <span style= color:#343434> {v1}</span> </tr>
        '''

    if year:
        my_td += f'''<tr><td style= background-color:oldlace;width:100px> <span style= columns:#343434;3434>{year} г.:</span> </td>
                <td style= background-color:oldlace;width:200px> <span style= color:#343434> {f'Прибыло {feature[year]} человек' if int(feature[year]) >= 0 else f'Покинуло {abs(int(feature[year]))} человек'}</span> </tr>'''

    my_td += f'''</tbody></table>'''

    my_td += f'''</Body>'''

    return my_td


def init_style(year):
    data = data_locale()
    data = data[(data['Год'] == year)]

    return data


def style_function_suburb(feature, year: str):
    k1 = feature["properties"]['Естест. движение насел']  # ['Ест_движ_нас']
    data = init_style(year)['Динамика']
    scale = (data.quantile((0.0, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.89, 0.98, 1.0))).tolist()
    for n, i in reversed(list(enumerate(scale))):
        blue = 183
        green = 86
        red = 24

        h, s, v = colorsys.rgb_to_hsv(red, green, blue)
        s -= n * 0.1
        red, green, blue = colorsys.hsv_to_rgb(h, s, v)

        if np.float_(k1[year]) >= scale[n]:
            return f'rgba({red},{green},{blue}, 0.9)'


def display_fraud_facts(df, year, state_name, metric_title, var):
    kpnm = df[(df['Год'] == year)]

    if state_name:
        kpnm = kpnm[kpnm['Городские округа:'] == state_name]

    st.metric(metric_title, '{:,}'.format(kpnm[var].sum()))


async def display_map(year, population_check: bool = True, moving_check: bool = False, migration_check: bool = False):
    geojson_kld_sub = init_json_kld()
    bra = branch()

    data_kld, data_kld_ind = init_data_kld()
    kld_people_natural_moving, ind = init_natural_move()
    kld_people_natural_moving_ind = kld_people_natural_moving.set_index('Городские округа:').astype('str')

    kld_people_natural_moving_ind = kld_people_natural_moving_ind.astype('str')

    # dynamic = kld_people_natural_moving.copy()._drop_axis(labels='Городские округа:', axis=1).astype(np.int64).sum(
    #     axis=1)

    # matplotlib.pyplot.legend()
    white_tile = branca.utilities.image_to_url([[1, 1], [1, 1]])

    # , tiles = 'Stamen Terrain'
    Kaliningrad_map = folium.Map(
        location=[54.709300, 20.5082600],
        zoom_start=9,
        maxBounds=[[54.3, 20.4], [55.40, 22.9]],
        tiles=white_tile,
        attr='white tile',
        zoom_control=False,
        png_enabled=True,
        control_scale=False,
        scrollWheelZoom=False,
        dragging=False,
        position='absolute'

    )

    formatter = "function(num) {return L.Util.formatNum(num, 5);};"
    mouse_position = MousePosition(
        position='topright',
        separator=' Long: ',
        empty_string='NaN',
        lng_first=False,
        num_digits=20,
        prefix='Lat:',
        lat_formatter=formatter,
        lng_formatter=formatter,
    )

    Kaliningrad_map.add_child(mouse_position)
    data_kld = data_kld[data_kld["Год"] == year]
    data_kld_ind = data_kld_ind[data_kld_ind["Год"] == year]
    data_kld_ind = data_kld_ind.astype('str')

    myscale = (data_kld['Население'].quantile((0.0, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.89, 0.98, 1.0))).tolist()

    coropleth = folium.Choropleth(
        geo_data=geojson_kld_sub,
        name="Население",
        data=data_kld,
        columns=['Городские округа:', 'Население'],
        key_on='properties.name',
        nan_fill_color='darkblue',
        nan_fill_opacity=0.3,
        threshold_scale=myscale,
        bins=3,
        # fill_color='BuPu',#'PuBuGn',  # 'YlGn',
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name='Население',
        smooth_factor=0,
        highlight=False,
        show=population_check
    ).add_to(Kaliningrad_map)

    for key in coropleth._children:
        if key.startswith('color_map'):
            del (coropleth._children[key])

    for s in coropleth.geojson.data['features']:
        s['properties']['population'] = data_kld_ind.loc[s['properties']['name'], 'Население']

    people_natural_moving = folium.Choropleth(
        geo_data=geojson_kld_sub,
        name="%Населения",
        data=kld_people_natural_moving,
        columns=['Городские округа:', '2012'],
        key_on='properties.name',
        nan_fill_color='darkblue',
        nan_fill_opacity=0.3,
        # threshold_scale=myscale,
        bins=3,
        fill_color='PuBuGn',  # 'YlGn',
        fill_opacity=0.7,
        line_opacity=0.4,
        # legend_name='%Населения',
        smooth_factor=0,
        highlight=True,
        overlay=True,
        show=False
    ).add_to(Kaliningrad_map)

    for key in people_natural_moving._children:
        if key.startswith('color_map'):
            del (people_natural_moving._children[key])

    for s in people_natural_moving.geojson.data['features']:
        s['properties']['Ест_движ_нас'] = {i: kld_people_natural_moving_ind.loc[s['properties']['name'], i] for i in
                                           bra}

    popup = GeoJsonPopup(  # Показывает информацию на карте при нажатии(выделении)
        fields=['name', 'population'],
        aliases=['Городской округ  ', "Население"],
        localize=True,
        labels=True,
        style="background-color: darkblue;",

    )

    tooltip = GeoJsonTooltip(  # Показывает информацию на карте при наведении
        fields=['name', 'population'],
        aliases=['Городской округ  ', "Население"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
                background-color: #F0EFEF;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
        max_width=800,
    )

    population_kld = folium.GeoJson(
        data=coropleth.geojson.data,

        style_function=lambda feature: {  # Меняет цветовую схему в статичном режиме
            'fillColor': '#1857de',  # '#ffff00',
            'fillOpacity': .3,
            'color': 'white',
            'clickable': True,
            'weight': 1.7,
            # 'dashArray': '5, 5'
        },
        highlight_function=lambda feature: {  # Меняет цветовую схему при наведении
            'fillColor': '#0a085f',
            'fillOpacity': 1.,
            'color': 'yellow',
            'clickable': True,
            'weight': 2.7,
            'dashArray': '3, 6'
        },
        tooltip=tooltip,
        popup=popup)  # .add_to(coropleth.geojson)
    cor = coropleth.geojson
    cor.add_child(population_kld)

    fg1 = folium.FeatureGroup(name="Естественное движение населения", show=moving_check)
    gdf_temp = folium.GeoJson(data=people_natural_moving.geojson.data)
    for feature in gdf_temp.data['features']:
        await get_my_dict_string(feature, year=year)

        gmc = folium.GeoJson(feature,
                             style_function=lambda feature: {  # Меняет цветовую схему в статичном режиме
                                 'fillColor': style_function_suburb(feature, year),
                                 'fillOpacity': 1,
                                 'color': 'white',
                                 'clickable': True,
                                 'weight': 1.7,
                                 # 'dashArray': '5, 5'
                             },
                             highlight_function=lambda feature: {  # Меняет цветовую схему при наведении
                                 'fillColor': '#0a085f',
                                 'fillOpacity': 1.,
                                 'color': 'yellow',
                                 'clickable': True,
                                 'weight': 2.7,
                                 'dashArray': '3, 6'
                             }
                             )
        # ca = folium.Marker(
        #     location=feature['geometry']['coordinates'][0][0][0]
        # )
        folium.Html(await get_my_dict_string(feature, year=year), script=True)  # pg; create HTML
        # pup1 = folium.Popup(html=pg).add_to(gmc)
        # pup1 = folium.Popup(html=iframe).add_to(gmc)
        folium.Tooltip(await get_my_dict_string(feature, year=year)).add_to(gmc)  # tol1;

        gmc.add_to(fg1)
    #  ca.add_to(fg1)
    Kaliningrad_map.add_child(fg1)

    folium.TileLayer("openstreetmap").add_to(Kaliningrad_map)
    folium.TileLayer("cartodbpositron", overlay=False, show=False, name="Viw in Light Mode").add_to(Kaliningrad_map)
    folium.TileLayer("cartodbdark_matter", overlay=False, show=True, name="View mapbox").add_to(Kaliningrad_map)
    folium.LayerControl().add_to(Kaliningrad_map)

    st_map = st_folium(Kaliningrad_map, width=1920, height=700)

    state_name = ''
    if st_map['last_active_drawing']:
        state_name = st_map['last_active_drawing']['properties']['name']

    return state_name


def data_locale(init=init_natural_move, var_name='Год', value_name="Динамика"):
    bra = branch(init)
    var_name = var_name.encode('utf8').decode('utf8')
    value_name = value_name.encode('utf8').decode('utf8')

    data = pd.melt(init()[0], id_vars='Городские округа:', var_name=var_name, value_name=value_name,
                   value_vars=bra)
    return data


@st.cache(allow_output_mutation=True)
def branch(init=init_natural_move, *, df=None):
    if df is not None:
        df = df.set_index('Городские округа:').columns.tolist()
        df.sort(reverse=True)
        return df
    bra = init()
    bra = bra[0].set_index('Городские округа:').columns.tolist()
    bra.sort(reverse=True)

    return bra


async def bar_chart(df: pd.DataFrame, dictionary: dict, state_name=None, x=None, y=None, year=None):
    dictionary = {e: k for e, k in enumerate(dictionary.values())}

    if state_name:
        df = df[df['Городские округа:'] == state_name]
    else:
        df = df[df['Год'] == year]

    if dictionary[0]:
        if state_name:
            fig = go.Figure()
            st.plotly_chart(px.funnel(data_frame=df, y=y, x=x))
            fig.add_trace(go.Scatter(x=df[x],
                                     y=df[y],
                                     mode='lines',
                                     # fill='toself',
                                     # fillcolor='#98FB98',  # '#42e360',
                                     # line_color='#98FB98',
                                     opacity=0.7,
                                     showlegend=True,
                                     # legendwidth=100,
                                     legendrank=10,
                                     name=f'Динамика изменения численности населения городского округа {state_name}'
                                     ))
            fig.update_layout(legend_orientation="h")
            st.plotly_chart(fig, use_container_width=True)
        else:
            df = df.sort_values(by=y)
            st.write("Население Калининградской области по округам")
            st.plotly_chart(px.funnel(data_frame=df, y='Городские округа:', x=y,
                                      orientation='h'))  # , values=y, names='Городские округа:', labels=x))

    # if dictionary[1]:
    #     if


def year_for_display():
    year = str(st.sidebar.slider("Год: ", min_value=int(min(branch())),
                                 max_value=int(max(branch())), value=int(max(branch())), step=1))
    return year


def display_region_filter(df: pd.DataFrame, state_name: str):
    state_list = [''] + list(df['Городские округа:'].unique())
    # state_list.sort()
    state_index = state_list.index(state_name) if state_name and state_name in state_list else 0
    return st.sidebar.selectbox(label='Выберите городской округ из списка', options=state_list, index=state_index)


def test(state_name: str, data_kld: pd.DataFrame) -> [str, bool]:
    if 'disabled_' not in st.session_state:
        st.session_state.disabled_ = True
        st.session_state.visibility = 'visible'
        st.session_state.disabled_1 = False
        st.session_state.disabled_2 = False

    var0 = st.sidebar.empty()
    ba = var0.write("Как выбрать муниципалитет")
    b = st.sidebar.columns(2, gap='small')
    with b[0]:
        var1 = st.empty()
    with b[1]:
        var2 = st.empty()

    bat = var1.checkbox("Кнопками", key='disabled_1', disabled=st.session_state.disabled_2)
    brat = var2.checkbox("Из списка", key='disabled_2', disabled=st.session_state.disabled_1)

    if bat or brat:
        if bat:
            data_kld = list(data_kld['Городские округа:'].unique())
            data_len = len(data_kld)

            max_columns = 3
            no = 0
            n = round(data_len / max_columns) + 1

            if data_len < max_columns:
                raise ValueError("Количество колонок превышает количество значений")

            a = st.sidebar.columns(max_columns, gap='small')
            for an in range(max_columns):
                with a[an]:
                    if n <= data_len:
                        for i in range(no, n):
                            if st.button(data_kld[i][0:4], key=f'{data_kld[i]}'):
                                state_name = data_kld[i]

                    no = n
                    n += round(data_len / max_columns)

            if st.sidebar.button("Калининградская область"):
                state_name = ''
            return state_name
        if brat:
            state_name = display_region_filter(state_name=state_name, df=data_kld)
            return state_name
    # if not ba:
    #     var1 = st.sidebar.empty()
    #     var2 = st.sidebar.empty()
    #     bat = var1.checkbox("Кнопками")
    #     brat = var2.checkbox("Из списка")
    #     if bat or brat:
    #         if brat:
    #
    #             st.sidebar.selectbox('Выберите город', ['1','2','3'])
    #         if bat:
    #             st.sidebar.button('12')
    #         var0.empty()
    #         var1.empty()
    #         var2.empty()


async def main():
    year = year_for_display()
    st.sidebar.write('Сортировать по')

    labels = {'Население': True, "Естественное движение населения": False}

    labels_keys = {e: i for e, i in enumerate(labels.keys())}
    radio = st.sidebar.radio('Фильтр', labels.keys(), key=1)
    for i in labels:
        if radio == i:
            labels[i] = True
        else:
            labels[i] = False

    data_kld = init_data_kld()[0]
    state_name = await display_map(year, population_check=labels['Население'],
                                   moving_check=labels["Естественное движение населения"])
    state_name = test(state_name, data_kld)
    # state_name = display_region_filter(state_name=state_name, df=data_kld)

    col1, col2, col3 = st.columns(3)
    with col1:

        if radio == labels_keys[0]:
            display_fraud_facts(data_kld, year, state_name, var='Население',
                                metric_title=f'''Население {f"городского округа {state_name} на {year} г."
                                if state_name else f"Калининградской области за {year} г."}'''
                                )

        if radio == labels_keys[1]:
            display_fraud_facts(data_locale(), year, state_name, var="Динамика",
                                metric_title=f'''Всё естественное движение в {f"городском округе {state_name}"
                                                                              f" на {year} г." if state_name else f"Калининградской области на {year} г."}
                                        '''
                                )
    with col2:
        pass

    await bar_chart(df=init_data_kld()[0].sort_values(by='Год'),
                    state_name=state_name, x='Год', y='Население', year=year, dictionary=labels)


async def test_display_map(year):
    kld_map = folium.Map(
        location=[54.709300, 20.5082600],
        zoom_start=9, )
    st_map = st_folium(kld_map)

    state_name = ''
    if st_map['last_active_drawing']:
        state_name = st_map['last_active_drawing']['properties']['name']

    return state_name


from loader import get_tooltip, get_geodata, get_melt, display_facts


async def test_main():
    # geodata, index_data = get_geodata()[0], get_geodata()[1]

    state_name = ''
    year = year_for_display()
    melt_data = [i for i in get_melt(gen_type='data')]
    dict_data = {i: False for i in get_melt(gen_type='names')}

    state_name = await test_display_map(year)
    state_name = test(state_name, melt_data[0])
    await radio_click(df=melt_data, dict_data=dict_data, year=year, state_name=state_name)
    await bar_chart(df=melt_data[0].sort_values(by='Год'),
                    state_name=state_name, x='Год', y='Население', year=year, dictionary=dict_data)


async def radio_click(df: pd.DataFrame, dict_data: dict, year: str, state_name: str):
    radio = st.sidebar.radio('Фильтр', dict_data.keys(), key=1)
    for i in dict_data:
        if radio == i:
            dict_data[i] = True
        else:
            dict_data[i] = False

    labels_keys = {e: i for e, i in enumerate(dict_data)}

    for e, i in enumerate(labels_keys):
        if radio == labels_keys[i]:
            display_facts(df=df[e], year=year, state_name=state_name, var='Динамика',
                          metric_title=f'''Население {f"городского округа {state_name} на {year} г."
                          if state_name else f"Калининградской области за {year} г."}'''
                          )

if __name__ == '__main__':
    asyncio.run(test_main())
