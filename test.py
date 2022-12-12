import altair as alt
import branca
import folium
import pandas as pd

two_charts_template = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
</head>
<body>

<div id="vis1"></div>
<div id="vis2"></div>

<script type="text/javascript">
  vegaEmbed('#vis1', {spec1}).catch(console.error);
  vegaEmbed('#vis2', {spec2}).catch(console.error);
</script>
</body>
</html>
"""


df = pd.DataFrame({'x': range(5), 'y': range(5)})

chart1 = alt.Chart(df).mark_point().encode(x='x', y='y')
chart2 = alt.Chart(df).mark_line().encode(x='x', y='y')

with open('charts.html', 'w') as f:
    f.write(two_charts_template.format(
        vega_version=alt.VEGA_VERSION,
        vegalite_version=alt.VEGALITE_VERSION,
        vegaembed_version=alt.VEGAEMBED_VERSION,
        spec1=chart1.to_json(indent=None),
        spec2=chart2.to_json(indent=None),
    ))

html_file = open('charts.html', 'r', encoding='utf-8')
charts_code = html_file.read()

# In case a file is not needed a direct assignment can be used
# charts_code = two_charts_template.format(
#            vega_version=alt.VEGA_VERSION,
#            vegalite_version=alt.VEGALITE_VERSION,
#            vegaembed_version=alt.VEGAEMBED_VERSION,
#            spec1=chart1.to_json(indent=None),
#            spec2=chart2.to_json(indent=None),
#        )
a_map = folium.Map()

iframe = branca.element.IFrame(html=charts_code, width=1500, height=400)
popup = folium.Popup(iframe, max_width=2000)

folium.Marker([51.5,-0.11], popup=popup).add_to(a_map)
a_map