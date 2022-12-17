from folium.plugins import MousePosition


def __mouse_position():
    formatter = "function(num) {return L.Util.formatNum(num, 5);};"
    mouse = MousePosition(
        position='topright',
        separator=' Долгота: ',
        empty_string='NaN',
        lng_first=False,
        num_digits=20,
        prefix='Широта:',
        lat_formatter=formatter,
        lng_formatter=formatter,
    )
    return mouse
