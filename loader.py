import warnings
import geopandas as gpd
import pandas as pd

from data import _all_geo_data
from choropleths import _choropleth, _mouse_position
from HTML.Footer import __customize_footer_streamlit__
from tables import tables


def get_geodata():
    """
    Выдаёт все данные связанные с CSV файлами.
    """
    return _all_geo_data._get_geojson_modification()


def get_melt(var_name: str = None, value_name: str = None, gen_type: str = None):
    """
    Генератор динамики, возвращает муниципалитет:год:динамика

    :param var_name: Название второй строки (по умолчанию - год)
    :param value_name: Название третьей строки (по умолчанию - динамика)
    :param gen_type: Выбор возвращаемого генератора, data -> возвращает данные таблиц,
    name -> возвращает наименования файлов, которые были записаны в geojson как ключи.
    """
    return _all_geo_data._get_all_melt(var_name=var_name, value_name=value_name, gen_type=gen_type)


def display_facts(df, year, metric_title, var: str = None, state_name=None, minikey=None):
    """
    Выводит на экран статистику по региону или муниципалитету
    """
    return _all_geo_data._display_fraud_facts(df, year, metric_title, var, state_name, minikey)


# def get_tooltip(feature: gpd.GeoDataFrame, index_data: str, *, year: str = None):
#     """
#     Возвращает html-код для folium.choropleth, который показывает информацию при наведении
#     """
#     return _tooltips.get_my_dict_string(feature=feature, index_data=index_data, year=year)

def get_mouse_position():
    """
    Выводит в правом верхнем углу при наведении указателя мыши данные о долготе и широте
    """
    return _mouse_position.__mouse_position()

def create_choropleth(*, geodata: gpd.GeoDataFrame, data: pd.DataFrame, index_data: str, year: str, name: str, iter: int, enable_this_layer: bool):
    """
    Создаёт и возвращает пользователю уже сгенерированный слой
    """
    return _choropleth._generate_choropleth(geodata=geodata, data=data, index_data=index_data, year=year, name=name, iter=iter, enable_this_layer=enable_this_layer)

def footer():
    return __customize_footer_streamlit__.footer()


def get_radio_switch(path):
    """
    Воссоздаёт переключатели в боковой панели

    :param path: = обязательная директория.
    """
    return tables.__get_derictories(path=path)

def get_path_data(path):
    return _all_geo_data.get_all_data(path)