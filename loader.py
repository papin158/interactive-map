import warnings
import geopandas as gpd

from data import _all_geo_data
from choropleths import _tooltips


def get_geodata():
    """
    Выдаёт все данные связанные с CSV файлами.
    """
    return _all_geo_data._get_geojson_modification()


def get_melt(var_name: str = None, value_name: str = None, gen_type: str = None):
    """
    Генератор динамики, возвращает муниципалитет:год:динамика
    """
    return _all_geo_data._get_all_melt(var_name=var_name, value_name=value_name, gen_type=gen_type)


def display_facts(df, year, metric_title, var: str = None, state_name=None):
    """
    Выводит на экран статистику по региону или муниципалитету
    """
    return _all_geo_data._display_fraud_facts(df, year, metric_title, var, state_name)


def get_tooltip(feature: gpd.GeoDataFrame, index_data: str, *, year: str = None):
    """
    Возвращает html-код для folium.choropleth, который показывает информацию при наведении
    """
    return _tooltips.get_my_dict_string(feature=feature, index_data=index_data, year=year)
