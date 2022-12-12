import asyncio

import branca
import folium
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt
import json

import matplotlib

from folium.plugins import MousePosition, DualMap
# Import folium DivIcon plugin
from folium.features import DivIcon, GeoJsonTooltip, GeoJsonPopup


@st.cache
def init_json_kld():
    geojson_kld_sub = gpd.read_file(r"./admin_level_6.geojson", encoding="utf8")
    geojson_kld_sub = geojson_kld_sub.loc[geojson_kld_sub['addr:region'] == "Калининградская область"]
    return geojson_kld_sub


@st.cache(allow_output_mutation=True)
def init_data_kld():
    data_kld = pd.read_csv('./январь_2021_г_,_23110000100030200002_Численность_постоянного_населения_на_1_января.csv',
                           encoding='cp1251')
    data_kld = data_kld.loc[data_kld['Городские округа:'] != 'Заглушка']
    return data_kld


@st.cache(allow_output_mutation=True)
def init_natural_move():
    data_kld = pd.read_csv('./Данные csv/КалининградСтат - Данные - Естест. движение насел.csv')

    return data_kld


@st.cache(allow_output_mutation=True)
def init_migratory_movement():
    data = pd.read_csv('./Данные csv/КалининградСтат - Данные - Миграционное движение.csv')

    return data


async def get_my_dict_string(feature):
    v1 = feature["properties"]['name']

    bra = init_natural_move().set_index('Городские округа:').columns.tolist()
    var_name = 'Год'.encode('utf8').decode('utf8')
    value_name = 'Динамика'.encode('utf8').decode('utf8')
    data_loc = pd.melt(init_natural_move(), id_vars='Городские округа:', var_name=var_name, value_name=value_name, value_vars=bra)
    for i in data_loc['Городские округа:']:
        data_loc = data_loc.loc[data_loc['Городские округа:'] == f'{v1}']

    chart = alt.Chart(data_loc).mark_line().encode(
        x=var_name,
        y=value_name,
        # color='Городские округа:'
    )

    char2 = json.loads(chart.to_json(indent=None))
    # popup = folium.Popup(max_width=300, html="Пидорас")
    # ka = folium.features.VegaLite(char2, height=300, width=300).add_to(popup)

    feature = feature["properties"]['Ест_движ_нас']
    my_td = '''<!DOCTYPE html><html><head>
    <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
    </head>'''
    my_td += f'''<Body style="background-color:white;width: 302px">
     <h3 style="color:rgb(236, 77, 77);background-color: oldlace;bottom:0px;padding-bottom:0px;margin-bottom: 0px; margin-top: 5px; margin-left:2px;width: 298px;">Естесственное </br> движение населения</h1>
     <table style="margin-left:0px;">
        <tbody>
             <tr><td style= background-color:oldlace;width:100px> <span style= columns:#343434;3434>Городской округ:</span> </td>
                <td style= background-color:oldlace;width:200px> <span style= color:#343434> {v1}</span> </tr>
        '''
    for i in feature:
        my_td += f'''<tr><td style= background-color:oldlace;width:100px> <span style= columns:#343434;3434>{i} г.:</span> </td>
                <td style= background-color:oldlace;width:200px> <span style= color:#343434> {f'Прибыло {feature[i]} человек' if int(feature[i]) >= 0 else f'Покинуло {abs(int(feature[i]))} человек'}</span> </tr>'''

    my_td += f'''</tbody></table>'''

    my_td += '''
    <div id="vis1"></div>
    <script type="text/javascript">
        vegaEmbed('#vis1', {spec1}).catch(console.error);
    </script>'''

    my_td += f'''</Body>'''

    with open('charts.html', 'w') as f:
        f.write(my_td.format(
            vega_version=alt.VEGA_VERSION,
            vegalite_version=alt.VEGALITE_VERSION,
            vegaembed_version=alt.VEGAEMBED_VERSION,
            spec1=char2
        ))

    return my_td


def style_function_suburb(feature):
    k1 = feature["properties"]['Ест_движ_нас']

   # data_kld['%Населения'] = [round(i * 100 / max(data_kld['Население']), 4) for i in data_kld['Население']]

    if int(k1['2020']) < -100:
        return '#ffffff'
    elif int(k1['2020']) < 0:
        return '#0000ff'
    elif 0 < int(k1['2020']) < 100:
        return '#edcf64'
    elif int(k1['2020']) > 100:
        return '#be2a3e'

async def main():
    geojson_kld_sub = init_json_kld()

    data_kld = init_data_kld()
    data_kld['%Населения'] = [round(i * 100 / max(data_kld['Население']), 4) for i in data_kld['Население']]
    data_kld['Население'] = [np.float_(i) for i in data_kld['Население']]
    data_kld_ind = data_kld.set_index('Городские округа:')

    kld_people_natural_moving = init_natural_move()
    kld_people_natural_moving_ind = kld_people_natural_moving.set_index('Городские округа:')

    kld_people_natural_moving_ind = kld_people_natural_moving_ind.astype('str')
    bra = kld_people_natural_moving_ind.columns.tolist()
    bra.sort(reverse=True)

    var_name = 'Год'.encode('utf8').decode('utf8')
    value_name = 'Динамика'.encode('utf8').decode('utf8')
    data_loc = pd.melt(init_natural_move(), id_vars='Городские округа:', var_name=var_name, value_name=value_name,
                       value_vars=bra)

    for i in data_loc['Городские округа:']:
        data_loc = data_loc.loc[data_loc['Городские округа:'] == 'Гурьевский']

    matplotlib.pyplot.legend()
    white_tile = branca.utilities.image_to_url([[1, 1], [1, 1]])

    # , tiles = 'Stamen Terrain'
    Kaliningrad_map = folium.Map(
        location=[54.709300, 20.5082600],
        zoom_start=9,
        maxBounds=[[53.3, 19.4], [56.40, 22.9]],
        tiles=white_tile,
        attr='white tile',
        # overlay=True,
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

    ################################################################
    ################################################################
    ################################################################
    ################################################################
    # file_path = r"./admin_level_6.geojson"
    # suburbs_json = json.load(open(file_path, "r"))
    # suburbs_id_map = {}
    # for feature in suburbs_json["features"]:
    #     feature["id"] = feature["properties"]["STATE_CODE"]
    #     suburbs_id_map[feature["properties"]["STATE_NAME"]] = feature["id"]

    Kaliningrad_map.add_child(mouse_position)
    # geojson_kld = geojson.loc[geojson['ref'] == 'RU-KGD']
    # geojson_kld_mun = geojson_kld_sub.loc[geojson_kld_sub['source'] == "СTП Калининградской области"]

    myscale = (data_kld['%Населения'].quantile((0.0, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.89, 0.98, 1.0))).tolist()

    coropleth = folium.Choropleth(
        geo_data=geojson_kld_sub,
        name="Население",
        data=data_kld,
        columns=['Городские округа:', '%Населения'],
        key_on='properties.name',
        nan_fill_color='darkblue',
        nan_fill_opacity=0.3,
        threshold_scale=myscale,
        bins=3,
        fill_color='PuBuGn',  # 'YlGn',
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name='Население',
        smooth_factor=0,
        highlight=True
    ).add_to(Kaliningrad_map)

    for key in coropleth._children:
        if key.startswith('color_map'):
            del (coropleth._children[key])

    for s in coropleth.geojson.data['features']:
        s['properties']['population'] = data_kld_ind.loc[s['properties']['name'], 'Население']

    # myscale = (kld_people_natural_moving['2012'].quantile((0.0, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.89, 0.98, 1.0))).tolist()

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
        highlight=False,
        overlay=False,
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
        style="background-color: yellow;",

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
            'fillColor': '#ffff00',
            'fillOpacity': .3,
            'color': 'black',
            'clickable': True,
            'weight': 0.7,
            # 'dashArray': '5, 5'
        },
        highlight_function=lambda feature: {  # Меняет цветовую схему при наведении
            'fillColor': '#0a085f',
            'fillOpacity': .4,
            'color': 'black',
            'clickable': True,
            'weight': 0.7,
            'dashArray': '3, 6'
        },
        tooltip=tooltip,
        popup=popup)  # .add_to(coropleth.geojson)

    (coropleth.geojson).add_child(population_kld)


    fg1 = folium.FeatureGroup(name="Естественное движение населения")
    gdf_temp = gmc = folium.GeoJson(data=people_natural_moving.geojson.data)
    for feature in gdf_temp.data['features']:
        await get_my_dict_string(feature)

        html_file = open('charts.html', 'r', encoding='cp1251')
        charts_code = html_file.read()
        iframe = folium.IFrame(html=charts_code, width=333, height=611)
        gmc = folium.GeoJson(feature,
                             style_function=lambda feature: {  # Меняет цветовую схему в статичном режиме
                                 'fillColor': style_function_suburb(feature),
                                 'fillOpacity': .3,
                                 'color': 'black',
                                 'clickable': True,
                                 'weight': 0.7,
                                 # 'dashArray': '5, 5'
                             },
                             highlight_function=lambda feature: {  # Меняет цветовую схему при наведении
                                 'fillColor': '#0a085f',
                                 'fillOpacity': .4,
                                 'color': 'black',
                                 'clickable': True,
                                 'weight': 0.7,
                                 'dashArray': '3, 6'
                             }
                             )
        # pg = folium.Html(await get_my_dict_string(feature), script=True)  # create HTML
        # pup1 = folium.Popup(html=pg).add_to(gmc)
        pup1 = folium.Popup(html=iframe).add_to(gmc)
        tol1 = folium.Tooltip(await get_my_dict_string(feature)).add_to(gmc)

        gmc.add_to(fg1)
    Kaliningrad_map.add_child(fg1)

    folium.TileLayer("openstreetmap").add_to(Kaliningrad_map)
    folium.TileLayer("cartodbpositron", overlay=True, name="Viw in Light Mode").add_to(Kaliningrad_map)
    folium.LayerControl().add_to(Kaliningrad_map)

    st_map = st_folium(Kaliningrad_map, width=1750, height=1200)

    kda = data_kld.plot.barh(y='Население')

    st.bar_chart(data_kld, y='Население', x='Городские округа:')

    # st.area_chart(kld_people_natural_moving, x='Городские округа:')

    # p = figure(
    #     title='Город',
    #     x_axis_label='Год',
    #     y_axis_label='Изменения')
    #
    # p.line(data_loc['variable'], data_loc['value'], legend_label='Trend', line_width=1)
    #
    #
    #
    # st.bokeh_chart(p, use_container_width=True)

    st.write(data_kld)


if __name__ == '__main__':
    asyncio.run(main())
