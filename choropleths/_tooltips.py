def get_my_dict_string(*, feature, index_data: str, year: str):
    v1 = feature["properties"]['name']

    feature = feature["properties"][index_data]

    if index_data:
        a = {f'Прибыло {feature[year]} человек' if int(
            feature[year]) >= 0 else f'Покинуло {abs(int(feature[year]))} человек'}

    width_h4 = len(index_data) * 10

    # if len(index_data) > 30:
    #     i_max = 30
    #     index_data = [index_data[i:i+i_max] for i in range(0, len(index_data), i_max)]
    #
    #     index_data = "-</br>".join(index_data)



    my_td = '''
    <!DOCTYPE html><html><head>
        <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
        <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
        <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
    </head>'''
    my_td += f'''
    <Body style="background-color:white;width: 3302px">
        <h4 style="color:rgb(2, 0, 105);background-color: oldlace;bottom:0px; padding-bottom:0px;margin-bottom: 0px; margin-top: 5px; margin-left:2px;width: {width_h4}px">{index_data}</h4>
     <table style="margin-left:0px;">
        <tbody>
             <tr><td style= background-color:oldlace;width:{width_h4}px> <span style= columns:#343434;3434>Мун.Образование:   </span></td>
                 <td style= background-color:oldlace;width:{width_h4}px;> <span style= color:#343434> {v1}</span> </tr>
        '''

    if year:
        my_td += f'''
        <tr><td style= background-color:oldlace;width:300px> <span style= columns:#343434;3434>{year} г.:</span> </td>
        <td style= background-color:oldlace;width:600px;padding-left:15px> <span style= color:#343434> {feature[year]} </span> </tr>'''

    my_td += f'''</tbody></table>'''

    my_td += f'''</Body>'''

    return my_td
