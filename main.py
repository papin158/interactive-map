import asyncio
from typing import List, Any

import folium
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from htbuilder import hr, styles
from htbuilder.units import percent, pxx

from loader import get_geodata, get_melt, display_facts, create_choropleth, get_mouse_position, footer, \
    get_radio_switch, get_path_data


async def bar_chart(df: List[pd.DataFrame], catalog: dict, state_name=None, x=None,
                    y=None, year=None, key=None, radio=None, ):
    old_catalog = [k for k in catalog]
    catalog = [k for k in catalog.values()]
    if catalog[key]:
        df = df[key].sort_values(by='Год', ascending=True)

        if state_name != "Все":
            df = df[df['Городские округа:'] == state_name]
        else:
            df = df[df['Год'] == year]

        st.markdown(f'{hr(style=styles(display="block", margin=pxx(8, 8, "auto", "auto"),border_style="inset",border_width=pxx(2)))}', unsafe_allow_html=True)
        if state_name != "Все":
            st.write(f'Динамика изменения показателя "{radio}" городского округа {state_name}', )
            colms = st.columns(1)
            fig = go.Figure()

            # with colms[0]:
            #     st.plotly_chart(px.bar(data_frame=df, y=x, x=y, orientation='h').update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True),
            #                     config={'displayModeBar': False})
            fig.add_trace(go.Scatter(x=df[x],
                                     y=df[y],
                                     mode='lines',
                                     opacity=0.7,
                                     # showlegend=True,
                                     legendrank=10,
                                     name=f'Динамика изменения численности населения городского округа {state_name}',
                                     ))
            fig.update_layout(legend_orientation="h", xaxis_fixedrange=True, yaxis_fixedrange=True)
            fig.write_html(r"./file.html")

            with colms[0]:
                config = {'displayModeBar': False}
                st.plotly_chart(fig, config=config, use_container_width=True)

        else:
            df.loc[len(df.index)] = ["Среднее значение по Калининградской области", year,
                                     df['Динамика'].sum() / len(df['Динамика'])]

            df = df.sort_values(by=y)
            st.write(f'Сравнение показателя "{old_catalog[key]}" по округам за {year} г.')

            fig = px.bar(data_frame=df, y='Городские округа:', x=y, orientation='h', text='Городские округа:') \
                .update_xaxes(col='Динамика').update_yaxes(visible=False, showticklabels=False) \
                .update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True, height=600) \
                .update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

            fig.write_html("./file.html")

            st.plotly_chart(fig,
                            config={'displayModeBar': False},
                            use_container_width=True,
                            height=600
                            )
        with open("./file.html") as f:
            st.download_button("Скачать график", f, mime='text/html')


def year_for_display(df: pd.DataFrame):
    df = df['Год'].astype(np.int32)
    year = str(st.sidebar.slider("Год: ", min_value=min(df),
                                 max_value=max(df), value=max(df), step=1))
    return year


def display_region_filter(df: pd.DataFrame, state_name: str):
    state_list = ['Все'] + list(df['Городские округа:'].unique())
    # state_list.sort()
    state_index = state_list.index(state_name) if state_name and state_name in state_list else 0
    return st.sidebar.selectbox(label='Выберите городской округ из списка', options=state_list, index=state_index)


async def display_table(radio, state_name, on_key_table, **kwargs):
    download_folder = kwargs.get('download_folder', )
    folder_name = kwargs.get('folder_name')

    if not download_folder:
        download_folder = 'Данные скачивания таблиц'
    if not folder_name:
        folder_name = "Данные csv"

    list_path_data = [i for i in get_path_data(folder_name)]
    name_data = [i.name for i in list_path_data]

    df = pd.DataFrame()
    for n, i in enumerate(name_data):
        if i[:-4] == radio:
            df = pd.read_csv(f'./{list_path_data[n]}')

    if state_name != "Все":
        df = df[df['Городские округа:'] == state_name]

    if on_key_table:
        st.write(f"""Изменение показателя "{radio}" по годам""")
        st.table(df)
        with pd.ExcelWriter(f"./{download_folder}/{radio}.xlsx", engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, engine='xlsxwriter', sheet_name=radio[0:30] if len(radio) > 30 else radio)

        with open(f"./{download_folder}/{radio}.xlsx", 'rb') as f:
            st.download_button('Скачать таблицу', f,
                               file_name=f'{radio}{"" if state_name == "Все" else f"_{state_name}"}.xlsx')

        st.write('''к - данные не публикуются в целях обеспечения конфиденциальности первичных статистических данных, 
        полученных от организаций, в соответствии с Федеральным законом от 29.11.07 № 282-ФЗ "Об официальном 
        статистическом учете и системе государственной статистики в Российской Федерации" (ст.4, п.5; ст.9, п.1).''')


async def test(state_name: str, data_kld: pd.DataFrame, radio) -> [str, bool]:
    if 'disabled_' not in st.session_state:
        st.session_state.disabled_ = True
        st.session_state.visibility = 'visible'
        st.session_state.disabled_1 = False
        st.session_state.disabled_2 = False
        st.session_state.disabled_3 = True

    st.sidebar.markdown(
        f'{hr(style=styles(display="block", margin=pxx(8, 8, "auto", "auto"), border_style="inset", border_width=pxx(2)))}',
        unsafe_allow_html=True)
    a = st.sidebar.columns(2)
    with a[0]:
        varZ = st.empty()
    with a[1]:
        var3 = st.empty()

    superKey = varZ.checkbox("Выбрать регион")
    mat = var3.checkbox("Таблица", value=True)

    if not superKey:
        state_name = 'Все'

    if superKey:

        variable = ["Кнопками", "Списком"]
        new_radio = st.sidebar.radio("", variable, horizontal=True)

        if new_radio:
            if new_radio == variable[0]:
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
                                if st.button(data_kld[i], key=f'{data_kld[i]}'):
                                    state_name = data_kld[i]

                        no = n
                        n += round(data_len / max_columns)

                if st.sidebar.button("Калининградская область"):
                    state_name = 'Все'
            if new_radio == variable[1]:
                state_name = display_region_filter(state_name=state_name, df=data_kld)
    return state_name, mat


async def test_display_map(year, melt_data: [pd.DataFrame], dict_data: dict, key):
    catalog = [k for k in dict_data.keys()]
    old_dict_data = dict_data
    dict_data = [k for k in dict_data.values()]

    API_key = r'd5833253-f0e7-44f9-a464-6d165eaa39db'

    kld_map = folium.Map(
        location=[54.74726381693468, 21.47545575464152],
        zoom_start=9,
        width=1440,
        scrollWheelZoom=False,
        min_zoom=7,
        max_zoom=10,
        # tiles='Yandex',
        # # tiles=r'https://api-maps.yandex.ru/2.1/?apikey=d5833253-f0e7-44f9-a464-6d165eaa39db&lang=ru_RU',
        # API_key = 'https://api-maps.yandex.ru/2.1/?apikey=d5833253-f0e7-44f9-a464-6d165eaa39db&lang=ru_RU',
        # attr='Yandex'
    )

    kld_map.add_child(folium.TileLayer('openstreetmap', attr=".", show=False, overlay=True))

    kld_map.add_child(get_mouse_position())

    geo_data = get_geodata()[0]

    create_choropleth(geodata=geo_data, data=melt_data[key], index_data=catalog[key], year=year, name=catalog[key],
                      iter=0,
                      enable_this_layer=dict_data[key]).add_to(kld_map)

    folium.LayerControl().add_to(kld_map)
    st_map = st_folium(kld_map, width=1440)
    state_name = 'Все'
    if st_map['last_active_drawing']:
        state_name = st_map['last_active_drawing']['properties']['name']

    return state_name


async def test_main():
    state_name = 'Все'
    on_key_table = False
    melt_data, dict_data = all_data()
    year = year_for_display(melt_data[0])

    labels_keys = {e: i for e, i in enumerate(dict_data.keys())}

    a = get_radio_switch(path='./Данные csv/')
    radio = st.sidebar.radio('Фильтры', a.keys(), key=2, horizontal=True)
    res = st.sidebar.radio(radio, a[radio])

    key = 0
    for n, i in enumerate(dict_data):
        if res == i:
            dict_data[i] = True
            key = n
        else:
            dict_data[i] = False

    state_name = await test_display_map(year, melt_data, dict_data, key)
    temp = await test(state_name, melt_data[0], res)
    if isinstance(temp, tuple):
        state_name, on_key_table = temp

    for e, i in enumerate(labels_keys):
        if res == labels_keys[i]:
            display_facts(df=melt_data[e], year=year, state_name=state_name, var='Динамика',
                          metric_title=f'''{res} {f"городского округа {state_name} на {year} г."
                          if state_name != "Все" else f"Калининградской области за {year} г."}''',
                          minikey=res
                          )
    await bar_chart(df=melt_data,
                    state_name=state_name, x='Год', y='Динамика', year=year, catalog=dict_data, key=key, radio=res)
    await display_table(radio=res, state_name=state_name, on_key_table=on_key_table)
    footer()


@st.cache(persist=True, allow_output_mutation=True)
def all_data() -> tuple[list[Any], dict]:
    melt_data = [i for i in get_melt(gen_type='data')]
    dict_data = {i: False for i in get_melt(gen_type='names')}
    return melt_data, dict_data


if __name__ == '__main__':
    asyncio.run(test_main())
