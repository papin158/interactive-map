import folium, colorsys, _tooltips
import numpy as np

def init_style(year, data_loc):
    data = data_loc
    data = data[(data['Год'] == year)]

    return data

def style_function_suburb(feature, index_data, year: str):
    k1 = feature["properties"][index_data]
    data = init_style(year, k1)['Динамика']
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

def generate_choropleth(geodata, index_data, year, name):
        fg1 = folium.FeatureGroup(name=name, show=True)
        for feature in geodata['features']:
                gmc = folium.GeoJson(feature,
                                     style_function=lambda feature: {  # Меняет цветовую схему в статичном режиме
                                             'fillColor': style_function_suburb(feature, index_data, year),
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
                tooltip = _tooltips.get_my_dict_string(feature=feature, index_data=index_data, year=year)
                #folium.Html(tooltip, script=True)  # pg; create HTML
                folium.Tooltip(tooltip).add_to(gmc)  # tol1;

                gmc.add_to(fg1)

